from datetime import datetime
from io import StringIO
import logging
from typing import Annotated, Generator

import pytest
import pytest_cases as pc

from engine.helpers.mocks import (MockDagFlow,
                                  MockDagFlowTemplate,
                                  MockJobRunnerSubclass,
                                  MockTask,
                                  MockTaskTemplate)


@pytest.fixture(scope='function')
def str_stream() -> StringIO:
    return StringIO()


@pytest.fixture(scope='function')
def simple_root_logger() -> Generator[logging.Logger, None, None]:
    root_logger = logging.root
    prev_level = root_logger.level
    root_logger.setLevel(logging.INFO)
    yield root_logger
    root_logger.setLevel(prev_level)


@pytest.fixture(scope='function')
def root_log_format_string() -> str:
    return '{asctime} - {levelname}: {message} ({name})'


@pytest.fixture(scope='function')
def root_log_datetime_fmt() -> str:
    return '%a %b %e %X %Y'


@pytest.fixture(scope='function')
def stream_root_logger(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_root_logger: Annotated[logging.Logger, pytest.fixture],
    root_log_format_string: Annotated[str, pytest.fixture],
    root_log_datetime_fmt: Annotated[str, pytest.fixture],
) -> Generator[logging.Logger, None, None]:
    stream_handler = logging.StreamHandler(str_stream)
    stream_handler.setFormatter(
        logging.Formatter(root_log_format_string, root_log_datetime_fmt, style='{'))
    simple_root_logger.addHandler(stream_handler)
    yield simple_root_logger
    simple_root_logger.removeHandler(stream_handler)


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
    import omnipy.hub.log.mixin

    prev_datetime = omnipy.hub.log.mixin.datetime
    omnipy.hub.log.mixin.datetime = mock_datetime

    yield mock_datetime

    omnipy.hub.log.mixin.datetime = prev_datetime
