import asyncio
from typing import Callable, Dict, Tuple

from omnipy.api.types import GeneralDecorator
from omnipy.compute.job import JobBase
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.iterate import IterateFuncJobBaseMixin
from omnipy.compute.mixins.params import ParamsFuncJobBaseMixin
from omnipy.compute.mixins.result_key import ResultKeyFuncJobBaseMixin
from omnipy.compute.mixins.serialize import SerializerFuncJobBaseMixin


class PlainFuncArgJobBase(JobBase):
    def __init__(self, job_func: Callable, *args: object, **kwargs: object) -> None:
        # JobBase.__init__(self, job_func, *args, **kwargs)
        self._job_func = job_func

    def _get_init_args(self) -> Tuple[object, ...]:
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
        self._call_func = call_func_decorator(self._call_func)


# Extra level needed for mixins to be able to overload _call_job (and possibly other methods)
class FuncArgJobBase(PlainFuncArgJobBase):
    ...


FuncArgJobBase.accept_mixin(SignatureFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(IterateFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(SerializerFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ResultKeyFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ParamsFuncJobBaseMixin)

# class FuncJobTemplate(FuncArgJobBase, JobTemplate, ABC):
#     def refine(self,
#                update: bool = True,
#                name: Optional[str] = None,
#                iterate_over_data_files: bool = False,
#                fixed_params: Optional[Mapping[str, object]] = None,
#                param_key_map: Optional[Mapping[str, str]] = None,
#                result_key: Optional[str] = None,
#                persist_outputs: Optional[PersistOutputsOptions] = None,
#                restore_outputs: Optional[RestoreOutputsOptions] = None,
#                **kwargs: object):  # -> FuncJobTemplateT:
#
#         return self._refine(
#             self,
#             update=update,
#             **remove_none_vals(
#                 name=name,
#                 iterate_over_data_files=iterate_over_data_files,
#                 fixed_params=fixed_params,
#                 param_key_map=param_key_map,
#                 result_key=result_key,
#                 persist_outputs=persist_outputs,
#                 restore_outputs=restore_outputs,
#                 **kwargs,
#             ))
