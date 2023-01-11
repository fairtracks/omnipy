import logging

from omnipy.config.job import GlobalResumePreviousRunsOptions, GlobalSerializeOutputsOptions
from omnipy.config.runtime import Runtime, RuntimeConfig, RuntimeObjects
from omnipy.engine.constants import EngineChoice

from .helpers.functions import assert_logger
from .helpers.mocks import (MockJobConfig,
                            MockJobCreator,
                            MockJobCreator2,
                            MockLocalRunner,
                            MockLocalRunner2,
                            MockLocalRunnerConfig,
                            MockLocalRunnerConfig2,
                            MockPrefectEngine,
                            MockPrefectEngine2,
                            MockPrefectEngineConfig,
                            MockPrefectEngineConfig2,
                            MockRunStateRegistry,
                            MockRunStateRegistry2,
                            MockRunStateRegistryConfig)


def assert_runtime_config_default(config: RuntimeConfig):
    from omnipy.config.engine import LocalRunnerConfig, PrefectEngineConfig
    from omnipy.config.job import JobConfig
    from omnipy.config.registry import RunStateRegistryConfig

    assert isinstance(config.job, JobConfig)
    assert isinstance(config.job.serialize_outputs, GlobalSerializeOutputsOptions)
    assert isinstance(config.job.resume_previous_runs, GlobalResumePreviousRunsOptions)
    assert isinstance(config.engine, str)
    assert isinstance(config.local, LocalRunnerConfig)
    assert isinstance(config.prefect, PrefectEngineConfig)
    assert isinstance(config.prefect.use_cached_results, bool)
    assert isinstance(config.registry, RunStateRegistryConfig)
    assert isinstance(config.registry.verbose, bool)

    assert config.job.serialize_outputs == \
           GlobalSerializeOutputsOptions.WRITE_FLOW_AND_TASK_OUTPUTS
    assert config.job.resume_previous_runs == \
           GlobalResumePreviousRunsOptions.OFF
    assert config.engine == EngineChoice.LOCAL
    assert config.prefect.use_cached_results is False
    assert config.registry.verbose is True


def assert_runtime_objects_default(objects: RuntimeObjects):
    from omnipy.compute.job import JobBase, JobCreator
    from omnipy.engine.local import LocalRunner
    from omnipy.engine.prefect import PrefectEngine
    from omnipy.engine.registry import RunStateRegistry

    assert isinstance(objects.logger, logging.Logger)
    assert isinstance(objects.registry, RunStateRegistry)
    assert isinstance(objects.job_creator, JobCreator)
    assert isinstance(objects.local, LocalRunner)
    assert isinstance(objects.prefect, PrefectEngine)

    assert_logger(objects.logger)
    assert objects.job_creator is JobBase.job_creator


def test_config_default(teardown_loggers) -> None:
    assert_runtime_config_default(RuntimeConfig())


def test_objects_default() -> None:
    assert_runtime_objects_default(RuntimeObjects())


def test_default_config() -> None:
    runtime = Runtime()

    assert isinstance(runtime.config, RuntimeConfig)
    assert isinstance(runtime.objects, RuntimeObjects)

    assert_runtime_config_default(runtime.config)
    assert_runtime_objects_default(runtime.objects)


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

    mock_run_state_registry_2 = MockRunStateRegistry2()
    assert mock_run_state_registry_2 is not runtime.objects.registry
    runtime.objects.registry = mock_run_state_registry_2

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

    runtime.objects.local = MockLocalRunner2()
    runtime.objects.prefect = MockPrefectEngine2()
    assert isinstance(runtime.config.local, MockLocalRunnerConfig2)
    assert isinstance(runtime.config.prefect, MockPrefectEngineConfig2)
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

    runtime.objects.registry = MockRunStateRegistry2()
    assert runtime.objects.logger is logger_2


