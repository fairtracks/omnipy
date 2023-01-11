from typing import cast, Type

from omnipy.compute.job import CallableDecoratingJobTemplateMixin
from omnipy.compute.job_types import IsFuncJobTemplateCallable, IsTaskTemplatesFlowTemplateCallable
from omnipy.compute.private.flow import (Flow,
                                         FlowBase,
                                         FlowTemplate,
                                         TaskTemplatesFlow,
                                         TaskTemplatesFlowBase,
                                         TaskTemplatesFlowTemplate)
from omnipy.engine.protocols import (IsDagFlow,
                                     IsDagFlowRunnerEngine,
                                     IsFuncFlow,
                                     IsFuncFlowRunnerEngine,
                                     IsLinearFlow,
                                     IsLinearFlowRunnerEngine)
from omnipy.util.callable_decorator_cls import callable_decorator_cls


class LinearFlowBase(TaskTemplatesFlowBase):
    ...


def linear_flow_template_callable_decorator_cls(
        cls: Type['LinearFlowTemplate']
) -> IsTaskTemplatesFlowTemplateCallable['LinearFlowTemplate']:
    return cast(IsTaskTemplatesFlowTemplateCallable['LinearFlowTemplate'],
                callable_decorator_cls(cls))


@linear_flow_template_callable_decorator_cls
class LinearFlowTemplate(CallableDecoratingJobTemplateMixin,
                         LinearFlowBase,
                         TaskTemplatesFlowTemplate['LinearFlow']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['LinearFlow']:
        return LinearFlow

    def _apply_engine_decorator(self, flow: IsLinearFlow) -> IsLinearFlow:
        if self.engine is not None and isinstance(self.engine, IsLinearFlowRunnerEngine):
            return self.engine.linear_flow_decorator(flow)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support linear flows')


class LinearFlow(LinearFlowBase, TaskTemplatesFlow[LinearFlowBase, LinearFlowTemplate]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[LinearFlowBase]:
        return LinearFlowBase

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[LinearFlowTemplate]:
        return LinearFlowTemplate


class DagFlowBase(TaskTemplatesFlowBase):
    ...


def dag_flow_template_callable_decorator_cls(
        cls: Type['DagFlowTemplate']) -> IsTaskTemplatesFlowTemplateCallable['DagFlowTemplate']:
    return cast(IsTaskTemplatesFlowTemplateCallable['DagFlowTemplate'], callable_decorator_cls(cls))


@dag_flow_template_callable_decorator_cls
class DagFlowTemplate(CallableDecoratingJobTemplateMixin,
                      DagFlowBase,
                      TaskTemplatesFlowTemplate['DagFlow']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['DagFlow']:
        return DagFlow

    def _apply_engine_decorator(self, job: IsDagFlow) -> IsDagFlow:
        if self.engine is not None and isinstance(self.engine, IsDagFlowRunnerEngine):
            return self.engine.dag_flow_decorator(job)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support DAG flows')


class DagFlow(DagFlowBase, TaskTemplatesFlow[DagFlowBase, DagFlowTemplate]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[DagFlowBase]:
        return DagFlowBase

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[DagFlowTemplate]:
        return DagFlowTemplate


class FuncFlowBase(FlowBase):
    ...


def func_flow_template_callable_decorator_cls(
        cls: Type['FuncFlowTemplate']) -> IsFuncJobTemplateCallable['FuncFlowTemplate']:
    return cast(IsFuncJobTemplateCallable['FuncFlowTemplate'], callable_decorator_cls(cls))


@func_flow_template_callable_decorator_cls
class FuncFlowTemplate(CallableDecoratingJobTemplateMixin, FuncFlowBase, FlowTemplate['FuncFlow']):
    def _apply_engine_decorator(self, flow: IsFuncFlow) -> IsFuncFlow:
        if self.engine is not None and isinstance(self.engine, IsFuncFlowRunnerEngine):
            return self.engine.func_flow_decorator(flow)
        else:
            raise RuntimeError(f'Engine "{self.engine}" does not support function flows')

    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['FuncFlow']:
        return FuncFlow


class FuncFlow(FuncFlowBase, Flow[FuncFlowBase, FuncFlowTemplate]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[FuncFlowBase]:
        return FuncFlowBase

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[FuncFlowTemplate]:
        return FuncFlowTemplate


# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
