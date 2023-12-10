from typing import Callable, cast

from omnipy.api.protocols.private.compute.job import (IsJob,
                                                      IsJobTemplate,
                                                      IsTaskTemplateArgsJobTemplate)
from omnipy.api.protocols.public.compute import IsTaskTemplate
from omnipy.compute.func_job import FuncArgJobBase


class TaskTemplateArgsJobBase(FuncArgJobBase):
    def __init__(self, job_func: Callable, *task_templates: IsTaskTemplate,
                 **kwargs: object) -> None:
        self._task_templates: tuple[IsTaskTemplate, ...] = task_templates

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func, *self._task_templates

    @property
    def task_templates(self) -> tuple[IsTaskTemplate, ...]:
        return self._task_templates

    def _refine(
            self,
            *task_templates: IsTaskTemplate,
            update: bool = True,
            **kwargs: object
    ) -> IsTaskTemplateArgsJobTemplate[IsTaskTemplate, IsJobTemplate, IsJob]:

        refined_template = super()._refine(
            *task_templates,
            update=update,
            **kwargs,
        )
        return cast(IsTaskTemplateArgsJobTemplate[IsTaskTemplate, IsJobTemplate, IsJob],
                    refined_template)
