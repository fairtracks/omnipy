from datetime import datetime
from io import StringIO
import logging
from typing import Annotated, Generator

import pytest
import pytest_cases as pc

from ..engine.helpers.mocks import (MockDagFlow,
                                    MockDagFlowTemplate,
                                    MockJobRunnerSubclass,
                                    MockTask,
                                    MockTaskTemplate)


@pytest.fixture(scope='function')
def str_stream() -> StringIO:
    return StringIO()


@pytest.fixture(scope='function')
def simple_logger() -> logging.Logger:
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    yield logger
    for handler in logger.handlers:
        logger.removeHandler(handler)


@pytest.fixture(scope='function')
def stream_logger(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
) -> logging.Logger:
    stream_handler = logging.StreamHandler(str_stream)
    simple_logger.addHandler(stream_handler)
    yield simple_logger
    simple_logger.removeHandler(stream_handler)


@pytest.fixture(scope='module')
def task_template_a() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='a')
    def concat_a(s: str) -> str:
        return s + 'a'

    return concat_a


@pytest.fixture(scope='module')
def task_template_b() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='b')
    def concat_b(s: str) -> str:
        return s + 'b'

    return concat_b


@pytest.fixture(scope='module')
def task_a(task_template_a) -> MockTask:
    return task_template_a.apply()


@pytest.fixture(scope='module')
def task_b(task_template_b) -> MockTask:
    return task_template_b.apply()


@pytest.fixture(scope='module')
def dag_flow_a(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='a')
    def concat_a(s: str) -> str:
        ...

    return concat_a.apply()


@pytest.fixture(scope='module')
def dag_flow_b(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='b')
    def concat_b(s: str) -> str:
        ...

    return concat_b.apply()


@pc.fixture(scope='function')
def mock_log_mixin_datetime(
        mock_datetime: Annotated[datetime, pytest.fixture]) -> Generator[datetime, None, None]:
    import omnipy.log.mixin

    prev_datetime = omnipy.log.mixin.datetime
    omnipy.log.mixin.datetime = mock_datetime

    yield mock_datetime

    omnipy.log.mixin.datetime = prev_datetime
