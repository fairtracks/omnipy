from datetime import datetime
from enum import Enum
import os
from pathlib import Path
from typing import Optional

from omnipy.config.job import ConfigPersistOutputsOptions as ConfigPersistOpts
from omnipy.config.job import ConfigRestoreOutputsOptions as ConfigRestoreOpts
from omnipy.data.dataset import Dataset
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
    def __call__(self, *args: object, **kwargs: object) -> object:
        if self.will_restore_outputs in [
                RestoreOpts.AUTO_ENABLE_IGNORE_PARAMS, RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS
        ]:
            try:
                results = self._deserialize_and_restore_outputs()
                return result
            except Exception:
                if self.will_restore_outputs is RestoreOpts.FORCE_ENABLE_IGNORE_PARAMS:
                    raise

        results = super().__call__(*args, **kwargs)

        if self.will_persist_outputs is PersistOpts.ENABLED:
            if isinstance(results, Dataset):
                self._serialize_and_persist_outputs(results)
            else:
                from omnipy import runtime
                if runtime:
                    runtime.objects.registry.log(
                        datetime.now(),
                        f'Results of {self.unique_name} is not a Dataset and cannot'
                        f'be automatically serialized and persisted!')

        return results

    def _create_serializer_registry(self):
        registry = SerializerRegistry()

        registry.register(PandasDatasetToTarFileSerializer)
        registry.register(RawDatasetToTarFileSerializer)
        registry.register(JsonDatasetToTarFileSerializer)

        return registry

    def _serialize_and_persist_outputs(self, results: Dataset):
        run_time = self.datetime_of_flow_run if self.datetime_of_flow_run is not None \
            else datetime.now()
        datetime_str = run_time.strftime('%Y_%m_%d-%H_%M_%S')
        output_path = Path(self.config.persist_data_dir_path).joinpath(datetime_str)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        num_cur_files = len(os.listdir(output_path))
        file_path = output_path.joinpath(f'{num_cur_files:02}-{self.name}.tar.gz')

        from omnipy import runtime
        if runtime:
            runtime.objects.registry.log(
                datetime.now(),
                f'Writing dataset as a gzipped tarpack of raw files to "{os.path.abspath(file_path)}"'
            )

        serializer_registry = self._create_serializer_registry()
        parsed_dataset, serializer = serializer_registry.auto_detect_tar_file_serializer(results)

        with open(file_path, 'wb') as tarfile:
            tarfile.write(serializer.serialize(parsed_dataset))

    def _deserialize_and_restore_outputs(self):
        raise RuntimeError('No persisted output')
