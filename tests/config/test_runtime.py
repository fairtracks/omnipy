import logging
import sys

import pytest

from engine.helpers.mocks import MockEngine, MockRunStateRegistry
from unifair.config.runtime import RuntimeConfig


def test_fail_init_no_engine():
    with pytest.raises(TypeError):
        runtime = RuntimeConfig()  # noqa


def test_init_default():
    runtime = RuntimeConfig()
    assert runtime.engine is None

    runtime.engine = MockEngine()
    assert (isinstance(runtime.engine, MockEngine))
    assert runtime.engine.runtime == runtime

    assert isinstance(runtime.logger, logging.Logger)
    assert runtime.logger.name == 'uniFAIR'
    assert runtime.logger.level == logging.INFO
    assert len(runtime.logger.handlers) == 1
    assert isinstance(runtime.logger.handlers[0], logging.StreamHandler)
    assert runtime.logger.handlers[0].stream is sys.stdout

    assert runtime.registry is None
    assert runtime.verbose is True


def test_init_registry():
    runtime = RuntimeConfig(engine=MockEngine(), registry=MockRunStateRegistry())
    assert (isinstance(runtime.registry, MockRunStateRegistry))
    assert runtime.registry.runtime == runtime

    runtime.registry = None
    assert runtime.registry is None

    runtime.registry = MockRunStateRegistry()
    assert (isinstance(runtime.registry, MockRunStateRegistry))
    assert runtime.registry.runtime == runtime
    # TODO: inconsistent with engine._runtime.registry.
    #       Decide on one solution for all
    assert runtime.registry.logger == runtime.logger


def test_init_logger():
    runtime = RuntimeConfig(engine=MockEngine(), logger=logging.getLogger())
    assert (isinstance(runtime.logger, logging.Logger))
    assert runtime.logger == logging.getLogger()

    runtime.logger = None
    assert runtime.logger is None

    runtime.logger = logging.getLogger()
    assert runtime.logger == logging.getLogger()


def test_init_engine_verbose():
    runtime = RuntimeConfig(engine=MockEngine(), verbose=True)
    assert runtime.verbose is True
