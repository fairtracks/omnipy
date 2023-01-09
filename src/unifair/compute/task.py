from __future__ import annotations

import asyncio
from typing import Any, Callable, Mapping, Optional, Tuple, Type, Union

from unifair.compute.job import (CallableDecoratingJobTemplateMixin,
                                 Job,
                                 JobConfig,
                                 JobConfigAndMixinAcceptorMeta,
                                 JobTemplate)
from unifair.compute.mixins.func_signature import SignatureFuncJobConfigMixin
from unifair.compute.mixins.name import NameFuncJobConfigMixin
from unifair.compute.mixins.params import ParamsFuncJobConfigMixin, ParamsFuncJobMixin
from unifair.compute.mixins.result_key import ResultKeyFuncJobConfigMixin, ResultKeyFuncJobMixin
from unifair.util.callable_decorator_cls import callable_decorator_cls
from unifair.util.mixin import DynamicMixinAcceptor


class TaskConfig(DynamicMixinAcceptor, metaclass=JobConfigAndMixinAcceptorMeta):
    def __init__(self,
                 task_func: Callable,
                 *,
                 name: Optional[str] = None,
                 fixed_params: Optional[Mapping[str, object]] = None,
                 param_key_map: Optional[Mapping[str, str]] = None,
                 result_key: Optional[str] = None,
                 **kwargs: object) -> None:

        super().__init__()

        self._job_func = task_func

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)


TaskConfig.accept_mixin(NameFuncJobConfigMixin)
TaskConfig.accept_mixin(SignatureFuncJobConfigMixin)
TaskConfig.accept_mixin(ParamsFuncJobConfigMixin)
TaskConfig.accept_mixin(ResultKeyFuncJobConfigMixin)


@callable_decorator_cls
class TaskTemplate(CallableDecoratingJobTemplateMixin['TaskTemplate'], TaskConfig, JobTemplate):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return Task

    @classmethod
    def _apply_engine_decorator(cls, task: Task) -> Task:
        if cls.engine is not None:
            return cls.engine.task_decorator(task)
        else:
            return task


class Task(TaskConfig, Job):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return TaskConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return TaskTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        return self._job_func(*args, **kwargs)


Task.accept_mixin(ParamsFuncJobMixin)
Task.accept_mixin(ResultKeyFuncJobMixin)

# TODO: Would we need the possibility to refine task templates by adding new task parameters?
