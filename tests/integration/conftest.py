"""Shared fixtures for integration tests."""

from typing import Annotated

from prefect.settings import PREFECT_FLOWS_HEARTBEAT_FREQUENCY, temporary_settings
import pytest
import pytest_cases as pc

from omnipy.components.prefect.lazy_import import prefect_test_harness
from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.protocols.hub.runtime import IsRuntime


@pc.fixture(scope='function')
@pc.parametrize(engine=[EngineChoice.LOCAL, EngineChoice.PREFECT], ids=['local', 'prefect'])
def runtime_all_engines(runtime: Annotated[IsRuntime, pytest.fixture], engine: str) -> None:
    """Provide the runtime all engines fixture."""
    runtime.config.engine.choice = engine  # type: ignore[assignment]


@pytest.fixture(autouse=True, scope='package')
def prefect_test_fixture():
    with temporary_settings({PREFECT_FLOWS_HEARTBEAT_FREQUENCY: None}):
        with prefect_test_harness():
            yield
