from datetime import datetime
from typing import Annotated, cast, Generator

import pytest
import pytest_cases as pc

from omnipy.compute._job import JobBase
from omnipy.compute.flow import (DagFlow,
                                 DagFlowTemplate,
                                 DagFlowTemplateCore,
                                 FuncFlow,
                                 FuncFlowTemplate,
                                 FuncFlowTemplateCore,
                                 LinearFlow,
                                 LinearFlowTemplate,
                                 LinearFlowTemplateCore)

from .helpers.classes import (AnyFlowClsTuple,
                              FlowClsTuple,
                              FuncArgFlowClsTuple,
                              FuncFlowTemplateCallable,
                              SingleTaskDagFlowTemplateCallable,
                              SingleTaskLinearFlowTemplateCallable,
                              TaskTemplateArgFlowClsTuple)
from .helpers.mocks import (IsMockJob,
                            IsMockJobTemplate,
                            MockJobSubclass,
                            MockJobTemplateSubclass,
                            MockLocalRunner)

MockJobClasses = tuple[type[IsMockJobTemplate], type[IsMockJob]]


@pytest.fixture(scope='function')
def mock_job_classes() -> MockJobClasses:
    return (cast(type[IsMockJobTemplate], MockJobTemplateSubclass),
            cast(type[IsMockJob], MockJobSubclass))


@pytest.fixture(scope='function')
def mock_local_runner(
        teardown_reset_job_creator: Annotated[None, pytest.fixture]) -> MockLocalRunner:
    mock_local_runner = MockLocalRunner()
    JobBase.job_creator.set_engine(mock_local_runner)
    return mock_local_runner


@pytest.fixture(scope='function')
def mock_job_datetime(
        mock_datetime: Annotated[datetime, pytest.fixture]) -> Generator[datetime, None, None]:
    import omnipy.compute._job_creator

    prev_datetime = omnipy.compute._job_creator.datetime
    omnipy.compute._job_creator.datetime = mock_datetime  # type: ignore[misc, assignment]

    mock_datetime.now()

    yield mock_datetime

    omnipy.compute._job_creator.datetime = prev_datetime  # type: ignore[misc]


@pc.fixture(scope='function')
def linear_flow_cls_tuple() -> FlowClsTuple[type[LinearFlow], SingleTaskLinearFlowTemplateCallable]:
    return FlowClsTuple(
        flow_cls=LinearFlow,
        flow_tmpl_cls=LinearFlowTemplate,
        assert_flow_tmpl_cls=LinearFlowTemplateCore,
    )


@pc.fixture(scope='function')
def dag_flow_cls_tuple() -> FlowClsTuple[type[DagFlow], SingleTaskDagFlowTemplateCallable]:
    return FlowClsTuple(
        flow_cls=DagFlow,
        flow_tmpl_cls=DagFlowTemplate,
        assert_flow_tmpl_cls=DagFlowTemplateCore,
    )


@pc.fixture(scope='function')
def func_flow_cls_tuple() -> FlowClsTuple[type[FuncFlow], FuncFlowTemplateCallable]:
    return FlowClsTuple(
        flow_cls=FuncFlow,
        flow_tmpl_cls=FuncFlowTemplate,
        assert_flow_tmpl_cls=FuncFlowTemplateCore,
    )


@pc.fixture(scope='function')
@pc.parametrize('flow_cls_tuple', [func_flow_cls_tuple])
def func_arg_flow_cls_tuple(
        flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pc.fixture]) -> FuncArgFlowClsTuple:
    return flow_cls_tuple


@pc.fixture(scope='function')
@pc.parametrize('flow_cls_tuple', [linear_flow_cls_tuple, dag_flow_cls_tuple])
def task_tmpl_arg_flow_cls_tuple(
    flow_cls_tuple: Annotated[TaskTemplateArgFlowClsTuple,
                              pc.fixture]) -> TaskTemplateArgFlowClsTuple:
    return flow_cls_tuple


@pc.fixture(scope='function')
@pc.parametrize('_flow_cls_tuple', [dag_flow_cls_tuple, linear_flow_cls_tuple, func_flow_cls_tuple])
def flow_cls_tuple(_flow_cls_tuple: AnyFlowClsTuple) -> AnyFlowClsTuple:
    return _flow_cls_tuple
