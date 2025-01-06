from typing import Any, TYPE_CHECKING

from omnipy.components.prefect.engine.prefect import PrefectEngine
from omnipy.compute._job import JobBase
from omnipy.config import ConfigBase
from omnipy.config.data import DataConfig
from omnipy.config.engine import LocalRunnerConfig, PrefectEngineConfig
from omnipy.config.job import JobConfig
from omnipy.config.root_log import RootLogConfig
from omnipy.data._data_class_creator import DataClassBase
from omnipy.data.serializer import SerializerRegistry
from omnipy.engine.local import LocalRunner
from omnipy.hub._registry import RunStateRegistry
from omnipy.hub.log._root_log import RootLogObjects
from omnipy.shared.enums import EngineChoice
from omnipy.shared.protocols.compute.job_creator import IsJobConfigHolder
from omnipy.shared.protocols.config import (IsDataConfig,
                                            IsEngineConfig,
                                            IsJobConfig,
                                            IsLocalRunnerConfig,
                                            IsPrefectEngineConfig,
                                            IsRootLogConfig)
from omnipy.shared.protocols.data import IsDataClassCreator, IsSerializerRegistry
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.shared.protocols.hub.runtime import IsRootLogObjects, IsRuntimeConfig, IsRuntimeObjects
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import called_from_omnipy_tests
from omnipy.util.publisher import DataPublisher, RuntimeEntryPublisher


def _job_creator_factory():
    return JobBase.job_creator


def _job_config_factory():
    return _job_creator_factory().config


def _data_class_creator_factory():
    return DataClassBase.data_class_creator


def _data_config_factory():
    return _data_class_creator_factory().config


class RuntimeConfig(RuntimeEntryPublisher, ConfigBase):
    job: IsJobConfig = pyd.Field(default_factory=_job_config_factory)
    data: IsDataConfig = pyd.Field(default_factory=_data_config_factory)
    engine: EngineChoice = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = pyd.Field(default_factory=LocalRunnerConfig)
    prefect: IsPrefectEngineConfig = pyd.Field(default_factory=PrefectEngineConfig)
    root_log: IsRootLogConfig = pyd.Field(default_factory=RootLogConfig)

    def reset_to_defaults(self) -> None:
        prev_back = self._back
        self._back = None

        self.job = JobConfig()
        self.data = DataConfig()
        self.engine = EngineChoice.LOCAL
        self.local = LocalRunnerConfig()
        self.prefect = PrefectEngineConfig()
        self.root_log = RootLogConfig()

        self._back = prev_back
        if self._back is not None:
            self._back.reset_subscriptions()


class RuntimeObjects(RuntimeEntryPublisher, DataPublisher):
    job_creator: IsJobConfigHolder = pyd.Field(default_factory=_job_creator_factory)
    data_class_creator: IsDataClassCreator = pyd.Field(default_factory=_data_class_creator_factory)
    local: IsEngine = pyd.Field(default_factory=LocalRunner)
    prefect: IsEngine = pyd.Field(default_factory=PrefectEngine)
    registry: IsRunStateRegistry = pyd.Field(default_factory=RunStateRegistry)
    serializers: IsSerializerRegistry = pyd.Field(default_factory=SerializerRegistry)
    root_log: IsRootLogObjects = pyd.Field(default_factory=RootLogObjects)


class Runtime(DataPublisher):
    config: IsRuntimeConfig = pyd.Field(default_factory=RuntimeConfig)
    objects: IsRuntimeObjects = pyd.Field(default_factory=RuntimeObjects)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        self.reset_subscriptions()

    def reset_subscriptions(self, data=None, **kwargs):
        """
        Resets all subscriptions for the current instance.

        This function unsubscribes all existing subscriptions and then sets up new subscriptions
        for the `config` and `objects` members.
        """

        self.reset_backlinks()

        self.config.unsubscribe_all()
        self.objects.unsubscribe_all()

        # Makes sure that the config references in the runtime objects always refer to the related
        # config in runtime, even when:
        #
        # 1. The runtime config is replaced with a new config object, or
        # 2. The runtime object is replaced with a new runtime object, or
        # 3. Both of the above
        #
        # This might e.g. happen due to the use of  mock objects for testing, or if the config is
        # reloaded from a file.

        self.config.subscribe_attr('job', self.objects.job_creator.set_config)
        self.config.subscribe_attr('data', self.objects.data_class_creator.set_config)
        self.config.subscribe_attr('local', self.objects.local.set_config)
        self.config.subscribe_attr('prefect', self.objects.prefect.set_config)
        self.config.subscribe_attr('root_log', self.objects.root_log.set_config)

        # Makes sure that the registry references in the job runners always refer to the registry
        # object in runtime, even when one or both of the objects are replaced with new objects.
        self.objects.subscribe_attr('registry', self.objects.local.set_registry)
        self.objects.subscribe_attr('registry', self.objects.prefect.set_registry)

        # Makes sure that the engine used by the job creator is always the one specified in the
        # 'engine' config item in runtime
        self.config.subscribe_attr('local', self._update_job_creator_engine)
        self.config.subscribe_attr('prefect', self._update_job_creator_engine)
        self.config.subscribe_attr('engine', self._update_job_creator_engine)

        # Makes sure that the local and prefect engine configs are always reloaded when the local
        # or prefect engine objects are replaced with new engine objects. This is necessary because
        # the `get_config_cls()` method of the engine objects define the classes of the respective
        # engine config objects to be used. If an engine object is replaced with a new engine that
        # require a different engine config class than is currently used, the config object will be
        # replaced with a new default config object of the correct type.
        self.objects.subscribe_attr('local', self._update_local_runner_config)
        self.objects.subscribe_attr('prefect', self._update_prefect_engine_config)

    def reset_backlinks(self):
        self.config._back = self  # pyright: ignore [reportAttributeAccessIssue]
        self.objects._back = self  # pyright: ignore [reportAttributeAccessIssue]

    def _get_engine_config(self, engine_choice: EngineChoice):
        return getattr(self.config, engine_choice)

    def _set_engine_config(self, engine_choice: EngineChoice, engine_config: IsEngineConfig):
        return setattr(self.config, engine_choice, engine_config)

    def _get_engine(self, engine_choice: EngineChoice):
        return getattr(self.objects, engine_choice)

    def _new_engine_config_if_new_cls(self, engine: IsEngine, engine_choice: EngineChoice) -> None:
        # TODO: when parsing config from file is implemented, make sure that the new engine
        #       config classes here reparse the config files
        engine_config_cls = engine.get_config_cls()
        if self._get_engine_config(engine_choice).__class__ is not engine_config_cls:
            self._set_engine_config(engine_choice, engine_config_cls())

    def _update_local_runner_config(self, local_runner: IsEngine):
        self._new_engine_config_if_new_cls(local_runner, EngineChoice.LOCAL)

    def _update_prefect_engine_config(self, prefect_engine: IsEngine):
        self._new_engine_config_if_new_cls(prefect_engine, EngineChoice.PREFECT)

    def _update_job_creator_engine(self, _item_changed: Any):
        self.objects.job_creator.set_engine(self._get_engine(self.config.engine))


if TYPE_CHECKING:
    runtime: 'Runtime' = Runtime()
else:
    runtime: 'Runtime | None' = None if called_from_omnipy_tests() else Runtime()
