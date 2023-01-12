from abc import ABC
import asyncio
import inspect
from typing import Any, Callable, Dict, Generic, Mapping, Optional, Tuple, Union

from omnipy.compute.job import Job, JobBase, JobBaseAndMixinAcceptorMeta, JobTemplate
from omnipy.compute.job_types import FuncJobTemplateT, JobBaseT, JobT, JobTemplateT
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.iterate import IterateFuncJobBaseMixin
from omnipy.compute.mixins.name import NameFuncJobBaseMixin
from omnipy.compute.mixins.params import ParamsFuncJobBaseMixin, ParamsFuncJobMixin
from omnipy.compute.mixins.result_key import ResultKeyFuncJobBaseMixin, ResultKeyFuncJobMixin
from omnipy.compute.mixins.serialize import (PersistOutputsOptions,
                                             RestoreOutputsOptions,
                                             SerializerFuncJobBaseMixin,
                                             SerializerFuncJobMixin)
from omnipy.util.helpers import remove_none_vals
from omnipy.util.mixin import DynamicMixinAcceptor


class FuncJobBase(JobBase, DynamicMixinAcceptor, metaclass=JobBaseAndMixinAcceptorMeta):
    def __init__(self,
                 job_func: Callable,
                 *,
                 name: Optional[str] = None,
                 fixed_params: Optional[Mapping[str, object]] = None,
                 param_key_map: Optional[Mapping[str, str]] = None,
                 result_key: Optional[str] = None,
                 iterate_over_data_files: bool = False,
                 persist_outputs: Optional[PersistOutputsOptions] = None,
                 restore_outputs: Optional[RestoreOutputsOptions] = None,
                 **kwargs: object) -> None:

        super().__init__()

        self._job_func = job_func

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)


FuncJobBase.accept_mixin(NameFuncJobBaseMixin)
FuncJobBase.accept_mixin(SignatureFuncJobBaseMixin)
FuncJobBase.accept_mixin(IterateFuncJobBaseMixin)
FuncJobBase.accept_mixin(ParamsFuncJobBaseMixin)
FuncJobBase.accept_mixin(ResultKeyFuncJobBaseMixin)
FuncJobBase.accept_mixin(SerializerFuncJobBaseMixin)


class FuncJobTemplate(FuncJobBase, JobTemplate[JobT], Generic[JobT], ABC):
    def refine(self: FuncJobTemplateT,
               update: bool = True,
               name: Optional[str] = None,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               iterate_over_data_files: bool = False,
               persist_outputs: Optional[PersistOutputsOptions] = None,
               restore_outputs: Optional[RestoreOutputsOptions] = None,
               **kwargs: Any) -> FuncJobTemplateT:

        return JobTemplate.refine(
            self,
            update=update,
            **remove_none_vals(
                name=name,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                iterate_over_data_files=iterate_over_data_files,
                persist_outputs=persist_outputs,
                restore_outputs=restore_outputs,
                **kwargs,
            ))


class FuncJob(FuncJobBase, Job[JobBaseT, JobTemplateT], Generic[JobBaseT, JobTemplateT], ABC):
    def __call__(self, *args: object, **kwargs: object) -> object:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: object, **kwargs: object) -> object:
        return self._job_func(*args, **kwargs)

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._job_func).bind(*args, **kwargs).arguments


FuncJob.accept_mixin(ParamsFuncJobMixin)
FuncJob.accept_mixin(ResultKeyFuncJobMixin)
FuncJob.accept_mixin(SerializerFuncJobMixin)
