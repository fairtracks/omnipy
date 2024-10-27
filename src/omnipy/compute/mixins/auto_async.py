import asyncio
from asyncio import AbstractEventLoop, get_event_loop
from inspect import iscoroutinefunction
from typing import Callable, cast, Coroutine

from omnipy.api.protocols.private.compute.job import IsJobBase, IsPlainFuncArgJobBase


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
        self_as_plain_func_arg_job_base = cast(IsPlainFuncArgJobBase, self)
        self_as_job_base = cast(IsJobBase, self)
        super_as_job_base = cast(IsJobBase, super())

        job_func = self_as_plain_func_arg_job_base._job_func
        job_func_is_coroutine: bool = iscoroutinefunction(job_func)
        super_call_job_func = cast(Callable[..., Coroutine], super_as_job_base._call_job)

        loop_is_running: bool
        try:
            loop_is_running = get_event_loop().is_running()
        except RuntimeError:
            loop_is_running = False

        if self.auto_async and job_func_is_coroutine and not self_as_job_base.in_flow_context:
            if loop_is_running:
                loop: AbstractEventLoop = get_event_loop()
                res: object = loop.create_task(super_call_job_func(*args, **kwargs))
            else:
                res = asyncio.run(super_call_job_func(*args, **kwargs))
        else:
            res = super_call_job_func(*args, **kwargs)

        return res
