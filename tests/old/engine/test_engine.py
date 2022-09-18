from inspect import Signature
from typing import Any, Callable, Dict, Iterable

import pytest

from unifair.compute.flow import Flow
from unifair.compute.task import TaskTemplate
from unifair.old.engine.engine import DagFlowWrapper, Engine, TaskWrapper


@pytest.fixture
def mock_backend_task_cls():
    class MockBackendTask:
        def __init__(self,
                     task: TaskTemplate,
                     engine_param_passthrough: bool = True,
                     **backend_task_kwargs: Any):
            self.finished = False
            self.task = task
            self.engine_param_passthrough = engine_param_passthrough
            self.backend_task_kwargs = backend_task_kwargs

        def run(self, *args: Any, **kwargs: Any):
            print('Running task "{}": ...'.format(self.task.task_name))
            result = self.task(*args, **kwargs)
            print('Result of task "{}": {}'.format(self.task.task_name, result))
            self.finished = True
            return result

    return MockBackendTask


@pytest.fixture
def mock_task_runner_engine_cls(mock_backend_task_cls):
    class MockTaskRunnerEngine(Engine):
        def __init__(self, engine_param: bool = True, **engine_kwargs):
            self.engine_param = engine_param

            class MockTaskWrapper(TaskWrapper):
                # TODO: Change to 'backend_task_factory' or similar?
                def __init__(self, task: TaskTemplate, **extra_kwargs):
                    super().__init__(task, **extra_kwargs)
                    self.backend_task = mock_backend_task_cls(task, engine_param, **extra_kwargs)

                # TODO: Change to get_execute_task_callback(backend_task) or similar
                def __call__(self, *args: Any, **kwargs):
                    return self.backend_task.run(*args, **kwargs)

            super().__init__(task_wrapper=MockTaskWrapper, **engine_kwargs)

    return MockTaskRunnerEngine


@pytest.fixture
def mock_task_runner_engine(mock_task_runner_engine_cls):
    return mock_task_runner_engine_cls()


def test_engine_init(mock_task_runner_engine_cls):
    my_engine = mock_task_runner_engine_cls()
    assert my_engine.engine_param is True
    assert my_engine.base_params == {}

    my_engine = mock_task_runner_engine_cls(engine_param=False)
    assert my_engine.engine_param is False
    assert my_engine.base_params == {}

    my_engine = mock_task_runner_engine_cls(engine_param=False, extra_param=123)
    assert my_engine.engine_param is False
    assert my_engine.base_params == {'extra_param': 123}


def test_run_task_basic(power_func):

    power = my_engine.task_decorator()(power_func)

    assert power(4, 2) == 16
    assert power.name == 'power'
    assert power.backend_task.engine_param_passthrough is True
    assert power.backend_task.backend_task_kwargs == {}
    assert power.backend_task.finished


def test_run_task_with_engine_and_backend_parameters(mock_task_runner_engine_cls, power_func):
    my_engine = mock_task_runner_engine_cls(engine_param=False)

    power = my_engine.task_decorator(cfg_task={'backend_task_parameter': 4})(power_func)

    assert power(4, 2) == 16
    assert power.backend_task.engine_param_passthrough is False
    assert power.backend_task.backend_task_kwargs['backend_task_parameter'] == 4


def test_run_task_with_unifair_and_backend_config(mock_task_runner_engine_cls, power_func):
    my_engine = mock_task_runner_engine_cls(engine_param=False)

    power = my_engine.task_decorator(cfg_task={
        'result_key': 'power', 'backend_task_parameter': 4
    })(
        power_func)

    assert power(4, 2) == {'power': 16}
    assert power.backend_task.engine_param_passthrough is False
    assert power.backend_task.backend_task_kwargs == {'backend_task_parameter': 4}


@pytest.fixture
def mock_task_wrapper_cls(mock_backend_task_cls):
    class MockTaskWrapper(TaskWrapper):
        def __init__(self, task: TaskTemplate, **extra_kwargs):
            super().__init__(task, **extra_kwargs)
            self.backend_task = mock_backend_task_cls(task, **extra_kwargs)

        def __call__(self, *args: Any, **kwargs):
            return self.backend_task.run(*args, **kwargs)

    return MockTaskWrapper


@pytest.fixture
def mock_backend_dag_flow_cls():
    class MockBackendDagFlow:
        def __init__(self,
                     name: str,
                     tasks: Iterable[TaskTemplate],
                     flow_signature: Signature,
                     flow_kwargs: Dict[str, Any],
                     engine_param_passthrough: int,
                     **backend_flow_kwargs: Any):
            self.finished = False
            self.name = name
            self.tasks = tasks
            self.flow_signature = flow_signature
            self.flow_kwargs = flow_kwargs
            self.engine_param_passthrough = engine_param_passthrough
            self.backend_flow_kwargs = backend_flow_kwargs

        def run(self, **runtime_kwargs: Any):
            print('Running flow "{}"...'.format(self.name))
            results = None
            runtime_kwargs.update(self.flow_kwargs)
            for task in self.tasks:
                results = task(**runtime_kwargs)
                runtime_kwargs.update(results)
            print('Result of flow "{}": {}'.format(self.name, results))
            self.finished = True
            return results

    return MockBackendDagFlow


@pytest.fixture
def mock_dag_flow_engine_cls(mock_task_wrapper_cls, mock_backend_dag_flow_cls):
    class MockDagFlowEngine(Engine):
        def __init__(self, engine_param: int = 0, **engine_kwargs: Any):
            self.engine_param = engine_param

            class MockDagFlowWrapper(DagFlowWrapper):
                def __init__(self,
                             name: str,
                             tasks: Iterable[TaskTemplate],
                             flow_signature: Signature,
                             flow_kwargs: Dict[str, Any],
                             **backend_flow_kwargs: Any):
                    self._mock_backend_flow = mock_backend_dag_flow_cls(
                        name,
                        tasks,
                        flow_signature,
                        flow_kwargs,
                        engine_param,
                        **backend_flow_kwargs)

                def __call__(self, **runtime_kwargs: Any):
                    return self._mock_backend_flow.run(**runtime_kwargs)

            super().__init__(
                task_wrapper=mock_task_wrapper_cls,
                dag_flow_wrapper=MockDagFlowWrapper,
                **engine_kwargs)

    return MockDagFlowEngine
