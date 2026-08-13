from typing import Awaitable, Callable

import pytest_cases as pc

from omnipy.shared.protocols.compute.job import IsTask

from ...helpers.classes import FlowCase
from .raw.flows import specialize_record_models_dag_flow, specialize_record_models_func_flow

RunTaskAndAssertType = Callable[[IsTask], None]
AsyncRunTaskAndAssertType = Callable[[IsTask], Awaitable[None]]


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
