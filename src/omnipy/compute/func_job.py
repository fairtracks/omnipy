import asyncio
from typing import Callable

from omnipy.api.typedefs import GeneralDecorator
from omnipy.compute.job import JobBase
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.iterate import IterateFuncJobBaseMixin
from omnipy.compute.mixins.params import ParamsFuncJobBaseMixin
from omnipy.compute.mixins.result_key import ResultKeyFuncJobBaseMixin
from omnipy.compute.mixins.serialize import SerializerFuncJobBaseMixin


class PlainFuncArgJobBase(JobBase):
    def __init__(self, job_func: Callable, *args: object, **kwargs: object) -> None:
        self._job_func = job_func

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func,

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)

    def _call_job(self, *args: object, **kwargs: object) -> object:
        """To be overloaded by mixins"""
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: object, **kwargs: object) -> object:
        """
        To be decorated by job runners and mixins that need early application. Should not
        be overloaded using inheritance. The method _accept_call_func_decorator accepts
        decorators.
        """
        return self._job_func(*args, **kwargs)

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        self._call_func = call_func_decorator(self._call_func)  # type:ignore


# Extra level needed for mixins to be able to overload _call_job (and possibly other methods)
class FuncArgJobBase(PlainFuncArgJobBase):
    ...


FuncArgJobBase.accept_mixin(SignatureFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(IterateFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(SerializerFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ResultKeyFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ParamsFuncJobBaseMixin)
