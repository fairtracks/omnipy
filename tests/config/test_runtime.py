import pytest

from engine.helpers.mocks import MockEngine, MockRunStateRegistry
from unifair.config.runtime import RuntimeConfig


def test_fail_init_no_engine():
    with pytest.raises(TypeError):
        runtime = RuntimeConfig()  # noqa


def test_init_engine_default():
    runtime = RuntimeConfig(engine=MockEngine())
    assert (isinstance(runtime.engine, MockEngine))
    assert runtime.engine.runtime == runtime
    assert runtime.registry is None
    assert runtime.verbose is False


def test_init_engine_registry():
    runtime = RuntimeConfig(engine=MockEngine(), registry=MockRunStateRegistry())
    assert (isinstance(runtime.registry, MockRunStateRegistry))
    assert runtime.registry.runtime == runtime


def test_init_engine_verbose():
    runtime = RuntimeConfig(engine=MockEngine(), verbose=True)
    assert runtime.verbose is True
