import pytest

from omnipy.compute.task import TaskTemplate


@pytest.fixture
def mock_local_runner(runtime_all_engines):
    return TaskTemplate.engine