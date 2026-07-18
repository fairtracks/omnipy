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

import inspect
import os
from textwrap import dedent
from typing import Callable, cast, ClassVar, Concatenate, Generic, Iterable, Mapping, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.compute._joblist_job import ChildJobListArgJobBase
from omnipy.compute._mixins.flow_context import FlowContextJobMixin
from omnipy.shared.enums.job import JobType, PersistOutputsOptions, RestoreOutputsOptions
from omnipy.shared.protocols.compute.job import (HasChildJobListArgJobTemplateInit,
                                                 IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFuncFlow,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate)
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.util.callable_decorator import callable_decorator_cls
from omnipy.util.helpers import is_package_editable

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

if is_package_editable('omnipy'):  # Only define environment variables when developing
    os.environ['OMNIPY_MACRO_FLOW_WRAP_INITIALIZER_DECORATOR_SUMMARY'] = dedent("""\
        Wrap a template initializer as a callable decorator factory.""")

    os.environ['OMNIPY_MACRO_FLOW_CAST_INIT_PROTOCOL_SUMMARY'] = dedent("""\
        Cast a template initializer to the shared init protocol.""")

    os.environ['OMNIPY_MACRO_FUNC_FLOW_TEMPLATE_DESCRIPTION'] = dedent("""\
        A function flow template wraps a Python callable that orchestrates
        work as a flow. Use this when the control flow is easiest to
        express directly in Python instead of as an explicit task list or
        dependency graph.""")


def _is_data_class_decorator_arg(arg: object) -> bool:
    """Identify dataset/model class arguments passed as flow child components."""
    has_dataset_interface = all(
        hasattr(arg, dataset_attr) for dataset_attr in ('get_type', 'to_data', 'from_data'))
    return inspect.isclass(arg) and (has_dataset_interface or hasattr(arg, 'full_type'))


class FlowBase:
    """Provide a shared marker base for Omnipy flow objects.

    ``FlowBase`` exists to give concrete flow templates and executable flow
    instances a common nominal base type. It does not define behavior on its
    own, but it makes flow-specific mixin registration and type-based checks
    possible within the compute subsystem.
    """

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
        """Return the executable flow type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete job class that should be instantiated from a linear flow
        template.

        Returns:
            type[IsLinearFlow[_CallP, _RetT]]: The executable ``LinearFlow``
                subclass associated with this template.
        """
        return cast(type[IsLinearFlow[_CallP, _RetT]], LinearFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def linear_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsLinearFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsLinearFlowTemplate[_CallP, _RetT]]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # {{FLOW_WRAP_INITIALIZER_DECORATOR_SUMMARY}}
    #
    # Args:
    #     decorated_cls: Linear-flow template initializer to adapt.
    #
    # Returns:
    #     A decorator factory that converts a Python callable into a linear flow template.
    #
    """Wrap a template initializer as a callable decorator factory.

    Args:
        decorated_cls: Linear-flow template initializer to adapt.

    Returns:
        A decorator factory that converts a Python callable into a linear flow template.
    """
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                     IsLinearFlowTemplate[_CallP, _RetT]],
            decorated_cls),
        single_callable_arg_is_decorator_arg=_is_data_class_decorator_arg)


