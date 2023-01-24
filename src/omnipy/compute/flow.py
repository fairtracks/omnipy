from typing import cast, Type

from omnipy.api.protocols import (IsDagFlowRunnerEngine,
                                  IsFuncFlowRunnerEngine,
                                  IsFuncJobTemplateCallable,
                                  IsLinearFlowRunnerEngine,
                                  IsTaskTemplatesFlowTemplateCallable)
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import Job, JobTemplate
from omnipy.compute.mixins.flow_context import FlowContextJobMixin
from omnipy.compute.tasklist_job import TaskTemplateArgsJobBase
from omnipy.util.callable_decorator_cls import callable_decorator_cls


class FlowBase:
    ...


# TODO: Reimplement typing of flows and task to harmonize with new structure
def linear_flow_template_callable_decorator_cls(
        cls: Type['LinearFlowTemplate']
) -> IsTaskTemplatesFlowTemplateCallable['LinearFlowTemplate']:
    return cast(IsTaskTemplatesFlowTemplateCallable['LinearFlowTemplate'],
                callable_decorator_cls(cls))


@linear_flow_template_callable_decorator_cls
class LinearFlowTemplate(JobTemplate, FlowBase, TaskTemplateArgsJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['LinearFlow']:
        return LinearFlow


class LinearFlow(Job, FlowBase, TaskTemplateArgsJobBase):
    def _apply_engine_decorator(self, engine: IsLinearFlowRunnerEngine) -> None:
        self._check_engine(IsLinearFlowRunnerEngine)
        engine = cast(IsLinearFlowRunnerEngine, self.engine)
        engine.apply_linear_flow_decorator(self, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[LinearFlowTemplate]:
        return LinearFlowTemplate


def dag_flow_template_callable_decorator_cls(
        cls: Type['DagFlowTemplate']) -> IsTaskTemplatesFlowTemplateCallable['DagFlowTemplate']:
    return cast(IsTaskTemplatesFlowTemplateCallable['DagFlowTemplate'], callable_decorator_cls(cls))


@dag_flow_template_callable_decorator_cls
class DagFlowTemplate(JobTemplate, FlowBase, TaskTemplateArgsJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['DagFlow']:
        return DagFlow


class DagFlow(Job, FlowBase, TaskTemplateArgsJobBase):
    def _apply_engine_decorator(self, engine: IsDagFlowRunnerEngine) -> None:
        self._check_engine(IsDagFlowRunnerEngine)
        engine = cast(IsDagFlowRunnerEngine, self.engine)
        engine.apply_dag_flow_decorator(self, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[DagFlowTemplate]:
        return DagFlowTemplate


def func_flow_template_callable_decorator_cls(
        cls: Type['FuncFlowTemplate']) -> IsFuncJobTemplateCallable['FuncFlowTemplate']:
    return cast(IsFuncJobTemplateCallable['FuncFlowTemplate'], callable_decorator_cls(cls))


@func_flow_template_callable_decorator_cls
class FuncFlowTemplate(JobTemplate, FlowBase, FuncArgJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type['FuncFlow']:
        return FuncFlow


class FuncFlow(Job, FlowBase, FuncArgJobBase):
    def _apply_engine_decorator(self, engine: IsFuncFlowRunnerEngine) -> None:
        self._check_engine(IsFuncFlowRunnerEngine)
        engine = cast(IsFuncFlowRunnerEngine, self.engine)
        engine.apply_func_flow_decorator(self, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[FuncFlowTemplate]:
        return FuncFlowTemplate


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
