import os
from textwrap import dedent
from typing import Callable, Generic, ParamSpec, TypeVar

from omnipy.compute._job import JobBase
from omnipy.compute._mixins.auto_async import AutoAsyncJobBaseMixin
from omnipy.compute._mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute._mixins.iterate import IterateFuncJobBaseMixin
from omnipy.compute._mixins.params import ParamsFuncJobBaseMixin
from omnipy.compute._mixins.result_key import ResultKeyFuncJobBaseMixin
from omnipy.compute._mixins.serialize import SerializerFuncJobBaseMixin
from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.typedefs import GeneralDecorator
from omnipy.util.callable_types import CallableType, get_callable_type
from omnipy.util.helpers import is_package_editable

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')

if is_package_editable('omnipy'):
    _JOB_TEMPLATE_SHARED_KWARG_DOCS = '\n'.join(
        (os.environ['OMNIPY_MACRO_JOB_TEMPLATE_NAME_ARG_DOC'],
         os.environ['OMNIPY_MACRO_JOB_TEMPLATE_ITERATE_ARG_DOCS'],
         os.environ['OMNIPY_MACRO_JOB_TEMPLATE_AUTO_ASYNC_ARG_DOC'],
         os.environ['OMNIPY_MACRO_JOB_TEMPLATE_RESULT_KEY_ARG_DOC'],
         os.environ['OMNIPY_MACRO_JOB_TEMPLATE_PARAMS_ARG_DOCS'],
         os.environ['OMNIPY_MACRO_JOB_TEMPLATE_SERIALIZE_ARG_DOC'],
         '**kwargs: Additional constructor keyword overrides.'))

    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_REFINE_COMMON_ARGS'] = dedent("""\
            update: Whether omitted values should be inherited from the
                current template.
            """) + _JOB_TEMPLATE_SHARED_KWARG_DOCS

    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_SHARED_KWARG_DOCS'] = _JOB_TEMPLATE_SHARED_KWARG_DOCS

    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_JOB_FUNC_ARG'] = dedent("""\
            job_func: Python callable to wrap as a job template.""")


class PlainFuncArgJobBase(JobBase[_JobTemplateT, _JobT, _CallP, _RetT],
                          Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    """Store the callable backing a task or function-flow job."""
    def __init__(self, job_func: Callable[_CallP, _RetT], /, *args: object,
                 **kwargs: object) -> None:
        self._job_func = job_func

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func,

    @property
    def callable_type(self) -> CallableType.Literals:
        return get_callable_type(self._job_func)

    def _call_job(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        """To be overloaded by mixins"""
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetT:
        """
        To be decorated by job runners and mixins that need early application. Should not
        be overloaded using inheritance. The method _accept_call_func_decorator accepts
        decorators.
        """
        return self._job_func(*args, **kwargs)

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        self._call_func = call_func_decorator(self._call_func)  # type:ignore


# Extra level needed for mixins to be able to overload _call_job (and possibly other methods)
class FuncArgJobBase(PlainFuncArgJobBase[_JobTemplateT, _JobT, _CallP, _RetT],
                     Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    """Provide the callable-based extension point that compute mixins compose onto."""

    ...


FuncArgJobBase.accept_mixin(SignatureFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(IterateFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(AutoAsyncJobBaseMixin)
FuncArgJobBase.accept_mixin(ResultKeyFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(ParamsFuncJobBaseMixin)
FuncArgJobBase.accept_mixin(SerializerFuncJobBaseMixin)
