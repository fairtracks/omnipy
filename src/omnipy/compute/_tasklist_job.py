from typing import Callable, Generic, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.protocols.compute.job import IsTaskTemplate

# TODO: Update TaskTemplateArgsJobBase typing to also allow sub-flows

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')


class TaskTemplateArgsJobBase(FuncArgJobBase[_JobTemplateT, _JobT, _CallP, _RetT],
                              Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    def __init__(self,
                 job_func: Callable[_CallP, _RetT],
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
                **kwargs: object) -> _JobTemplateT:

        refined_template = super()._refine(
            *task_templates,
            update=update,
            **kwargs,
        )
        return refined_template
