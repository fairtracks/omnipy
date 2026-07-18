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
    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_COMMON_LIFECYCLE'] = dedent("""\
        ### Lifecycle

        Apply a template with [`apply()`][omnipy.compute._job.JobTemplateMixin.apply]
        to create a runnable job with engine decorators and current config attached.
        Call the resulting applied job with runtime arguments.

        Use [`run()`][omnipy.compute._job.JobTemplateMixin.run] as a shorthand for
        ``apply()`` followed immediately by calling the applied job.

        Use [`refine()`][omnipy.compute._job.JobTemplateMixin.refine] to reuse a
        template while changing configuration such as ``name``, ``fixed_params``,
        or ``param_key_map``.

        Use [`revise()`][omnipy.compute._job.JobMixin.revise] on an applied job to
        reconstruct a template from that job's current configuration.

        Examples:
            >>> import omnipy as om
            >>> @om.TaskTemplate()
            ... def plus_one(number: int) -> int:
            ...     return number + 1
            >>> plus_one.run(1)
            2
            >>> applied_job = plus_one.apply()
            >>> applied_job(2)
            3
            >>> refined_template = plus_one.refine(name='plus_one_renamed')
            >>> revised_template = applied_job.revise()""")

    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_DECORATOR_USAGE'] = dedent("""\
        ### Decorator usage

        Apply the template factory as a decorator to a Python callable.
        The wrapped callable becomes a reusable job template whose public outer
        signature is visible to template users and to the applied jobs created
        from it.""")

    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_OUTER_SIGNATURE_AND_MODIFIERS'] = dedent("""\
        ### Outer signature and modifiers

        The wrapped callable's parameter list and return annotation define the
        outer interface of the template.

        ``fixed_params`` permanently supplies selected callable parameters.

        ``param_key_map`` renames selected callable parameters to external
        keyword names that callers or parent flows use when supplying inputs.

        ``iterate_over_data_files``, ``output_dataset_param``, and
        ``output_dataset_cls`` adapt that outer interface for dataset-wise
        iteration.

        When ``iterate_over_data_files=True`` and the inner first parameter is
        annotated as ``Model[T]``, callers see an outer
        ``dataset: Dataset[Model[T]]`` parameter and the outer return type
        becomes a dataset of the per-item return type. The inner callable still
        receives one model object at a time.

        ``result_key`` wraps the returned value in a single-key dictionary,
        which is especially useful when a downstream DAG step should receive
        the result under a predictable name.

        Examples:
            >>> # With modifiers
            >>> import omnipy as om
            >>> @om.TaskTemplate()
            ... def plus_other(number: int, other: int) -> int:
            ...     return number + other
            >>> plus_one = plus_other.refine(fixed_params={'other': 1})
            >>> plus_one.run(4)
            5
            >>> plus_x = plus_other.refine(param_key_map={'other': 'x'})
            >>> plus_x.run(4, x=3)
            7
            >>> plus_one_dict = plus_one.refine(result_key='number')
            >>> plus_one_dict.run(4)
            {'number': 5}

        Examples:
            >>> # With dataset-wise iteration
            >>> import omnipy as om
            >>> class TextModel(om.Model[str]):
            ...     ...
            >>> class TextDataset(om.Dataset[TextModel]):
            ...     ...
            >>> @om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TextDataset)
            ... def add_suffix(
            ...     data_file: TextModel,
            ...     suffix: str,
            ... ) -> TextModel:
            ...     return f'{data_file.content}{suffix}'
            >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
            >>> expected = TextDataset({'a': 'hi!', 'b': 'bye!'})
            >>> add_suffix.run(text_files, suffix='!') == expected
            True""")

    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_TASKS_AND_FLOWS'] = dedent("""\
        ### Tasks and flows

        Tasks are terminal jobs: they wrap one callable and execute one compute
        step.

        Flows are orchestration jobs: they may contain child tasks and child
        flows, so larger pipelines can be assembled hierarchically from smaller
        reusable pieces.""")

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
