from datetime import datetime
from enum import Enum
import os
from pathlib import Path
import tarfile
from typing import Optional

from omnipy.config.job import ConfigPersistOutputsOptions as ConfigPersistOpts
from omnipy.config.job import ConfigRestoreOutputsOptions as ConfigRestoreOpts
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import SerializerRegistry
from omnipy.modules.json.serializers import JsonDatasetToTarFileSerializer
from omnipy.modules.pandas.serializers import PandasDatasetToTarFileSerializer
from omnipy.modules.raw.serializers import RawDatasetToTarFileSerializer


class PersistOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    FOLLOW_CONFIG = 'config'
    ENABLED = 'enabled'


class RestoreOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    FOLLOW_CONFIG = 'config'
    AUTO_ENABLE_IGNORE_PARAMS = 'auto_ignore_params'
    FORCE_ENABLE_IGNORE_PARAMS = 'force_ignore_params'


PersistOpts = PersistOutputsOptions
RestoreOpts = RestoreOutputsOptions


class SerializerFuncJobBaseMixin:
    def __init__(self,
                 *,
                 persist_outputs: Optional[PersistOutputsOptions] = None,
                 restore_outputs: Optional[RestoreOutputsOptions] = None):

        if persist_outputs is None:
            self._persist_outputs = PersistOpts.FOLLOW_CONFIG if self._has_job_config else None
        else:
            self._persist_outputs = PersistOpts(persist_outputs)

        if restore_outputs is None:
            self._restore_outputs = RestoreOpts.FOLLOW_CONFIG if self._has_job_config else None
        else:
            self._restore_outputs = RestoreOpts(restore_outputs)

    @property
    def _has_job_config(self) -> bool:
        return self.config is not None

    @property
    def persist_outputs(self) -> Optional[PersistOutputsOptions]:
        return self._persist_outputs

    @property
    def restore_outputs(self) -> Optional[RestoreOutputsOptions]:
        return self._restore_outputs

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions:
        if not self._has_job_config or self._persist_outputs is not PersistOpts.FOLLOW_CONFIG:
            return self._persist_outputs if self._persist_outputs is not None \
                    else PersistOpts.DISABLED
        else:
            from omnipy.compute.private.flow import FlowBase
            from omnipy.compute.task import TaskBase

            config_persist_opt = self.config.persist_outputs

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
            config_restore_opt = self.config.restore_outputs

            if config_restore_opt == ConfigRestoreOpts.AUTO_ENABLE_IGNORE_PARAMS:
                return RestoreOpts.AUTO_ENABLE_IGNORE_PARAMS
            assert config_restore_opt == ConfigRestoreOpts.DISABLED
            return RestoreOpts.DISABLED


class SerializerFuncJobMixin:
    def __init__(self) -> None:
        self._serializer_registry = self._create_serializer_registry()

    def _create_serializer_registry(self):
        registry = SerializerRegistry()

        registry.register(PandasDatasetToTarFileSerializer)
        registry.register(RawDatasetToTarFileSerializer)
        registry.register(JsonDatasetToTarFileSerializer)

        return registry

    def __call__(self, *args: object, **kwargs: object) -> object:
        if self.will_restore_outputs in [
                RestoreOpts.AUTO_ENABLE_IGNORE_PARAMS, RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS
        ]:
            try:
                return self._deserialize_and_restore_outputs()
            except Exception:
                if self.will_restore_outputs is RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS:
                    raise

        results = super().__call__(*args, **kwargs)

        if self.will_persist_outputs is PersistOpts.ENABLED:
            if isinstance(results, Dataset):
                self._serialize_and_persist_outputs(results)
            else:
                self._log_message(f'Results of {self.unique_name} is not a Dataset and cannot '
                                  f'be automatically serialized and persisted!')

        return results

    def _serialize_and_persist_outputs(self, results: Dataset):
        run_time = self.datetime_of_flow_run if self.datetime_of_flow_run is not None \
            else datetime.now()
        datetime_str = run_time.strftime('%Y_%m_%d-%H_%M_%S')
        output_path = Path(self.config.persist_data_dir_path).joinpath(datetime_str)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        num_cur_files = len(os.listdir(output_path))
        file_path = output_path.joinpath(f'{num_cur_files:02}-{self.name}.tar.gz')

        parsed_dataset, serializer = \
            self._serializer_registry.auto_detect_tar_file_serializer(results)

        self._log_message(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(file_path)}"')

        with open(file_path, 'wb') as tarfile:
            tarfile.write(serializer.serialize(parsed_dataset))

    # TODO: Refactor
    def _deserialize_and_restore_outputs(self) -> Dataset:
        output_path = Path(self.config.persist_data_dir_path)
        if os.path.exists(output_path):
            sorted_date_dirs = list(sorted(os.listdir(output_path)))
            if len(sorted_date_dirs) > 0:
                last_dir = sorted_date_dirs[-1]
                last_dir_path = output_path.joinpath(last_dir)
                for job_output_name in reversed(sorted(os.listdir(last_dir_path))):
                    name_part_of_filename = job_output_name[3:-7]
                    print(name_part_of_filename)
                    if name_part_of_filename == self.name:
                        tar_file_path = last_dir_path.joinpath(job_output_name)
                        with tarfile.open(tar_file_path, 'r:gz') as tarfile_obj:
                            file_suffixes = set(fn.split('.')[-1] for fn in tarfile_obj.getnames())
                        if len(file_suffixes) != 1:
                            self._log_message(f'Tar archive contains files with different or '
                                              f'no file suffixes: {file_suffixes}. Serializer '
                                              f'cannot be uniquely determined. Aborting '
                                              f'restore.')
                        else:
                            file_suffix = file_suffixes.pop()
                            serializers = self._serializer_registry.\
                                detect_tar_file_serializers_from_file_suffix(file_suffix)
                            if len(serializers) == 0:
                                self._log_message(
                                    f'No serializer for file suffix "{file_suffix}" can be'
                                    f'determined. Aborting restore.')
                            else:
                                self._log_message(f'Reading dataset from a gzipped tarpack at'
                                                  f' "{os.path.abspath(tar_file_path)}"')

                                serializer = serializers[0]
                                with open(tar_file_path, 'rb') as tarfile_binary:
                                    dataset = serializer.deserialize(tarfile_binary.read())
                                if dataset.get_model_class() is \
                                        self.return_type().get_model_class():
                                    return dataset
                                else:
                                    try:
                                        new_dataset = self.return_type()
                                        if new_dataset.get_model_class() is Model[str]:
                                            new_dataset.from_data(dataset.to_json())
                                        else:
                                            new_dataset.from_json(dataset.to_data())
                                        return new_dataset
                                    except:
                                        return dataset

        raise RuntimeError('No persisted output')

    @classmethod
    def _log_message(cls, log_message: str) -> None:
        from omnipy import runtime
        if runtime:
            runtime.objects.registry.log(datetime.now(), log_message)

    # TODO: Refactor logging as a general mixin and add it to at least RunStateRegistry (as now)
    #       and also JobCreator, possibly engines, and more. Use RuntimeConfig to subscribe to
    #       loggers, as now.
