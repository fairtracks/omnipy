from typing import Callable, cast, Concatenate, Generic, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.compute._mixins.flow_context import FlowContextJobMixin
from omnipy.compute._tasklist_job import TaskTemplateArgsJobBase
from omnipy.shared.protocols.compute._job import (HasFuncArgJobTemplateInit,
                                                  HasTaskTemplateArgsJobTemplateInit)
from omnipy.shared.protocols.compute.job import (IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFuncFlow,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import (IsDagFlowRunnerEngine,
                                                       IsFuncFlowRunnerEngine,
                                                       IsLinearFlowRunnerEngine)
from omnipy.util.callable_decorator import callable_decorator_cls

__all__ = [
    'DagFlow',
    'DagFlowTemplate',
    'DagFlowTemplateCore',
    'FlowBase',
    'FuncFlow',
    'FuncFlowTemplate',
    'FuncFlowTemplateCore',
    'LinearFlow',
    'LinearFlowTemplate',
    'LinearFlowTemplateCore',
]

_InitP = ParamSpec('_InitP')
_CallP = ParamSpec('_CallP')
_CallableT = TypeVar('_CallableT')
_RetT = TypeVar('_RetT')


class FlowBase:
    ...


class LinearFlowTemplateCore(TaskTemplateArgsJobBase[IsLinearFlowTemplate[_CallP, _RetT],
                                                     IsLinearFlow[_CallP, _RetT],
                                                     _CallP,
                                                     _RetT],
                             JobTemplateMixin[IsLinearFlowTemplate[_CallP, _RetT],
                                              IsLinearFlow[_CallP, _RetT],
                                              _CallP,
                                              _RetT],
                             FlowBase,
                             Generic[_CallP, _RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsLinearFlow[_CallP, _RetT]]:
        return cast(type[IsLinearFlow[_CallP, _RetT]], LinearFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def linear_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsLinearFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsLinearFlowTemplate[_CallP, _RetT]]]:
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                     IsLinearFlowTemplate[_CallP, _RetT]],
            decorated_cls))


def to_linear_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            LinearFlowTemplateCore[_CallP, _RetT]]
) -> HasTaskTemplateArgsJobTemplateInit[
        IsLinearFlowTemplate[_CallP, _RetT], IsTaskTemplate, _CallP, _RetT]:
    return cast(
        HasTaskTemplateArgsJobTemplateInit[IsLinearFlowTemplate[_CallP, _RetT],
                                           IsTaskTemplate,
                                           _CallP,
                                           _RetT],
        decorated_cls)


LinearFlowTemplate = linear_flow_template_as_callable_decorator(
    to_linear_flow_template_init_protocol(LinearFlowTemplateCore))


class LinearFlow(JobMixin[IsLinearFlowTemplate[_CallP, _RetT],
                          IsLinearFlow[_CallP, _RetT],
                          _CallP,
                          _RetT],
                 FlowBase,
                 TaskTemplateArgsJobBase[IsLinearFlowTemplate[_CallP, _RetT],
                                         IsLinearFlow[_CallP, _RetT],
                                         _CallP,
                                         _RetT],
                 Generic[_CallP, _RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsLinearFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsLinearFlow, self)
            engine.apply_linear_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsLinearFlowTemplate[_CallP, _RetT]]:
        return cast(type[IsLinearFlowTemplate[_CallP, _RetT]], LinearFlowTemplate)


class DagFlowTemplateCore(TaskTemplateArgsJobBase[IsDagFlowTemplate[_CallP, _RetT],
                                                  IsDagFlow[_CallP, _RetT],
                                                  _CallP,
                                                  _RetT],
                          JobTemplateMixin[IsDagFlowTemplate[_CallP, _RetT],
                                           IsDagFlow[_CallP, _RetT],
                                           _CallP,
                                           _RetT],
                          FlowBase,
                          Generic[_CallP, _RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsDagFlow[_CallP, _RetT]]:
        return cast(type[IsDagFlow[_CallP, _RetT]], DagFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def dag_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsDagFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsDagFlowTemplate[_CallP, _RetT]]]:
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP], IsDagFlowTemplate[_CallP,
                                                                                     _RetT]],
            decorated_cls))


def to_dag_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            DagFlowTemplateCore[_CallP, _RetT]]
) -> HasTaskTemplateArgsJobTemplateInit[
        IsDagFlowTemplate[_CallP, _RetT], IsTaskTemplate, _CallP, _RetT]:
    return cast(
        HasTaskTemplateArgsJobTemplateInit[IsDagFlowTemplate[_CallP, _RetT],
                                           IsTaskTemplate,
                                           _CallP,
                                           _RetT],
        decorated_cls)


DagFlowTemplate = dag_flow_template_as_callable_decorator(
    to_dag_flow_template_init_protocol(DagFlowTemplateCore))


class DagFlow(JobMixin[IsDagFlowTemplate[_CallP, _RetT], IsDagFlow[_CallP, _RetT], _CallP, _RetT],
              FlowBase,
              TaskTemplateArgsJobBase[IsDagFlowTemplate[_CallP, _RetT],
                                      IsDagFlow[_CallP, _RetT],
                                      _CallP,
                                      _RetT],
              Generic[_CallP, _RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsDagFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsDagFlow, self)
            engine.apply_dag_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsDagFlowTemplate[_CallP, _RetT]]:
        return cast(type[IsDagFlowTemplate[_CallP, _RetT]], DagFlowTemplate)


class FuncFlowTemplateCore(FuncArgJobBase[IsFuncFlowTemplate[_CallP, _RetT],
                                          IsFuncFlow[_CallP, _RetT],
                                          _CallP,
                                          _RetT],
                           JobTemplateMixin[IsFuncFlowTemplate[_CallP, _RetT],
                                            IsFuncFlow[_CallP, _RetT],
                                            _CallP,
                                            _RetT],
                           FlowBase,
                           Generic[_CallP, _RetT]):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsFuncFlow[_CallP, _RetT]]:
        return cast(type[IsFuncFlow[_CallP, _RetT]], FuncFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def func_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsFuncFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsFuncFlowTemplate[_CallP, _RetT]]]:
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                     IsFuncFlowTemplate[_CallP, _RetT]],
            decorated_cls))


def to_func_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            FuncFlowTemplateCore[_CallP, _RetT]]
) -> HasFuncArgJobTemplateInit[IsFuncFlowTemplate[_CallP, _RetT], _CallP, _RetT]:
    return cast(HasFuncArgJobTemplateInit[IsFuncFlowTemplate[_CallP, _RetT], _CallP, _RetT],
                decorated_cls)


FuncFlowTemplate = func_flow_template_as_callable_decorator(
    to_func_flow_template_init_protocol(FuncFlowTemplateCore))


class FuncFlow(JobMixin[IsFuncFlowTemplate[_CallP, _RetT], IsFuncFlow[_CallP, _RetT], _CallP,
                        _RetT],
               FlowBase,
               FuncArgJobBase[IsFuncFlowTemplate[_CallP, _RetT],
                              IsFuncFlow[_CallP, _RetT],
                              _CallP,
                              _RetT],
               Generic[_CallP, _RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsFuncFlowRunnerEngine, self.engine)
            self_with_mixins = cast(IsFuncFlow, self)
            engine.apply_func_flow_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsFuncFlowTemplate[_CallP, _RetT]]:
        return cast(type[IsFuncFlowTemplate[_CallP, _RetT]], FuncFlowTemplate)


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
