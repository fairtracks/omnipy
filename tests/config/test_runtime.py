import logging

from tests.engine.helpers.mocks import (MockLocalRunner,
                                        MockLocalRunnerConfig,
                                        MockPrefectEngine,
                                        MockPrefectEngineConfig,
                                        MockRunStateRegistry,
                                        MockTaskTemplate)
from unifair.compute.task import TaskTemplate
from unifair.config.engine import LocalRunnerConfig, PrefectEngineConfig
from unifair.config.registry import RunStateRegistryConfig
import unifair.config.runtime
from unifair.config.runtime import Runtime, RuntimeClasses, RuntimeConfig, RuntimeObjects
from unifair.engine.constants import EngineChoice
from unifair.engine.local import LocalRunner
from unifair.engine.prefect import PrefectEngine
from unifair.engine.registry import RunStateRegistry


def test_config_default(teardown_loggers) -> None:
    config = RuntimeConfig()
    assert isinstance(config.local, LocalRunnerConfig)
    assert isinstance(config.prefect, PrefectEngineConfig)
    assert isinstance(config.registry, RunStateRegistryConfig)


def _assert_logger(logger: logging.Logger) -> None:
    assert logger.name == 'uniFAIR'
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].stream is unifair.config.runtime.stdout


def test_objects_default() -> None:
    objects = RuntimeObjects()

    assert isinstance(objects.logger, logging.Logger)
    _assert_logger(objects.logger)

    assert isinstance(objects.registry, RunStateRegistry)
    assert isinstance(objects.local, LocalRunner)
    assert isinstance(objects.prefect, PrefectEngine)


def test_classes_default() -> None:
    classes = RuntimeClasses()
    assert classes.task_template is TaskTemplate


def test_default_config() -> None:
    runtime = Runtime()

    assert isinstance(runtime.config, RuntimeConfig)
    assert isinstance(runtime.config.engine, str)
    assert isinstance(runtime.config.local, LocalRunnerConfig)
    assert isinstance(runtime.config.prefect, PrefectEngineConfig)
    assert isinstance(runtime.config.registry, RunStateRegistryConfig)
    assert isinstance(runtime.config.registry.verbose, bool)

    assert isinstance(runtime.objects, RuntimeObjects)
    assert isinstance(runtime.objects.logger, logging.Logger)
    assert isinstance(runtime.objects.local, LocalRunner)
    assert isinstance(runtime.objects.prefect, PrefectEngine)
    assert isinstance(runtime.objects.registry, RunStateRegistry)

    assert runtime.classes.task_template is TaskTemplate

    assert runtime.config.engine == EngineChoice.LOCAL
    assert runtime.config.registry.verbose is True


def test_engines_subscribe_to_registry() -> None:
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    runtime = Runtime(
        objects=RuntimeObjects(
            local=mock_local_runner,
            prefect=mock_prefect_engine,
        ))

    assert runtime.objects.local is mock_local_runner
    assert runtime.objects.prefect is mock_prefect_engine

    assert isinstance(runtime.objects.registry, RunStateRegistry)
    assert runtime.objects.local.registry is runtime.objects.registry
    assert runtime.objects.prefect.registry is runtime.objects.registry

    mock_local_runner_2 = MockLocalRunner()
    mock_prefect_engine_2 = MockPrefectEngine()
    runtime.objects.local = mock_local_runner_2
    runtime.objects.prefect = mock_prefect_engine_2

    assert runtime.objects.local is mock_local_runner_2 is not mock_local_runner
    assert runtime.objects.prefect is mock_prefect_engine_2 is not mock_prefect_engine
    assert runtime.objects.local.registry is runtime.objects.registry
    assert runtime.objects.prefect.registry is runtime.objects.registry

    run_state_registry_2 = RunStateRegistry()
    assert run_state_registry_2 is not runtime.objects.registry
    runtime.objects.registry = run_state_registry_2

    assert runtime.objects.local.registry is runtime.objects.registry
    assert runtime.objects.prefect.registry is runtime.objects.registry


