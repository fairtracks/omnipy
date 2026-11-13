"""Tests for job bundles and `python -m omnipy run`."""

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Annotated

import pytest

from omnipy import Dataset, Model
from omnipy.hub.job_bundle import (
    BUNDLE_MANIFEST_FILE,
    JobBundleError,
    load_job_bundle_result,
    LOG_FILE,
    OUTPUTS_DIR,
    run_job_bundle,
    write_job_bundle,
)
from omnipy.shared.protocols.hub.runtime import IsRuntime

from .helpers import bundle_jobs

JOBS_MODULE = bundle_jobs.__name__
REPO_ROOT = Path(__file__).parents[2]


def _ref(name: str) -> str:
    return f'{JOBS_MODULE}:{name}'


def _run(runtime: IsRuntime, bundle_dir: Path, name: str, **write_kwargs: object) -> object:
    write_job_bundle(bundle_dir, _ref(name), config=runtime.config, **write_kwargs)  # type: ignore[arg-type]
    return run_job_bundle(_ref(name), bundle_dir, runtime=runtime)


def test_scalar_result_round_trip(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    assert _run(runtime, tmp_path, 'add', params={'a': 1, 'b': 2}) == 3
    assert load_job_bundle_result(bundle_jobs.add, tmp_path / OUTPUTS_DIR) == 3


def test_string_result_that_looks_like_json_is_kept(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    assert _run(runtime, tmp_path, 'echo_text', params={'text': '1'}) == '1'
    assert load_job_bundle_result(bundle_jobs.echo_text, tmp_path / OUTPUTS_DIR) == '1'


def test_dataset_input_and_output(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    data = Dataset[Model[int]]({'x': 1, 'y': 2})

    result = _run(runtime, tmp_path, 'double_values', inputs={'data': data})
    assert result == Dataset[Model[int]]({'x': 2, 'y': 4})

    loaded = load_job_bundle_result(bundle_jobs.double_values, tmp_path / OUTPUTS_DIR)
    assert loaded == Dataset[Model[int]]({'x': 2, 'y': 4})


def test_model_input(runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path) -> None:
    items = Model[list[int]]([1, 2, 3])
    assert _run(runtime, tmp_path, 'count_items', inputs={'items': items}) == 3


def test_flow_result_is_persisted(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    assert _run(runtime, tmp_path, 'plus_two', params={'number': 1}) == 3
    assert load_job_bundle_result(bundle_jobs.plus_two, tmp_path / OUTPUTS_DIR) == 3

    tar_files = list((tmp_path / OUTPUTS_DIR).glob('*/*.tar.gz'))
    assert [path.name for path in tar_files] == ['00_linear_flow_plus_two.tar.gz']


def test_submitting_config_is_applied_except_engine(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    runtime.config.data.model.dynamically_convert_elements_to_models = True
    runtime.config.engine.choice = 'prefect'
    write_job_bundle(tmp_path, _ref('dynamic_conversion_setting'), config=runtime.config)

    runtime.config.data.model.dynamically_convert_elements_to_models = False
    runtime.config.engine.choice = 'local'

    assert run_job_bundle(_ref('dynamic_conversion_setting'), tmp_path, runtime=runtime) is True
    assert runtime.config.engine.choice == 'local'
    assert runtime.config.job.output_storage.local.persist_data_dir_path == str(
        tmp_path / OUTPUTS_DIR
    )


def test_log_is_written_to_outputs(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    _run(runtime, tmp_path, 'add', params={'a': 1, 'b': 2})

    log_text = (tmp_path / OUTPUTS_DIR / LOG_FILE).read_text()
    assert 'task-add' in log_text


def test_version_mismatch_is_rejected(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    write_job_bundle(tmp_path, _ref('add'), params={'a': 1, 'b': 2}, config=runtime.config)
    manifest_path = tmp_path / BUNDLE_MANIFEST_FILE
    manifest = json.loads(manifest_path.read_text())
    manifest['omnipy_version'] = '0.0.1'
    manifest_path.write_text(json.dumps(manifest))

    with pytest.raises(JobBundleError, match='same Omnipy version'):
        run_job_bundle(_ref('add'), tmp_path, runtime=runtime)


def test_other_job_is_rejected(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    write_job_bundle(tmp_path, _ref('add'), params={'a': 1, 'b': 2}, config=runtime.config)

    with pytest.raises(JobBundleError, match='is for job'):
        run_job_bundle(_ref('echo_text'), tmp_path, runtime=runtime)


def test_unpersistable_final_output_is_an_error(
    runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path
) -> None:
    with pytest.raises(RuntimeError, match='cannot be persisted'):
        _run(runtime, tmp_path, 'unpersistable')


def test_command_line_run(runtime: Annotated[IsRuntime, pytest.fixture], tmp_path: Path) -> None:
    bundle_dir = tmp_path / 'bundle'
    write_job_bundle(bundle_dir, _ref('add'), params={'a': 20, 'b': 22}, config=runtime.config)

    env = os.environ | {'PYTHONPATH': str(REPO_ROOT)}
    completed = subprocess.run(
        [sys.executable, '-m', 'omnipy', 'run', _ref('add'), str(bundle_dir)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert completed.returncode == 0, completed.stderr
    assert load_job_bundle_result(bundle_jobs.add, bundle_dir / OUTPUTS_DIR) == 42
    assert (bundle_dir / OUTPUTS_DIR / LOG_FILE).exists()
