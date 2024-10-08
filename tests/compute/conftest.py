from datetime import datetime
from typing import Annotated, Generator, Type

import pytest

from omnipy.compute.flow import (DagFlow,
                                 DagFlowTemplate,
                                 FuncFlow,
                                 FuncFlowTemplate,
                                 LinearFlow,
                                 LinearFlowTemplate)
from omnipy.compute.job import JobBase, JobMixin, JobTemplateMixin

from .helpers.classes import FlowClsTuple
from .helpers.mocks import MockJobSubclass, MockJobTemplateSubclass, MockLocalRunner


@pytest.fixture(scope='function')
def mock_job_classes() -> tuple[Type[JobTemplateMixin], Type[JobMixin]]:
    return MockJobTemplateSubclass, MockJobSubclass


@pytest.fixture(scope='function')
def mock_local_runner(
        teardown_reset_job_creator: Annotated[None, pytest.fixture]) -> MockLocalRunner:
    mock_local_runner = MockLocalRunner()
    JobBase.job_creator.set_engine(mock_local_runner)
    return mock_local_runner


@pytest.fixture(scope='function')
def mock_job_datetime(
        mock_datetime: Annotated[datetime, pytest.fixture]) -> Generator[datetime, None, None]:
    import omnipy.compute.job_creator

    prev_datetime = omnipy.compute.job_creator.datetime
    omnipy.compute.job_creator.datetime = mock_datetime

    yield mock_datetime

    omnipy.compute.job_creator.datetime = prev_datetime


@pytest.fixture(scope='function')
def all_flow_classes() -> tuple[FlowClsTuple, ...]:
    return (
        FlowClsTuple(template_cls=LinearFlowTemplate, flow_cls=LinearFlow),
        FlowClsTuple(template_cls=DagFlowTemplate, flow_cls=DagFlow),
        FlowClsTuple(template_cls=FuncFlowTemplate, flow_cls=FuncFlow),
    )
