from typing import cast, Type

from omnipy.api.protocols.private.compute.job import (IsFuncArgJobTemplateCallable,
                                                      IsJob,
                                                      IsJobTemplate,
                                                      IsTaskTemplateArgsJobTemplateCallable)
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.compute import (IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFuncFlow,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)
from omnipy.api.protocols.public.engine import (IsDagFlowRunnerEngine,
                                                IsFuncFlowRunnerEngine,
                                                IsLinearFlowRunnerEngine)
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import JobMixin, JobTemplateMixin
from omnipy.compute.mixins.flow_context import FlowContextJobMixin
from omnipy.compute.tasklist_job import TaskTemplateArgsJobBase
from omnipy.util.callable_decorator import callable_decorator_cls


class FlowBase:
    ...


def linear_flow_template_callable_decorator_cls(
    cls: Type['LinearFlowTemplate']
) -> IsTaskTemplateArgsJobTemplateCallable[IsTaskTemplate, IsLinearFlowTemplate]:
    return cast(IsTaskTemplateArgsJobTemplateCallable[IsTaskTemplate, IsLinearFlowTemplate],
                callable_decorator_cls(cls))


@linear_flow_template_callable_decorator_cls
class LinearFlowTemplate(JobTemplateMixin, FlowBase, TaskTemplateArgsJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob]:
        return cast(Type[IsLinearFlow], LinearFlow)


class LinearFlow(JobMixin, FlowBase, TaskTemplateArgsJobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsLinearFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsLinearFlow, self)
            engine.apply_linear_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return cast(Type[IsLinearFlowTemplate], LinearFlowTemplate)


def dag_flow_template_callable_decorator_cls(
    cls: Type['DagFlowTemplate']
) -> IsTaskTemplateArgsJobTemplateCallable[IsTaskTemplate, IsDagFlowTemplate]:
    return cast(IsTaskTemplateArgsJobTemplateCallable[IsTaskTemplate, IsDagFlowTemplate],
                callable_decorator_cls(cls))


@dag_flow_template_callable_decorator_cls
class DagFlowTemplate(JobTemplateMixin, FlowBase, TaskTemplateArgsJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob]:
        return cast(Type[IsDagFlow], DagFlow)


class DagFlow(JobMixin, FlowBase, TaskTemplateArgsJobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsDagFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsDagFlow, self)
            engine.apply_dag_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return cast(Type[IsDagFlowTemplate], DagFlowTemplate)


def func_flow_template_callable_decorator_cls(
        cls: Type['FuncFlowTemplate']) -> IsFuncArgJobTemplateCallable[IsFuncFlowTemplate]:
    return cast(IsFuncArgJobTemplateCallable[IsFuncFlowTemplate], callable_decorator_cls(cls))


@func_flow_template_callable_decorator_cls
class FuncFlowTemplate(JobTemplateMixin, FlowBase, FuncArgJobBase):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob]:
        return cast(Type[IsFuncFlow], FuncFlow)


class FuncFlow(JobMixin, FlowBase, FuncArgJobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsFuncFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsFuncFlow, self)
            engine.apply_func_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return cast(Type[IsFuncFlowTemplate], FuncFlowTemplate)


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
