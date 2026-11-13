"""Serialization and persisted-output options for compute jobs.

This module provides the mixin that persists and restores dataset outputs,
along with the public option enums used to control that behavior.

Attributes:
    ConfigPersistOpts: Runtime configuration enum that defines the default
        persistence policy for flows and tasks.
    PersistOpts: Enum that controls whether a job persists its outputs after a
        successful run.
    RestoreOpts: Enum that controls whether a job restores previously
        persisted outputs instead of recomputing them.
    ProtocolOpts: Enum that selects the storage and serialization protocol used
        for persisted outputs.
"""

import asyncio
from collections.abc import Awaitable, Generator
from datetime import datetime
import inspect
import os
from pathlib import Path
from textwrap import dedent
from typing import cast

from omnipy.components import get_serializer_registry
from omnipy.compute._mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute._mixins.name import NameJobBaseMixin
from omnipy.data.dataset import Dataset, is_dataset_instance, is_dataset_subclass
from omnipy.data.model import is_model_instance, is_model_subclass
from omnipy.shared.enums.job import ConfigPersistOutputsOptions as ConfigPersistOpts
from omnipy.shared.enums.job import (
    OutputStorageProtocolOptions,
    PersistOutputsOptions,
    RestoreOutputsOptions,
)
from omnipy.shared.protocols.compute.job import IsFlow, IsJob, IsJobBase
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.data import IsSerializerRegistry
from omnipy.util.helpers import get_job_name_slug, is_package_editable
from omnipy.util.mixin import strip_mixins_suffix

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_SERIALIZE_ARG_DOC'] = dedent("""\
            persist_outputs: Per-job output-persistence preference.
            restore_outputs: Per-job output-restore preference.""")

PersistOpts = PersistOutputsOptions
"""Options enum for controlling whether job outputs are persisted."""

RestoreOpts = RestoreOutputsOptions
"""Options enum for controlling whether persisted outputs are restored."""

ProtocolOpts = OutputStorageProtocolOptions
"""Options enum for selecting the output storage and serialization protocol."""

PERSISTED_VALUE_KEY = 'value'
"""Key under which results that are neither models nor datasets are persisted.

