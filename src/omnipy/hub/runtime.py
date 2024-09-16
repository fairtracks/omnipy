from dataclasses import dataclass, field
from typing import Any

from omnipy.api.enums import EngineChoice
from omnipy.api.protocols.private.compute.job_creator import IsJobConfigHolder
from omnipy.api.protocols.private.data import IsDataClassCreator
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.config import (IsDataConfig,
                                                IsEngineConfig,
                                                IsJobConfig,
                                                IsLocalRunnerConfig,
                                                IsPrefectEngineConfig,
                                                IsRootLogConfig)
from omnipy.api.protocols.public.data import IsSerializerRegistry
from omnipy.api.protocols.public.hub import IsRootLogObjects, IsRuntimeConfig, IsRuntimeObjects
from omnipy.compute.job import JobBase
from omnipy.config.data import DataConfig
from omnipy.config.job import JobConfig
from omnipy.data.data_class_creator import DataClassBase
from omnipy.data.serializer import SerializerRegistry
from omnipy.engine.local import LocalRunner, LocalRunnerConfigEntryPublisher
from omnipy.hub.log.root_log import RootLogConfigEntryPublisher, RootLogObjects
from omnipy.hub.registry import RunStateRegistry
from omnipy.modules.prefect.engine.prefect import PrefectEngine, PrefectEngineConfigEntryPublisher
from omnipy.util.helpers import called_from_omnipy_tests
from omnipy.util.publisher import DataPublisher, RuntimeEntryPublisher


def _job_creator_factory():
    return JobBase.job_creator


def _data_class_creator_factory():
    return DataClassBase.data_class_creator


def _data_config_factory():
    return _data_class_creator_factory().config


@dataclass
class RuntimeConfig(RuntimeEntryPublisher):
    job: IsJobConfig = field(default_factory=JobConfig)
    data: IsDataConfig = field(default_factory=_data_config_factory)
    engine: EngineChoice = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = field(default_factory=LocalRunnerConfigEntryPublisher)
    prefect: IsPrefectEngineConfig = field(default_factory=PrefectEngineConfigEntryPublisher)
    root_log: IsRootLogConfig = field(default_factory=RootLogConfigEntryPublisher)

    def reset_to_defaults(self) -> None:
        prev_back = self._back
        self._back = None

        self.job = JobConfig()
        self.data = DataConfig()
        self.engine = EngineChoice.LOCAL
        self.local = LocalRunnerConfigEntryPublisher()
        self.prefect = PrefectEngineConfigEntryPublisher()
        self.root_log = RootLogConfigEntryPublisher()

        self._back = prev_back
        if self._back is not None:
            self._back.reset_subscriptions()


@dataclass
class RuntimeObjects(RuntimeEntryPublisher):
    job_creator: IsJobConfigHolder = field(default_factory=_job_creator_factory)
    data_class_creator: IsDataClassCreator = field(default_factory=_data_class_creator_factory)
    local: IsEngine = field(default_factory=LocalRunner)
    prefect: IsEngine = field(default_factory=PrefectEngine)
    registry: IsRunStateRegistry = field(default_factory=RunStateRegistry)
    serializers: IsSerializerRegistry = field(default_factory=SerializerRegistry)
    root_log: IsRootLogObjects = field(default_factory=RootLogObjects)
    waiting_for_terminal_repr: bool = False


@dataclass
class Runtime(DataPublisher):
    config: IsRuntimeConfig = field(default_factory=RuntimeConfig)
    objects: IsRuntimeObjects = field(default_factory=RuntimeObjects)

    def __post_init__(self):
        super().__init__()

        self.reset_subscriptions()

    def reset_subscriptions(self):
        """
        Resets all subscriptions for the current instance.

        This function unsubscribes all existing subscriptions and then sets up new subscriptions
        for the `config` and `objects` members.
        """

        self.reset_backlinks()

        self.config.unsubscribe_all()
        self.objects.unsubscribe_all()

        self.config.subscribe('job', self.objects.job_creator.set_config)
        self.config.subscribe('data', self.objects.data_class_creator.set_config)
        self.config.subscribe('local', self.objects.local.set_config)
        self.config.subscribe('prefect', self.objects.prefect.set_config)
        self.config.subscribe('root_log', self.objects.root_log.set_config)

        self.config.subscribe('local', self._update_job_creator_engine)
        self.config.subscribe('prefect', self._update_job_creator_engine)
        self.config.subscribe('engine', self._update_job_creator_engine)

        self.objects.subscribe('registry', self.objects.local.set_registry)
        self.objects.subscribe('registry', self.objects.prefect.set_registry)

        self.objects.subscribe('local', self._update_local_runner_config)
        self.objects.subscribe('prefect', self._update_prefect_engine_config)

    def reset_backlinks(self):
        self.config._back = self
        self.config.local._back = self
        self.config.prefect._back = self
        self.config.root_log._back = self
        self.objects._back = self

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


runtime: 'Runtime | None' = None if called_from_omnipy_tests() else Runtime()
