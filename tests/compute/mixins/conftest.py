from typing import Annotated

import pytest

from omnipy.api.protocols.public.compute import IsDagFlowTemplate
from omnipy.compute.flow import DagFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import mypy_fix_dag_flow_template
from omnipy.data.model import Model

from ..cases.raw.functions import power_m1_func
from ..helpers.mocks import MockLocalRunner


@pytest.fixture(scope='function')
def my_empty_dag_flow(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> IsDagFlowTemplate:
    @mypy_fix_dag_flow_template
    @DagFlowTemplate()
    def my_empty_dag_flow(number: int):
        ...

    return my_empty_dag_flow


@pytest.fixture(scope='function')
def my_double_power_m1_dag_flow(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> IsDagFlowTemplate:

    power_m1_template = TaskTemplate()(power_m1_func)

    @mypy_fix_dag_flow_template
    @DagFlowTemplate(
        power_m1_template,
        power_m1_template,
    )
    def my_double_power_m1_dag_flow(number: int | Model[int], exponent: int):
        ...

    return my_double_power_m1_dag_flow
