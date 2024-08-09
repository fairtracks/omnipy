from datetime import datetime, timedelta
from io import StringIO
import logging
from typing import Annotated, Type

import pytest
import pytest_cases as pc

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.hub.log.mixin import LogMixin
from omnipy.util.mixin import DynamicMixinAcceptor

from ..helpers.functions import assert_log_line_from_stream, format_datetime_obj


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
    runtime: Annotated[IsRuntime, pytest.fixture],
    my_class_with_log_mixin: Annotated[Type, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    my_obj = my_class_with_log_mixin(42, False)

    now = datetime.now()

    for i in range(2):
        my_obj.log(f'Log message {i}', level=logging.INFO, datetime_obj=now)

        assert_log_line_from_stream(
            my_stdout,
            msg=f'Log message {i}',
            level='INFO',
            logger='tests.hub.log.test_log_mixin.MyClass',
            datetime_str=format_datetime_obj(now, runtime),
        )

        now += timedelta(seconds=1)