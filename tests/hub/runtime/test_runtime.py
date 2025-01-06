from collections import defaultdict
import os
from pathlib import Path
from typing import Annotated, Type

import pytest
import pytest_cases as pc

from omnipy.api.enums import (BackoffStrategy,
                              ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions,
                              EngineChoice)
from omnipy.api.protocols.public.config import IsEngineConfig
from omnipy.api.protocols.public.hub import IsRuntime, IsRuntimeConfig
from omnipy.components.prefect.engine.prefect import PrefectEngine
from omnipy.compute.job import JobBase
from omnipy.compute.job_creator import JobCreator
from omnipy.config.data import DataConfig
from omnipy.config.engine import LocalRunnerConfig, PrefectEngineConfig
from omnipy.config.job import JobConfig
from omnipy.config.root_log import RootLogConfig
from omnipy.data.data_class_creator import DataClassBase, DataClassCreator
from omnipy.data.serializer import SerializerRegistry
from omnipy.engine.local import LocalRunner
from omnipy.hub.log.root_log import RootLogObjects
from omnipy.hub.registry import RunStateRegistry
from omnipy.hub.runtime import RuntimeConfig, RuntimeObjects

from .helpers.mocks import (MockLocalRunner,
                            MockLocalRunnerConfig,
                            MockPrefectEngine,
                            MockPrefectEngineConfig)


def _assert_runtime_config_default(config: IsRuntimeConfig, dir_path: Path):
    assert isinstance(config.job, JobConfig)
    assert config.job.output_storage.persist_outputs == \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert config.job.output_storage.restore_outputs == \
           ConfigRestoreOutputsOptions.DISABLED
    assert config.job.output_storage.protocol == \
           ConfigOutputStorageProtocolOptions.LOCAL
    assert config.job.output_storage.local.persist_data_dir_path == str(dir_path / 'outputs')
    assert config.job.output_storage.s3.persist_data_dir_path == os.path.join('omnipy', 'outputs')
    assert config.job.output_storage.s3.endpoint_url == ''
    assert config.job.output_storage.s3.bucket_name == ''
    assert config.job.output_storage.s3.access_key == ''
    assert config.job.output_storage.s3.secret_key == ''

    assert isinstance(config.data, DataConfig)
    assert config.data.interactive_mode is True
    assert config.data.dynamically_convert_elements_to_models is False
    assert config.data.terminal_size_columns == 80
    assert config.data.terminal_size_lines == 24
    assert config.data.http_defaults.requests_per_time_period == 60
    assert config.data.http_defaults.time_period_in_secs == 60
    assert config.data.http_defaults.retry_http_statuses == (408, 425, 429, 500, 502, 503, 504)
    assert config.data.http_defaults.retry_attempts == 5
    assert config.data.http_defaults.retry_backoff_strategy == BackoffStrategy.EXPONENTIAL
    assert isinstance(config.data.http_config_for_host, defaultdict)

    assert config.engine == EngineChoice.LOCAL
    assert isinstance(config.local, LocalRunnerConfig)
    assert isinstance(config.prefect, PrefectEngineConfig)
    assert config.prefect.use_cached_results is False


def _assert_runtime_objects_default(objects: RuntimeObjects):
    assert isinstance(objects.job_creator, JobCreator)
    assert objects.job_creator is JobBase.job_creator

    assert isinstance(objects.data_class_creator, DataClassCreator)
    assert objects.data_class_creator is DataClassBase.data_class_creator

    assert isinstance(objects.local, LocalRunner)
    assert isinstance(objects.prefect, PrefectEngine)
    assert isinstance(objects.registry, RunStateRegistry)
    assert isinstance(objects.serializers, SerializerRegistry)

    assert isinstance(objects.root_log, RootLogObjects)


def test_config_default() -> None:
    _assert_runtime_config_default(RuntimeConfig(), Path.cwd())


