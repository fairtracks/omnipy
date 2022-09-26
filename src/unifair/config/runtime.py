from dataclasses import dataclass, field
import logging
from sys import stdout
from typing import Any, Optional

from unifair.compute.job import JobConfig
from unifair.config.engine import LocalRunnerConfig, PrefectEngineConfig
from unifair.config.publisher import ConfigPublisher
from unifair.config.registry import RunStateRegistryConfig
from unifair.engine.constants import EngineChoice
from unifair.engine.local import LocalRunner
from unifair.engine.prefect import PrefectEngine
from unifair.engine.protocols import (IsEngine,
                                      IsEngineConfig,
                                      IsJobCreator,
                                      IsLocalRunnerConfig,
                                      IsPrefectEngineConfig,
                                      IsRunStateRegistry,
                                      IsRunStateRegistryConfig,
                                      IsRuntimeConfig,
                                      IsRuntimeObjects)
from unifair.engine.registry import RunStateRegistry


def get_default_logger():
    logger = logging.getLogger('uniFAIR')
    logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(logging.StreamHandler(stdout))
    return logger


@dataclass
class RuntimeEntry(ConfigPublisher):
    _back: Optional['Runtime'] = field(default=None, init=False, repr=False)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if hasattr(self, key) and not key.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()


@dataclass
class RuntimeObjects(RuntimeEntry, ConfigPublisher):
    logger: logging.Logger = get_default_logger()
    registry: IsRunStateRegistry = RunStateRegistry()
    job_creator: IsJobCreator = JobConfig.job_creator
    local: IsEngine = LocalRunner()
    prefect: IsEngine = PrefectEngine()


@dataclass
class RuntimeConfig(RuntimeEntry, ConfigPublisher):
    engine: EngineChoice = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = LocalRunnerConfig()
    prefect: IsPrefectEngineConfig = PrefectEngineConfig()
    registry: IsRunStateRegistryConfig = RunStateRegistryConfig()


@dataclass
class Runtime(ConfigPublisher):
    objects: IsRuntimeObjects = RuntimeObjects()
    config: IsRuntimeConfig = RuntimeConfig()

    def __post_init__(self):
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
        # TODO: when parsing config from file is implemented, make sure that the new engine config
        #       classes here reparse the config files
        engine_config_cls = engine.get_config_cls()
        if self._get_engine_config(engine_choice).__class__ is not engine_config_cls:
            self._set_engine_config(engine_choice, engine_config_cls())

    def _update_local_runner_config(self, local_runner: IsEngine):
        self._new_engine_config_if_new_cls(local_runner, EngineChoice.LOCAL)

    def _update_prefect_engine_config(self, prefect_engine: IsEngine):
        self._new_engine_config_if_new_cls(prefect_engine, EngineChoice.PREFECT)

    def _update_job_creator_engine(self, _item_changed: Any):
        self.objects.job_creator.set_engine(self._get_engine(self.config.engine))
