from datetime import datetime
from io import StringIO
import logging
from logging import root, WARN
from logging.handlers import TimedRotatingFileHandler
import os
from typing import Annotated, Type

import pytest
import pytest_cases as pc

from omnipy.api.protocols import IsRuntime
from omnipy.log.mixin import LogMixin
from omnipy.util.helpers import get_datetime_format
from omnipy.util.mixin import DynamicMixinAcceptor

from .helpers.functions import (assert_log_line_from_stream,
                                assert_log_lines_from_stream,
                                read_log_line_from_stream)


@pc.case(id='my_class_as_regular_log_mixin_subclass')
def case_my_class_as_regular_log_mixin_subclass() -> Type:
    class MyClass(LogMixin):
        def __init__(self, foo: int, bar: bool = True, **kwargs: object):
            super().__init__(**kwargs)
            self.foo = foo
            self.bar = bar

    return MyClass


@pc.case(id='my_class_as_dynamic_log_mixin_subclass')
def case_my_class_as_dynamic_log_mixin_subclass() -> Type:
    class MyClass(DynamicMixinAcceptor):
        def __init__(self, foo: int, bar: bool = True, **kwargs: object):
            self.foo = foo
            self.bar = bar

    MyClass.accept_mixin(LogMixin)
    return MyClass


@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_default_log(
    str_stream: Annotated[StringIO, pytest.fixture],
    stream_root_logger: Annotated[logging.Logger, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
    mock_log_mixin_datetime: Annotated[datetime, pytest.fixture],
):
    my_obj = my_class_with_log_mixin(42, False)

    fixed_datetime_now = mock_log_mixin_datetime.now()

    my_obj.log('Log message', level=logging.INFO)

    assert_log_line_from_stream(
        str_stream,
        msg='Log message',
        level='INFO',
        logger='tests.log.test_log_mixin.MyClass',
        datetime_obj=fixed_datetime_now,
    )


#TODO: Move date localization into root log formatter


@pytest.mark.skip("TODO: Move date localization into root log formatter")
@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_logging_date_localization(
    str_stream: Annotated[StringIO, pytest.fixture],
    stream_root_logger: Annotated[logging.Logger, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
    mock_log_mixin_datetime: Annotated[datetime, pytest.fixture],
):
    my_obj = my_class_with_log_mixin(42, False)
    fixed_datetime_now = mock_log_mixin_datetime.now()

    locale = ('de_DE', 'UTF-8')
    my_obj.set_logger(stream_root_logger, locale=locale)
    my_obj.log('Log message')

    log_lines = assert_log_lines_from_stream(1, str_stream)

    assert fixed_datetime_now.strftime(get_datetime_format(locale)) in log_lines[0]
    assert '(root)' in log_lines[0]
