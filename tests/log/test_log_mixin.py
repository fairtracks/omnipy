from datetime import datetime
from io import StringIO
import logging
from typing import Annotated, Generator, Type

import pytest
import pytest_cases as pc

from log.helpers.functions import (assert_log_line_from_stream,
                                   assert_log_lines_from_stream,
                                   read_log_line_from_stream)
from omnipy.log.mixin import LogDynMixin
from omnipy.util.helpers import get_datetime_format
from omnipy.util.mixin import DynamicMixinAcceptor


@pc.case(id='my_class_as_regular_log_mixin_subclass')
def case_my_class_as_regular_log_mixin_subclass() -> Type:
    class MyClass(LogDynMixin):
        def __init__(self, foo: int, bar: bool = True):
            super().__init__()
            self.foo = foo
            self.bar = bar

    return MyClass


@pc.case(id='my_class_as_dynamic_log_mixin_subclass')
def case_my_class_as_dynamic_log_mixin_subclass() -> Type:
    class MyClass(DynamicMixinAcceptor):
        def __init__(self, foo: int, bar: bool = True):
            self.foo = foo
            self.bar = bar

    MyClass.accept_mixin(LogDynMixin)
    return MyClass


@pytest.fixture
def log_to_string_stream(
    str_stream: Annotated[StringIO, pytest.fixture],) -> Generator[StringIO, None, None]:
    import logging

    stream_handler = logging.StreamHandler(str_stream)
    logging.root.addHandler(stream_handler)

    yield str_stream

    logging.root.removeHandler(stream_handler)


@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_default_log(
    str_stream: Annotated[StringIO, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
    mock_log_mixin_datetime: Annotated[datetime, pytest.fixture],
):
    my_obj = my_class_with_log_mixin(42, False)
    default_logger = my_obj.logger
    default_formatter = default_logger.handlers[0].formatter

    for handler in default_logger.handlers:
        default_logger.removeHandler(handler)
    stream_handler = logging.StreamHandler(str_stream)
    stream_handler.setFormatter(default_formatter)
    default_logger.addHandler(stream_handler)

    fixed_datetime_now = mock_log_mixin_datetime.now()

    my_obj.log('Log message', logging.WARN)

    assert_log_line_from_stream(
        str_stream,
        msg='Log message',
        level='WARNING',
        logger='tests.log.test_log_mixin.MyClass',
        datetime_obj=fixed_datetime_now,
    )


@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_set_logger(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
    mock_log_mixin_datetime: Annotated[datetime, pytest.fixture],
):
    simple_logger.addHandler(logging.StreamHandler(str_stream))
    fixed_datetime_now = mock_log_mixin_datetime.now()

    my_obj = my_class_with_log_mixin(42, False)
    my_obj.set_logger(simple_logger)

    assert my_obj.logger == simple_logger
    with pytest.raises(AttributeError):
        my_obj.logger = simple_logger

    my_obj.log('Log message', logging.WARN)

    assert_log_line_from_stream(
        str_stream,
        msg='Log message',
        level='WARNING',
        logger='test',
        datetime_obj=fixed_datetime_now,
    )


@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_state_change_logging_unset(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
):
    simple_logger.addHandler(logging.StreamHandler(str_stream))

    my_obj = my_class_with_log_mixin(42, False)

    my_obj.set_logger(simple_logger)
    my_obj.log('Log message')
    assert_log_lines_from_stream(1, str_stream)

    my_obj.set_logger(None)
    my_obj.log('New log message')
    assert_log_lines_from_stream(0, str_stream)

    my_obj.set_logger(simple_logger)
    my_obj.log('Another log message')
    assert_log_lines_from_stream(1, str_stream)


@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_state_change_logging_handler_formatting_variants(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
):
    my_obj = my_class_with_log_mixin(42, False)

    # Handler added after set_logger
    my_obj.set_logger(simple_logger, set_omnipy_formatter_on_handlers=True)
    simple_logger.addHandler(logging.StreamHandler(str_stream))
    my_obj.log('Log message')

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' not in log_line

    # Handler added before set_logger, set_omnipy_formatter_on_handlers=False
    my_obj.set_logger(simple_logger, set_omnipy_formatter_on_handlers=False)
    my_obj.log('New log message')

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' not in log_line

    # Handler added before set_logger, set_omnipy_formatter_on_handlers=True
    my_obj.set_logger(simple_logger, set_omnipy_formatter_on_handlers=True)
    my_obj.log('Another log message')

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' in log_line


@pc.parametrize_with_cases('my_class_with_log_mixin', cases='.')
def test_state_change_logging_date_localization(
    str_stream: Annotated[StringIO, pytest.fixture],
    stream_logger: Annotated[logging.Logger, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
    mock_log_mixin_datetime: Annotated[datetime, pytest.fixture],
):
    my_obj = my_class_with_log_mixin(42, False)
    fixed_datetime_now = mock_log_mixin_datetime.now()

    locale = ('de_DE', 'UTF-8')
    my_obj.set_logger(stream_logger, locale=locale)
    my_obj.log('Log message')

    log_lines = assert_log_lines_from_stream(1, str_stream)

    assert fixed_datetime_now.strftime(get_datetime_format(locale)) in log_lines[0]
    assert 'INFO (test)' in log_lines[0]
