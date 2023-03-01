import logging
import os
from pathlib import Path
from typing import Annotated, Type

import pytest

from omnipy.api.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions, EngineChoice
from omnipy.api.protocols import IsRuntime
from omnipy.hub.runtime import RuntimeConfig, RuntimeObjects

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
                            MockRootLogConfig,
                            MockRootLogObjects,
                            MockRootLogObjects2,
                            MockRunStateRegistry,
                            MockRunStateRegistry2)


def _assert_runtime_config_default(config: RuntimeConfig, dir_path: str):
    from omnipy.config.engine import LocalRunnerConfig, PrefectEngineConfig
    from omnipy.config.job import JobConfig

    assert isinstance(config.job, JobConfig)
    assert isinstance(config.local, LocalRunnerConfig)
    assert isinstance(config.prefect, PrefectEngineConfig)

    assert config.job.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert config.job.restore_outputs == \
           ConfigRestoreOutputsOptions.DISABLED
    assert config.job.persist_data_dir_path == \
           os.path.join(dir_path, 'data')
    assert config.engine == EngineChoice.LOCAL
    assert config.prefect.use_cached_results is False


def _assert_runtime_objects_default(objects: RuntimeObjects, config: RuntimeConfig):
    from omnipy.compute.job import JobBase
    from omnipy.compute.job_creator import JobCreator
    from omnipy.engine.local import LocalRunner
    from omnipy.log.registry import RunStateRegistry
    from omnipy.modules.prefect.engine.prefect import PrefectEngine

    assert isinstance(objects.job_creator, JobCreator)
    assert objects.job_creator is JobBase.job_creator

    # TDDD: add level "objects.engine" ?
    assert isinstance(objects.local, LocalRunner)
    assert isinstance(objects.prefect, PrefectEngine)

    assert isinstance(objects.registry, RunStateRegistry)


def test_config_default(teardown_rm_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_runtime_config_default(RuntimeConfig(), str(Path.cwd()))


def test_objects_default(teardown_rm_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_runtime_objects_default(RuntimeObjects(), RuntimeConfig())


def test_default_config(runtime: Annotated[IsRuntime, pytest.fixture],
                        tmp_dir_path: Annotated[str, pytest.fixture]) -> None:
    assert isinstance(runtime.config, RuntimeConfig)
    assert isinstance(runtime.objects, RuntimeObjects)

    _assert_runtime_config_default(runtime.config, tmp_dir_path)
    _assert_runtime_objects_default(runtime.objects, runtime.config)


def test_engines_subscribe_to_registry(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    mock_registry = MockRunStateRegistry()

    runtime = runtime_cls(
        objects=RuntimeObjects(
            local=mock_local_runner,
            prefect=mock_prefect_engine,
            registry=mock_registry,
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


def test_engines_subscribe_to_config(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    runtime = runtime_cls(
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


def test_root_log_object_subscribe_to_config(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:
    mock_root_log_objects = MockRootLogObjects()
    mock_root_log_config = MockRootLogConfig(log_to_stderr=False)
    runtime = runtime_cls(
        objects=RuntimeObjects(root_log=mock_root_log_objects),
        config=RuntimeConfig(root_log=mock_root_log_config),
    )
    assert runtime.objects.root_log.config is runtime.config.root_log is mock_root_log_config
    assert runtime.objects.root_log.config.log_to_stderr is False

    runtime.config.root_log.log_to_stderr = True
    assert runtime.objects.root_log.config.log_to_stderr is True

    mock_root_log_config_2 = MockRootLogConfig(log_to_stderr=False)
    assert mock_root_log_config_2 is not mock_root_log_config
    runtime.config.root_log = mock_root_log_config_2
    assert runtime.objects.root_log.config is runtime.config.root_log is mock_root_log_config_2
    assert runtime.objects.root_log.config.log_to_stderr is False

    runtime.objects.root_log = MockRootLogObjects()
    assert runtime.objects.root_log.config is runtime.config.root_log is mock_root_log_config_2
    assert runtime.objects.root_log.config.log_to_stderr is False

    runtime.objects.root_log = MockRootLogObjects2()
    assert runtime.config.root_log is mock_root_log_config_2


def test_job_creator_subscribe_to_engine(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:
    mock_job_creator = MockJobCreator()
    mock_local_runner = MockLocalRunner()
    mock_prefect_engine = MockPrefectEngine()
    runtime = runtime_cls(
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


def test_job_creator_subscribe_to_job_config(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:
    mock_job_creator = MockJobCreator()
    mock_job_config = MockJobConfig(persist_outputs=False, restore_outputs=True)
    runtime = runtime_cls(
        objects=RuntimeObjects(job_creator=mock_job_creator),
        config=RuntimeConfig(job=mock_job_config),
    )
    assert runtime.objects.job_creator.config is runtime.config.job is mock_job_config
    assert runtime.objects.job_creator.config.persist_outputs is False
    assert runtime.objects.job_creator.config.restore_outputs is True

    runtime.config.job.persist_outputs = True
    assert runtime.objects.job_creator.config.persist_outputs is True
    runtime.config.job.restore_outputs = False
    assert runtime.objects.job_creator.config.restore_outputs is False

    mock_job_config_2 = MockJobConfig(persist_outputs=False, restore_outputs=True)
    assert mock_job_config_2 is not mock_job_config
    runtime.config.job = mock_job_config_2
    assert runtime.objects.job_creator.config is runtime.config.job is mock_job_config_2
    assert runtime.objects.job_creator.config.persist_outputs is False
    assert runtime.objects.job_creator.config.restore_outputs is True

    runtime.objects.job_creator = MockJobCreator()
    assert runtime.objects.job_creator.config is runtime.config.job is mock_job_config_2
    assert runtime.objects.job_creator.config.persist_outputs is False
    assert runtime.objects.job_creator.config.restore_outputs is True

    runtime.objects.job_creator = MockJobCreator2()
    assert runtime.config.job is mock_job_config_2
