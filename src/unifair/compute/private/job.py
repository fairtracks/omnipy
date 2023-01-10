from abc import ABC
import asyncio
import inspect
from typing import Any, Callable, Dict, Generic, Mapping, Optional, Tuple, Union

from unifair.compute.job import Job, JobConfig, JobConfigAndMixinAcceptorMeta, JobTemplate
from unifair.compute.mixins.func_signature import SignatureFuncJobConfigMixin
from unifair.compute.mixins.name import NameFuncJobConfigMixin
from unifair.compute.mixins.params import ParamsFuncJobConfigMixin, ParamsFuncJobMixin
from unifair.compute.mixins.result_key import ResultKeyFuncJobConfigMixin, ResultKeyFuncJobMixin
from unifair.compute.types import FuncJobTemplateT, JobConfigT, JobT, JobTemplateT
from unifair.util.helpers import remove_none_vals
from unifair.util.mixin import DynamicMixinAcceptor


class FuncJobConfig(JobConfig, DynamicMixinAcceptor, metaclass=JobConfigAndMixinAcceptorMeta):
    def __init__(self,
                 job_func: Callable,
                 *,
                 name: Optional[str] = None,
                 fixed_params: Optional[Mapping[str, object]] = None,
                 param_key_map: Optional[Mapping[str, str]] = None,
                 result_key: Optional[str] = None,
                 **kwargs: object) -> None:

        super().__init__()

        self._job_func = job_func

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)


FuncJobConfig.accept_mixin(NameFuncJobConfigMixin)
FuncJobConfig.accept_mixin(SignatureFuncJobConfigMixin)
FuncJobConfig.accept_mixin(ParamsFuncJobConfigMixin)
FuncJobConfig.accept_mixin(ResultKeyFuncJobConfigMixin)


class FuncJobTemplate(FuncJobConfig, JobTemplate[JobT], Generic[JobT], ABC):
    def refine(self,
               update: bool = True,
               name: Optional[str] = None,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               **kwargs: Any) -> FuncJobTemplateT:

        return JobTemplate.refine(
            self,
            update=update,
            **remove_none_vals(
                name=name,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                **kwargs,
            ))


class FuncJob(FuncJobConfig, Job[JobConfigT, JobTemplateT], Generic[JobConfigT, JobTemplateT], ABC):
    def __call__(self, *args: object, **kwargs: object) -> object:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: object, **kwargs: object) -> object:
        return self._job_func(*args, **kwargs)

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._job_func).bind(*args, **kwargs).arguments


FuncJob.accept_mixin(ParamsFuncJobMixin)
FuncJob.accept_mixin(ResultKeyFuncJobMixin)
