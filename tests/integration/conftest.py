from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.api.enums import EngineChoice
from omnipy.api.protocols.public.runtime import IsRuntime


@pc.fixture(scope='function')
@pc.parametrize(engine=[EngineChoice.LOCAL, EngineChoice.PREFECT], ids=['local', 'prefect'])
def runtime_all_engines(runtime: Annotated[IsRuntime, pytest.fixture], engine: str) -> None:
    runtime.config.engine = engine
