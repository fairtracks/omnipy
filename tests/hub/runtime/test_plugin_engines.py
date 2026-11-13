"""Tests for plugin engines registered through the ``omnipy.engines`` entry point group."""

from collections.abc import Iterator
from importlib.metadata import EntryPoint
import sys
from typing import Annotated, Any

import pytest

from omnipy.engine.local import LocalRunner
import omnipy.engine.registry as registry_module
from omnipy.engine.registry import ENGINE_ENTRY_POINT_GROUP, engine_registry
from omnipy.hub._registry import RunStateRegistry
from omnipy.shared.protocols.hub.runtime import IsRuntime
import omnipy.util.pydantic as pyd

from .helpers.plugin_engine import (
    MockPluginEngine,
    MockPluginEngineConfig,
    OtherMockPluginEngine,
    OtherMockPluginEngineConfig,
    PLUGIN_ENGINE_IMPORT_PATH,
    PLUGIN_ENGINE_MODULE,
)

PLUGIN = 'mock_plugin'


@pytest.fixture
def plugin_entry_point(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Make the mock plugin engine discoverable through a fake entry point."""

    def _entry_points(*, group: str) -> list[EntryPoint]:
        assert group == ENGINE_ENTRY_POINT_GROUP
        return [EntryPoint(PLUGIN, PLUGIN_ENGINE_IMPORT_PATH, ENGINE_ENTRY_POINT_GROUP)]

    monkeypatch.setattr(registry_module, 'entry_points', _entry_points)
    engine_registry.refresh()
    yield
    engine_registry.refresh()


def _engine_attr(obj: object, name: str = PLUGIN) -> Any:
    return getattr(obj, name)


def test_choosing_plugin_engine_loads_it(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(sys.modules, PLUGIN_ENGINE_MODULE)

    assert PLUGIN not in runtime.objects.__dict__
    assert PLUGIN not in runtime.config.engine.__dict__

    runtime.config.engine.choice = PLUGIN
    assert PLUGIN_ENGINE_MODULE in sys.modules

    engine = _engine_attr(runtime.objects)
    engine_config = _engine_attr(runtime.config.engine)

    assert type(engine).__name__ == 'MockPluginEngine'
    assert type(engine_config).__name__ == 'MockPluginEngineConfig'
    assert runtime.objects.job_creator.engine is engine
    assert engine.config is engine_config
    assert engine.registry is runtime.objects.registry

    runtime.config.engine.choice = 'local'
    assert isinstance(runtime.objects.job_creator.engine, LocalRunner)


def test_reading_plugin_engine_attribute_loads_it(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    assert _engine_attr(runtime.config.engine).server_url == ''

    assert isinstance(_engine_attr(runtime.objects), MockPluginEngine)
    assert runtime.config.engine.choice == 'local'
    assert isinstance(runtime.objects.job_creator.engine, LocalRunner)


def test_load_engine_returns_the_same_engine(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    engine = runtime.load_engine(PLUGIN)

    assert runtime.load_engine(PLUGIN) is engine
    assert _engine_attr(runtime.objects) is engine
    assert runtime.load_engine('local') is runtime.objects.local


def test_plugin_engine_config_changes_reach_engine(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    engine = runtime.load_engine(PLUGIN)
    assert isinstance(engine, MockPluginEngine)

    num_received = len(engine.received_configs)
    _engine_attr(runtime.config.engine).server_url = 'http://localhost:9000'
    assert len(engine.received_configs) == num_received + 1
    assert engine.config.server_url == 'http://localhost:9000'

    new_config = MockPluginEngineConfig(server_url='http://localhost:8000')
    setattr(runtime.config.engine, PLUGIN, new_config)
    assert engine.config is new_config


def test_reset_subscriptions_does_not_duplicate_plugin_subscriptions(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    engine = runtime.load_engine(PLUGIN)
    assert isinstance(engine, MockPluginEngine)

    runtime.reset_subscriptions()
    runtime.reset_subscriptions()

    num_received = len(engine.received_configs)
    _engine_attr(runtime.config.engine).server_url = 'http://localhost:8000'
    assert len(engine.received_configs) == num_received + 1


def test_replacing_plugin_engine_object_updates_config_class(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    runtime.config.engine.choice = PLUGIN
    old_config = _engine_attr(runtime.config.engine)

    other_engine = OtherMockPluginEngine()
    setattr(runtime.objects, PLUGIN, other_engine)

    assert isinstance(_engine_attr(runtime.config.engine), OtherMockPluginEngineConfig)
    assert other_engine.config is _engine_attr(runtime.config.engine)
    assert runtime.objects.job_creator.engine is other_engine

    setattr(runtime.objects, PLUGIN, MockPluginEngine())

    assert isinstance(_engine_attr(runtime.config.engine), MockPluginEngineConfig)
    assert _engine_attr(runtime.config.engine) is not old_config


def test_replacing_run_state_registry_reaches_plugin_engine(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    engine = runtime.load_engine(PLUGIN)
    assert isinstance(engine, MockPluginEngine)

    new_registry = RunStateRegistry()
    runtime.objects.registry = new_registry

    assert engine.registry is new_registry


def test_reset_to_defaults_keeps_plugin_engine_with_default_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    runtime.config.engine.choice = PLUGIN
    engine = _engine_attr(runtime.objects)
    _engine_attr(runtime.config.engine).server_url = 'http://localhost:8000'

    runtime.config.reset_to_defaults()

    assert runtime.config.engine.choice == 'local'
    assert _engine_attr(runtime.objects) is engine
    assert _engine_attr(runtime.config.engine).server_url == ''
    assert engine.config is _engine_attr(runtime.config.engine)


def test_unregistered_names_are_rejected(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    with pytest.raises(pyd.ValidationError, match='Registered engines: "local", "prefect", "mock_'):
        runtime.config.engine.choice = 'tez'

    with pytest.raises(pyd.ValidationError, match='neither an attribute of EngineConfig'):
        setattr(runtime.config.engine, 'tez', MockPluginEngineConfig())

    with pytest.raises(pyd.ValidationError, match='neither an attribute of RuntimeObjects'):
        setattr(runtime.objects, 'tez', MockPluginEngine())

    with pytest.raises(AttributeError, match="no attribute 'tez'"):
        getattr(runtime.objects, 'tez')

    assert runtime.config.engine.choice == 'local'


def test_engine_name_clashing_with_runtime_attribute_is_rejected(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    engine_registry.register('registry', MockPluginEngine)

    with pytest.raises(ValueError, match='clashes with an attribute'):
        runtime.load_engine('registry')

    assert isinstance(runtime.objects.registry, RunStateRegistry)


def test_plugin_engine_config_shows_in_config_dict(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
) -> None:
    assert PLUGIN not in runtime.config.engine.dict()

    runtime.load_engine(PLUGIN)

    assert runtime.config.engine.dict()[PLUGIN] == {'server_url': ''}


def test_engine_declared_job_mixins_are_added_while_engine_is_selected(
    runtime: Annotated[IsRuntime, pytest.fixture],
    plugin_entry_point: Annotated[None, pytest.fixture],
    restore_job_base_mixins: Annotated[None, pytest.fixture],
) -> None:
    from omnipy import TaskTemplate

    def _task(a: int) -> int:
        return a

    assert not hasattr(TaskTemplate()(_task), 'plugin_option')

    runtime.config.engine.choice = PLUGIN
    assert TaskTemplate()(_task).plugin_option is None  # type: ignore[attr-defined]

    runtime.config.engine.choice = 'local'
    assert not hasattr(TaskTemplate()(_task), 'plugin_option')
    assert TaskTemplate(plugin_option='x')(_task).plugin_option == 'x'  # type: ignore[attr-defined]
    assert TaskTemplate(plugin_option='x')(_task).run(4) == 4
