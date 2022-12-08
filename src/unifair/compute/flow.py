from abc import abstractmethod
import asyncio
import inspect
from types import MappingProxyType
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from unifair.compute.job import CallableDecoratingJobTemplateMixin, Job, JobConfig, JobTemplate
from unifair.engine.protocols import (IsDagFlowRunnerEngine,
                                      IsFuncFlowRunnerEngine,
                                      IsTask,
                                      IsTaskTemplate)
from unifair.util.callable_decorator_cls import callable_decorator_cls


class FlowConfig(JobConfig):
    def __init__(self, *, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name=name, **kwargs)

        if self._name is not None:
            self._check_not_empty_string('name', self.name)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class FlowTemplate(JobTemplate, FlowConfig):
    @abstractmethod
    def _apply_engine_decorator(cls, job: Job) -> Job:
        pass

    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return Flow


class Flow(Job, FlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return FlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return FlowTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    @abstractmethod
    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        pass


class DagFlowConfig(FlowConfig):
    def __init__(
        self,
        flow_func: Callable,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        self._flow_func = flow_func
        self._flow_func_signature = inspect.signature(self._flow_func)
        self._task_templates: Tuple[IsTaskTemplate] = task_templates
        self._tasks: Optional[Tuple[IsTask]] = None
        name = name if name is not None else self._flow_func.__name__
        super().__init__(name=name, **kwargs)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._flow_func, *self._task_templates

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    def has_coroutine_flow_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._flow_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._flow_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._flow_func_signature.return_annotation


@callable_decorator_cls
class DagFlowTemplate(CallableDecoratingJobTemplateMixin['DagFlowTemplate'],
                      FlowTemplate,
                      DagFlowConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return DagFlow

    def _apply_engine_decorator(self, flow: 'DagFlow') -> 'DagFlow':
        if self.engine is not None and isinstance(self.engine, IsDagFlowRunnerEngine):
            flow._tasks = tuple(task_template.apply() for task_template in self.task_templates)
            return self.engine.dag_flow_decorator(flow)  # noqa  # Pycharm static type checker bug
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')

    @property
    def task_templates(self) -> Tuple[IsTaskTemplate]:
        return self._task_templates


class DagFlow(Flow, DagFlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return DagFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return DagFlowTemplate  # noqa  # Pycharm static type checker bug

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @property
    def tasks(self) -> Tuple[IsTask]:
        return self._tasks

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._flow_func).bind(*args, **kwargs).arguments


class FuncFlowConfig(FlowConfig):
    def __init__(
        self,
        flow_func: Callable,
        *,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        name = name if name is not None else flow_func.__name__
        super().__init__(name=name)
        self._flow_func = flow_func

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._flow_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


@callable_decorator_cls
class FuncFlowTemplate(CallableDecoratingJobTemplateMixin['FuncFlowTemplate'],
                       FlowTemplate,
                       FuncFlowConfig):
    def _apply_engine_decorator(self, flow: 'FuncFlow') -> 'FuncFlow':
        if self.engine is not None and isinstance(self.engine, IsFuncFlowRunnerEngine):
            return self.engine.func_flow_decorator(flow)  # noqa  # Pycharm type checker bug
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')

    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return FuncFlow


class FuncFlow(Flow, FuncFlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return FuncFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return FuncFlowTemplate  # noqa  # Pycharm static type checker bug

    def _call_func(self, *args: object, **kwargs: object) -> Any:
        return self._flow_func(*args, **kwargs)


# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
