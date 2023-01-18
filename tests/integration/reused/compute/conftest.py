import pytest

from omnipy.compute.task import TaskTemplate

from ....compute.conftest import all_flow_classes  # noqa


@pytest.fixture
def mock_local_runner(runtime_all_engines):
    return TaskTemplate.engine
