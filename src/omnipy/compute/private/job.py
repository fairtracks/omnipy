from abc import ABC
import asyncio
import inspect
from typing import Any, Callable, Dict, Generic, Mapping, Optional, Tuple, Union

from omnipy.compute.job import Job, JobBase, JobTemplate
from omnipy.compute.job_creator import JobBaseMeta
# from omnipy.compute.job_types import FuncJobTemplateT, JobBaseT, JobT, JobTemplateT
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.iterate import IterateFuncJobBaseMixin
from omnipy.compute.mixins.params import ParamsFuncJobBaseMixin
from omnipy.compute.mixins.result_key import ResultKeyFuncJobBaseMixin
from omnipy.compute.mixins.serialize import (PersistOutputsOptions,
                                             RestoreOutputsOptions,
                                             SerializerFuncJobBaseMixin)
from omnipy.util.helpers import remove_none_vals
from omnipy.util.mixin import DynamicMixinAcceptor


class PlainFuncArgJobBase(JobBase):
    def __init__(self, job_func: Callable, *args: object, **kwargs: object) -> None:
        # JobBase.__init__(self, job_func, *args, **kwargs)
        self._job_func = job_func

    def _get_init_args(self) -> Tuple[object, ...]:
        return self._job_func,

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)

    def _call_job(self, *args: object, **kwargs: object) -> object:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: object, **kwargs: object) -> object:
        return self._job_func(*args, **kwargs)

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._job_func).bind(*args, **kwargs).arguments


# Needs a separate level. If not, self._call_func changes from IterateFuncJobBaseMixin
# would be overwritten by FuncArgJobBase
PlainFuncArgJobBase.accept_mixin(IterateFuncJobBaseMixin)


class FuncArgJobBase(PlainFuncArgJobBase):
    ...


FuncArgJobBase.accept_mixin(SignatureFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ParamsFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ResultKeyFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(SerializerFuncJobBaseMixin)

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
