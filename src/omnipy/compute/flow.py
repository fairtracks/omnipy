"""Flow definitions for composing tasks and subflows.

This module exposes Omnipy's public flow types. Use ``LinearFlowTemplate`` for
sequential pipelines, ``DagFlowTemplate`` for dependency-driven directed
acyclic graphs, and ``FuncFlowTemplate`` for flows expressed as a single
coordinating callable.

Attributes:
    LinearFlowTemplate: Decorator-style template factory for sequential flows.
    DagFlowTemplate: Decorator-style template factory for directed acyclic
        graph flows.
    FuncFlowTemplate: Decorator-style template factory for callable-backed
        coordinating flows.
"""

from typing import Callable, cast, Concatenate, Generic, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.compute._joblist_job import ChildJobListArgJobBase
from omnipy.compute._mixins.flow_context import FlowContextJobMixin
from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import (HasChildJobListArgJobTemplateInit,
                                                 HasFuncArgJobTemplateInit,
                                                 IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFuncFlow,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate)
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
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
    """Marker base class for Omnipy flow objects."""

    ...


class LinearFlowTemplateCore(
        ChildJobListArgJobBase[
            IsLinearFlowTemplate[_CallP, _RetT],
            IsLinearFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        JobTemplateMixin[
            IsLinearFlowTemplate[_CallP, _RetT],
            IsLinearFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        FlowBase,
        Generic[_CallP, _RetT],
):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsLinearFlow[_CallP, _RetT]]:
        return cast(type[IsLinearFlow[_CallP, _RetT]], LinearFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def linear_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsLinearFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsLinearFlowTemplate[_CallP, _RetT]]]:
    """Wrap a linear-flow initializer as a callable decorator factory.

    Args:
        decorated_cls: Linear-flow template initializer to adapt.

    Returns:
        A decorator factory that converts a Python callable into a linear flow template.
    """
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                     IsLinearFlowTemplate[_CallP, _RetT]],
            decorated_cls))


def to_linear_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            LinearFlowTemplateCore[_CallP, _RetT]]
) -> HasChildJobListArgJobTemplateInit[IsLinearFlowTemplate[_CallP, _RetT], _CallP, _RetT]:
    return cast(
        HasChildJobListArgJobTemplateInit[IsLinearFlowTemplate[_CallP, _RetT], _CallP, _RetT],
        decorated_cls)


LinearFlowTemplate = linear_flow_template_as_callable_decorator(
    to_linear_flow_template_init_protocol(LinearFlowTemplateCore))
"""Decorator-style factory for defining sequential flows.

Use ``@LinearFlowTemplate(...)`` when a flow should execute tasks in a fixed,
step-by-step order.
"""


class LinearFlow(JobMixin[IsLinearFlowTemplate[_CallP, _RetT],
                          IsLinearFlow[_CallP, _RetT],
                          _CallP,
                          _RetT],
                 FlowBase,
                 ChildJobListArgJobBase[IsLinearFlowTemplate[_CallP, _RetT],
                                        IsLinearFlow[_CallP, _RetT],
                                        _CallP,
                                        _RetT],
                 Generic[_CallP, _RetT]):
    """Executable sequential flow.

    A ``LinearFlow`` runs its constituent tasks in declaration order, making
    each step wait for the previous one to finish. Use it for pipelines where
    every stage depends on the output or side effects of the stage before it.
    """

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsLinearFlow, self)
            engine.apply_job_decorator(
                JobType.LINEAR_FLOW,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsLinearFlowTemplate[_CallP, _RetT]]:
        return cast(type[IsLinearFlowTemplate[_CallP, _RetT]], LinearFlowTemplate)


class DagFlowTemplateCore(ChildJobListArgJobBase[IsDagFlowTemplate[_CallP, _RetT],
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
    """Wrap a DAG-flow initializer as a callable decorator factory.

    Args:
        decorated_cls: DAG-flow template initializer to adapt.

    Returns:
        A decorator factory that converts a Python callable into a DAG flow template.
    """
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP], IsDagFlowTemplate[_CallP,
                                                                                     _RetT]],
            decorated_cls))


def to_dag_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            DagFlowTemplateCore[_CallP, _RetT]]
) -> HasChildJobListArgJobTemplateInit[IsDagFlowTemplate[_CallP, _RetT], _CallP, _RetT]:
    return cast(HasChildJobListArgJobTemplateInit[IsDagFlowTemplate[_CallP, _RetT], _CallP, _RetT],
                decorated_cls)


DagFlowTemplate = dag_flow_template_as_callable_decorator(
    to_dag_flow_template_init_protocol(DagFlowTemplateCore))
"""Decorator-style factory for defining directed acyclic graph flows.

Use ``@DagFlowTemplate(...)`` when task dependencies form a DAG with possible
branching and joining, but no cycles.
"""


class DagFlow(
        JobMixin[IsDagFlowTemplate[_CallP, _RetT], IsDagFlow[_CallP, _RetT], _CallP, _RetT],
        FlowBase,
        ChildJobListArgJobBase[
            IsDagFlowTemplate[_CallP, _RetT],
            IsDagFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        Generic[_CallP, _RetT],
):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsDagFlow, self)
            engine.apply_job_decorator(
                JobType.DAG_FLOW,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

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
    """Core implementation for callable-backed flow templates.

    A function flow template wraps a Python callable that orchestrates work as
    a flow. Use this when the control flow is easiest to express directly in
    Python instead of as an explicit task list or dependency graph.
    """

    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsFuncFlow[_CallP, _RetT]]:
        return cast(type[IsFuncFlow[_CallP, _RetT]], FuncFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def func_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsFuncFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsFuncFlowTemplate[_CallP, _RetT]]]:
    """Wrap a function-flow initializer as a callable decorator factory.

    Args:
        decorated_cls: Function-flow template initializer to adapt.

    Returns:
        A decorator factory that converts a Python callable into a function flow template.
    """
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                     IsFuncFlowTemplate[_CallP, _RetT]],
            decorated_cls))


def to_func_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            FuncFlowTemplateCore[_CallP, _RetT]]
) -> HasFuncArgJobTemplateInit[IsFuncFlowTemplate[_CallP, _RetT], _CallP, _RetT]:
    """Cast a function-flow initializer to the shared init protocol.

    Args:
        decorated_cls: Function-flow template initializer to cast.

    Returns:
        The initializer typed as ``HasFuncArgJobTemplateInit``.
    """
    return cast(HasFuncArgJobTemplateInit[IsFuncFlowTemplate[_CallP, _RetT], _CallP, _RetT],
                decorated_cls)


FuncFlowTemplate = func_flow_template_as_callable_decorator(
    to_func_flow_template_init_protocol(FuncFlowTemplateCore))
"""Decorator-style factory for defining callable-backed coordinating flows.

Use ``@FuncFlowTemplate()`` when a Python callable should orchestrate the flow
imperatively.
"""


class FuncFlow(
        JobMixin[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        FlowBase,
        FuncArgJobBase[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        Generic[_CallP, _RetT],
):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsFuncFlow, self)
            engine.apply_job_decorator(
                JobType.FUNC_FLOW,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsFuncFlowTemplate[_CallP, _RetT]]:
        return cast(type[IsFuncFlowTemplate[_CallP, _RetT]], FuncFlowTemplate)


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
