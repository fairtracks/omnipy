"""Tests for base engine behavior."""

from .helpers.mocks import MockEngineConfig, MockJobRunnerSubclass


def test_engine_init() -> None:
    """Test engine initialization from config values."""
    engine = MockJobRunnerSubclass()
    assert engine.backend_verbose is True

    engine = MockJobRunnerSubclass()
    engine.set_config(MockEngineConfig(backend_verbose=True))
    assert engine.backend_verbose is True

    engine = MockJobRunnerSubclass()
    engine.set_config(MockEngineConfig(backend_verbose=False))
    assert engine.backend_verbose is False
