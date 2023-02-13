import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from typing import Annotated, Optional, Type

import pytest

import omnipy
from omnipy.api.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions, EngineChoice
from omnipy.api.protocols import IsRuntime
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.root_log import RootLogObjects
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
    assert isinstance(config.job.persist_outputs, ConfigPersistOutputsOptions)
    assert isinstance(config.job.restore_outputs, ConfigRestoreOutputsOptions)
    assert isinstance(config.job.persist_data_dir_path, str)
    assert isinstance(config.engine, str)
    assert isinstance(config.local, LocalRunnerConfig)
    assert isinstance(config.prefect, PrefectEngineConfig)
    assert isinstance(config.prefect.use_cached_results, bool)
    assert isinstance(config.root_log, RootLogConfig)
    assert isinstance(config.root_log.log_to_stdout, bool)
    assert isinstance(config.root_log.log_to_stderr, bool)
    assert isinstance(config.root_log.log_to_file, bool)
    assert isinstance(config.root_log.stdout_log_min_level, int)
    assert isinstance(config.root_log.stderr_log_min_level, int)
    assert isinstance(config.root_log.file_log_min_level, int)
    assert isinstance(config.root_log.file_log_dir_path, str)

    assert config.job.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert config.job.restore_outputs == \
           ConfigRestoreOutputsOptions.DISABLED
    assert config.job.persist_data_dir_path == \
           os.path.join(dir_path, 'data')
    assert config.engine == EngineChoice.LOCAL
    assert config.prefect.use_cached_results is False
    assert config.root_log.log_to_stdout
    assert config.root_log.log_to_stderr
    assert config.root_log.log_to_file
    assert config.root_log.stdout_log_min_level == logging.INFO
    assert config.root_log.stderr_log_min_level == logging.ERROR
    assert config.root_log.file_log_min_level == logging.WARNING
    assert config.root_log.file_log_dir_path == os.path.join(dir_path, 'logs')


def _log_record_for_level(level: int):
    test_logger = logging.getLogger('test_logger')
    return test_logger.makeRecord(
        name=test_logger.name, level=level, fn='', lno=0, msg='my log msg', args=(), exc_info=None)


def _assert_root_stdout_handler(root_stdout_handler: Optional[logging.StreamHandler],
                                root_log_config: RootLogConfig):
    if root_log_config.log_to_stdout:
        assert isinstance(root_stdout_handler, logging.StreamHandler)
        assert root_stdout_handler.stream is omnipy.hub.root_log.stdout
        assert root_stdout_handler.level == root_log_config.stdout_log_min_level

        for level in [
                logging.NOTSET,
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL
        ]:
            if root_log_config.stdout_log_min_level <= level:
                if root_log_config.log_to_stderr and root_log_config.stderr_log_min_level <= level:
                    assert root_stdout_handler.filter(_log_record_for_level(level)) is False
                else:
                    assert root_stdout_handler.filter(_log_record_for_level(level)) is True
    else:
        assert root_stdout_handler is None


def _assert_root_stderr_handler(root_stderr_handler: Optional[logging.StreamHandler],
                                root_log_config: RootLogConfig):
    if root_log_config.log_to_stderr:
        assert isinstance(root_stderr_handler, logging.StreamHandler)
        assert root_stderr_handler.stream is omnipy.hub.root_log.stderr
        assert root_stderr_handler.level == root_log_config.stderr_log_min_level
    else:
        assert root_stderr_handler is None


def _assert_root_file_handler(root_file_handler: Optional[TimedRotatingFileHandler],
                              root_log_config: RootLogConfig):
    if root_log_config.log_to_file:
        assert isinstance(root_file_handler, TimedRotatingFileHandler)
        assert root_file_handler.when == 'D'
        assert root_file_handler.interval == 60 * 60 * 24
        assert root_file_handler.backupCount == 7
        assert root_file_handler.level == root_log_config.file_log_min_level
        assert root_file_handler.baseFilename == \
               str(Path(root_log_config.file_log_dir_path).joinpath('omnipy.log'))
    else:
        assert root_file_handler is None


