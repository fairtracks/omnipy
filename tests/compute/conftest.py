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
