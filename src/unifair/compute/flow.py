from abc import abstractmethod
import asyncio
import inspect
from types import MappingProxyType
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from unifair.compute.job import CallableDecoratingJobTemplateMixin, Job, JobConfig, JobTemplate
from unifair.engine.protocols import (IsDagFlowRunnerEngine,
                                      IsFuncFlowRunnerEngine,
                                      IsLinearFlowRunnerEngine,
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


class LinearFlowConfig(FlowConfig):
    def __init__(
        self,
        linear_flow_func: Callable,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        self._linear_flow_func = linear_flow_func
        self._linear_flow_func_signature = inspect.signature(self._linear_flow_func)
        self._task_templates: Tuple[IsTaskTemplate] = task_templates
        name = name if name is not None else self._linear_flow_func.__name__
        super().__init__(name=name, **kwargs)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._linear_flow_func, *self._task_templates

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    @property
    def task_templates(self) -> Tuple[IsTaskTemplate]:
        return self._task_templates

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._linear_flow_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._linear_flow_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._linear_flow_func_signature.return_annotation


@callable_decorator_cls
class LinearFlowTemplate(CallableDecoratingJobTemplateMixin['LinearFlowTemplate'],
                         FlowTemplate,
                         LinearFlowConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return LinearFlow

    def _apply_engine_decorator(self, flow: 'LinearFlow') -> 'LinearFlow':
        if self.engine is not None and isinstance(self.engine, IsLinearFlowRunnerEngine):
            return self.engine.linear_flow_decorator(flow)  # noqa  # Pycharm type checker bug
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')


class LinearFlow(Flow, LinearFlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return LinearFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return LinearFlowTemplate  # noqa  # Pycharm static type checker bug

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._linear_flow_func).bind(*args, **kwargs).arguments


class DagFlowConfig(FlowConfig):
    def __init__(
        self,
        dag_flow_func: Callable,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        self._dag_flow_func = dag_flow_func
        self._dag_flow_func_signature = inspect.signature(self._dag_flow_func)
        self._task_templates: Tuple[IsTaskTemplate] = task_templates
        name = name if name is not None else self._dag_flow_func.__name__
        super().__init__(name=name, **kwargs)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._dag_flow_func, *self._task_templates

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    @property
    def task_templates(self) -> Tuple[IsTaskTemplate]:
        return self._task_templates

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._dag_flow_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._dag_flow_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._dag_flow_func_signature.return_annotation


@callable_decorator_cls
class DagFlowTemplate(CallableDecoratingJobTemplateMixin['DagFlowTemplate'],
                      FlowTemplate,
                      DagFlowConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return DagFlow

    def _apply_engine_decorator(self, flow: 'DagFlow') -> 'DagFlow':
        if self.engine is not None and isinstance(self.engine, IsDagFlowRunnerEngine):
            return self.engine.dag_flow_decorator(flow)  # noqa  # Pycharm static type checker bug
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')


class DagFlow(Flow, DagFlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return DagFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return DagFlowTemplate  # noqa  # Pycharm static type checker bug

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._dag_flow_func).bind(*args, **kwargs).arguments


class FuncFlowConfig(FlowConfig):
    def __init__(
        self,
        func_flow_func: Callable,
        *,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        name = name if name is not None else func_flow_func.__name__
        super().__init__(name=name)
        self._func_flow_func = func_flow_func

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._func_flow_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._func_flow_func)


@callable_decorator_cls
class FuncFlowTemplate(CallableDecoratingJobTemplateMixin['FuncFlowTemplate'],
                       FlowTemplate,
                       FuncFlowConfig):
    def _apply_engine_decorator(self, flow: 'FuncFlow') -> 'FuncFlow':
        if self.engine is not None and isinstance(self.engine, IsFuncFlowRunnerEngine):
            return self.engine.func_flow_decorator(flow)  # noqa  # Pycharm type checker bug
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support function flows')

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
        return self._func_flow_func(*args, **kwargs)


# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
