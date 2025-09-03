from collections import defaultdict
import logging
import os
from pathlib import Path
import sys
from typing import Annotated, Type

import pytest
import pytest_cases as pc

from omnipy.components.prefect.engine.prefect import PrefectEngine
from omnipy.compute._job import JobBase
from omnipy.compute._job_creator import JobCreator
from omnipy.config.data import (BrowserUserInterfaceConfig,
                                ColorConfig,
                                DataConfig,
                                HttpConfig,
                                HttpRequestsConfig,
                                JupyterUserInterfaceConfig,
                                LayoutConfig,
                                ModelConfig,
                                OverflowConfig,
                                TerminalUserInterfaceConfig,
                                TextConfig,
                                UserInterfaceConfig)
from omnipy.config.engine import EngineConfig, LocalRunnerConfig, PrefectEngineConfig
from omnipy.config.job import (JobConfig,
                               LocalOutputStorageConfig,
                               OutputStorageConfig,
                               S3OutputStorageConfig)
from omnipy.config.root_log import RootLogConfig
from omnipy.data._data_class_creator import DataClassBase, DataClassCreator
from omnipy.data._display.integrations.jupyter.helpers import ReactiveConfigCopy, ReactiveObjects
from omnipy.data.serializer import SerializerRegistry
from omnipy.engine.local import LocalRunner
from omnipy.hub._registry import RunStateRegistry
from omnipy.hub.log._root_log import RootLogObjects
from omnipy.hub.runtime import RuntimeConfig, RuntimeObjects
from omnipy.shared.enums.colorstyles import RecommendedColorStyles
from omnipy.shared.enums.data import BackoffStrategy
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         DisplayDimensionsUpdateMode,
                                         HorizontalOverflowMode,
                                         PanelDesign,
                                         PrettyPrinterLib,
                                         VerticalOverflowMode)
from omnipy.shared.enums.job import (ConfigOutputStorageProtocolOptions,
                                     ConfigPersistOutputsOptions,
                                     ConfigRestoreOutputsOptions,
                                     EngineChoice)
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.runtime import IsRuntime, IsRuntimeConfig

from .helpers.mocks import (MockLocalRunner,
                            MockLocalRunnerConfig,
                            MockPrefectEngine,
                            MockPrefectEngineConfig)


