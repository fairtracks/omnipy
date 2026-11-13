"""Tests for the engine registry and plugin engine discovery through entry points."""

from collections.abc import Iterator
from importlib.metadata import EntryPoint
import sys
from typing import Annotated

import pytest

from omnipy.components.prefect.engine.prefect import PrefectEngine
from omnipy.engine.local import LocalRunner
import omnipy.engine.registry as registry_module
from omnipy.engine.registry import ENGINE_ENTRY_POINT_GROUP, EngineRegistry

from ..hub.runtime.helpers.plugin_engine import (
    MockPluginEngine,
    OTHER_PLUGIN_ENGINE_IMPORT_PATH,
    OtherMockPluginEngine,
    PLUGIN_ENGINE_IMPORT_PATH,
)


def _entry_point(name: str, value: str) -> EntryPoint:
    return EntryPoint(name, value, ENGINE_ENTRY_POINT_GROUP)


@pytest.fixture
def fake_entry_points(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[EntryPoint]]:
    """Replace the installed engine entry points with a list that tests can fill."""
    fake: list[EntryPoint] = []

    def _entry_points(*, group: str) -> list[EntryPoint]:
        assert group == ENGINE_ENTRY_POINT_GROUP
        return fake

    monkeypatch.setattr(registry_module, 'entry_points', _entry_points)
    yield fake


def test_builtin_engines(fake_entry_points: Annotated[list[EntryPoint], pytest.fixture]) -> None:
    registry = EngineRegistry()

    assert registry.names() == ('local', 'prefect')
    assert registry.get_engine_cls('local') is LocalRunner
    assert registry.get_engine_cls('prefect') is PrefectEngine
    assert registry.is_loaded('local')


def test_unknown_engine_error_lists_registered_engines(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
) -> None:
    registry = EngineRegistry()

    with pytest.raises(ValueError, match='Unknown engine "tez". Registered engines: "local", '):
        registry.check_name('tez')

    assert not registry.is_registered('tez')


def test_entry_point_engine_is_loaded_lazily(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_name = PLUGIN_ENGINE_IMPORT_PATH.split(':')[0]
    monkeypatch.delitem(sys.modules, module_name)
    fake_entry_points.append(_entry_point('mock_plugin', PLUGIN_ENGINE_IMPORT_PATH))

    registry = EngineRegistry()

    assert registry.names() == ('local', 'prefect', 'mock_plugin')
    assert not registry.is_loaded('mock_plugin')
    assert module_name not in sys.modules

    engine_cls = registry.get_engine_cls('mock_plugin')

    assert engine_cls.__name__ == 'MockPluginEngine'
    assert registry.is_loaded('mock_plugin')
    assert module_name in sys.modules


def test_entry_points_are_read_once(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
) -> None:
    registry = EngineRegistry()
    assert registry.names() == ('local', 'prefect')

    fake_entry_points.append(_entry_point('mock_plugin', PLUGIN_ENGINE_IMPORT_PATH))
    assert registry.names() == ('local', 'prefect')

    registry.refresh()
    assert registry.names() == ('local', 'prefect', 'mock_plugin')


def test_invalid_and_clashing_entry_points_are_ignored(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
    caplog: pytest.LogCaptureFixture,
) -> None:
    fake_entry_points.extend(
        [
            _entry_point('_hidden', PLUGIN_ENGINE_IMPORT_PATH),
            _entry_point('not-an-identifier', PLUGIN_ENGINE_IMPORT_PATH),
            _entry_point('local', PLUGIN_ENGINE_IMPORT_PATH),
            _entry_point('mock_plugin', PLUGIN_ENGINE_IMPORT_PATH),
            _entry_point('mock_plugin', OTHER_PLUGIN_ENGINE_IMPORT_PATH),
        ]
    )

    registry = EngineRegistry()

    assert registry.names() == ('local', 'prefect', 'mock_plugin')
    assert registry.get_engine_cls('local') is LocalRunner
    assert registry.get_engine_cls('mock_plugin') is MockPluginEngine
    assert caplog.text.count('Ignoring engine entry point') == 4


def test_register_explicitly(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
) -> None:
    registry = EngineRegistry()

    registry.register('mock_plugin', MockPluginEngine)
    registry.register('mock_plugin', MockPluginEngine)

    assert registry.names() == ('local', 'prefect', 'mock_plugin')
    assert registry.get_engine_cls('mock_plugin') is MockPluginEngine

    with pytest.raises(ValueError, match='already registered'):
        registry.register('mock_plugin', OtherMockPluginEngine)

    with pytest.raises(ValueError, match='already registered'):
        registry.register('local', MockPluginEngine)

    with pytest.raises(ValueError, match='Invalid engine name'):
        registry.register('_mock', MockPluginEngine)


def test_register_matching_entry_point_does_nothing(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
) -> None:
    fake_entry_points.append(_entry_point('mock_plugin', PLUGIN_ENGINE_IMPORT_PATH))
    registry = EngineRegistry()

    registry.register('mock_plugin', MockPluginEngine)

    assert registry.is_loaded('mock_plugin')
    assert registry.get_engine_cls('mock_plugin') is MockPluginEngine

    with pytest.raises(ValueError, match='already registered'):
        registry.register('mock_plugin', OtherMockPluginEngine)


def test_refresh_forgets_explicitly_registered_engines(
    fake_entry_points: Annotated[list[EntryPoint], pytest.fixture],
) -> None:
    registry = EngineRegistry()
    registry.register('mock_plugin', MockPluginEngine)

    registry.refresh()

    assert registry.names() == ('local', 'prefect')
