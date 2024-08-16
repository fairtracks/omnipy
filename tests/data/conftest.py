from typing import Annotated, Iterator

import pytest

from omnipy.api.protocols.public.hub import IsRuntime


@pytest.fixture(scope='function', autouse=True)
def autouse_runtime_data_config_variants(
        runtime_data_config_variants: Annotated[IsRuntime, pytest.fixture]) -> IsRuntime:
    return runtime_data_config_variants
