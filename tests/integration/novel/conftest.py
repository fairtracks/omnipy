from typing import Annotated

import pytest

from omnipy.shared.protocols.hub.runtime import IsRuntime


@pytest.fixture(scope='function')
def runtime(runtime_data_config_variants: Annotated[IsRuntime, pytest.fixture]) -> IsRuntime:
    return runtime_data_config_variants
