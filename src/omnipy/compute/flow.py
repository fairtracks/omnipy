from typing import Callable, cast, Concatenate, Generic, ParamSpec

from typing_extensions import TypeVar

from omnipy.api.protocols.private.compute.job import (HasFuncArgJobTemplateInit,
                                                      HasTaskTemplateArgsJobTemplateInit)
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

InitP = ParamSpec('InitP')
CallP = ParamSpec('CallP')
CallableT = TypeVar('CallableT')
RetT = TypeVar('RetT')


class FlowBase:
    ...


class LinearFlowTemplateCore(TaskTemplateArgsJobBase[IsLinearFlowTemplate[CallP, RetT],
                                                     IsLinearFlow[CallP, RetT],
                                                     CallP,
                                                     RetT],
                             JobTemplateMixin[IsLinearFlowTemplate[CallP, RetT],
                                              IsLinearFlow[CallP, RetT],
                                              CallP,
                                              RetT],
                             FlowBase,
                             Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsLinearFlow[CallP, RetT]]:
        return cast(type[IsLinearFlow[CallP, RetT]], LinearFlow[CallP, RetT])


# Needed for pyright and PyCharm
def linear_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[CallableT, InitP], IsLinearFlowTemplate]) -> \
        Callable[InitP, Callable[[Callable[CallP, RetT]], IsLinearFlowTemplate[CallP, RetT]]]:
    return callable_decorator_cls(
        cast(Callable[Concatenate[Callable[CallP, RetT], InitP], IsLinearFlowTemplate[CallP, RetT]],
             decorated_cls))


def to_linear_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[CallP, RetT], InitP],
                            LinearFlowTemplateCore[CallP, RetT]]
) -> HasTaskTemplateArgsJobTemplateInit[
        IsLinearFlowTemplate[CallP, RetT], IsTaskTemplate, CallP, RetT]:
    return cast(
        HasTaskTemplateArgsJobTemplateInit[IsLinearFlowTemplate[CallP, RetT],
                                           IsTaskTemplate,
                                           CallP,
                                           RetT],
        decorated_cls)


LinearFlowTemplate = linear_flow_template_as_callable_decorator(
    to_linear_flow_template_init_protocol(LinearFlowTemplateCore))


class LinearFlow(JobMixin[IsLinearFlowTemplate[CallP, RetT], IsLinearFlow[CallP, RetT], CallP,
                          RetT],
                 FlowBase,
                 TaskTemplateArgsJobBase[IsLinearFlowTemplate[CallP, RetT],
                                         IsLinearFlow[CallP, RetT],
                                         CallP,
                                         RetT],
                 Generic[CallP, RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsLinearFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsLinearFlow, self)
            engine.apply_linear_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsLinearFlowTemplate[CallP, RetT]]:
        return cast(type[IsLinearFlowTemplate[CallP, RetT]], LinearFlowTemplate)


class DagFlowTemplateCore(TaskTemplateArgsJobBase[IsDagFlowTemplate[CallP, RetT],
                                                  IsDagFlow[CallP, RetT],
                                                  CallP,
                                                  RetT],
                          JobTemplateMixin[IsDagFlowTemplate[CallP, RetT],
                                           IsDagFlow[CallP, RetT],
                                           CallP,
                                           RetT],
                          FlowBase,
                          Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsDagFlow[CallP, RetT]]:
        return cast(type[IsDagFlow[CallP, RetT]], DagFlow[CallP, RetT])


# Needed for pyright and PyCharm
def dag_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[CallableT, InitP], IsDagFlowTemplate]) -> \
        Callable[InitP, Callable[[Callable[CallP, RetT]], IsDagFlowTemplate[CallP, RetT]]]:
    return callable_decorator_cls(
        cast(Callable[Concatenate[Callable[CallP, RetT], InitP], IsDagFlowTemplate[CallP, RetT]],
             decorated_cls))


def to_dag_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[CallP, RetT], InitP],
                            DagFlowTemplateCore[CallP, RetT]]
) -> HasTaskTemplateArgsJobTemplateInit[IsDagFlowTemplate[CallP, RetT], IsTaskTemplate, CallP,
                                        RetT]:
    return cast(
        HasTaskTemplateArgsJobTemplateInit[IsDagFlowTemplate[CallP, RetT],
                                           IsTaskTemplate,
                                           CallP,
                                           RetT],
        decorated_cls)


DagFlowTemplate = dag_flow_template_as_callable_decorator(
    to_dag_flow_template_init_protocol(DagFlowTemplateCore))


class DagFlow(JobMixin[IsDagFlowTemplate[CallP, RetT], IsDagFlow[CallP, RetT], CallP, RetT],
              FlowBase,
              TaskTemplateArgsJobBase[IsDagFlowTemplate[CallP, RetT],
                                      IsDagFlow[CallP, RetT],
                                      CallP,
                                      RetT],
              Generic[CallP, RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsDagFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsDagFlow, self)
            engine.apply_dag_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsDagFlowTemplate[CallP, RetT]]:
        return cast(type[IsDagFlowTemplate[CallP, RetT]], DagFlowTemplate)


class FuncFlowTemplateCore(FuncArgJobBase[IsFuncFlowTemplate[CallP, RetT],
                                          IsFuncFlow[CallP, RetT],
                                          CallP,
                                          RetT],
                           JobTemplateMixin[IsFuncFlowTemplate[CallP, RetT],
                                            IsFuncFlow[CallP, RetT],
                                            CallP,
                                            RetT],
                           FlowBase,
                           Generic[CallP, RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsFuncFlow[CallP, RetT]]:
        return cast(type[IsFuncFlow[CallP, RetT]], FuncFlow[CallP, RetT])


# Needed for pyright and PyCharm
def func_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[CallableT, InitP], IsFuncFlowTemplate]) -> \
        Callable[InitP, Callable[[Callable[CallP, RetT]], IsFuncFlowTemplate[CallP, RetT]]]:
    return callable_decorator_cls(
        cast(Callable[Concatenate[Callable[CallP, RetT], InitP], IsFuncFlowTemplate[CallP, RetT]],
             decorated_cls))


def to_func_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[CallP, RetT], InitP],
                            FuncFlowTemplateCore[CallP, RetT]]
) -> HasFuncArgJobTemplateInit[IsFuncFlowTemplate[CallP, RetT], CallP, RetT]:
    return cast(HasFuncArgJobTemplateInit[IsFuncFlowTemplate[CallP, RetT], CallP, RetT],
                decorated_cls)


FuncFlowTemplate = func_flow_template_as_callable_decorator(
    to_func_flow_template_init_protocol(FuncFlowTemplateCore))


class FuncFlow(JobMixin[IsFuncFlowTemplate[CallP, RetT], IsFuncFlow[CallP, RetT], CallP, RetT],
               FlowBase,
               FuncArgJobBase[IsFuncFlowTemplate[CallP, RetT], IsFuncFlow[CallP, RetT], CallP,
                              RetT],
               Generic[CallP, RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsFuncFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsFuncFlow, self)
            engine.apply_func_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsFuncFlowTemplate[CallP, RetT]]:
        return cast(type[IsFuncFlowTemplate[CallP, RetT]], FuncFlowTemplate)


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