def test_objects_default(teardown_rm_default_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_runtime_objects_default(RuntimeObjects())


def test_default_runtime(runtime: Annotated[IsRuntime, pytest.fixture],
                         tmp_dir_path: Annotated[Path, pytest.fixture]) -> None:
    assert isinstance(runtime.config, RuntimeConfig)
    assert isinstance(runtime.objects, RuntimeObjects)

    _assert_runtime_config_default(runtime.config, tmp_dir_path)
    _assert_runtime_objects_default(runtime.objects)


def test_data_config_http_config_for_host_default(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    assert runtime.config.data.http_config_for_host['myserver.com']\
        .requests_per_time_period == 60
    runtime.config.data.http_defaults.requests_per_time_period = 30
    assert runtime.config.data.http_config_for_host['myotherserver.com']\
        .requests_per_time_period == 30
    assert runtime.config.data.http_config_for_host['myserver.com']\
        .requests_per_time_period == 60


def test_init_runtime_config_after_data_class_creator(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:

    DataClassBase.data_class_creator.config.dynamically_convert_elements_to_models = True
    runtime = runtime_cls()

    assert runtime.config.data.dynamically_convert_elements_to_models is True

    runtime.config.reset_to_defaults()

    _assert_runtime_config_default(runtime.config, Path.cwd())
    assert DataClassBase.data_class_creator.config.dynamically_convert_elements_to_models is False


def test_init_runtime_config_after_job_creator(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:

    JobBase.job_creator.config.output_storage.persist_outputs = ConfigPersistOutputsOptions.DISABLED
    runtime = runtime_cls()

    assert runtime.config.job.output_storage.persist_outputs == ConfigPersistOutputsOptions.DISABLED

    runtime.config.reset_to_defaults()

    _assert_runtime_config_default(runtime.config, Path.cwd())
    assert runtime.config.job.output_storage.persist_outputs \
           == ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS


@pc.parametrize(
    argnames=[
        'publisher_runtime_attr_names',
        'publisher_cls',
        'subscriber_runtime_attr_names',
        'subscriber_cls',
        'subscriber_attr_name',
    ],
    argvalues=[
        (
            ('config', 'job'),
            JobConfig,
            ('objects', 'job_creator'),
            JobCreator,
            'config',
        ),
        (
            ('config', 'data'),
            DataConfig,
            ('objects', 'data_class_creator'),
            DataClassCreator,
            'config',
        ),
        (
            ('config', 'local'),
            LocalRunnerConfig,
            ('objects', 'local'),
            LocalRunner,
            'config',
        ),
        (
            ('config', 'prefect'),
            PrefectEngineConfig,
            ('objects', 'prefect'),
            PrefectEngine,
            'config',
        ),
        (
            ('config', 'root_log'),
            RootLogConfig,
            ('objects', 'root_log'),
            RootLogObjects,
            'config',
        ),
        (
            ('objects', 'registry'),
            RunStateRegistry,
            ('objects', 'local'),
            LocalRunner,
            'registry',
        ),
        (
            ('objects', 'registry'),
            RunStateRegistry,
            ('objects', 'prefect'),
            PrefectEngine,
            'registry',
        ),
    ],
    ids=[
        'config->job => objects->job_creator',
        'config->data => objects->data_class_creator',
        'config->local => objects->local',
        'config->prefect => objects->prefect',
        'config->root_log => objects->root_log',
        'objects->registry => objects->local',
        'objects->registry => objects->prefect',
    ])
def test_basic_runtime_subscriptions(
    runtime: Annotated[IsRuntime, pytest.fixture],
    publisher_runtime_attr_names: tuple[str, ...],
    publisher_cls: type,
    subscriber_runtime_attr_names: tuple[str, ...],
    subscriber_cls: type,
    subscriber_attr_name: str,
) -> None:
    def _get_runtime_nested_attr(attr_names: tuple[str, ...]) -> object:
        obj = runtime
        for attr_name in attr_names:
            obj = getattr(obj, attr_name)
        return obj

    def _publisher() -> object:
        return _get_runtime_nested_attr(publisher_runtime_attr_names)

    def _subscriber() -> object:
        return _get_runtime_nested_attr(subscriber_runtime_attr_names)

    def _subscriber_attr(subscriber: object) -> object:
        return getattr(subscriber, subscriber_attr_name)

    publisher = _publisher()
    publisher_parent = _get_runtime_nested_attr(publisher_runtime_attr_names[:-1])
    publisher_parent_attr_name = publisher_runtime_attr_names[-1]

    subscriber = _subscriber()
    subscriber_parent = _get_runtime_nested_attr(subscriber_runtime_attr_names[:-1])
    subscriber_parent_attr_name = subscriber_runtime_attr_names[-1]

    assert isinstance(publisher, publisher_cls)
    assert isinstance(subscriber, subscriber_cls)
    assert _subscriber_attr(subscriber) is publisher

    subscriber_2 = subscriber_cls()
    setattr(subscriber_parent, subscriber_parent_attr_name, subscriber_2)
    assert _subscriber() is subscriber_2 is not subscriber
    assert _subscriber_attr(subscriber_2) is publisher

    publisher_2 = publisher_cls()
    setattr(publisher_parent, publisher_parent_attr_name, publisher_2)
    assert _publisher() is publisher_2 is not publisher
    assert _subscriber() is subscriber_2 is not subscriber
    assert _subscriber_attr(subscriber_2) is publisher_2 is not publisher

    setattr(subscriber_parent, subscriber_parent_attr_name, subscriber)
    assert _subscriber() is subscriber is not subscriber_2
    assert _subscriber_attr(subscriber) is publisher_2


def test_job_creator_subscribes_to_selected_engine(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    local_runner = runtime.objects.local
    prefect_engine = runtime.objects.prefect

    assert isinstance(runtime.objects.job_creator, JobCreator)
    assert isinstance(local_runner, LocalRunner)
    assert isinstance(prefect_engine, PrefectEngine)
    assert isinstance(runtime.config.engine, str)

    assert runtime.config.engine == EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is local_runner

    runtime.config.engine = EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is prefect_engine

    runtime.config.engine = EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is local_runner

    local_runner_2 = LocalRunner()
    prefect_engine_2 = PrefectEngine()
    assert local_runner_2 is not local_runner
    assert prefect_engine_2 is not prefect_engine

    runtime.objects.local = local_runner_2
    runtime.objects.prefect = prefect_engine_2

    assert runtime.config.engine == EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is runtime.objects.local is local_runner_2

    runtime.config.engine = EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is runtime.objects.prefect is prefect_engine_2

    runtime.config.engine = EngineChoice.LOCAL
    runtime.objects.job_creator = JobCreator()
    assert runtime.objects.job_creator.engine is runtime.objects.local is local_runner_2


@pc.parametrize(
    'engine_name, engine_cls, config_cls, mock_engine_cls, mock_config_class',
    [
        ('local', LocalRunner, LocalRunnerConfig, MockLocalRunner, MockLocalRunnerConfig),
        ('prefect', PrefectEngine, PrefectEngineConfig, MockPrefectEngine, MockPrefectEngineConfig),
    ],
    ids=['local', 'prefect'])
def test_new_engine_object_updates_engine_config_if_needed(
    runtime: Annotated[IsRuntime, pytest.fixture],
    engine_name: str,
    engine_cls: type,
    config_cls: type,
    mock_engine_cls: type,
    mock_config_class: type,
) -> None:
    def _get_engine_config() -> IsEngineConfig:
        return getattr(runtime.config, engine_name)

    def _get_engine_object() -> IsEngineConfig:
        return getattr(runtime.objects, engine_name)

    def _set_engine_object(value) -> None:
        setattr(runtime.objects, engine_name, value)

    assert isinstance(_get_engine_object(), engine_cls)
    assert isinstance(_get_engine_config(), config_cls)

    config = _get_engine_config()
    _set_engine_object(engine_cls())

    assert isinstance(_get_engine_config(), config_cls)
    assert _get_engine_config() is config

    _set_engine_object(mock_engine_cls())

    assert isinstance(_get_engine_config(), mock_config_class)
    assert _get_engine_config() is not config

    mock_config = _get_engine_config()
    _set_engine_object(mock_engine_cls())

    assert isinstance(_get_engine_config(), mock_config_class)
    assert _get_engine_config() is mock_config

    _set_engine_object(engine_cls())

    assert isinstance(_get_engine_config(), config_cls)
    assert _get_engine_config() is not config
    assert _get_engine_config() is not mock_config