def _assert_runtime_config_default(config: IsRuntimeConfig, dir_path: Path):
    # runtime
    assert isinstance(config, RuntimeConfig)

    # data
    assert isinstance(config.data, DataConfig)
    assert config.data.ui.cache_dir_path == str(dir_path / '_cache')

    assert isinstance(config.data.ui, UserInterfaceConfig)

    assert isinstance(config.data.ui.terminal, TerminalUserInterfaceConfig)
    assert config.data.ui.terminal.width == 80
    assert config.data.ui.terminal.height == 24
    assert config.data.ui.terminal.dims_mode == DisplayDimensionsUpdateMode.AUTO
    assert isinstance(config.data.ui.terminal.color, ColorConfig)
    assert config.data.ui.terminal.color.system == DisplayColorSystem.AUTO
    assert config.data.ui.terminal.color.style == RecommendedColorStyles.ANSI_LIGHT
    assert config.data.ui.terminal.color.solid_background is False

    assert isinstance(config.data.ui.jupyter, JupyterUserInterfaceConfig)
    assert config.data.ui.jupyter.width == 112
    assert config.data.ui.jupyter.height == 48
    assert config.data.ui.jupyter.dims_mode == DisplayDimensionsUpdateMode.AUTO
    assert isinstance(config.data.ui.jupyter.color, ColorConfig)
    assert config.data.ui.jupyter.color.system is DisplayColorSystem.ANSI_RGB
    assert config.data.ui.jupyter.color.style \
           is RecommendedColorStyles.OMNIPY_SELENIZED_WHITE
    assert config.data.ui.jupyter.color.dark_background is False
    assert config.data.ui.jupyter.color.solid_background is False

    assert isinstance(config.data.ui.browser, BrowserUserInterfaceConfig)
    assert config.data.ui.browser.width == 160
    assert config.data.ui.browser.height is None
    assert not hasattr(config.data.ui.browser, 'dims_mode')
    assert isinstance(config.data.ui.browser.color, ColorConfig)
    assert config.data.ui.browser.color.system is DisplayColorSystem.ANSI_RGB
    assert config.data.ui.browser.color.style \
           is RecommendedColorStyles.OMNIPY_SELENIZED_WHITE
    assert config.data.ui.jupyter.color.dark_background is False
    assert config.data.ui.browser.color.solid_background is False

    assert isinstance(config.data.ui.text, TextConfig)

    assert isinstance(config.data.ui.text.overflow, OverflowConfig)
    assert config.data.ui.text.overflow.horizontal \
           is HorizontalOverflowMode.ELLIPSIS
    assert config.data.ui.text.overflow.vertical \
           is VerticalOverflowMode.ELLIPSIS_BOTTOM

    assert config.data.ui.text.tab_size == 4
    assert config.data.ui.text.indent_tab_size == 2
    assert config.data.ui.text.pretty_printer is PrettyPrinterLib.AUTO
    assert config.data.ui.text.debug_mode is False

    assert isinstance(config.data.ui.layout, LayoutConfig)

    assert isinstance(config.data.ui.layout.overflow, OverflowConfig)
    assert config.data.ui.layout.overflow.horizontal \
           is HorizontalOverflowMode.ELLIPSIS
    assert config.data.ui.layout.overflow.vertical \
           is VerticalOverflowMode.ELLIPSIS_BOTTOM

    assert config.data.ui.layout.panel_design is PanelDesign.TABLE_GRID
    assert config.data.ui.layout.panel_title_at_top is True

    assert isinstance(config.data.model, ModelConfig)
    assert config.data.model.interactive is True
    assert config.data.model.dynamically_convert_elements_to_models is False

    assert isinstance(config.data.http, HttpConfig)

    assert isinstance(config.data.http.defaults, HttpRequestsConfig)
    assert config.data.http.defaults.requests_per_time_period == 60
    assert config.data.http.defaults.time_period_in_secs == 60
    assert config.data.http.defaults.retry_http_statuses == (408, 425, 429, 500, 502, 503, 504)
    assert config.data.http.defaults.retry_attempts == 5
    assert config.data.http.defaults.retry_backoff_strategy is BackoffStrategy.EXPONENTIAL

    assert isinstance(config.data.http.for_host, defaultdict)

    assert isinstance(config.data.http.for_host['some_server.com'], HttpRequestsConfig)
    assert config.data.http.for_host['some_server.com'].requests_per_time_period == 60
    assert config.data.http.for_host['some_server.com'].time_period_in_secs == 60
    assert config.data.http.for_host['some_server.com'].retry_http_statuses \
           == (408, 425, 429, 500, 502, 503, 504)
    assert config.data.http.for_host['some_server.com'].retry_attempts == 5
    assert config.data.http.for_host['some_server.com'].retry_backoff_strategy \
           is BackoffStrategy.EXPONENTIAL

    # engine
    assert isinstance(config.engine, EngineConfig)

    assert config.engine.choice == EngineChoice.LOCAL

    assert isinstance(config.engine.local, LocalRunnerConfig)

    assert isinstance(config.engine.prefect, PrefectEngineConfig)
    assert config.engine.prefect.use_cached_results is False

    # job
    assert isinstance(config.job, JobConfig)

    assert isinstance(config.job.output_storage, OutputStorageConfig)
    assert config.job.output_storage.persist_outputs is \
           ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    assert config.job.output_storage.restore_outputs is \
           ConfigRestoreOutputsOptions.DISABLED
    assert config.job.output_storage.protocol is \
           ConfigOutputStorageProtocolOptions.LOCAL

    assert isinstance(config.job.output_storage.local, LocalOutputStorageConfig)
    assert config.job.output_storage.local.persist_data_dir_path == str(dir_path / 'outputs')

    assert isinstance(config.job.output_storage.s3, S3OutputStorageConfig)
    assert config.job.output_storage.s3.persist_data_dir_path == os.path.join('omnipy', 'outputs')
    assert config.job.output_storage.s3.endpoint_url == ''
    assert config.job.output_storage.s3.bucket_name == ''
    assert config.job.output_storage.s3.access_key == ''
    assert config.job.output_storage.s3.secret_key == ''

    # root_log
    assert isinstance(config.root_log, RootLogConfig)
    assert config.root_log.log_format_str \
           == '[{engine}] {asctime} - {levelname}: {message} ({name})'
    assert config.root_log.locale[1] == 'UTF-8'  # seems safe to assume this
    assert config.root_log.log_to_stdout is True
    assert config.root_log.log_to_stderr is True
    assert config.root_log.log_to_file is True
    assert config.root_log.stdout is sys.stdout
    assert config.root_log.stderr is sys.stderr
    assert config.root_log.stdout_log_min_level is logging.INFO
    assert config.root_log.stderr_log_min_level is logging.ERROR
    assert config.root_log.file_log_min_level is logging.WARNING
    assert config.root_log.file_log_path.endswith('logs/omnipy.log')


