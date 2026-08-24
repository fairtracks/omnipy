"""Shared fixtures for integration tests."""

import os
from pathlib import Path
from typing import Annotated
from unittest.mock import patch

from prefect.settings import PREFECT_FLOWS_HEARTBEAT_FREQUENCY, temporary_settings
import pytest
import pytest_cases as pc

from omnipy.components.prefect.lazy_import import prefect_test_harness
from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.protocols.hub.runtime import IsRuntime

_PREFECT_SQLITE_TMPDIR = '/tmp/omnipy-prefect-sqlite-tmp'
_PREFECT_TEST_PORT = '40000'


@pc.fixture(scope='function')
@pc.parametrize(engine=[EngineChoice.LOCAL, EngineChoice.PREFECT], ids=['local', 'prefect'])
def runtime_all_engines(runtime: Annotated[IsRuntime, pytest.fixture], engine: str) -> None:
    """Provide the runtime all engines fixture."""
    runtime.config.engine.choice = engine  # type: ignore[assignment]


@pytest.fixture(autouse=True, scope='package')
def prefect_test_fixture():
    Path(_PREFECT_SQLITE_TMPDIR).mkdir(parents=True, exist_ok=True)

    with temporary_settings({PREFECT_FLOWS_HEARTBEAT_FREQUENCY: None}):
        prefect_test_envs = {
            'TMPDIR': _PREFECT_SQLITE_TMPDIR,
            'SQLITE_TMPDIR': _PREFECT_SQLITE_TMPDIR,
            'PREFECT_TEST_PORT': _PREFECT_TEST_PORT,
        }
        with patch.dict(os.environ, prefect_test_envs):
            with prefect_test_harness():
                yield
