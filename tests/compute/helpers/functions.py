import inspect
from typing import Callable

from omnipy.shared.protocols.compute._job import IsJob, IsJobTemplate


def assert_updated_wrapper(a, b):
    assert a.__name__ == b.__name__
    assert a.__qualname__ == b.__qualname__
    assert a.__module__ == b.__module__
    assert a.__doc__ == b.__doc__
    assert a.__annotations__ == b.__annotations__

    equal_signatures = inspect.signature(a) == inspect.signature(b)
    assert equal_signatures


def assert_flow_or_flow_template(
    flow_obj: IsJobTemplate | IsJob,
    assert_flow_cls: type,
    assert_func: Callable,
    assert_name: str,
) -> None:
    assert isinstance(flow_obj, assert_flow_cls)
    assert_updated_wrapper(flow_obj, assert_func)
    assert flow_obj.name == assert_name
