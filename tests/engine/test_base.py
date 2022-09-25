from .helpers.mocks import MockEngineConfig, MockEngineSubclass


def test_engine_init() -> None:
    engine = MockEngineSubclass()
    assert engine.backend_verbose is True

    engine = MockEngineSubclass()
    engine.set_config(MockEngineConfig(backend_verbose=True))
    assert engine.backend_verbose is True

    engine = MockEngineSubclass()
    engine.set_config(MockEngineConfig(backend_verbose=False))
    assert engine.backend_verbose is False
