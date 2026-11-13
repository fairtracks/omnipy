"""Job bundles: the files that carry one job run to another machine and back.

A job bundle is a directory with this layout::

    bundle.json          versions and the job reference, checked by the worker
    params.json          JSON-compatible keyword arguments of the job
    config.json          portable runtime config of the submitting machine
    inputs/<name>.tar.gz one gzipped tar per dataset or model argument
    outputs/             written by the worker: persisted outputs and the omnipy log

[`write_job_bundle`][omnipy.hub.job_bundle.write_job_bundle] creates a bundle on the submitting
machine. ``python -m omnipy run <module:job> <bundle dir>`` runs the job on any machine with the
same Omnipy version, using [`run_job_bundle`][omnipy.hub.job_bundle.run_job_bundle]. The
outputs are written through output persistence, and
[`load_job_bundle_result`][omnipy.hub.job_bundle.load_job_bundle_result] reads the result back.
"""

import argparse
from collections.abc import Mapping, Sequence
import importlib
import json
import logging
from pathlib import Path
import platform
import sys
from typing import Any, cast

from omnipy.shared.enums.job import (
    ConfigPersistOutputsOptions,
    ConfigRestoreOutputsOptions,
    PersistOutputsOptions,
)

BUNDLE_MANIFEST_FILE = 'bundle.json'
PARAMS_FILE = 'params.json'
CONFIG_FILE = 'config.json'
INPUTS_DIR = 'inputs'
OUTPUTS_DIR = 'outputs'
LOG_FILE = 'omnipy.log'

_logger = logging.getLogger(__name__)


class JobBundleError(Exception):
    """Raised when a job bundle cannot be run, for example on a version mismatch."""


def _omnipy_version() -> str:
    import omnipy

    return omnipy.__version__


def _python_version() -> str:
    return '.'.join(platform.python_version_tuple()[:2])


def _import_job(job_ref: str) -> Any:
    module_name, sep, attr_path = job_ref.partition(':')
    if not sep or not module_name or not attr_path:
        raise JobBundleError(f'Job reference "{job_ref}" must have the form "module:job"')

    obj: Any = importlib.import_module(module_name)
    for attr in attr_path.split('.'):
        obj = getattr(obj, attr)
    return obj


def _serialize_input(name: str, value: object, tar_file_path: Path) -> None:
    from omnipy.components import get_serializer_registry
    from omnipy.data.dataset import Dataset, is_dataset_instance
    from omnipy.data.model import is_model_instance

    if is_model_instance(value):
        value = cast(Any, Dataset)[value.__class__]({name: value})
    if not is_dataset_instance(value):
        raise JobBundleError(f'Input "{name}" is neither a Model nor a Dataset')

    parsed_dataset, serializer = get_serializer_registry().auto_detect_tar_file_serializer(value)
    if serializer is None or parsed_dataset is None:
        raise JobBundleError(f'No serializer found for input "{name}" of type {type(value)}')
    tar_file_path.write_bytes(serializer.serialize(parsed_dataset))


def write_job_bundle(
    bundle_dir: str | Path,
    job_ref: str,
    params: Mapping[str, object] | None = None,
    inputs: Mapping[str, object] | None = None,
    config: Any | None = None,
) -> Path:
    """Write a job bundle for running a job on another machine.

    Args:
        bundle_dir: Directory to write the bundle to. Created if needed.
        job_ref: Import reference of the job template, as ``"module:job"``.
        params: JSON-compatible keyword arguments of the job.
        inputs: Keyword arguments that are Omnipy models or datasets, stored as gzipped tars.
        config: Runtime config to send along, by default the config of the global runtime.
            Secrets and machine-local values are left out.

    Returns:
        Path: The bundle directory.

    Raises:
        JobBundleError: If an input cannot be serialized.
        TypeError: If ``params`` is not JSON-compatible.
    """
    bundle_path = Path(bundle_dir)
    (bundle_path / INPUTS_DIR).mkdir(parents=True, exist_ok=True)
    (bundle_path / OUTPUTS_DIR).mkdir(exist_ok=True)

    if config is None:
        from omnipy.hub.runtime import runtime

        config = runtime.config

    manifest = {
        'omnipy_version': _omnipy_version(),
        'python_version': _python_version(),
        'job': job_ref,
    }
    (bundle_path / BUNDLE_MANIFEST_FILE).write_text(json.dumps(manifest, indent=2))
    (bundle_path / PARAMS_FILE).write_text(json.dumps(dict(params or {}), indent=2))
    (bundle_path / CONFIG_FILE).write_text(json.dumps(config.to_portable_dict(), indent=2))

    for name, value in (inputs or {}).items():
        _serialize_input(name, value, bundle_path / INPUTS_DIR / f'{name}.tar.gz')

    return bundle_path


def _check_manifest(bundle_path: Path, job_ref: str) -> None:
    manifest = json.loads((bundle_path / BUNDLE_MANIFEST_FILE).read_text())

    bundle_version = manifest.get('omnipy_version')
    if bundle_version != _omnipy_version():
        raise JobBundleError(
            f'The job bundle was written by Omnipy {bundle_version}, but this is Omnipy '
            f'{_omnipy_version()}. Remote runs need the same Omnipy version on both sides.'
        )

    bundle_job = manifest.get('job')
    if bundle_job is not None and bundle_job != job_ref:
        raise JobBundleError(f'The job bundle is for job "{bundle_job}", not "{job_ref}"')

    bundle_python = manifest.get('python_version')
    if bundle_python is not None and bundle_python != _python_version():
        _logger.warning(
            f'The job bundle was written with Python {bundle_python}, but this is Python '
            f'{_python_version()}. Results may differ.'
        )


