"""Task-list job bases used by linear and DAG flow templates.

This module extends the callable-based job hierarchy with an immutable tuple of
task-template dependencies. Concrete flow template classes compose this base with
`JobTemplateMixin`, which lets flow templates preserve both the callable entrypoint
and the ordered task list across refine/apply/revise operations.
"""

from collections.abc import AsyncGenerator, AsyncIterator, Generator, Iterator
import inspect
from typing import Any, Callable, Generic, get_args, get_origin, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.protocols.compute.job import IsFuncArgJobTemplate
from omnipy.util.callable_types import callable_type_from_flags, CallableType

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')


class ChildJobListArgJobBase(FuncArgJobBase[_JobTemplateT, _JobT, _CallP, _RetT],
                             Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    def __init__(self,
                 job_func: Callable[_CallP, _RetT],
                 /,
                 *child_job_templates: IsFuncArgJobTemplate,
                 **kwargs: object) -> None:
        super().__init__(job_func, *child_job_templates, **kwargs)
        self._child_job_templates: tuple[IsFuncArgJobTemplate, ...] = child_job_templates
        self._validate_callable_type_against_child_job_templates()

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func, *self._child_job_templates

    @property
    def child_job_templates(self) -> tuple[IsFuncArgJobTemplate, ...]:
        return self._child_job_templates

    @staticmethod
    def _return_annotation_is_generator_like(return_annotation: Any) -> bool:
        if return_annotation is inspect.Signature.empty:
            return False

        origin = get_origin(return_annotation)
        generator_like_origins = {
            Generator,
            AsyncGenerator,
            Iterator,
            AsyncIterator,
        }

        if origin in generator_like_origins:
            return True

        for arg in get_args(return_annotation):
            if ChildJobListArgJobBase._return_annotation_is_generator_like(arg):
                return True

        return False

    def _effective_callable_type_from_child_job_templates(self) -> CallableType.Literals:
        assert len(
            self._child_job_templates) > 0, 'Linear/DAG flows must define child job templates'

        terminal_child = self._child_job_templates[-1]
        terminal_child_callable_type = terminal_child.callable_type
        is_generator = terminal_child_callable_type in (
            CallableType.SYNC_GENERATOR,
            CallableType.ASYNC_GENERATOR,
        )

        if (not is_generator and terminal_child_callable_type in (
                CallableType.SYNC_FUNCTION,
                CallableType.ASYNC_COROUTINE,
        )):
            is_generator = self._return_annotation_is_generator_like(terminal_child.return_type)

        is_async = any(
            child_job_template.callable_type in (
                CallableType.ASYNC_COROUTINE,
                CallableType.ASYNC_GENERATOR,
            ) for child_job_template in self._child_job_templates)

        return callable_type_from_flags(is_async=is_async, is_generator=is_generator)

    def _validate_callable_type_against_child_job_templates(self) -> None:
        if len(self._child_job_templates) == 0:
            return

        expected_callable_type = self._effective_callable_type_from_child_job_templates()
        actual_callable_type = self.callable_type

        if actual_callable_type is not expected_callable_type:
            raise TypeError('linear/dag flow callable type must match child-job composition: '
                            f'expected {expected_callable_type!r}, got {actual_callable_type!r}')

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
