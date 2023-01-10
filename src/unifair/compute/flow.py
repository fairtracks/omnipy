from abc import abstractmethod
import asyncio
import inspect
from typing import (Any,
                    Callable,
                    cast,
                    Dict,
                    Generic,
                    Mapping,
                    Optional,
                    Protocol,
                    Tuple,
                    Type,
                    TypeVar,
                    Union)

from unifair.compute.job import (CallableDecoratingJobTemplateMixin,
                                 Job,
                                 JobConfig,
                                 JobConfigAndMixinAcceptorMeta,
                                 JobTemplate)
from unifair.compute.mixins.func_signature import SignatureFuncJobConfigMixin
from unifair.compute.mixins.name import NameFuncJobConfigMixin
from unifair.compute.mixins.params import ParamsFuncJobConfigMixin, ParamsFuncJobMixin
from unifair.compute.mixins.result_key import ResultKeyFuncJobConfigMixin, ResultKeyFuncJobMixin
from unifair.engine.protocols import (IsDagFlow,
                                      IsDagFlowRunnerEngine,
                                      IsFlow,
                                      IsFuncFlow,
                                      IsFuncFlowRunnerEngine,
                                      IsLinearFlow,
                                      IsLinearFlowRunnerEngine,
                                      IsTaskTemplate)
from unifair.util.callable_decorator_cls import callable_decorator_cls
from unifair.util.mixin import DynamicMixinAcceptor


class FlowConfig(JobConfig, DynamicMixinAcceptor, metaclass=JobConfigAndMixinAcceptorMeta):
    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)


FlowConfig.accept_mixin(NameFuncJobConfigMixin)

FlowT = TypeVar('FlowT', bound='Flow', covariant=True)


class FlowTemplate(JobTemplate[FlowT], Generic[FlowT]):
    @abstractmethod
    def _apply_engine_decorator(self, job: IsFlow) -> IsFlow:
        pass


FlowConfigT = TypeVar('FlowConfigT', bound=FlowConfig, covariant=True)
FlowTemplateT = TypeVar('FlowTemplateT', bound=FlowTemplate, covariant=True)


class Flow(Job[FlowConfigT, FlowTemplateT], Generic[FlowConfigT, FlowTemplateT]):
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
        super().__init__()

        self._job_func = linear_flow_func
        self._task_templates: Tuple[IsTaskTemplate, ...] = task_templates

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func, *self._task_templates

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    @property
    def task_templates(self) -> Tuple[IsTaskTemplate, ...]:
        return self._task_templates

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._linear_flow_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._linear_flow_func_signature.return_annotation


@callable_decorator_cls
class LinearFlowTemplate(CallableDecoratingJobTemplateMixin['LinearFlowTemplate'],
                         LinearFlowConfig,
                         FlowTemplate['LinearFlow']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['LinearFlow']:
        return LinearFlow

    def _apply_engine_decorator(self, flow: IsLinearFlow) -> IsLinearFlow:
        if self.engine is not None and isinstance(self.engine, IsLinearFlowRunnerEngine):
            return self.engine.linear_flow_decorator(flow)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support linear flows')


class LinearFlow(LinearFlowConfig, Flow[LinearFlowConfig, LinearFlowTemplate]):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[LinearFlowConfig]:
        return LinearFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[LinearFlowTemplate]:
        return LinearFlowTemplate

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._job_func).bind(*args, **kwargs).arguments


class DagFlowConfig(FlowConfig):
    def __init__(
        self,
        dag_flow_func: Callable,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__()

        self._job_func = dag_flow_func
        self._dag_flow_func_signature = inspect.signature(self._job_func)
        self._task_templates: Tuple[IsTaskTemplate, ...] = task_templates

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func, *self._task_templates

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    @property
    def task_templates(self) -> Tuple[IsTaskTemplate, ...]:
        return self._task_templates

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._dag_flow_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._dag_flow_func_signature.return_annotation


@callable_decorator_cls
class DagFlowTemplate(CallableDecoratingJobTemplateMixin['DagFlowTemplate'],
                      DagFlowConfig,
                      FlowTemplate['DagFlow']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['DagFlow']:
        return DagFlow

    def _apply_engine_decorator(self, flow: 'DagFlow') -> 'DagFlow':
        if self.engine is not None and isinstance(self.engine, IsDagFlowRunnerEngine):
            return self.engine.dag_flow_decorator(job)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')


class DagFlow(DagFlowConfig, Flow[DagFlowConfig, DagFlowTemplate]):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[DagFlowConfig]:
        return DagFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[DagFlowTemplate]:
        return DagFlowTemplate

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._job_func).bind(*args, **kwargs).arguments


class FuncFlowConfig(FlowConfig):
    def __init__(
        self,
        func_flow_func: Callable,
        *,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__()
        self._job_func = func_flow_func
        self._func_flow_func_signature = inspect.signature(self._job_func)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._job_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._func_flow_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._func_flow_func_signature.return_annotation


@callable_decorator_cls
class FuncFlowTemplate(CallableDecoratingJobTemplateMixin['FuncFlowTemplate'],
                       FuncFlowConfig,
                       FlowTemplate['FuncFlow']):
    def _apply_engine_decorator(self, flow: IsFuncFlow) -> IsFuncFlow:
        if self.engine is not None and isinstance(self.engine, IsFuncFlowRunnerEngine):
            return self.engine.func_flow_decorator(flow)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support function flows')

    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['FuncFlow']:
        return FuncFlow


class FuncFlow(FuncFlowConfig, Flow[FuncFlowConfig, FuncFlowTemplate]):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[FuncFlowConfig]:
        return FuncFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[FuncFlowTemplate]:
        return FuncFlowTemplate

    def _call_func(self, *args: object, **kwargs: object) -> Any:
        return self._job_func(*args, **kwargs)


# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