def _apply_config(runtime: Any, bundle_path: Path) -> None:
    config_path = bundle_path / CONFIG_FILE
    if config_path.exists():
        portable = json.loads(config_path.read_text())
        # The engine section belongs to the submitting side; the worker runs jobs locally
        portable.pop('engine', None)
        runtime.config.update_from_portable_dict(portable)

    runtime.config.engine.choice = 'local'

    output_storage = runtime.config.job.output_storage
    output_storage.local.persist_data_dir_path = str(bundle_path / OUTPUTS_DIR)
    output_storage.protocol = 'local'
    output_storage.restore_outputs = ConfigRestoreOutputsOptions.DISABLED
    if output_storage.persist_outputs != ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS:
        output_storage.persist_outputs = ConfigPersistOutputsOptions.ENABLE_FLOW_OUTPUTS

    root_log = runtime.config.root_log
    root_log.file_log_path = str(bundle_path / OUTPUTS_DIR / LOG_FILE)
    root_log.file_log_min_level = root_log.stdout_log_min_level
    root_log.log_to_file = True


def _load_input(job: Any, name: str, tar_file_path: Path) -> object:
    from omnipy.components import get_serializer_registry
    from omnipy.data.dataset import Dataset, is_dataset_subclass
    from omnipy.data.model import is_model_subclass

    registry = get_serializer_registry()
    param = job.param_signatures.get(name)
    annotation: Any = param.annotation if param is not None else None

    if is_dataset_subclass(annotation):
        dataset = registry.load_from_tar_file_path_based_on_file_suffix(
            _logger.info, str(tar_file_path), annotation()
        )
        return dataset if isinstance(dataset, annotation) else annotation(dataset)

    if is_model_subclass(annotation):
        dataset = registry.load_from_tar_file_path_based_on_file_suffix(
            _logger.info, str(tar_file_path), cast(Any, Dataset)[annotation]()
        )
        assert dataset is not None
        return annotation(next(iter(dataset.values())))

    dataset = registry.load_from_tar_file_path_based_on_file_suffix(
        _logger.info, str(tar_file_path), Dataset()
    )
    return dataset


def run_job_bundle(job_ref: str, bundle_dir: str | Path, runtime: Any | None = None) -> object:
    """Run the job of a job bundle, writing its outputs and log to the bundle's output directory.

    The worker checks that the bundle was written by the same Omnipy version, applies the
    submitting machine's portable config except its engine section, and runs the job on the local
    engine. Outputs are persisted to ``outputs/``: the result of the job always, the results of
    nested flows by default, and the outputs of all steps if the submitting config persists all
    outputs.

    Args:
        job_ref: Import reference of the job template, as ``"module:job"``.
        bundle_dir: Directory of the job bundle.
        runtime: Runtime to configure, by default the global runtime.

    Returns:
        object: The result of the job.

    Raises:
        JobBundleError: If the bundle was written by another Omnipy version or for another job.
    """
    bundle_path = Path(bundle_dir)
    _check_manifest(bundle_path, job_ref)

    if runtime is None:
        from omnipy.hub.runtime import runtime as global_runtime

        runtime = global_runtime

    _apply_config(runtime, bundle_path)
    (bundle_path / OUTPUTS_DIR).mkdir(exist_ok=True)

    job_template = _import_job(job_ref)
    kwargs: dict[str, object] = json.loads((bundle_path / PARAMS_FILE).read_text())

    inputs_path = bundle_path / INPUTS_DIR
    if inputs_path.exists():
        for tar_file_path in sorted(inputs_path.glob('*.tar.gz')):
            name = tar_file_path.name.removesuffix('.tar.gz')
            kwargs[name] = _load_input(job_template, name, tar_file_path)

    sizes = {
        key: len(cast(Any, val)) if hasattr(val, '__len__') else 1 for key, val in kwargs.items()
    }
    _logger.info(f'Running job "{job_ref}" with arguments {sorted(kwargs)} (sizes: {sizes})')

    # The result of the job itself is always persisted, whatever the config says for the steps
    persisted_job_template = job_template.refine(persist_outputs=PersistOutputsOptions.ENABLED)
    return persisted_job_template.run(**kwargs)


def load_job_bundle_result(job_template: Any, outputs_dir: str | Path) -> object:
    """Load the result of a job run from the output directory of a job bundle.

    Args:
        job_template: The job template that was run.
        outputs_dir: The bundle's output directory, or a downloaded copy of it.

    Returns:
        object: The restored result, as a dataset, or as a JSON value for jobs whose return type
            is neither a Model nor a Dataset.
    """
    from omnipy.data.dataset import is_dataset_subclass

    job = job_template.apply()
    result = job._deserialize_and_restore_outputs(outputs_dir)

    # Restore returns the deserialized dataset when its type differs from the declared one
    return_type = job.return_type
    if is_dataset_subclass(return_type) and not isinstance(result, return_type):
        return return_type(result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    """Run ``python -m omnipy run``.

    Args:
        argv: Command line arguments after ``run``.

    Returns:
        int: Exit code, 0 on success.
    """
    parser = argparse.ArgumentParser(
        prog='python -m omnipy run',
        description=(
            'Run a job from a job bundle, writing its outputs and log to the output directory of '
            'the bundle. Used by engines that run jobs on other machines.'
        ),
    )
    parser.add_argument('job', help='Import reference of the job template, as "module:job".')
    parser.add_argument('bundle_dir', type=Path, help='Directory of the job bundle.')
    args = parser.parse_args(argv)

    try:
        run_job_bundle(args.job, args.bundle_dir)
    except JobBundleError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    return 0
