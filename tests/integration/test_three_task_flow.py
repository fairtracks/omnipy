from typing import Any, Dict

import pytest

from unifair.compute.flow import DagFlow, FlowTemplate, FuncFlow
from unifair.config.runtime import RuntimeConfig
from unifair.engine.local import LocalRunner


@pytest.fixture
def runtime():
    return RuntimeConfig()


@pytest.fixture
def runtime_local_runner(runtime):
    runtime.engine = LocalRunner()
    return runtime


@pytest.fixture
def uppercase(runtime):
    @runtime.task_template()
    def uppercase(text: str) -> str:
        return text.upper()

    return uppercase


@pytest.fixture
def square_root(runtime):
    @runtime.task_template()
    def square_root(number: int) -> Dict[str, float]:
        return {'neg_root': -number**1 / 2, 'pos_root': number**1 / 2}

    return square_root


@pytest.fixture
def merge_key_value_into_str(runtime):
    @runtime.task_template()
    def merge_key_value_into_str(key: Any, val: Any) -> str:
        return '{}: {}'.format(key, val)

    return merge_key_value_into_str


@pytest.fixture
def pos_square_root_dag_flow(runtime, uppercase, square_root, merge_key_value_into_str):
    @runtime.dag_flow_template(
        uppercase.refine(result_key='upper'),
        square_root,
        merge_key_value_into_str.refine(
            param_key_map={
                'key': 'upper', 'val': 'pos_root'
            }, result_key='pos_square_root'))
    def pos_square_root(number: int, text: str) -> str:
        ...

    return pos_square_root


@pytest.fixture
def pos_square_root_func_flow(runtime, uppercase, square_root, merge_key_value_into_str):
    @runtime.func_flow_template(result_key='pos_square_root')
    def pos_square_root(number: int, text: str, result_key: str) -> Dict[str, int]:
        upper = uppercase(text)
        _neg_root, pos_root = square_root(number)
        return {result_key: merge_key_value_into_str(upper, pos_root)}

    return pos_square_root


def _common_test_run_three_task_flow(runtime: RuntimeConfig, pos_square_root: FlowTemplate):
    f_pos_square_root = pos_square_root.refine(
        name='f_pos_square_root', text='result').apply(verbose=True)

    assert runtime.engine.verbose is True  # noqa

    assert f_pos_square_root(4) == {'pos_square_root': 'RESULT: 2.0'}
    assert f_pos_square_root(number=9) == {'pos_square_root': 'RESULT: 3.0'}

    assert f_pos_square_root.name == 'f_pos_square_root'
    assert f_pos_square_root._mock_backend_flow.kwargs == {  # noqa
        'backend_flow_param_1': True, 'backend_flow_param_2': 5
    }

    with pytest.raises(TypeError):
        f_pos_square_root()

    with pytest.raises(TypeError):
        f_pos_square_root(4, 'answer')

    pos_square_root_new = f_pos_square_root.revise()
    if isinstance(f_pos_square_root, DagFlow):
        tasks = pos_square_root_new.tasks
        f_pos_square_root = f_pos_square_root.revise().refine(
            {
                2: tasks[2].refine(result_key='Positive square root')
            },
            fixed_params={
                'text': 'answer'
            },
        ).apply()
    elif isinstance(f_pos_square_root, FuncFlow):
        f_pos_square_root = f_pos_square_root.revise().refine(
            fixed_params={
                'text': 'answer', 'result_key': 'Positive square root'
            },).apply()
    else:
        raise RuntimeError('Should not occur')

    assert runtime.engine.verbose is False  # noqa

    assert f_pos_square_root(4) == {'Positive square root': 'ANSWER: 2.0'}


def test_run_three_task_dag_flow(runtime_local_runner, pos_square_root_dag_flow):
    _common_test_run_three_task_flow(runtime_local_runner, pos_square_root_dag_flow)


def test_run_three_task_func_flow(runtime_local_runner, pos_square_root_func_flow):
    _common_test_run_three_task_flow(runtime_local_runner, pos_square_root_func_flow)