def _assert_root_log_objects(root_log_objects: RootLogObjects,
                             root_log_config: RootLogConfig) -> None:
    _assert_root_stdout_handler(root_log_objects.stdout_handler, root_log_config)
    _assert_root_stderr_handler(root_log_objects.stderr_handler, root_log_config)
    _assert_root_file_handler(root_log_objects.file_handler, root_log_config)


def _assert_runtime_objects_default(objects: RuntimeObjects, config: RuntimeConfig):
    from omnipy.compute.job import JobBase
    from omnipy.compute.job_creator import JobCreator
    from omnipy.engine.local import LocalRunner
    from omnipy.log.registry import RunStateRegistry
    from omnipy.modules.prefect.engine.prefect import PrefectEngine

    assert isinstance(objects.job_creator, JobCreator)
    assert objects.job_creator is JobBase.job_creator

    # TODO: add level "objects.engine" ?
    assert isinstance(objects.local, LocalRunner)
    assert isinstance(objects.prefect, PrefectEngine)

    assert isinstance(objects.registry, RunStateRegistry)

    _assert_root_log_objects(objects.root_log, config.root_log)


def test_config_default(runtime: Annotated[IsRuntime, pytest.fixture],
                        teardown_loggers: Annotated[None, pytest.fixture],
                        tmp_dir_path: Annotated[str, pytest.fixture]) -> None:
    _assert_runtime_config_default(RuntimeConfig(), str(Path.cwd()))


def test_objects_default(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    _assert_runtime_objects_default(RuntimeObjects(), RuntimeConfig())


def test_default_config(runtime: Annotated[IsRuntime, pytest.fixture],
                        tmp_dir_path: Annotated[str, pytest.fixture]) -> None:
    assert isinstance(runtime.config, RuntimeConfig)
    assert isinstance(runtime.objects, RuntimeObjects)

    _assert_runtime_config_default(runtime.config, tmp_dir_path)
    _assert_runtime_objects_default(runtime.objects, runtime.config)


def test_root_log_config_dependencies(runtime: Annotated[IsRuntime, pytest.fixture],
                                      tmp_dir_path: Annotated[str, pytest.fixture]) -> None:
    runtime.config.root_log.log_to_stdout = False
    runtime.config.root_log.log_to_stderr = False

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = False
    runtime.config.root_log.log_to_stderr = True
    runtime.config.root_log.stderr_log_min_level = logging.WARNING

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = True
    runtime.config.root_log.log_to_stderr = False
    runtime.config.root_log.stdout_log_min_level = logging.DEBUG

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = True
    runtime.config.root_log.log_to_stderr = True
    runtime.config.root_log.stdout_log_min_level = logging.INFO
    runtime.config.root_log.stderr_log_min_level = logging.WARNING

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = True
    runtime.config.root_log.log_to_stderr = True
    runtime.config.root_log.stdout_log_min_level = logging.WARNING
    runtime.config.root_log.stderr_log_min_level = logging.INFO

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_file = True
    runtime.config.root_log.file_log_min_level = logging.INFO
    runtime.config.root_log.file_log_dir_path = str(Path(tmp_dir_path).joinpath('extra_level'))

    _assert_root_file_handler(runtime.objects.root_log.file_handler, runtime.config.root_log)


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


#
# def test_registry_subscribe_to_logger(
#         runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:
#     logger_1 = logging.getLogger('logger_1')
#     logger_2 = logging.getLogger('logger_2')
#     assert logger_1 is not logger_2
#
#     mock_registry = MockRunStateRegistry()
#     runtime = runtime_cls(objects=RuntimeObjects(
#         logger=logger_1,
#         registry=mock_registry,
#     ))
#
#     assert runtime.objects.registry.logger is runtime.objects.logger is logger_1
#
#     runtime.objects.logger = logger_2
#     assert runtime.objects.registry.logger is runtime.objects.logger is logger_2
#
#     runtime.objects.registry = MockRunStateRegistry()
#     assert runtime.objects.registry.logger is runtime.objects.logger is logger_2
#
#     runtime.objects.registry = MockRunStateRegistry2()
#     assert runtime.objects.logger is logger_2


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
