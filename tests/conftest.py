from datetime import datetime
import logging
import os
import shutil
import tempfile
from typing import Annotated, Generator, Type

import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.compute.job_creator import JobBaseMeta, JobCreator
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.runtime import RuntimeConfig


@pytest.fixture(scope='function')
def teardown_rm_root_log_dir() -> Generator[None, None, None]:
    root_log_config = RootLogConfig()
    log_dir_path = root_log_config.file_log_dir_path
    yield
    if os.path.exists(log_dir_path):
        shutil.rmtree(log_dir_path)


@pytest.fixture(scope='function')
def teardown_remove_root_log_handlers() -> Generator[None, None, None]:
    root_logger = logging.root
    num_root_log_handlers = len(root_logger.handlers)
    yield
    assert len(root_logger.handlers[num_root_log_handlers:]) <= 3
    for handler in root_logger.handlers[num_root_log_handlers:]:
        root_logger.removeHandler(handler)


@pytest.fixture(scope='function')
def tmp_dir_path() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as _tmp_dir_path:
        yield _tmp_dir_path


@pytest.fixture(scope='function')
def runtime_cls(
    teardown_rm_root_log_dir: Annotated[None, pytest.fixture],
    teardown_remove_root_log_handlers: Annotated[None, pytest.fixture],
) -> Type[IsRuntime]:
    from omnipy.hub.runtime import Runtime
    return Runtime


@pytest.fixture(scope='function')
def runtime(
    runtime_cls: Annotated[Type[IsRuntime], pytest.fixture],
    tmp_dir_path: Annotated[str, pytest.fixture],
) -> Generator[IsRuntime, None, None]:
    runtime = runtime_cls()

    runtime.config.job.output_storage.local.persist_data_dir_path = os.path.join(
        tmp_dir_path, 'outputs')
    runtime.config.root_log.file_log_dir_path = os.path.join(tmp_dir_path, 'logs')

    yield runtime

    JobBaseMeta._job_creator_obj = JobCreator()


@pytest.fixture(scope='function')
def mock_datetime() -> datetime:
    class MockDatetime(datetime):
        def __init__(self, *args: object, **kwargs: object):
            self._now = datetime.now()

        def now(self, tz=None):
            return self._now

    return MockDatetime(2000, 1, 1)
