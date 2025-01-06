from dataclasses import dataclass
from functools import update_wrapper
from typing import Any, Callable, Generic, ParamSpec, TypeVar

import pytest_cases as pc

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)

from .tasks import TaskCase

CallP = ParamSpec('CallP')
RetT = TypeVar('RetT')


@dataclass
class FlowCase(Generic[CallP, RetT]):
    flow_func: Callable[CallP, RetT]
    flow_template: IsLinearFlowTemplate | IsDagFlowTemplate | IsFuncFlowTemplate
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    assert_results_func: Callable[..., None]
    # assert_signature_and_return_type_func: Callable[..., None]


# TODO: Add assert_signature_and_return_type_func


@pc.case(
    id='sync-linearflow-single-task',
    tags=['sync', 'linearflow', 'singlethread', 'success'],
)
@pc.parametrize_with_cases('task_case', cases='.tasks')
def case_sync_linearflow_single_task(task_case: TaskCase) -> FlowCase[[], None]:
    task_template = TaskTemplate()(task_case.task_func)
    linear_flow = LinearFlowTemplate(task_template)(task_case.task_func)

    return FlowCase(
        flow_func=task_case.task_func,
        flow_template=linear_flow,
        args=task_case.args,
        kwargs=task_case.kwargs,
        assert_results_func=task_case.assert_results_func,
        # assert_signature_and_return_type_func=task_case.assert_signature_and_return_type_func,
    )


@pc.case(
    id='sync-dagflow-single-task',
    tags=['sync', 'dagflow', 'singlethread', 'success'],
)
@pc.parametrize_with_cases('task_case', cases='.tasks')
def case_sync_dagflow_single_task(task_case: TaskCase) -> FlowCase[[], None]:
    task_template = TaskTemplate()(task_case.task_func)
    dag_flow = DagFlowTemplate(task_template)(task_case.task_func)

    return FlowCase(
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
    task_template = TaskTemplate()(task_case.task_func)

    def single_task_func_decorator(task: IsTaskTemplate) -> Callable:
        def single_task_func(*args, **kwargs):
            return task(*args, **kwargs)

        update_wrapper(single_task_func, task, updated=[])
        return single_task_func

    single_task_func = single_task_func_decorator(task_template)

    func_flow = FuncFlowTemplate()(single_task_func)

    return FlowCase(
        flow_func=single_task_func,
        flow_template=func_flow,
        args=task_case.args,
        kwargs=task_case.kwargs,
        assert_results_func=task_case.assert_results_func,
        # assert_signature_and_return_type_func=task_case.assert_signature_and_return_type_func,
    )
