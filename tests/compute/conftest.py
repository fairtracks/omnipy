from datetime import datetime
from typing import Annotated

import pytest

from omnipy.compute.job import JobBase, JobCreator

from .helpers.mocks import MockLocalRunner


@pytest.fixture(scope='function')
def teardown_reset_job_creator() -> None:
    yield None
    JobBase._job_creator = JobCreator()


@pytest.fixture(scope='function')
def mock_local_runner(
        teardown_reset_job_creator: Annotated[None, pytest.fixture]) -> MockLocalRunner:
    mock_local_runner = MockLocalRunner()
    JobBase.job_creator.set_engine(mock_local_runner)
    return mock_local_runner


@pytest.fixture(scope='function')
def mock_job_datetime():
    class MockDatetime:
        def __init__(self):
            self._now = datetime.now()

        def now(self):
            return self._now

    mock_datetime = MockDatetime()

    import omnipy.compute.job
    prev_datetime = omnipy.compute.job.datetime
    omnipy.compute.job.datetime = mock_datetime

    yield mock_datetime

    omnipy.compute.job.datetime = prev_datetime