Such results are stored as a JSON dataset with one item, ``{"value": <result>}``. The value is
wrapped because JSON models parse top-level strings as JSON, which would turn a string result
such as ``'1'`` into a number.
"""


def _is_unpersistable_result(results: object) -> bool:
    return results is None or inspect.isgenerator(results) or inspect.isasyncgen(results)


class SerializerFuncJobBaseMixin:
    """Mixin that adds automatic dataset output persistence and restoration.

    Jobs using this mixin can restore previously serialized dataset outputs
    before execution and persist new dataset outputs after execution according
    to the selected option enums and runtime configuration.
    """

    _serializer_registry: IsSerializerRegistry | None = None

    def __init__(
        self,
        *,
        persist_outputs: PersistOutputsOptions.Literals = PersistOpts.FOLLOW_CONFIG,
        restore_outputs: RestoreOutputsOptions.Literals = RestoreOpts.FOLLOW_CONFIG,
        output_storage_protocol: OutputStorageProtocolOptions.Literals = ProtocolOpts.FOLLOW_CONFIG,
    ):

        # TODO: Possibly reimplement logic using a state machine, e.g. "transitions" package
        self._persist_outputs: PersistOutputsOptions.Literals = persist_outputs
        self._restore_outputs: RestoreOutputsOptions.Literals = restore_outputs
        self._output_storage_protocol: OutputStorageProtocolOptions.Literals = (
            output_storage_protocol
        )

    @property
    def _job_config(self) -> IsJobConfig:
        self_as_job_base = cast(IsJobBase, self)
        return self_as_job_base.config

    def _log(self, msg: str) -> None:
        self_as_job_base = cast(IsJobBase, self)
        self_as_job_base.log_message(msg)

    @property
    def _return_type(self) -> type[object]:
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)
        return self_as_signature_func_job_base_mixin.return_type

    @property
    def persist_outputs(self) -> PersistOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_PERSIST_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_PERSIST_OUTPUTS_DETAILS}}
        """Return the configured per-job output-persistence preference.

        Returns:
            PersistOutputsOptions.Literals: Persistence setting before config fallback.
        """
        return self._persist_outputs

    @property
    def restore_outputs(self) -> RestoreOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_RESTORE_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_RESTORE_OUTPUTS_DETAILS}}
        """Return the configured per-job output-restore preference.

        Returns:
            RestoreOutputsOptions.Literals: Restore setting before config fallback.
        """
        return self._restore_outputs

    @property
    def output_storage_protocol(self) -> OutputStorageProtocolOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_DETAILS}}
        """Return the configured output-storage protocol preference.

        Returns:
            OutputStorageProtocolOptions.Literals: Storage-protocol setting before
                config fallback.
        """
        return self._output_storage_protocol

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_WILL_PERSIST_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_WILL_PERSIST_OUTPUTS_DETAILS}}
        """Return the resolved output-persistence behavior for this run.

        Returns:
            PersistOutputsOptions.Literals: Effective persistence behavior after
                applying config-following rules.
        """
        if self._persist_outputs is not PersistOpts.FOLLOW_CONFIG:
            return self._persist_outputs
        else:
            # TODO: Refactor using Flow and Task Mixins
            from omnipy.compute.flow import FlowBase
            from omnipy.compute.task import TaskBase

            match self._job_config.output_storage.persist_outputs:
                case ConfigPersistOpts.ENABLE_FLOW_OUTPUTS:
                    return (
                        PersistOpts.ENABLED if isinstance(self, FlowBase) else PersistOpts.DISABLED
                    )
                case ConfigPersistOpts.ENABLE_FLOW_AND_TASK_OUTPUTS:
                    return (
                        PersistOpts.ENABLED
                        if any(isinstance(self, cls) for cls in (FlowBase, TaskBase))
                        else PersistOpts.DISABLED
                    )
                case ConfigPersistOpts.DISABLED:
                    return PersistOpts.DISABLED

    @property
    def will_restore_outputs(self) -> RestoreOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_WILL_RESTORE_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_WILL_RESTORE_OUTPUTS_DETAILS}}
        """Return the resolved output-restore behavior for this run.

        Returns:
            RestoreOutputsOptions.Literals: Effective restore behavior after applying
                config-following rules.
        """
        if self._restore_outputs is RestoreOpts.FOLLOW_CONFIG:
            return self._job_config.output_storage.restore_outputs
        else:
            return self._restore_outputs

    @property
    def output_storage_protocol_to_use(self) -> OutputStorageProtocolOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_TO_USE_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_TO_USE_DETAILS}}
        """Return the resolved storage protocol used for persisted outputs.

        Returns:
            OutputStorageProtocolOptions.Literals: Effective storage protocol for this
                run.
        """
        if self._output_storage_protocol is ProtocolOpts.FOLLOW_CONFIG:
            return self._job_config.output_storage.protocol
        else:
            return self._output_storage_protocol

    def _call_job(self, *args: object, **kwargs: object) -> object:
        if self._serializer_registry is None:
            self._serializer_registry = get_serializer_registry()

        if self.will_restore_outputs in [
            RestoreOpts.AUTO_ENABLE_IGNORE_PARAMS,
            RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS,
        ]:
            try:
                return self._deserialize_and_restore_outputs()
            except Exception:
                if self.will_restore_outputs is RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS:
                    raise

        super_as_job_base = cast(IsJobBase, super())
        results = super_as_job_base._call_job(*args, **kwargs)

        if self.will_persist_outputs is PersistOpts.ENABLED:
            if isinstance(results, asyncio.Task):

                def _persist_task_outputs(task: asyncio.Task) -> None:
                    self._serialize_and_persist_outputs(task.result())

                results.add_done_callback(_persist_task_outputs)
            elif inspect.isawaitable(results):

                async def _async_persist_outputs(results: Awaitable) -> object:
                    awaited_results = await results
                    self._serialize_and_persist_outputs(awaited_results)
                    return awaited_results

                return _async_persist_outputs(results)
            else:
                self._serialize_and_persist_outputs(results)

        return results

    def _is_final_output(self) -> bool:
        """Return whether this job's results are the final output of a run, not of a flow step."""
        return not cast(IsJobBase, self).in_flow_context

    def _persist_failed(self, msg: str) -> None:
        if self._is_final_output():
            raise RuntimeError(msg)
        self._log(msg)

    def _serialize_and_persist_outputs(self, results: object) -> None:
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)

        if _is_unpersistable_result(results):
            self._log(
                f'Results of {self_as_name_job_base_mixin.unique_name} are empty or a generator, '
                'and are not persisted'
            )
            return

        if is_model_instance(results):
            results = Dataset[results.__class__]({self._job_name(): results})
        elif not is_dataset_instance(results):
            from omnipy.components.json.datasets import JsonDataset

            try:
                results = JsonDataset({self._job_name(): {PERSISTED_VALUE_KEY: results}})
            except Exception as exc:
                self._persist_failed(
                    f'Results of {self_as_name_job_base_mixin.unique_name} are neither a Model, '
                    f'a Dataset nor JSON-compatible, and cannot be persisted: {exc}'
                )
                return

        assert self._serializer_registry is not None

        datetime_str = self._generate_datetime_str()
        output_path = Path(self._job_config.output_storage.local.persist_data_dir_path).joinpath(
            datetime_str
        )

        os.makedirs(output_path, exist_ok=True)

        num_cur_files = len(os.listdir(output_path))
        job_name = self._job_name()

        file_path = output_path.joinpath(f'{num_cur_files:02}_{job_name}.tar.gz')

        parsed_dataset, serializer = self._serializer_registry.auto_detect_tar_file_serializer(
            results
        )

        if serializer is None:
            self._persist_failed(
                'Unable to find a serializer for results of job '
                f'"{self_as_name_job_base_mixin.name}", with data type "{type(results)}". '
                f'Will abort persisting results...'
            )
        else:
            assert parsed_dataset is not None
            self._log(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(file_path)}"')

            with open(file_path, 'wb') as tarfile:
                tarfile.write(serializer.serialize(parsed_dataset))

    def _job_name(self):
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)
        job_cls_name = strip_mixins_suffix(self.__class__.__name__)

        assert self_as_name_job_base_mixin.name is not None
        return get_job_name_slug(job_cls_name, self_as_name_job_base_mixin.name).replace('-', '_')

    def _generate_datetime_str(self):
        self_as_job = cast(IsJob, self)

        if self_as_job.time_of_cur_toplevel_flow_run:
            run_time = self_as_job.time_of_cur_toplevel_flow_run
        else:
            self_as_flow = cast(IsFlow, self)
            if hasattr(self, 'time_of_last_run') and self_as_flow.time_of_last_run:
                run_time = self_as_flow.time_of_last_run
            else:
                run_time = datetime.now()

        datetime_str = run_time.strftime('%Y_%m_%d-%H_%M_%S')
        return datetime_str

    @staticmethod
    def _all_job_output_file_paths_in_reverse_order_for_last_run(
        persist_data_dir_path: Path, job_name: str
    ) -> Generator[Path, None, None]:

        # Only run folders count; other entries, such as a log file, are skipped
        run_dir_names = [
            name
            for name in os.listdir(persist_data_dir_path)
            if (persist_data_dir_path / name).is_dir()
        ]
        sorted_date_dirs = iter(reversed(sorted(run_dir_names)))

        try:
            last_dir = next(sorted_date_dirs)
        except StopIteration:
            raise

        last_dir_path = persist_data_dir_path / last_dir
        for job_output_name in reversed(sorted(os.listdir(last_dir_path))):
            name_part_of_filename = job_output_name[3:-7]
            if name_part_of_filename == job_name:
                yield last_dir_path / job_output_name

    # TODO: Further refactor _deserialize_and_restore_outputs
    def _deserialize_and_restore_outputs(
        self, persist_data_dir_path: str | Path | None = None
    ) -> object:
        """Load the newest persisted output of this job from the last run folder.

        Args:
            persist_data_dir_path: Directory holding the run folders. Defaults to the configured
                local output directory. A client loading the outputs of a remote run passes the
                downloaded output directory.

        Returns:
            object: The restored dataset, or for jobs whose return type is neither a Model nor a
                Dataset, the restored JSON value.

        Raises:
            RuntimeError: If no persisted output of this job is found.
        """
        if self._serializer_registry is None:
            self._serializer_registry = get_serializer_registry()

        self_as_job_base = cast(IsJobBase, self)

        if persist_data_dir_path is None:
            persist_data_dir_path = self._job_config.output_storage.local.persist_data_dir_path
        persist_data_dir_path = Path(persist_data_dir_path)

        if os.path.exists(persist_data_dir_path):
            for tar_file_path in self._all_job_output_file_paths_in_reverse_order_for_last_run(
                persist_data_dir_path, self._job_name()
            ):
                if is_model_subclass(self._return_type) or is_dataset_subclass(self._return_type):
                    to_dataset = cast(type[Dataset], self._return_type)
                    return self._serializer_registry.load_from_tar_file_path_based_on_file_suffix(
                        self_as_job_base, str(tar_file_path), to_dataset()
                    )
                return self._load_persisted_value(str(tar_file_path))

        raise RuntimeError('No persisted output')

    def _load_persisted_value(self, tar_file_path: str) -> object:
        from omnipy.components.json.datasets import JsonDataset

        assert self._serializer_registry is not None
        dataset = self._serializer_registry.load_from_tar_file_path_based_on_file_suffix(
            cast(IsJobBase, self), tar_file_path, JsonDataset()
        )
        assert dataset is not None
        data = dataset.to_data()
        item = data.get(self._job_name()) if isinstance(data, dict) else None
        if isinstance(item, dict) and set(item) == {PERSISTED_VALUE_KEY}:
            return item[PERSISTED_VALUE_KEY]
        return dataset


# TODO: Add configuration option for serialize mixin to specify per flow to not preserve
#       task outputs
