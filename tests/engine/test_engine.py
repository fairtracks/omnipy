from .helpers.mocks import MockEngineConfig, MockTaskRunnerEngine, MockTaskTemplate


def test_engine_init() -> None:
    engine = MockTaskRunnerEngine(config=MockEngineConfig(verbose=True))
    assert engine.verbose is True
    engine = MockTaskRunnerEngine(config=MockEngineConfig(verbose=False))
    assert engine.verbose is False


def test_run_mock_task_run(runtime_mock_task_runner, power_task_template) -> None:
    MockTaskTemplate.set_runtime(runtime_mock_task_runner)

    power = power_task_template.apply()

    assert power(4, 2) == 16
    assert power.name == 'power'
    assert power.runtime.engine.backend_task.verbose is False
    assert power.runtime.engine.backend_task.finished
