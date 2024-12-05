from typing import Callable, cast, Generic, ParamSpec, TypeVar

from typing_extensions import Concatenate

from omnipy.api.protocols.private.compute.job import HasFuncArgJobTemplateInit
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.compute import IsTask, IsTaskTemplate
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import JobMixin, JobTemplateMixin
from omnipy.util.callable_decorator import callable_decorator_cls

InitP = ParamSpec('InitP')
CallP = ParamSpec('CallP')
CallableT = TypeVar('CallableT')
RetT = TypeVar('RetT')


class TaskBase:
    # TODO: Can this and FlowBase be replaced with IsTask/IsFlow, or similar?
    ...


class TaskTemplateCore(FuncArgJobBase[IsTaskTemplate[CallP, RetT], IsTask[CallP, RetT], CallP,
                                      RetT],
                       JobTemplateMixin[IsTaskTemplate[CallP, RetT],
                                        IsTask[CallP, RetT],
                                        CallP,
                                        RetT],
                       TaskBase,
                       Generic[CallP, RetT]):
    """"""
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsTask[CallP, RetT]]:
        return cast(type[IsTask[CallP, RetT]], Task[CallP, RetT])


# Needed for pyright and PyCharm
def task_template_as_callable_decorator(
    decorated_cls: Callable[Concatenate[CallableT, InitP], IsTaskTemplate]) -> \
        Callable[InitP, Callable[[Callable[CallP, RetT]], IsTaskTemplate[CallP, RetT]]]:
    return callable_decorator_cls(
        cast(Callable[Concatenate[Callable[CallP, RetT], InitP], IsTaskTemplate[CallP, RetT]],
             decorated_cls))


def to_task_template_init_protocol(
    decorated_cls: Callable[Concatenate[Callable[CallP, RetT], InitP],
                            TaskTemplateCore[CallP, RetT]]
) -> HasFuncArgJobTemplateInit[IsTaskTemplate[CallP, RetT], CallP, RetT]:
    return cast(HasFuncArgJobTemplateInit[IsTaskTemplate[CallP, RetT], CallP, RetT], decorated_cls)


TaskTemplate = task_template_as_callable_decorator(to_task_template_init_protocol(TaskTemplateCore))
# Only works with mypy, not pyright or PyCharm
#
# TaskTemplate = callable_decorator_cls(to_task_template_init_protocol(TaskTemplateCore))


class Task(JobMixin[IsTaskTemplate[CallP, RetT], IsTask[CallP, RetT], CallP, RetT],
           TaskBase,
           FuncArgJobBase[IsTaskTemplate[CallP, RetT], IsTask[CallP, RetT], CallP, RetT],
           Generic[CallP, RetT]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask[CallP, RetT], self)
            engine.apply_task_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsTaskTemplate[CallP, RetT]]:
        return cast(type[IsTaskTemplate[CallP, RetT]], TaskTemplate)


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