def test_registry_subscribe_to_config() -> None:
    mock_registry = MockRunStateRegistry()
    mock_registry_config = MockRunStateRegistryConfig(verbose=False)
    runtime = Runtime(
        objects=RuntimeObjects(registry=mock_registry),
        config=RuntimeConfig(registry=mock_registry_config),
    )
    assert runtime.objects.registry.config is runtime.config.registry is mock_registry_config
    assert runtime.objects.registry.config.verbose is False

    runtime.config.registry.verbose = True
    assert runtime.objects.registry.config.verbose is True

    mock_registry_config_2 = MockRunStateRegistryConfig(verbose=False)
    assert mock_registry_config_2 is not mock_registry_config
    runtime.config.registry = mock_registry_config_2
    assert runtime.objects.registry.config is runtime.config.registry is mock_registry_config_2
    assert runtime.objects.registry.config.verbose is False

    runtime.objects.registry = MockRunStateRegistry()
    assert runtime.objects.registry.config is runtime.config.registry is mock_registry_config_2
    assert runtime.objects.registry.config.verbose is False

    runtime.objects.registry = MockRunStateRegistry2()
    assert runtime.config.registry is mock_registry_config_2


def test_job_creator_subscribe_to_engine() -> None:
    mock_job_creator = MockJobCreator()
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    runtime = Runtime(
        objects=RuntimeObjects(
            job_creator=mock_job_creator,
            local=mock_local_runner,
            prefect=mock_prefect_engine,
        ),
        config=RuntimeConfig(engine=EngineChoice.PREFECT),
    )

    assert isinstance(runtime.objects.job_creator, MockJobCreator)
    assert isinstance(runtime.objects.local, MockLocalRunner)
    assert isinstance(runtime.objects.prefect, MockPrefectEngine)
    assert isinstance(runtime.config.engine, str)

    assert runtime.config.engine == EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is runtime.objects.prefect

    runtime.config.engine = EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is runtime.objects.local

    runtime.config.engine = EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is runtime.objects.prefect

    mock_local_runner_2 = MockLocalRunner()
    mock_prefect_engine_2 = MockPrefectEngine()
    assert mock_local_runner_2 is not mock_local_runner
    assert mock_prefect_engine_2 is not mock_prefect_engine

    runtime.objects.local = mock_local_runner_2
    runtime.objects.prefect = mock_prefect_engine_2

    assert runtime.config.engine == EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is runtime.objects.prefect is mock_prefect_engine_2

    runtime.config.engine = EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is runtime.objects.local is mock_local_runner_2

    runtime.config.engine = EngineChoice.PREFECT
    runtime.objects.job_creator = MockJobCreator2()
    assert runtime.objects.job_creator.engine is runtime.objects.prefect is mock_prefect_engine_2


def test_job_creator_subscribe_to_job_config() -> None:
    mock_job_creator = MockJobCreator()
    mock_job_config = MockJobConfig(serialize_outputs=False, resume_previous_runs=True)
    runtime = Runtime(
        objects=RuntimeObjects(job_creator=mock_job_creator),
        config=RuntimeConfig(job=mock_job_config),
    )
    assert runtime.objects.job_creator.config is runtime.config.job is mock_job_config
    assert runtime.objects.job_creator.config.serialize_outputs is False
    assert runtime.objects.job_creator.config.resume_previous_runs is True

    runtime.config.job.serialize_outputs = True
    assert runtime.objects.job_creator.config.serialize_outputs is True
    runtime.config.job.resume_previous_runs = False
    assert runtime.objects.job_creator.config.resume_previous_runs is False

    mock_job_config_2 = MockJobConfig(serialize_outputs=False, resume_previous_runs=True)
    assert mock_job_config_2 is not mock_job_config
    runtime.config.job = mock_job_config_2
    assert runtime.objects.job_creator.config is runtime.config.job is mock_job_config_2
    assert runtime.objects.job_creator.config.serialize_outputs is False
    assert runtime.objects.job_creator.config.resume_previous_runs is True

    runtime.objects.job_creator = MockJobCreator()
    assert runtime.objects.job_creator.config is runtime.config.job is mock_job_config_2
    assert runtime.objects.job_creator.config.serialize_outputs is False
    assert runtime.objects.job_creator.config.resume_previous_runs is True

    runtime.objects.job_creator = MockJobCreator2()
    assert runtime.config.job is mock_job_config_2
