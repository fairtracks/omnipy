from datetime import datetime
from io import StringIO
import logging
from typing import Annotated, Type

import pytest
import pytest_cases as pc

from omnipy.log.mixin import LogMixin
from omnipy.util.mixin import DynamicMixinAcceptor

from .helpers.functions import assert_log_line_from_stream


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

    my_obj.log('Log message', level=logging.INFO)

    assert_log_line_from_stream(
        str_stream,
        msg='Log message',
        level='INFO',
        logger='tests.log.test_log_mixin.MyClass',
    )
