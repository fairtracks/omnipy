from __future__ import annotations

from typing import cast, Type

from unifair.compute.job import CallableDecoratingJobTemplateMixin
from unifair.compute.private.job import FuncJob, FuncJobBase, FuncJobTemplate
from unifair.compute.types import FuncJobTemplateCallable
from unifair.engine.protocols import IsTask
from unifair.util.callable_decorator_cls import callable_decorator_cls


class TaskBase(FuncJobBase):
    ...


def task_template_callable_decorator_cls(
        cls: Type['TaskTemplate']) -> FuncJobTemplateCallable['TaskTemplate']:
    return cast(FuncJobTemplateCallable['TaskTemplate'], callable_decorator_cls(cls))


@task_template_callable_decorator_cls
class TaskTemplate(CallableDecoratingJobTemplateMixin['TaskTemplate'],
                   TaskBase,
                   FuncJobTemplate['Task']):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Task]:
        return Task

    @classmethod
    def _apply_engine_decorator(cls, task: IsTask) -> IsTask:
        if cls.engine is not None:
            return cls.engine.task_decorator(task)
        else:
            return task


class Task(TaskBase, FuncJob[TaskBase, TaskTemplate]):
    @classmethod
    def _get_job_base_subcls_for_init(cls) -> Type[TaskBase]:
        return TaskBase

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[TaskTemplate]:
        return TaskTemplate


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
