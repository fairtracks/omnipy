from typing import cast, Type

from omnipy.api.protocols.private.compute.job import (IsFuncArgJobTemplateCallable,
                                                      IsJob,
                                                      IsJobTemplate)
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.compute import IsTask, IsTaskTemplate
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.compute.func_job import FuncArgJobBase
from omnipy.compute.job import JobMixin, JobTemplateMixin
from omnipy.util.callable_decorator import callable_decorator_cls


def task_template_callable_decorator_cls(
        cls: 'Type[TaskTemplate]') -> IsFuncArgJobTemplateCallable[IsTaskTemplate]:
    return cast(IsFuncArgJobTemplateCallable[IsTaskTemplate], callable_decorator_cls(cls))


class TaskBase:
    # TODO: Can this and FlowBase be replaced with IsTask/IsFlow, or similar?
    ...


@task_template_callable_decorator_cls
class TaskTemplate(JobTemplateMixin, TaskBase, FuncArgJobBase):
    """"""
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[IsJob]:
        return cast(Type[IsTask], Task)


class Task(JobMixin, TaskBase, FuncArgJobBase):
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        if self.engine:
            engine = cast(IsTaskRunnerEngine, self.engine)
            self_with_mixins = cast(IsTask, self)
            engine.apply_task_decorator(self_with_mixins, self._accept_call_func_decorator)

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[IsJobTemplate]:
        return cast(Type[IsTaskTemplate], TaskTemplate)


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
