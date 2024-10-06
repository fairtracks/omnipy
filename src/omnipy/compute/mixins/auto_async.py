# from inspect import iscoroutine
from typing import cast

from omnipy.api.protocols.private.compute.job import IsJobBase

# import anyio


class AutoAsyncJobBaseMixin:
    def __init__(
        self,
        *,
        auto_async: bool = True,
    ):
        self._auto_async = auto_async

    @property
    def auto_async(self) -> str | None:
        return self._auto_async

    async def _call_job(self, *args: object, **kwargs: object) -> object:
        super_as_job_base = cast(IsJobBase, super())
        res = await super_as_job_base._call_job(*args, **kwargs)
        print('res', res)
        # if self.auto_async:
        #     if not iscoroutine(res):
        #         return anyio.to_thread.run_sync(lambda: res)
        return res
