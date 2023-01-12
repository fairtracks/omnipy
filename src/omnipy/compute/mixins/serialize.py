from enum import Enum
from typing import Optional

from omnipy.config.job import ConfigPersistOutputsOptions as ConfigPersistOpts
from omnipy.config.job import ConfigRestoreOutputsOptions as ConfigRestoreOpts


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


# class SerializerFuncJobMixin:
#     def __call__(self, *args: object, **kwargs: object) -> object:
#
#         result = super().__call__(*args, **kwargs)
#
