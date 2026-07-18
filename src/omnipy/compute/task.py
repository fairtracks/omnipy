"""Task definitions for callable-backed compute jobs.

This module exposes Omnipy's public task-building API. Use ``TaskTemplate`` to
define a reusable task from a Python callable, and use ``Task`` for the bound
executable job instance created from that template.

Attributes:
    TaskTemplate: Decorator-style task template factory for wrapping a callable
        as a reusable Omnipy task.
"""

import os
from textwrap import dedent
from typing import Callable, cast, Generic, Iterable, Mapping, ParamSpec, TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.shared.enums.job import JobType, PersistOutputsOptions, RestoreOutputsOptions
from omnipy.shared.protocols.compute.job import IsTask, IsTaskTemplate
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.util.callable_decorator import callable_decorator_cls
from omnipy.util.helpers import is_package_editable

__all__ = [
    'Task',
    'TaskBase',
    'TaskTemplate',
    'TaskTemplateCore',
]

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')

if is_package_editable('omnipy'):  # Only define environment variables when developing
    os.environ['OMNIPY_MACRO_TASK_TEMPLATE_DESCRIPTION'] = dedent("""\
        A task template wraps a Python callable that performs a single unit of work
        as a task. Use this when the work can be expressed as a self-contained
        function call.""")


class TaskBase:
    """Provide a shared marker base for Omnipy task objects.

    ``TaskBase`` exists to give concrete task templates and executable task
    instances a common nominal base type. It does not add runtime behavior on
    its own, but it supports task-specific typing and internal mixin handling.
    """

    # TODO: Can this and FlowBase be replaced with IsTask/IsFlow, or similar?
    ...


class TaskTemplateCore(
        FuncArgJobBase[
            IsTaskTemplate[_CallP, _RetT],
            IsTask[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        JobTemplateMixin[
            IsTaskTemplate[_CallP, _RetT],
            IsTask[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        TaskBase,
        Generic[_CallP, _RetT],
):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Implement the core template behavior for tasks.
    #
    # {{TASK_TEMPLATE_DESCRIPTION}}
    #
    # Instances are normally produced through the [TaskTemplate][] decorator
    # factory rather than by direct construction.
    #
    """Implement the core template behavior for tasks.

    A task template wraps a Python callable that performs a single unit of work
    as a task. Use this when the work can be expressed as a self-contained
    function call.

    Instances are normally produced through the [TaskTemplate][] decorator
    factory rather than by direct construction.
    """
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsTask[_CallP, _RetT]]:
        """Return the executable task type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete job class that should be instantiated from a task template.

        Returns:
            type[IsTask[_CallP, _RetT]]: The executable [Task][] subclass
                associated with this template.
        """
        return cast(type[IsTask[_CallP, _RetT]], Task[_CallP, _RetT])


_TaskTemplateFactory = callable_decorator_cls(TaskTemplateCore)


def TaskTemplate(
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
) -> Callable[[Callable[_CallP, _RetT]], IsTaskTemplate[_CallP, _RetT]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Decorator-style factory for defining reusable callable-backed tasks.
    #
    # {{TASK_TEMPLATE_DESCRIPTION}}
    #
    # Args:
    #     {{JOB_TEMPLATE_SHARED_KWARG_DOCS}}
    # Returns:
    #     TaskTemplate: New TaskTemplate instance wrapping ``job_func``.
    """Decorator-style factory for defining reusable callable-backed tasks.

    A task template wraps a Python callable that performs a single unit of work
    as a task. Use this when the work can be expressed as a self-contained
    function call.

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
        TaskTemplate: New TaskTemplate instance wrapping ``job_func``."""
    ret = _TaskTemplateFactory(
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
    return cast(Callable[[Callable[_CallP, _RetT]], IsTaskTemplate[_CallP, _RetT]], ret)


class Task(JobMixin[IsTaskTemplate[_CallP, _RetT], IsTask[_CallP, _RetT], _CallP, _RetT],
           TaskBase,
           FuncArgJobBase[IsTaskTemplate[_CallP, _RetT], IsTask[_CallP, _RetT], _CallP, _RetT],
           Generic[_CallP, _RetT]):
    """Execute a single callable-backed Omnipy task.

    A ``Task`` is the runnable job object produced from a ``TaskTemplate``.
    When invoked, it delegates execution of the wrapped callable to the
    configured task runner engine.

    Use this type when one callable should be scheduled, configured, logged,
    and optionally persisted as a standalone compute step.

    Instances are typically produced by calling a ``TaskTemplate``.
    """
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        """Register the engine decorator for task execution.

        When a runner engine is bound to the task, this method asks that
        engine to wrap the task's callable with task-specific execution
        behavior.

        Args:
            self: Current task instance.
            engine: Engine candidate supplied during job setup.
        """
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask[_CallP, _RetT], self)
            engine.apply_job_decorator(
                JobType.TASK,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsTaskTemplate[_CallP, _RetT]]:
        """Return the template type used to revise this task.

        Revision operations use this hook to recover the decorator-backed task
        template class corresponding to an executable task instance.

        Returns:
            type[IsTaskTemplate[_CallP, _RetT]]: The [TaskTemplate][] class
                associated with this task.
        """
        return cast(type[IsTaskTemplate[_CallP, _RetT]], TaskTemplateCore)


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
