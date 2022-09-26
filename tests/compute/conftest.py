import pytest

from unifair.compute.job import JobConfig, JobCreator

from .helpers.mocks import MockLocalRunner


@pytest.fixture(scope='function')
def mock_local_runner() -> MockLocalRunner:
    mock_local_runner = MockLocalRunner()
    JobConfig.job_creator.set_engine(mock_local_runner)
    return mock_local_runner
