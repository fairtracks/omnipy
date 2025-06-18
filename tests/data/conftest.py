from typing import Annotated, Iterator

import pytest
import pytest_cases as pc

from omnipy.shared.protocols.hub.runtime import IsRuntime


@pytest.fixture(scope='function', autouse=True)
def autouse_runtime_data_config_variants(
        runtime_data_config_variants: Annotated[IsRuntime, pytest.fixture]) -> IsRuntime:
    return runtime_data_config_variants


@pc.fixture(scope='function')
def register_runtime(runtime: Annotated[IsRuntime, pytest.fixture]) -> Iterator[None]:
    """
    Fixture to register the test runtime in the dynamic_styles module, used
    for determining the cache directory path for base16 themes.
    """
    import omnipy.data._display.styles.dynamic_styles
    omnipy.data._display.styles.dynamic_styles._runtime = runtime
    yield
    omnipy.data._display.styles.dynamic_styles._runtime = None
