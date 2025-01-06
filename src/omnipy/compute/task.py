from typing import Callable, cast, Generic, ParamSpec, TypeVar

from typing_extensions import Concatenate

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.shared.protocols.compute._job import HasFuncArgJobTemplateInit
from omnipy.shared.protocols.compute.job import IsTask, IsTaskTemplate
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsTaskRunnerEngine
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
    # TODO: Can this and FlowBase be replaced with IsTask/IsFlow, or similar?
    ...


class TaskTemplateCore(FuncArgJobBase[IsTaskTemplate[_CallP, _RetT],
                                      IsTask[_CallP, _RetT],
                                      _CallP,
                                      _RetT],
                       JobTemplateMixin[IsTaskTemplate[_CallP, _RetT],
                                        IsTask[_CallP, _RetT],
                                        _CallP,
                                        _RetT],
                       TaskBase,
                       Generic[_CallP, _RetT]):
    """"""
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsTask[_CallP, _RetT]]:
        return cast(type[IsTask[_CallP, _RetT]], Task[_CallP, _RetT])


# Needed for pyright and PyCharm
def task_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[_CallableT, _InitP], IsTaskTemplate]) -> \
        Callable[_InitP, Callable[[Callable[_CallP, _RetT]], IsTaskTemplate[_CallP, _RetT]]]:
    return callable_decorator_cls(
        cast(Callable[Concatenate[Callable[_CallP, _RetT], _InitP], IsTaskTemplate[_CallP, _RetT]],
             decorated_cls))


def to_task_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[_CallP, _RetT], _InitP],
                            TaskTemplateCore[_CallP, _RetT]]
) -> HasFuncArgJobTemplateInit[IsTaskTemplate[_CallP, _RetT], _CallP, _RetT]:
    return cast(HasFuncArgJobTemplateInit[IsTaskTemplate[_CallP, _RetT], _CallP, _RetT],
                decorated_cls)


TaskTemplate = task_template_as_callable_decorator(to_task_template_init_protocol(TaskTemplateCore))
# Only works with mypy, not pyright or PyCharm
#
# TaskTemplate = callable_decorator_cls(to_task_template_init_protocol(TaskTemplateCore))


class Task(JobMixin[IsTaskTemplate[_CallP, _RetT], IsTask[_CallP, _RetT], _CallP, _RetT],
           TaskBase,
           FuncArgJobBase[IsTaskTemplate[_CallP, _RetT], IsTask[_CallP, _RetT], _CallP, _RetT],
           Generic[_CallP, _RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask[_CallP, _RetT], self)
            engine.apply_task_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsTaskTemplate[_CallP, _RetT]]:
        return cast(type[IsTaskTemplate[_CallP, _RetT]], TaskTemplate)


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
