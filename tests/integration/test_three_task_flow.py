import pytest

from unifair.compute.flow import DagFlow, FlowTemplate, FuncFlow
from unifair.config.runtime import RuntimeConfig


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
