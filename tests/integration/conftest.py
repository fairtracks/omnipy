from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.shared.enums import EngineChoice
from omnipy.shared.protocols.hub.runtime import IsRuntime


@pytest.fixture(scope='function')
def runtime(runtime_data_config_variants: Annotated[IsRuntime, pytest.fixture]) -> IsRuntime:
    return runtime_data_config_variants


@pc.fixture(scope='function')
@pc.parametrize(engine=[EngineChoice.LOCAL, EngineChoice.PREFECT], ids=['local', 'prefect'])
def runtime_all_engines(runtime: Annotated[IsRuntime, pytest.fixture], engine: str) -> None:
    runtime.config.engine.choice = engine  # type: ignore[assignment]
