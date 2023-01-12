from dataclasses import dataclass, field
import logging
from sys import stdout
from typing import Any, Optional

from omnipy.compute.job import JobBase
from omnipy.config.engine import LocalRunnerConfig, PrefectEngineConfig
from omnipy.config.job import JobConfig
from omnipy.config.publisher import ConfigPublisher
from omnipy.config.registry import RunStateRegistryConfig
from omnipy.engine.constants import EngineChoice
from omnipy.engine.local import LocalRunner
from omnipy.engine.prefect import PrefectEngine
from omnipy.engine.protocols import (IsEngine,
                                     IsEngineConfig,
                                     IsJobConfig,
                                     IsJobCreator,
                                     IsLocalRunnerConfig,
                                     IsPrefectEngineConfig,
                                     IsRunStateRegistry,
                                     IsRunStateRegistryConfig,
                                     IsRuntime,
                                     IsRuntimeConfig,
                                     IsRuntimeObjects)
from omnipy.engine.registry import RunStateRegistry


def get_default_logger():
    logger = logging.getLogger('omnipy')
    logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(logging.StreamHandler(stdout))
    return logger


@dataclass
class RuntimeEntry(ConfigPublisher):
    _back: Optional[IsRuntime] = field(default=None, init=False, repr=False)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if hasattr(self, key) and not key.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()


def _job_creator_factory():
    return JobBase.job_creator


@dataclass
class RuntimeObjects(RuntimeEntry, ConfigPublisher):
    logger: logging.Logger = field(default_factory=get_default_logger)
    registry: IsRunStateRegistry = field(default_factory=RunStateRegistry)
    job_creator: IsJobCreator = field(default_factory=_job_creator_factory)
    local: IsEngine = field(default_factory=LocalRunner)
    prefect: IsEngine = field(default_factory=PrefectEngine)


@dataclass
class RuntimeConfig(RuntimeEntry, ConfigPublisher):
    job: IsJobConfig = field(default_factory=JobConfig)
    engine: EngineChoice = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = field(default_factory=LocalRunnerConfig)
    prefect: IsPrefectEngineConfig = field(default_factory=PrefectEngineConfig)
    registry: IsRunStateRegistryConfig = field(default_factory=RunStateRegistryConfig)


@dataclass
class Runtime(ConfigPublisher):
    objects: IsRuntimeObjects = field(default_factory=RuntimeObjects)
    config: IsRuntimeConfig = field(default_factory=RuntimeConfig)

    def __post_init__(self):
        super().__init__()

        self.objects._back = self
        self.config._back = self

        self.reset_subscriptions()

    def reset_subscriptions(self):
        self.objects.unsubscribe_all()
        self.config.unsubscribe_all()

        self.objects.subscribe('registry', self.objects.local.set_registry)
        self.objects.subscribe('registry', self.objects.prefect.set_registry)
        self.objects.subscribe('logger', self.objects.registry.set_logger)

        self.objects.subscribe('local', self._update_local_runner_config)
        self.objects.subscribe('prefect', self._update_prefect_engine_config)

        self.config.subscribe('job', self.objects.job_creator.set_config)
        self.config.subscribe('local', self.objects.local.set_config)
        self.config.subscribe('prefect', self.objects.prefect.set_config)
        self.config.subscribe('registry', self.objects.registry.set_config)

        self.config.subscribe('local', self._update_job_creator_engine)
        self.config.subscribe('prefect', self._update_job_creator_engine)
        self.config.subscribe('engine', self._update_job_creator_engine)

    def _get_engine(self, engine_choice: EngineChoice):
        return getattr(self.objects, engine_choice)

    def _get_engine_config(self, engine_choice: EngineChoice):
        return getattr(self.config, engine_choice)

    def _set_engine_config(self, engine_choice: EngineChoice, engine_config: IsEngineConfig):
        return setattr(self.config, engine_choice, engine_config)

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
