from omnipy.compute.task import TaskTemplate
import pytest


@pytest.fixture
def mock_local_runner(runtime_all_engines):
    return TaskTemplate.engine