from engine.helpers.mocks import MockEngineConfig, MockTaskRunnerEngine


def test_engine_init() -> None:
    engine = MockTaskRunnerEngine()
    assert engine.backend_verbose is True

    engine = MockTaskRunnerEngine()
    engine.set_config(MockEngineConfig(backend_verbose=True))
    assert engine.backend_verbose is True

    engine = MockTaskRunnerEngine()
    engine.set_config(MockEngineConfig(backend_verbose=False))
    assert engine.backend_verbose is False
