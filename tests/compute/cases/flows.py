from dataclasses import dataclass
from functools import update_wrapper
from typing import Any, Callable, Dict, Generic, Tuple, TypeVar

import pytest_cases as pc

from unifair.compute.flow import DagFlowTemplate, FlowTemplate, FuncFlowTemplate
from unifair.compute.task import TaskTemplate

from .tasks import TaskCase

ArgT = TypeVar('ArgT')
ReturnT = TypeVar('ReturnT')


@dataclass
class FlowCase(Generic[ArgT, ReturnT]):
    name: str
    flow_func: Callable[[ArgT], ReturnT]
    flow_template: FlowTemplate
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    assert_results_func: Callable[[Any], None]
    # assert_signature_and_return_type_func: Callable[[Any], None]


# TODO: Add assert_signature_and_return_type_func


@pc.case(
    id='sync-dagflow-single-task',
    tags=['sync', 'dagflow', 'singlethread', 'success'],
)
@pc.parametrize_with_cases('task_case', cases='.tasks')
def case_sync_dagflow_single_task(task_case: TaskCase) -> FlowCase[[], None]:
    task_template = TaskTemplate(task_case.task_func)
    dag_flow = DagFlowTemplate(task_template)(task_case.task_func)

    return FlowCase(
        name=task_case.name,
        flow_func=task_case.task_func,
        flow_template=dag_flow,
        args=task_case.args,
        kwargs=task_case.kwargs,
        assert_results_func=task_case.assert_results_func,
        # assert_signature_and_return_type_func=task_case.assert_signature_and_return_type_func,
    )


@pc.case(
    id='sync-funcflow-single-task',
    tags=['sync', 'funcflow', 'singlethread', 'success'],
)
@pc.parametrize_with_cases('task_case', cases='.tasks')
def case_sync_funcflow_single_task(task_case: TaskCase) -> FlowCase[[], None]:
    task_template = TaskTemplate(task_case.task_func)

    def single_task_func_decorator(task: TaskTemplate) -> Callable:
        def single_task_func(*args, **kwargs):
            return task(*args, **kwargs)

        update_wrapper(single_task_func, task, updated=[])
        return single_task_func

    single_task_func = single_task_func_decorator(task_template)

    func_flow = FuncFlowTemplate(single_task_func)

    return FlowCase(
        name=task_case.name,
        flow_func=single_task_func,
        flow_template=func_flow,
        args=task_case.args,
        kwargs=task_case.kwargs,
        assert_results_func=task_case.assert_results_func,
        # assert_signature_and_return_type_func=task_case.assert_signature_and_return_type_func,
    )
