"""Task-list job bases used by linear and DAG flow templates.

This module extends the callable-based job hierarchy with an immutable tuple of
task-template dependencies. Concrete flow template classes compose this base with
`JobTemplateMixin`, which lets flow templates preserve both the callable entrypoint
and the ordered task list across refine/apply/revise operations.
"""

from typing import Callable, Generic, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.protocols.compute.job import IsFuncArgJobTemplate

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')


class ChildJobListArgJobBase(FuncArgJobBase[_JobTemplateT, _JobT, _CallP, _RetT],
                             Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    def __init__(self,
                 job_func: Callable[_CallP, _RetT],
                 /,
                 *child_job_templates: IsFuncArgJobTemplate,
                 **kwargs: object) -> None:
        self._child_job_templates: tuple[IsFuncArgJobTemplate, ...] = child_job_templates

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func, *self._child_job_templates

    @property
    def child_job_templates(self) -> tuple[IsFuncArgJobTemplate, ...]:
        return self._child_job_templates

    def _refine(self,
                *child_job_templates: IsFuncArgJobTemplate,
                update: bool = True,
                **kwargs: object) -> _JobTemplateT:

        refined_template = super()._refine(
            *child_job_templates,
            update=update,
            **kwargs,
        )
        return refined_template