def to_linear_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            LinearFlowTemplateCore[_CallP, _RetT]]
) -> HasChildJobListArgJobTemplateInit[IsLinearFlowTemplate[_CallP, _RetT], _CallP, _RetT]:
    """Cast a linear-flow template initializer to the shared init protocol.

    Args:
        decorated_cls: Linear-flow template initializer to cast.

    Returns:
        The initializer typed as ``HasChildJobListArgJobTemplateInit``.
    """
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
    """Execute a flow whose tasks run in declaration order.

    A ``LinearFlow`` runs its constituent tasks in declaration order, making
    each step wait for the previous one to finish. Use it for pipelines where
    every stage depends on the output or side effects of the stage before it.

    Instances are typically produced by calling a ``LinearFlowTemplate``
    rather than by constructing ``LinearFlow`` directly.
    """
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        """Register the engine decorator for linear-flow execution.

        When the flow already holds a runner engine, this method asks that
        engine to wrap the flow's call function with the engine-specific
        linear-flow execution behavior.

        Args:
            self: Current linear flow instance.
            engine: Engine candidate supplied during job setup.
        """
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
        """Return the template type used to revise this flow.

        Revision operations use this hook to recover the decorator-backed
        template class corresponding to an executable linear flow instance.

        Returns:
            type[IsLinearFlowTemplate[_CallP, _RetT]]: The ``LinearFlowTemplate``
                class associated with this flow.
        """
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
    _coerce_data_class_children_from_kwargs: ClassVar[bool] = True

    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsDagFlow[_CallP, _RetT]]:
        """Return the executable DAG flow type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete flow class to instantiate from a DAG flow template.

        Returns:
            type[IsDagFlow[_CallP, _RetT]]: The executable ``DagFlow`` subclass
                associated with this template.
        """
        return cast(type[IsDagFlow[_CallP, _RetT]], DagFlow[_CallP, _RetT])


# Needed for pyright and PyCharm
def dag_flow_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsDagFlowTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsDagFlowTemplate[_CallP, _RetT]]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # {{FLOW_WRAP_INITIALIZER_DECORATOR_SUMMARY}}
    #
    # Args:
    #     decorated_cls: DAG-flow template initializer to adapt.
    #
    # Returns:
    #     A decorator factory that converts a Python callable into a DAG flow template.
    #
    """Wrap a template initializer as a callable decorator factory.

    Args:
        decorated_cls: DAG-flow template initializer to adapt.

    Returns:
        A decorator factory that converts a Python callable into a DAG flow template.
    """
    return callable_decorator_cls(
        cast(
            Callable[Concatenate[Callable[_CallP, _RetT], _InitP], IsDagFlowTemplate[_CallP,
                                                                                     _RetT]],
            decorated_cls),
        single_callable_arg_is_decorator_arg=_is_data_class_decorator_arg)


def to_dag_flow_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            DagFlowTemplateCore[_CallP, _RetT]]
) -> HasChildJobListArgJobTemplateInit[IsDagFlowTemplate[_CallP, _RetT], _CallP, _RetT]:
    """Cast a DAG-flow template initializer to the shared init protocol.

    Args:
        decorated_cls: DAG-flow template initializer to cast.

    Returns:
        The initializer typed as ``HasChildJobListArgJobTemplateInit``.
    """
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
        """Register the engine decorator for DAG-flow execution.

        When a runner engine is bound to the flow, this method asks that
        engine to wrap the flow's call function with DAG-specific execution
        behavior.

        Args:
            self: Current DAG flow instance.
            engine: Engine candidate supplied during job setup.
        """
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
        """Return the template type used to revise this flow.

        Revision operations use this hook to recover the decorator-backed DAG
        flow template class corresponding to an executable DAG flow instance.

        Returns:
            type[IsDagFlowTemplate[_CallP, _RetT]]: The ``DagFlowTemplate``
                class associated with this flow.
        """
        return cast(type[IsDagFlowTemplate[_CallP, _RetT]], DagFlowTemplate)


