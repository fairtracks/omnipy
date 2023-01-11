import pytest_cases as pc

from omnipy.config.runtime import Runtime
from omnipy.engine.constants import EngineChoice


@pc.fixture
@pc.parametrize(engine=[EngineChoice.LOCAL, EngineChoice.PREFECT], ids=['local', 'prefect'])
def runtime_all_engines(engine: str) -> None:
    runtime = Runtime()
    runtime.config.engine = engine
