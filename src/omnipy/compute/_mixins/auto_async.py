import asyncio
from inspect import iscoroutinefunction
from typing import Callable, cast, Coroutine

from omnipy.shared.protocols.compute._job import IsJobBase
from omnipy.util.helpers import get_event_loop_and_check_if_loop_is_running


class AutoAsyncJobBaseMixin:
    def __init__(
        self,
        *,
        auto_async: bool = True,
    ):
        self._auto_async = auto_async

    @property
    def auto_async(self) -> bool:
        return self._auto_async

    def _call_job(self, *args: object, **kwargs: object) -> object:
        self_as_job_base = cast(IsJobBase, self)
        super_as_job_base = cast(IsJobBase, super())

        assert hasattr(self, '_job_func')
        self._job_func: Callable
        job_func_is_coroutine: bool = iscoroutinefunction(self._job_func)
        super_call_job_func = cast(Callable[..., Coroutine], super_as_job_base._call_job)

        loop, loop_is_running = get_event_loop_and_check_if_loop_is_running()
        if self.auto_async and job_func_is_coroutine and not self_as_job_base.in_flow_context:
            if loop and loop_is_running:
                res: object = loop.create_task(super_call_job_func(*args, **kwargs))
            else:
                res = asyncio.run(super_call_job_func(*args, **kwargs))
        else:
            res = super_call_job_func(*args, **kwargs)

        return res