def _assert_runtime_objects_default(objects: RuntimeObjects):
    assert isinstance(objects.job_creator, JobCreator)
    assert objects.job_creator is JobBase.job_creator

    assert isinstance(objects.data_class_creator, DataClassCreator)
    assert objects.data_class_creator is DataClassBase.data_class_creator

    assert isinstance(objects.reactive, ReactiveObjects)
    assert isinstance(objects.reactive.jupyter_ui_config, ReactiveConfigCopy)

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
    assert runtime.config.data.http.for_host['myserver.com']\
        .requests_per_time_period == 60
    runtime.config.data.http.defaults.requests_per_time_period = 30
    assert runtime.config.data.http.for_host['myotherserver.com']\
        .requests_per_time_period == 30
    assert runtime.config.data.http.for_host['myserver.com']\
        .requests_per_time_period == 60


def test_data_config_display_dimensions(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    runtime.config.data.ui.terminal.width = 80
    runtime.config.data.ui.terminal.height = 24
    runtime.config.data.ui.terminal.dims_mode = DisplayDimensionsUpdateMode.FIXED
    os.environ['COLUMNS'] = '100'
    os.environ['LINES'] = '50'
    assert runtime.config.data.ui.terminal.width == 80
    assert runtime.config.data.ui.terminal.height == 24
    runtime.config.data.ui.terminal.dims_mode = DisplayDimensionsUpdateMode.AUTO
    assert runtime.config.data.ui.terminal.width == 100
    assert runtime.config.data.ui.terminal.height == 50
    os.environ.pop('COLUMNS')
    os.environ.pop('LINES')
    assert runtime.config.data.ui.terminal.width == 100
    assert runtime.config.data.ui.terminal.height == 50
    os.environ['COLUMNS'] = '80'
    os.environ['LINES'] = '24'
    assert runtime.config.data.ui.terminal.width == 80
    assert runtime.config.data.ui.terminal.height == 24
    os.environ.pop('COLUMNS')
    os.environ.pop('LINES')


def test_init_runtime_config_after_data_class_creator(
        runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> None:

    DataClassBase.data_class_creator.config.model.dynamically_convert_elements_to_models = True
    runtime = runtime_cls()

    assert runtime.config.data.model.dynamically_convert_elements_to_models is True

    runtime.config.reset_to_defaults()

    _assert_runtime_config_default(runtime.config, Path.cwd())
    assert DataClassBase.data_class_creator.config.model.dynamically_convert_elements_to_models \
           is False


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
            ('config', 'data'),
            DataConfig,
            ('objects', 'data_class_creator'),
            DataClassCreator,
            'config',
        ),
        (
            ('config', 'engine', 'local'),
            LocalRunnerConfig,
            ('objects', 'local'),
            LocalRunner,
            'config',
        ),
        (
            ('config', 'engine', 'prefect'),
            PrefectEngineConfig,
            ('objects', 'prefect'),
            PrefectEngine,
            'config',
        ),
        (
            ('config', 'job'),
            JobConfig,
            ('objects', 'job_creator'),
            JobCreator,
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
            ('objects', 'reactive'),
            ReactiveObjects,
            ('objects', 'data_class_creator'),
            DataClassCreator,
            'reactive_objects',
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
        'config->data => objects->data_class_creator',
        'config.engine->local => objects->local',
        'config.engine->prefect => objects->prefect',
        'config->job => objects->job_creator',
        'config->root_log => objects->root_log',
        'objects->reactive => objects->data_class_creator',
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
    assert isinstance(runtime.config.engine.choice, str)

    assert runtime.config.engine.choice == EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is local_runner

    runtime.config.engine.choice = EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is prefect_engine

    runtime.config.engine.choice = EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is local_runner

    local_runner_2 = LocalRunner()
    prefect_engine_2 = PrefectEngine()
    assert local_runner_2 is not local_runner
    assert prefect_engine_2 is not prefect_engine

    runtime.objects.local = local_runner_2
    runtime.objects.prefect = prefect_engine_2

    assert runtime.config.engine.choice is EngineChoice.LOCAL
    assert runtime.objects.job_creator.engine is runtime.objects.local is local_runner_2

    runtime.config.engine.choice = EngineChoice.PREFECT
    assert runtime.objects.job_creator.engine is runtime.objects.prefect is prefect_engine_2

    runtime.config.engine.choice = EngineChoice.LOCAL
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
    def _get_engine_config() -> IsJobRunnerConfig:
        return getattr(runtime.config.engine, engine_name)

    def _get_engine_object() -> IsJobRunnerConfig:
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
