import pytest

from engine.helpers.mocks import MockEngineConfig, MockEngineSubclass
from unifair.engine.protocols import IsEngine


@pytest.fixture(scope='module')
def mock_engine() -> IsEngine:
    mock_engine = MockEngineSubclass()
    mock_engine.set_config(MockEngineConfig())
    return mock_engine
