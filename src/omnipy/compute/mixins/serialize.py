from datetime import datetime
import os
from pathlib import Path
import tarfile
from typing import cast, Generator, Type

from omnipy.api.enums import ConfigPersistOutputsOptions as ConfigPersistOpts
from omnipy.api.enums import ConfigRestoreOutputsOptions as ConfigRestoreOpts
from omnipy.api.enums import (OutputStorageProtocolOptions,
                              PersistOutputsOptions,
                              RestoreOutputsOptions)
from omnipy.api.protocols.private.compute.job import IsJobBase
from omnipy.api.protocols.public.config import IsJobConfig
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.name import NameJobBaseMixin
from omnipy.config.job import JobConfig
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import SerializerRegistry

PersistOpts = PersistOutputsOptions
RestoreOpts = RestoreOutputsOptions
ProtocolOpts = OutputStorageProtocolOptions


class SerializerFuncJobBaseMixin:
    def __init__(self,
                 *,
                 persist_outputs: PersistOutputsOptions | None = None,
                 restore_outputs: RestoreOutputsOptions | None = None,
                 output_storage_protocol: OutputStorageProtocolOptions | None = None):

        # TODO: Possibly reimplement logic using a state machine, e.g. "transitions" package
        if persist_outputs is None:
            self._persist_outputs = PersistOpts.FOLLOW_CONFIG if self._has_job_config else None
        else:
            self._persist_outputs = PersistOpts(persist_outputs)

        if restore_outputs is None:
            self._restore_outputs = RestoreOpts.FOLLOW_CONFIG if self._has_job_config else None
        else:
            self._restore_outputs = RestoreOpts(restore_outputs)

        if output_storage_protocol is None:
            self._output_storage_protocol = \
                ProtocolOpts.FOLLOW_CONFIG if self._has_job_config else None
        else:
            self._output_storage_protocol = ProtocolOpts(output_storage_protocol)

        self._serializer_registry = self._create_serializer_registry()

    def _create_serializer_registry(self):
        from omnipy.modules.json.serializers import JsonDatasetToTarFileSerializer
        from omnipy.modules.pandas.serializers import PandasDatasetToTarFileSerializer
        from omnipy.modules.raw.serializers import RawDatasetToTarFileSerializer

        # TODO: store in runtime, to remove dependencies
        registry = SerializerRegistry()

        registry.register(PandasDatasetToTarFileSerializer)
        registry.register(RawDatasetToTarFileSerializer)
        registry.register(JsonDatasetToTarFileSerializer)

        return registry

    @property
    def _has_job_config(self) -> bool:
        self_as_job_base = cast(IsJobBase, self)
        return self_as_job_base.config is not None

    @property
    def _job_config(self) -> IsJobConfig:
        self_as_job_base = cast(IsJobBase, self)
        if self_as_job_base.config is None:
            return JobConfig()
        else:
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
        if not self._has_job_config or self._persist_outputs is not PersistOpts.FOLLOW_CONFIG:
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
        if not self._has_job_config or self._restore_outputs is not RestoreOpts.FOLLOW_CONFIG:
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
        if not self._has_job_config \
                or self._output_storage_protocol is not ProtocolOpts.FOLLOW_CONFIG:
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
            self._log(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(file_path)}"')

            with open(file_path, 'wb') as tarfile:
                tarfile.write(serializer.serialize(parsed_dataset))

    def _job_name(self):
        return '_'.join(self.unique_name.split('-')[:-2])

    def _generate_datetime_str(self):
        if self.time_of_cur_toplevel_flow_run:
            run_time = self.time_of_cur_toplevel_flow_run
        else:
            if hasattr(self, 'time_of_last_run') and self.time_of_last_run:
                run_time = self.time_of_last_run
            else:
                run_time = datetime.now()
        datetime_str = run_time.strftime('%Y_%m_%d-%H_%M_%S')
        return datetime_str

    @staticmethod
    def _all_job_output_file_paths_in_reverse_order_for_last_run(
            persist_data_dir_path: Path, job_name: str) -> Generator[Path, None, None]:
        sorted_date_dirs = list(sorted(os.listdir(persist_data_dir_path)))
        if len(sorted_date_dirs) > 0:
            last_dir = sorted_date_dirs[-1]
            last_dir_path = persist_data_dir_path.joinpath(last_dir)
            for job_output_name in reversed(sorted(os.listdir(last_dir_path))):
                name_part_of_filename = job_output_name[3:-7]
                if name_part_of_filename == job_name:
                    yield last_dir_path.joinpath(job_output_name)
        else:
            raise StopIteration

    # TODO: Further refactor _deserialize_and_restore_outputs
    def _deserialize_and_restore_outputs(self) -> Dataset:
        persist_data_dir_path = Path(self._job_config.output_storage.local.persist_data_dir_path)
        if os.path.exists(persist_data_dir_path):
            for tar_file_path in self._all_job_output_file_paths_in_reverse_order_for_last_run(
                    persist_data_dir_path, self._job_name()):
                with tarfile.open(tar_file_path, 'r:gz') as tarfile_obj:
                    file_suffixes = set(fn.split('.')[-1] for fn in tarfile_obj.getnames())
                if len(file_suffixes) != 1:
                    self._log(f'Tar archive contains files with different or '
                              f'no file suffixes: {file_suffixes}. Serializer '
                              f'cannot be uniquely determined. Aborting '
                              f'restore.')
                else:
                    file_suffix = file_suffixes.pop()
                    serializers = self._serializer_registry.\
                        detect_tar_file_serializers_from_file_suffix(file_suffix)
                    if len(serializers) == 0:
                        self._log(f'No serializer for file suffix "{file_suffix}" can be'
                                  f'determined. Aborting restore.')
                    else:
                        self._log(f'Reading dataset from a gzipped tarpack at'
                                  f' "{os.path.abspath(tar_file_path)}"')

                        serializer = serializers[0]
                        with open(tar_file_path, 'rb') as tarfile_binary:
                            dataset = serializer.deserialize(tarfile_binary.read())
                        return_dataset_cls = cast(Type[Dataset], self._return_type)
                        if return_dataset_cls().get_model_class() is dataset.get_model_class():
                            return dataset
                        else:
                            try:
                                new_dataset = return_dataset_cls()
                                if new_dataset.get_model_class() is Model[str]:
                                    new_dataset.from_data(dataset.to_json())
                                else:
                                    new_dataset.from_json(dataset.to_data())
                                return new_dataset
                            except Exception:
                                return dataset

        raise RuntimeError('No persisted output')


# TODO: Add configuration option for serialize mixin to specify per flow to not preserve
#       task outputs
