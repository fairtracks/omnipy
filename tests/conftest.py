from datetime import datetime
import os
import tempfile
from typing import Annotated, Generator, Type

import pytest

from omnipy.api.protocols import IsRuntime


@pytest.fixture(scope='function')
def runtime_cls() -> Type[IsRuntime]:
    from omnipy.hub.runtime import Runtime
    return Runtime


@pytest.fixture(scope='function')
def tmp_dir_path() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as _tmp_dir_path:
        yield _tmp_dir_path


@pytest.fixture(scope='function')
def runtime(
    runtime_cls: Annotated[Type[IsRuntime], pytest.fixture],
    tmp_dir_path: Annotated[str, pytest.fixture],
) -> Generator[IsRuntime, None, None]:
    runtime = runtime_cls()

    runtime.config.job.persist_data_dir_path = os.path.join(tmp_dir_path, 'data')
    runtime.config.registry.log_dir_path = os.path.join(tmp_dir_path, 'logs')

    yield runtime


@pytest.fixture(scope='function')
def mock_datetime() -> datetime:
    class MockDatetime(datetime):
        def __init__(self, *args: object, **kwargs: object):
            self._now = datetime.now()

        def now(self, tz=None):
            return self._now

    return MockDatetime(2000, 1, 1)
