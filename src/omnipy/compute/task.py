from __future__ import annotations

from typing import Callable, cast, Generic, Protocol, Type, TypeVar

from omnipy.api.protocols.private.compute.job import (IsFuncArgJobTemplateCallable,
                                                      IsJob,
                                                      IsJobTemplate)
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.util import IsCallableClass
from omnipy.api.protocols.public.compute import IsTask, IsTaskTemplate
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.api.types import DecoratorClassT
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import JobMixin, JobTemplateMixin
from omnipy.util.callable_decorator_cls import callable_decorator_cls, IsDecoratorClass

C = TypeVar('C', bound=Callable)


def task_template_callable_decorator_cls(
        cls: Type[TaskTemplateInner[C]]) -> IsFuncArgJobTemplateCallable[IsTaskTemplate[C], C]:
    decorated = callable_decorator_cls(cls)
    reveal_type(decorated)
    return cast(IsFuncArgJobTemplateCallable[IsTaskTemplate[C], C], decorated)


reveal_type(task_template_callable_decorator_cls)


class TaskBase:
    # TODO: Can this and FlowBase be replaced with IsTask/IsFlow, or similar?
    ...


# @task_template_callable_decorator_cls
class TaskTemplateInner(FuncArgJobBase[C],
                        JobTemplateMixin[C],
                        TaskBase,
                        Generic[C],
                        IsDecoratorClass[C]):
    """"""
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob[C]]:
        return cast(Type[IsTask[C]], Task[C])


#
# class A(Protocol):
#     def __call__(self, a: int) -> int:
#         ...


def a(a: int) -> int:
    return a + 2


#
# def get_task_template() -> IsFuncArgJobTemplateCallable[IsTaskTemplate[C], C]:
#     return task_template_callable_decorator_cls(TaskTemplateInner[C])
#
#
# TaskTemplate = get_task_template()

TaskTemplate = task_template_callable_decorator_cls(TaskTemplateInner)
reveal_type(TaskTemplate)

tstt = TaskTemplate()
reveal_type(tstt)

t = tstt(a)
reveal_type(t)


class Task(JobMixin[C], TaskBase, FuncArgJobBase[C], Generic[C]):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask[C], self)
            engine.apply_task_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate[C]]:
        return cast(Type[IsTaskTemplate[C]], TaskTemplate[C])


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