class FuncFlowTemplateCore(
        FuncArgJobBase[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        JobTemplateMixin[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        FlowBase,
        Generic[_CallP, _RetT],
):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Implement the core template behavior for function flows.
    #
    # {{FUNC_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Instances are normally produced through the [FuncFlowTemplate][] decorator
    # factory rather than by direct construction.
    #
    """Implement the core template behavior for function flows.

    A function flow template wraps a Python callable that orchestrates
    work as a flow. Use this when the control flow is easiest to
    express directly in Python instead of as an explicit task list or
    dependency graph.

    Instances are normally produced through the [FuncFlowTemplate][] decorator
    factory rather than by direct construction.
    """
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsFuncFlow[_CallP, _RetT]]:
        """Return the executable function flow type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete flow class that should be instantiated from a function flow
        template.

        Returns:
            type[IsFuncFlow[_CallP, _RetT]]: The executable [FuncFlow][]
                subclass associated with this template.
        """
        return cast(type[IsFuncFlow[_CallP, _RetT]], FuncFlow[_CallP, _RetT])


_FuncFlowTemplateFactory = callable_decorator_cls(FuncFlowTemplateCore)


def FuncFlowTemplate(
    *,
    name: str | None = None,
    iterate_over_data_files: bool = False,
    output_dataset_param: str | None = None,
    output_dataset_cls: type[IsDataset] | None = None,
    auto_async: bool = True,
    result_key: str | None = None,
    fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
    param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
    restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
    **kwargs: object,
) -> Callable[[Callable[_CallP, _RetT]], IsFuncFlowTemplate[_CallP, _RetT]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Decorator-style factory for defining callable-backed coordinating flows.
    #
    # {{FUNC_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Args:
    #     {{JOB_TEMPLATE_SHARED_KWARG_DOCS}}
    # Returns:
    #     FuncFlowTemplate: New FuncFlowTemplate instance wrapping ``job_func``.
    """Decorator-style factory for defining callable-backed coordinating flows.

    A function flow template wraps a Python callable that orchestrates
    work as a flow. Use this when the control flow is easiest to
    express directly in Python instead of as an explicit task list or
    dependency graph.

    Args:
        name: Name of the job template. If not provided, the name of the
            wrapped callable is used.
        iterate_over_data_files: Whether dataset inputs should be
            processed item-wise. output_dataset_param: Optional name of
            an explicit output-dataset parameter.
        output_dataset_cls: Optional dataset class to use for iterated
            outputs.
        auto_async: Whether coroutine jobs at the outermost level (not
            in a flow context) should be automatically run in accordance
            with context (use existing event loop, if available,
            otherwise create temporary event loop and run coroutine
            until completion).)
        result_key: Optional key used to wrap the returned result in a
            dictionary. Especially useful in DAG flows to avoid name
            collisions.
        fixed_params: Fixed keyword-argument values for the job. May not
            target *args or **kwargs-style params.
        param_key_map: Mapping from external keyword names to callable
            parameter names. May not target *args or **kwargs-style
            params.
        persist_outputs: Per-job output-persistence preference.
        restore_outputs: Per-job output-restore preference.
        **kwargs: Additional constructor keyword overrides.
    Returns:
        FuncFlowTemplate: New FuncFlowTemplate instance wrapping ``job_func``."""
    ret = _FuncFlowTemplateFactory(
        name=name,
        iterate_over_data_files=iterate_over_data_files,
        output_dataset_param=output_dataset_param,
        output_dataset_cls=output_dataset_cls,
        auto_async=auto_async,
        result_key=result_key,
        fixed_params=fixed_params,
        param_key_map=param_key_map,
        persist_outputs=persist_outputs,
        restore_outputs=restore_outputs,
        **kwargs,
    )
    return cast(Callable[[Callable[_CallP, _RetT]], IsFuncFlowTemplate[_CallP, _RetT]], ret)


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
        """Register the engine decorator for callable-backed flow execution.

        When a runner engine is bound to the flow, this method asks that
        engine to wrap the coordinating callable with function-flow execution
        behavior.

        Args:
            self: Current function flow instance.
            engine: Engine candidate supplied during job setup.
        """
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
        """Return the template type used to revise this flow.

        Revision operations use this hook to recover the decorator-backed
        function flow template class corresponding to an executable function
        flow instance.

        Returns:
            type[IsFuncFlowTemplate[_CallP, _RetT]]: The [FuncFlowTemplate][]
                class associated with this flow.
        """
        return cast(type[IsFuncFlowTemplate[_CallP, _RetT]], FuncFlowTemplateCore)


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
