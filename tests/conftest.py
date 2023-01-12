from typing import Annotated, Type

import pytest

from omnipy.engine.protocols import IsRuntime


@pytest.fixture(scope='function')
def runtime_cls() -> Type[IsRuntime]:
    from omnipy.config.runtime import Runtime
    return Runtime


@pytest.fixture(scope='function')
def runtime(runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> IsRuntime:
    return runtime_cls()
