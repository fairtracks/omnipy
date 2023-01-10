from abc import ABC, abstractmethod
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

from unifair.compute.func_job import FuncJob, FuncJobConfig, FuncJobTemplate
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
from unifair.util.helpers import remove_none_vals
from unifair.util.mixin import DynamicMixinAcceptor

FlowT = TypeVar('FlowT', bound='Flow', covariant=True)
FlowConfigT = TypeVar('FlowConfigT', bound='FlowConfig', covariant=True)
FlowTemplateT = TypeVar('FlowTemplateT', bound='FlowTemplate', covariant=True)


class FlowConfig(FuncJobConfig):
    ...


class FlowTemplate(FuncJobTemplate[FlowT], Generic[FlowT], ABC):
    ...


class Flow(FuncJob[FlowConfigT, FlowTemplateT], Generic[FlowConfigT, FlowTemplateT], ABC):
    ...


class TaskTemplatesFlowConfig(FlowConfig):
    def __init__(
        self,
        job_func: Callable,
        *task_templates: IsTaskTemplate,
        name: Optional[str] = None,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
        result_key: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            job_func,
            **remove_none_vals(
                name=name,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                **kwargs,
            ))

        self._task_templates: Tuple[IsTaskTemplate, ...] = task_templates

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._job_func, *self._task_templates

    @property
    def task_templates(self) -> Tuple[IsTaskTemplate, ...]:
        return self._task_templates

    def refine(self,
               *task_templates: IsTaskTemplate,
               update: bool = True,
               name: Optional[str] = None,
               fixed_params: Optional[Mapping[str, object]] = None,
               param_key_map: Optional[Mapping[str, str]] = None,
               result_key: Optional[str] = None,
               **kwargs: Any) -> 'DagFlowTemplate':

        args = tuple([self._job_func] + list(*task_templates)) if task_templates else ()

        return super().refine(
            *args,
            update=update,
            **remove_none_vals(
                name=name,
                fixed_params=fixed_params,
                param_key_map=param_key_map,
                result_key=result_key,
                **kwargs,
            ))


class TaskTemplatesFlowTemplate(TaskTemplatesFlowConfig, FlowTemplate[FlowT], Generic[FlowT], ABC):
    ...


class TaskTemplatesFlow(TaskTemplatesFlowConfig,
                        Flow[FlowConfigT, FlowTemplateT],
                        Generic[FlowConfigT, FlowTemplateT],
                        ABC):
    ...


class LinearFlowConfig(TaskTemplatesFlowConfig):
    ...


@callable_decorator_cls
class LinearFlowTemplate(CallableDecoratingJobTemplateMixin['LinearFlowTemplate'],
                         LinearFlowConfig,
                         TaskTemplatesFlowTemplate['LinearFlow']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['LinearFlow']:
        return LinearFlow

    def _apply_engine_decorator(self, flow: IsLinearFlow) -> IsLinearFlow:
        if self.engine is not None and isinstance(self.engine, IsLinearFlowRunnerEngine):
            return self.engine.linear_flow_decorator(flow)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support linear flows')


class LinearFlow(LinearFlowConfig, TaskTemplatesFlow[LinearFlowConfig, LinearFlowTemplate]):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[LinearFlowConfig]:
        return LinearFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[LinearFlowTemplate]:
        return LinearFlowTemplate


class DagFlowConfig(TaskTemplatesFlowConfig):
    ...


@callable_decorator_cls
class DagFlowTemplate(CallableDecoratingJobTemplateMixin['DagFlowTemplate'],
                      DagFlowConfig,
                      TaskTemplatesFlowTemplate['DagFlow']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['DagFlow']:
        return DagFlow

    def _apply_engine_decorator(self, job: IsDagFlow) -> IsDagFlow:
        if self.engine is not None and isinstance(self.engine, IsDagFlowRunnerEngine):
            return self.engine.dag_flow_decorator(job)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')


class DagFlow(DagFlowConfig, TaskTemplatesFlow[DagFlowConfig, DagFlowTemplate]):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[DagFlowConfig]:
        return DagFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[DagFlowTemplate]:
        return DagFlowTemplate


class FuncFlowConfig(FlowConfig):
    ...


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


# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
