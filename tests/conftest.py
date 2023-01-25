import tempfile
from datetime import datetime
from typing import Annotated, Type

import pytest

from omnipy.api.protocols import IsRuntime


@pytest.fixture(scope='function')
def runtime_cls() -> Type[IsRuntime]:
    from omnipy.hub.runtime import Runtime
    return Runtime


@pytest.fixture(scope='function')
def runtime(runtime_cls: Annotated[Type[IsRuntime], pytest.fixture]) -> IsRuntime:
    runtime = runtime_cls()

    with tempfile.TemporaryDirectory() as tmp_dir_path:
        runtime.config.job.persist_data_dir_path = tmp_dir_path

        yield runtime


@pytest.fixture(scope='function')
def mock_datetime() -> datetime:
    class MockDatetime(datetime):
        def __init__(self, *args: object, **kwargs: object):
            self._now = datetime.now()

        def now(self, tz=None):
            return self._now

    return MockDatetime(2000, 1, 1)