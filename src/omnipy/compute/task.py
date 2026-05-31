"""Task definitions for callable-backed compute jobs.

This module exposes Omnipy's public task-building API. Use ``TaskTemplate`` to
define a reusable task from a Python callable, and use ``Task`` for the bound
executable job instance created from that template.

Attributes:
    TaskTemplate: Decorator-style task template factory for wrapping a callable
        as a reusable Omnipy task.
"""

from typing import Callable, cast, Generic, ParamSpec, TypeVar

from typing_extensions import Concatenate

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import HasFuncArgJobTemplateInit, IsTask, IsTaskTemplate
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.util.callable_decorator import callable_decorator_cls

__all__ = [
    'Task',
    'TaskBase',
    'TaskTemplate',
    'TaskTemplateCore',
]

_InitP = ParamSpec('_InitP')
_CallP = ParamSpec('_CallP')
_CallableT = TypeVar('_CallableT')
_RetT = TypeVar('_RetT')


class TaskBase:
    """Marker base class for Omnipy task objects."""

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
    """"""
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsTask[_CallP, _RetT]]:
        return cast(type[IsTask[_CallP, _RetT]], Task[_CallP, _RetT])


# Needed for pyright and PyCharm
def task_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsTaskTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsTaskTemplate[_CallP, _RetT]]]:
    """Wrap a task-template initializer as a callable decorator factory.

    Args:
        decorated_cls: Task-template initializer to adapt.

    Returns:
        A decorator factory that converts a Python callable into a task template.
    """
    return callable_decorator_cls(
        cast(Callable[Concatenate[Callable[_CallP, _RetT], _InitP], IsTaskTemplate[_CallP, _RetT]],
             decorated_cls))


def to_task_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            TaskTemplateCore[_CallP, _RetT]]
) -> HasFuncArgJobTemplateInit[IsTaskTemplate[_CallP, _RetT], _CallP, _RetT]:
    """Cast a task-template initializer to the shared init protocol.

    Args:
        decorated_cls: Task-template initializer to cast.

    Returns:
        The initializer typed as ``HasFuncArgJobTemplateInit``.
    """
    return cast(HasFuncArgJobTemplateInit[IsTaskTemplate[_CallP, _RetT], _CallP, _RetT],
                decorated_cls)


TaskTemplate = task_template_as_callable_decorator(to_task_template_init_protocol(TaskTemplateCore))
"""Decorator-style factory for defining reusable callable-backed tasks.

Use ``@TaskTemplate()`` on a Python callable to create a reusable task
template. Calling the resulting template produces executable ``Task``
instances that run as single Omnipy compute steps.
"""

# Only works with mypy, not pyright or PyCharm
#
# TaskTemplate = callable_decorator_cls(to_task_template_init_protocol(TaskTemplateCore))


class Task(JobMixin[IsTaskTemplate[_CallP, _RetT], IsTask[_CallP, _RetT], _CallP, _RetT],
           TaskBase,
           FuncArgJobBase[IsTaskTemplate[_CallP, _RetT], IsTask[_CallP, _RetT], _CallP, _RetT],
           Generic[_CallP, _RetT]):
    """Executable callable-backed task.

    A ``Task`` is the runnable job object produced from a ``TaskTemplate``.
    When invoked, it delegates execution of the wrapped callable to the
    configured task runner engine.

    Use this type when one callable should be scheduled, configured, logged,
    and optionally persisted as a standalone compute step.
    """

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
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
        return cast(type[IsTaskTemplate[_CallP, _RetT]], TaskTemplate)


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
