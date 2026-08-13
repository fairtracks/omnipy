from typing import Awaitable, Callable

import pytest_cases as pc

from omnipy.shared.protocols.compute.job import IsTask

from ...helpers.classes import FlowCase
from .raw.flows import pos_square_root_dag_flow, pos_square_root_func_flow

RunTaskAndAssertType = Callable[[IsTask], None]
AsyncRunTaskAndAssertType = Callable[[IsTask], Awaitable[None]]


@pc.case(
    id='sync-function-dagflow-three_task_flow',
    tags=['sync', 'dagflow', 'singlethread', 'pos_square_root'],
)
def case_sync_dagflow_pos_square_root() -> FlowCase:
    return FlowCase(
        name='pos_square_root',
        flow_template=pos_square_root_dag_flow,  # noqa
    )


@pc.case(
    id='sync-function-funcflow-three_task_flow',
    tags=['sync', 'funcflow', 'singlethread', 'pos_square_root'],
)
def case_sync_funcflow_pos_square_root() -> FlowCase:
    return FlowCase(
        name='pos_square_root',
        flow_template=pos_square_root_func_flow,  # noqa
    )
