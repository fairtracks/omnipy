"""Provide shared compute test fixtures."""

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
                              ChildJobListArgFlowClsTuple,
                              FlowClsTuple,
                              FuncArgFlowClsTuple,
                              FuncFlowTemplateCallable,
                              SingleChildJobDagFlowTemplateCallable,
                              SingleChildJobLinearFlowTemplateCallable)
from .helpers.mocks import (IsMockJob,
                            IsMockJobTemplate,
                            MockJobSubclass,
                            MockJobTemplateSubclass,
                            MockLocalRunner)

MockJobClasses = tuple[type[IsMockJobTemplate], type[IsMockJob]]


@pytest.fixture(scope='function')
def mock_job_classes() -> MockJobClasses:
    """Return mock job template and job classes."""
    return (cast(type[IsMockJobTemplate], MockJobTemplateSubclass),
            cast(type[IsMockJob], MockJobSubclass))


@pytest.fixture(scope='function')
def mock_local_runner(
        teardown_reset_job_creator: Annotated[None, pytest.fixture]) -> MockLocalRunner:
    """Return a mock runner installed on the shared job creator."""
    mock_local_runner = MockLocalRunner()
    JobBase.job_creator.set_engine(mock_local_runner)
    return mock_local_runner


@pytest.fixture(scope='function')
def mock_job_datetime(
        mock_datetime: Annotated[datetime, pytest.fixture]) -> Generator[datetime, None, None]:
    """Patch job creator time calls with the mock datetime."""
    import omnipy.compute._job_creator

    prev_datetime = omnipy.compute._job_creator.datetime
    omnipy.compute._job_creator.datetime = mock_datetime  # type: ignore[misc, assignment]

    mock_datetime.now()

    yield mock_datetime

    omnipy.compute._job_creator.datetime = prev_datetime  # type: ignore[misc]


@pc.fixture(scope='function')
def linear_flow_cls_tuple(
) -> FlowClsTuple[type[LinearFlow], SingleChildJobLinearFlowTemplateCallable]:
    return FlowClsTuple(
        flow_cls=LinearFlow,
        flow_tmpl_cls=LinearFlowTemplate,
        assert_flow_tmpl_cls=LinearFlowTemplateCore,
    )


@pc.fixture(scope='function')
def dag_flow_cls_tuple() -> FlowClsTuple[type[DagFlow], SingleChildJobDagFlowTemplateCallable]:
    return FlowClsTuple(
        flow_cls=DagFlow,
        flow_tmpl_cls=DagFlowTemplate,
        assert_flow_tmpl_cls=DagFlowTemplateCore,
    )


@pc.fixture(scope='function')
def func_flow_cls_tuple() -> FlowClsTuple[type[FuncFlow], FuncFlowTemplateCallable]:
    """Provide the function flow class tuple for reuse."""
    return FlowClsTuple(
        flow_cls=FuncFlow,
        flow_tmpl_cls=FuncFlowTemplate,
        assert_flow_tmpl_cls=FuncFlowTemplateCore,
    )


@pc.fixture(scope='function')
@pc.parametrize('flow_cls_tuple', [func_flow_cls_tuple])
def func_arg_flow_cls_tuple(
        flow_cls_tuple: Annotated[FuncArgFlowClsTuple, pc.fixture]) -> FuncArgFlowClsTuple:
    """Provide flow classes that take only callable arguments."""
    return flow_cls_tuple


@pc.fixture(scope='function')
@pc.parametrize('flow_cls_tuple', [linear_flow_cls_tuple, dag_flow_cls_tuple])
def child_job_list_arg_flow_cls_tuple(
    flow_cls_tuple: Annotated[ChildJobListArgFlowClsTuple,
                              pc.fixture]) -> ChildJobListArgFlowClsTuple:
    return flow_cls_tuple


@pc.fixture(scope='function')
@pc.parametrize('_flow_cls_tuple', [dag_flow_cls_tuple, linear_flow_cls_tuple, func_flow_cls_tuple])
def flow_cls_tuple(_flow_cls_tuple: AnyFlowClsTuple) -> AnyFlowClsTuple:
    """Provide any supported flow class tuple."""
    return _flow_cls_tuple
