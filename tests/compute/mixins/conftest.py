from typing import Annotated

import pytest

from ..helpers.mocks import MockLocalRunner


@pytest.fixture(scope='function', autouse=True)
def autouse_mock_local_runner(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> MockLocalRunner:
    """Automatically install mock_local_runner for all compute mixin tests."""
    ...
