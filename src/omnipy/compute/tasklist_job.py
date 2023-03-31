from typing import Callable, Generic, ParamSpec

from typing_extensions import TypeVar

from omnipy.api.protocols.public.compute import IsTaskTemplate
from omnipy.api.typedefs import JobT, JobTemplateT
from omnipy.compute.func_job import FuncArgJobBase

# TODO: Update TaskTemplateArgsJobBase typing to also allow sub-flows

CallP = ParamSpec('CallP')
RetT = TypeVar('RetT')


class TaskTemplateArgsJobBase(FuncArgJobBase[JobTemplateT, JobT, CallP, RetT],
                              Generic[JobTemplateT, JobT, CallP, RetT]):
    def __init__(self,
                 job_func: Callable[CallP, RetT],
                 /,
                 *task_templates: IsTaskTemplate,
                 **kwargs: object) -> None:
        self._task_templates: tuple[IsTaskTemplate, ...] = task_templates

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func, *self._task_templates

    @property
    def task_templates(self) -> tuple[IsTaskTemplate, ...]:
        return self._task_templates

    def _refine(self,
                *task_templates: IsTaskTemplate,
                update: bool = True,
                **kwargs: object) -> JobTemplateT:

        refined_template = super()._refine(
            *task_templates,
            update=update,
            **kwargs,
        )
        return refined_template
