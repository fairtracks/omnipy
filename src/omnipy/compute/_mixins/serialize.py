from datetime import datetime
import os
from pathlib import Path
from typing import cast, Generator, Type

from omnipy.components import get_serializer_registry
from omnipy.compute._mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute._mixins.name import NameJobBaseMixin
from omnipy.data.dataset import Dataset
from omnipy.shared.enums import ConfigPersistOutputsOptions as ConfigPersistOpts
from omnipy.shared.enums import ConfigRestoreOutputsOptions as ConfigRestoreOpts
from omnipy.shared.enums import (OutputStorageProtocolOptions,
                                 PersistOutputsOptions,
                                 RestoreOutputsOptions)
from omnipy.shared.protocols.compute._job import IsJob, IsJobBase
from omnipy.shared.protocols.compute.job import IsFlow
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.data import IsDataset, IsSerializerRegistry

PersistOpts = PersistOutputsOptions
RestoreOpts = RestoreOutputsOptions
ProtocolOpts = OutputStorageProtocolOptions


class SerializerFuncJobBaseMixin:

    _serializer_registry: IsSerializerRegistry = get_serializer_registry()

    def __init__(self,
                 *,
                 persist_outputs: PersistOutputsOptions | None = None,
                 restore_outputs: RestoreOutputsOptions | None = None,
                 output_storage_protocol: OutputStorageProtocolOptions | None = None):

        # TODO: Possibly reimplement logic using a state machine, e.g. "transitions" package
        if persist_outputs is None:
            self._persist_outputs = PersistOpts.FOLLOW_CONFIG
        else:
            self._persist_outputs = PersistOpts(persist_outputs)

        if restore_outputs is None:
            self._restore_outputs = RestoreOpts.FOLLOW_CONFIG
        else:
            self._restore_outputs = RestoreOpts(restore_outputs)

        if output_storage_protocol is None:
            self._output_storage_protocol = ProtocolOpts.FOLLOW_CONFIG
        else:
            self._output_storage_protocol = ProtocolOpts(output_storage_protocol)

    @property
    def _job_config(self) -> IsJobConfig:
        self_as_job_base = cast(IsJobBase, self)
        return self_as_job_base.config

    def _log(self, msg: str) -> None:
        self_as_job_base = cast(IsJobBase, self)
        self_as_job_base.log(msg)

    @property
    def _return_type(self) -> Type[object]:
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)
        return self_as_signature_func_job_base_mixin.return_type

    @property
    def persist_outputs(self) -> PersistOutputsOptions | None:
        return self._persist_outputs

    @property
    def restore_outputs(self) -> RestoreOutputsOptions | None:
        return self._restore_outputs

    @property
    def output_storage_protocol(self) -> OutputStorageProtocolOptions | None:
        return self._output_storage_protocol

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions:
        if self._persist_outputs is not PersistOpts.FOLLOW_CONFIG:
            return self._persist_outputs if self._persist_outputs is not None \
                else PersistOpts.DISABLED
        else:
            # TODO: Refactor using Flow and Task Mixins
            from omnipy.compute.flow import FlowBase
            from omnipy.compute.task import TaskBase

            config_persist_opt = self._job_config.output_storage.persist_outputs

            if config_persist_opt == ConfigPersistOpts.ENABLE_FLOW_OUTPUTS:
                return PersistOpts.ENABLED if isinstance(self, FlowBase) else PersistOpts.DISABLED
            elif config_persist_opt == ConfigPersistOpts.ENABLE_FLOW_AND_TASK_OUTPUTS:
                return PersistOpts.ENABLED \
                    if any(isinstance(self, cls) for cls in (FlowBase, TaskBase)) \
                    else PersistOpts.DISABLED
            else:
                assert config_persist_opt == ConfigPersistOpts.DISABLED
                return PersistOpts.DISABLED

    @property
    def will_restore_outputs(self) -> RestoreOutputsOptions:
        if self._restore_outputs is not RestoreOpts.FOLLOW_CONFIG:
            return self._restore_outputs if self._restore_outputs is not None \
                else RestoreOpts.DISABLED
        else:
            config_restore_opt = self._job_config.output_storage.restore_outputs

            if config_restore_opt == ConfigRestoreOpts.AUTO_ENABLE_IGNORE_PARAMS:
                return RestoreOpts.AUTO_ENABLE_IGNORE_PARAMS
            assert config_restore_opt == ConfigRestoreOpts.DISABLED
            return RestoreOpts.DISABLED

    @property
    def output_storage_protocol_to_use(self) -> OutputStorageProtocolOptions:
        if self._output_storage_protocol is not ProtocolOpts.FOLLOW_CONFIG:
            return self._output_storage_protocol if self._output_storage_protocol is not None \
                else ProtocolOpts.LOCAL
        else:
            config_protocol = self._job_config.output_storage.protocol
            return ProtocolOpts(config_protocol)

    def _call_job(self, *args: object, **kwargs: object) -> object:
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)

        if self.will_restore_outputs in [
                RestoreOpts.AUTO_ENABLE_IGNORE_PARAMS, RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS
        ]:
            try:
                return self._deserialize_and_restore_outputs()
            except Exception:
                if self.will_restore_outputs is RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS:
                    raise

        super_as_job_base = cast(IsJobBase, super())
        results = super_as_job_base._call_job(*args, **kwargs)

        if self.will_persist_outputs is PersistOpts.ENABLED:
            if isinstance(results, Dataset):
                self._serialize_and_persist_outputs(results)
            else:
                self._log(
                    f'Results of {self_as_name_job_base_mixin.unique_name} is not a Dataset and '
                    f'cannot be automatically serialized and persisted!')

        return results

    def _serialize_and_persist_outputs(self, results: Dataset):
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)

        datetime_str = self._generate_datetime_str()
        output_path = Path(
            self._job_config.output_storage.local.persist_data_dir_path).joinpath(datetime_str)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        num_cur_files = len(os.listdir(output_path))
        job_name = self._job_name()

        file_path = output_path.joinpath(f'{num_cur_files:02}_{job_name}.tar.gz')

        parsed_dataset, serializer = \
            self._serializer_registry.auto_detect_tar_file_serializer(results)

        if serializer is None:
            self._log('Unable to find a serializer for results of job '
                      f'"{self_as_name_job_base_mixin.name}", with data type "{type(results)}". '
                      f'Will abort persisting results...')
        else:
            assert parsed_dataset is not None
            self._log(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(file_path)}"')

            with open(file_path, 'wb') as tarfile:
                tarfile.write(serializer.serialize(parsed_dataset))

    def _job_name(self):
        self_as_job_base = cast(IsJobBase, self)
        return '_'.join(self_as_job_base.unique_name.split('-')[:-2])

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
            persist_data_dir_path: Path, job_name: str) -> Generator[Path, None, None]:

        sorted_date_dirs = iter(reversed(sorted(os.listdir(persist_data_dir_path))))

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
    def _deserialize_and_restore_outputs(self) -> IsDataset | None:
        self_as_job_base = cast(IsJobBase, self)

        persist_data_dir_path = Path(self._job_config.output_storage.local.persist_data_dir_path)
        if os.path.exists(persist_data_dir_path):
            for tar_file_path in self._all_job_output_file_paths_in_reverse_order_for_last_run(
                    persist_data_dir_path, self._job_name()):
                to_dataset = cast(Type[Dataset], self._return_type)
                return self._serializer_registry.load_from_tar_file_path_based_on_file_suffix(
                    self_as_job_base, str(tar_file_path), to_dataset())

        raise RuntimeError('No persisted output')


# TODO: Add configuration option for serialize mixin to specify per flow to not preserve
#       task outputs
