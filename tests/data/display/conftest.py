from typing import Annotated

import pytest

from omnipy.shared.protocols.hub.runtime import IsRuntime


# Override autouse_runtime_data_config_variants fixture in tests.data.conftest
@pytest.fixture(scope='function', autouse=True)
def autouse_runtime_data_config_variants(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> IsRuntime:
    return runtime
