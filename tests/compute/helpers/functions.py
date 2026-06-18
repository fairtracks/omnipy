from typing import Callable

from omnipy.shared.protocols.compute._job import IsJob, IsJobTemplate

from ...helpers.functions import assert_func_wrapper


def assert_flow_or_flow_template(
    flow_obj: IsJobTemplate | IsJob,
    assert_flow_cls: type,
    assert_func: Callable,
    assert_name: str,
) -> None:
    assert isinstance(flow_obj, assert_flow_cls)
    assert_func_wrapper(flow_obj, assert_func)
    assert flow_obj.name == assert_name
