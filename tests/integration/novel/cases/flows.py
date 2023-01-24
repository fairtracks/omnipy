from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, TypeVar

import pytest_cases as pc

from omnipy.abstract.protocols import IsTask, IsFlowTemplate

from .raw.flows import (pos_square_root_dag_flow,
                        pos_square_root_func_flow,
                        specialize_record_models_dag_flow,
                        specialize_record_models_func_flow)

RunTaskAndAssertType = Callable[[IsTask], None]
AsyncRunTaskAndAssertType = Callable[[IsTask], Awaitable[None]]

ArgT = TypeVar('ArgT')
ReturnT = TypeVar('ReturnT')


@dataclass
class FlowCase(Generic[ArgT, ReturnT]):
    name: str
    flow_template: IsFlowTemplate


#
# test_three_task_flow
#


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


#
# test_multi_model_dataset
#


@pc.case(
    id='sync-function-dagflow-multi_model_dataset',
    tags=['sync', 'dagflow', 'singlethread', 'specialize_record_models'],
)
def case_sync_dagflow_specialize_record_models() -> FlowCase:
    return FlowCase(
        name='specialize_record_models',
        flow_template=specialize_record_models_dag_flow,  # noqa
    )


@pc.case(
    id='sync-function-funcflow-multi_model_dataset',
    tags=['sync', 'funcflow', 'singlethread', 'specialize_record_models'],
)
def case_sync_funcflow_specialize_record_models() -> FlowCase:
    return FlowCase(
        name='specialize_record_models',
        flow_template=specialize_record_models_func_flow,  # noqa
    )