def test_engines_subscribe_to_config() -> None:
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    runtime = Runtime(
        objects=RuntimeObjects(
            local=mock_local_runner,
            prefect=mock_prefect_engine,
        ))

    assert isinstance(runtime.config.local, MockLocalRunnerConfig)
    assert isinstance(runtime.config.prefect, MockPrefectEngineConfig)
    assert runtime.objects.local.config is runtime.config.local
    assert runtime.objects.prefect.config is runtime.config.prefect
    assert runtime.objects.local.config.backend_verbose is True
    assert runtime.objects.prefect.config.server_url == ''

    runtime.config.local.backend_verbose = False
    runtime.config.prefect.server_url = 'https://my.prefectserver.nowhere'
    assert runtime.objects.local.config.backend_verbose is False
    assert runtime.objects.prefect.config.server_url == 'https://my.prefectserver.nowhere'

    mock_local_runner_config = MockLocalRunnerConfig(backend_verbose=True)
    mock_prefect_engine_config = MockPrefectEngineConfig(
        server_url='https://another.prefectserver.nowhere')
    runtime.config.local = mock_local_runner_config
    runtime.config.prefect = mock_prefect_engine_config

    assert runtime.objects.local.config is runtime.config.local is mock_local_runner_config
    assert runtime.objects.prefect.config is runtime.config.prefect is mock_prefect_engine_config
    assert runtime.objects.local.config.backend_verbose is True
    assert runtime.objects.prefect.config.server_url == 'https://another.prefectserver.nowhere'

    runtime.objects.local = MockLocalRunner()
    runtime.objects.prefect = MockPrefectEngine()
    assert runtime.objects.local.config is runtime.config.local is mock_local_runner_config
    assert runtime.objects.prefect.config is runtime.config.prefect is mock_prefect_engine_config
    assert runtime.objects.local.config.backend_verbose is True
    assert runtime.objects.prefect.config.server_url == 'https://another.prefectserver.nowhere'

    runtime.objects.local = LocalRunner()
    runtime.objects.prefect = PrefectEngine()
    assert isinstance(runtime.config.local, LocalRunnerConfig)
    assert isinstance(runtime.config.prefect, PrefectEngineConfig)
    assert runtime.config.local is not mock_local_runner_config
    assert runtime.config.prefect is not mock_prefect_engine_config


def test_registry_subscribe_to_logger() -> None:
    logger_1 = logging.getLogger('logger_1')
    logger_2 = logging.getLogger('logger_2')
    assert logger_1 is not logger_2

    mock_registry = MockRunStateRegistry()
    runtime = Runtime(objects=RuntimeObjects(
        logger=logger_1,
        registry=mock_registry,
    ))

    assert runtime.objects.registry.logger is runtime.objects.logger is logger_1

    runtime.objects.logger = logger_2
    assert runtime.objects.registry.logger is runtime.objects.logger is logger_2

    runtime.objects.registry = MockRunStateRegistry()
    assert runtime.objects.registry.logger is runtime.objects.logger is logger_2

    runtime.objects.registry = RunStateRegistry()
    assert runtime.objects.logger is logger_2


def test_registry_subscribe_to_config() -> None:
    mock_registry = MockRunStateRegistry()
    registry_config = RunStateRegistryConfig(verbose=False)
    runtime = Runtime(
        objects=RuntimeObjects(registry=mock_registry),
        config=RuntimeConfig(registry=registry_config),
    )
    assert runtime.objects.registry.config is runtime.config.registry is registry_config
    assert runtime.objects.registry.config.verbose is False

    runtime.config.registry.verbose = True
    assert runtime.objects.registry.config.verbose is True

    registry_config_2 = RunStateRegistryConfig(verbose=False)
    assert registry_config_2 is not registry_config
    runtime.config.registry = registry_config_2
    assert runtime.objects.registry.config is runtime.config.registry is registry_config_2
    assert runtime.objects.registry.config.verbose is False

    runtime.objects.registry = MockRunStateRegistry()
    assert runtime.objects.registry.config is runtime.config.registry is registry_config_2
    assert runtime.objects.registry.config.verbose is False

    runtime.objects.registry = RunStateRegistry()
    assert runtime.config.registry is registry_config_2


def test_task_class_subscribe_to_engine() -> None:
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    runtime = Runtime(
        objects=RuntimeObjects(
            local=mock_local_runner,
            prefect=mock_prefect_engine,
        ),
        classes=RuntimeClasses(task_template=MockTaskTemplate),
        config=RuntimeConfig(engine=EngineChoice.PREFECT),
    )

    assert issubclass(runtime.classes.task_template, MockTaskTemplate)
    assert isinstance(runtime.objects.local, MockLocalRunner)
    assert isinstance(runtime.objects.prefect, MockPrefectEngine)
    assert isinstance(runtime.config.engine, str)

    assert runtime.config.engine == EngineChoice.PREFECT
    assert runtime.classes.task_template.engine is runtime.objects.prefect

    runtime.config.engine = EngineChoice.LOCAL
    assert runtime.classes.task_template.engine is runtime.objects.local

    runtime.config.engine = EngineChoice.PREFECT
    assert runtime.classes.task_template.engine is runtime.objects.prefect

    mock_local_runner_2 = MockLocalRunner()
    mock_prefect_engine_2 = MockPrefectEngine()
    assert mock_local_runner_2 is not mock_local_runner
    assert mock_prefect_engine_2 is not mock_prefect_engine

    runtime.objects.local = mock_local_runner_2
    runtime.objects.prefect = mock_prefect_engine_2

    assert runtime.config.engine == EngineChoice.PREFECT
    assert runtime.classes.task_template.engine is runtime.objects.prefect is mock_prefect_engine_2

    runtime.config.engine = EngineChoice.LOCAL
    assert runtime.classes.task_template.engine is runtime.objects.local is mock_local_runner_2

    runtime.config.engine = EngineChoice.PREFECT
    runtime.classes.task_template = TaskTemplate
