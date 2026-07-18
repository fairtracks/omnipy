"""Flow definitions for composing tasks and subflows.

This module exposes Omnipy's public flow types. Use ``LinearFlowTemplate`` for
sequential pipelines, ``DagFlowTemplate`` for dependency-driven directed
acyclic graphs, and ``FuncFlowTemplate`` for flows expressed as a single
coordinating callable.

Attributes:
    LinearFlowTemplate: Decorator-style template factory for sequential flows.
    DagFlowTemplate: Decorator-style template factory for directed acyclic
        graph flows.
    FuncFlowTemplate: Decorator-style template factory for callable-backed
        coordinating flows.
"""

import inspect
import os
from textwrap import dedent
from typing import Callable, cast, ClassVar, Generic, Iterable, Mapping, ParamSpec

from typing_extensions import TypeVar

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobMixin, JobTemplateMixin
from omnipy.compute._joblist_job import ChildJobListArgJobBase
from omnipy.compute._mixins.flow_context import FlowContextJobMixin
from omnipy.shared.enums.job import JobType, PersistOutputsOptions, RestoreOutputsOptions
from omnipy.shared.protocols.compute.job import (ChildJobTemplateLike,
                                                 IsDagFlow,
                                                 IsDagFlowTemplate,
                                                 IsFuncFlow,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlow,
                                                 IsLinearFlowTemplate)
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.util.callable_decorator import callable_decorator_cls
from omnipy.util.helpers import is_package_editable

__all__ = [
    'DagFlow',
    'DagFlowTemplate',
    'DagFlowTemplateCore',
    'FlowBase',
    'FuncFlow',
    'FuncFlowTemplate',
    'FuncFlowTemplateCore',
    'LinearFlow',
    'LinearFlowTemplate',
    'LinearFlowTemplateCore',
]

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')

if is_package_editable('omnipy'):  # Only define environment variables when developing
    os.environ['OMNIPY_MACRO_FUNC_FLOW_TEMPLATE_DESCRIPTION'] = '\n\n'.join((
        dedent("""\
            A function flow template wraps a Python callable that orchestrates
            work as a flow. Use this when the control flow is easiest to
            express directly in Python instead of as an explicit task list or
            dependency graph."""),
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_DECORATOR_USAGE'],
        dedent("""\
            ### Wrapped callable

            The wrapped callable defines both the implementation and the public
            outer signature of the flow.

            Examples:
                >>> import omnipy as om
                >>> class TextModel(om.Model[str]):
                ...     ...

                >>> class TextDataset(om.Dataset[TextModel]):
                ...     ...

                >>> @om.FuncFlowTemplate()
                ... def append_suffix_to_all(
                ...     dataset: TextDataset,
                ...     suffix: str,
                ... ) -> TextDataset:
                ...     output_dataset = TextDataset()
                ...     for title, data_file in dataset.items():
                ...         output_dataset[title] = f'{data_file.content}{suffix}'
                ...     return output_dataset

                >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
                >>> expected = TextDataset({'a': 'hi!', 'b': 'bye!'})
                >>> append_suffix_to_all.run(text_files, '!') == expected
                True"""),
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_OUTER_SIGNATURE_AND_MODIFIERS'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_TASKS_AND_FLOWS'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_COMMON_LIFECYCLE'],
    ))

    os.environ['OMNIPY_MACRO_LINEAR_FLOW_TEMPLATE_DESCRIPTION'] = '\n\n'.join((
        dedent("""\
            A linear flow template wraps a Python callable together with an ordered
            list of child job templates that run sequentially. Use this when work
            should proceed step by step in a fixed declaration order."""),
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_DECORATOR_USAGE'],
        dedent("""\
            ### Outer callable and child jobs

            The wrapped callable defines the public outer signature of the flow,
            while the child-job list defines the executed body.

            Examples:
                >>> import omnipy as om
                >>> class TextModel(om.Model[str]):
                ...     ...

                >>> class TextDataset(om.Dataset[TextModel]):
                ...     ...

                >>> @om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TextDataset)
                ... def normalize_text(data_file: TextModel) -> TextModel:
                ...     return data_file.content.strip().lower()

                >>> @om.LinearFlowTemplate(normalize_text)
                ... def clean_texts(
                ...     dataset: TextDataset,
                ... ) -> TextDataset:
                ...     return dataset

                >>> text_files = TextDataset({'a': ' Hi ', 'b': 'BYE '})
                >>> expected = TextDataset({'a': 'hi', 'b': 'bye'})
                >>> clean_texts.run(text_files) == expected
                True"""),
        os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_CHILDREN_AND_DATA_CLASSES'],
        os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_CALLABLE_TYPE_RULES'],
        os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_VOID_SHORTHAND'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_OUTER_SIGNATURE_AND_MODIFIERS'],
        os.environ['OMNIPY_MACRO_LINEAR_FLOW_TEMPLATE_ORCHESTRATION'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_TASKS_AND_FLOWS'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_COMMON_LIFECYCLE'],
    ))

    os.environ['OMNIPY_MACRO_DAG_FLOW_TEMPLATE_DESCRIPTION'] = '\n\n'.join((
        dedent("""\
            A DAG flow template wraps a Python callable together with child job
            templates whose dependencies form a directed acyclic graph. Use this
            when flow steps branch and join but must not form cycles."""),
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_DECORATOR_USAGE'],
        dedent("""\
            ### Outer callable and child jobs

            The wrapped callable defines the public outer signature of the flow,
            while the child-job list defines the executed body.

            Examples:
                >>> import omnipy as om
                >>> class TextModel(om.Model[str]):
                ...     ...

                >>> class TextDataset(om.Dataset[TextModel]):
                ...     ...

                >>> @om.TaskTemplate(iterate_over_data_files=True)
                ... def uppercase(data_file: TextModel) -> TextModel:
                ...     return data_file.content.upper()

                >>> @om.TaskTemplate()
                ... def join_texts(
                ...     upper: TextDataset,
                ...     original: TextDataset,
                ... ) -> TextDataset:
                ...     merged = TextDataset()
                ...     for title in upper:
                ...         merged[title] = f'{upper[title].content}|{original[title].content}'
                ...     return merged

                >>> @om.DagFlowTemplate(
                ...     uppercase.refine(result_key='upper'),
                ...     join_texts.refine(param_key_map={'upper': 'upper', 'original': 'dataset'}),
                ... )
                ... def my_dag(
                ...     dataset: TextDataset,
                ... ) -> TextDataset:
                ...     return dataset

                >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
                >>> expected = TextDataset({'a': 'HI|hi', 'b': 'BYE|bye'})
                >>> my_dag.run(text_files) == expected
                True"""),
        os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_CHILDREN_AND_DATA_CLASSES'],
        os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_CALLABLE_TYPE_RULES'],
        os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_VOID_SHORTHAND'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_OUTER_SIGNATURE_AND_MODIFIERS'],
        os.environ['OMNIPY_MACRO_DAG_FLOW_TEMPLATE_ORCHESTRATION'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_TASKS_AND_FLOWS'],
        os.environ['OMNIPY_MACRO_JOB_TEMPLATE_COMMON_LIFECYCLE'],
    ))


def _is_data_class_decorator_arg(arg: object) -> bool:
    """Identify dataset/model class arguments passed as flow child components."""
    has_dataset_interface = all(
        hasattr(arg, dataset_attr) for dataset_attr in ('get_type', 'to_data', 'from_data'))
    return inspect.isclass(arg) and (has_dataset_interface or hasattr(arg, 'full_type'))


class FlowBase:
    """Provide a shared marker base for Omnipy flow objects.

    ``FlowBase`` exists to give concrete flow templates and executable flow
    instances a common nominal base type. It does not define behavior on its
    own, but it makes flow-specific mixin registration and type-based checks
    possible within the compute subsystem.
    """

    ...


class LinearFlowTemplateCore(
        ChildJobListArgJobBase[
            IsLinearFlowTemplate[_CallP, _RetT],
            IsLinearFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        JobTemplateMixin[
            IsLinearFlowTemplate[_CallP, _RetT],
            IsLinearFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        FlowBase,
        Generic[_CallP, _RetT],
):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Implement the core template behavior for linear flows.
    #
    # {{LINEAR_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Instances are normally produced through the [LinearFlowTemplate][]
    # decorator factory rather than by direct construction.
    #
    """Implement the core template behavior for linear flows.

    A linear flow template wraps a Python callable together with an ordered
    list of child job templates that run sequentially. Use this when work
    should proceed step by step in a fixed declaration order.

    ### Decorator usage

    Apply the template factory as a decorator to a Python callable.
    The wrapped callable becomes a reusable job template whose public outer
    signature is visible to template users and to the applied jobs created
    from it.

    ### Outer callable and child jobs

    The wrapped callable defines the public outer signature of the flow,
    while the child-job list defines the executed body.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TextDataset)
        ... def normalize_text(data_file: TextModel) -> TextModel:
        ...     return data_file.content.strip().lower()

        >>> @om.LinearFlowTemplate(normalize_text)
        ... def clean_texts(
        ...     dataset: TextDataset,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': ' Hi ', 'b': 'BYE '})
        >>> expected = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> clean_texts.run(text_files) == expected
        True

    ### Child jobs and data classes

    Child-job templates may be
    [TaskTemplate][omnipy.compute.task.TaskTemplate] or flow-template
    instances.
    This lets flows nest other flows as well as terminal tasks.

    In linear and DAG flows, Model and Dataset subclasses are also allowed
    as child-job entries. During apply, they are coerced into helper task
    templates that construct the requested data object from positional
    input in linear flows or from keyword-matched input in DAG flows.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.LinearFlowTemplate(TextModel)
        ... def wrap_text(raw_text: str) -> TextModel:
        ...     return TextModel(raw_text)

        >>> wrap_text.run('hello').content
        'hello'
        >>> @om.DagFlowTemplate(TextDataset)
        ... def collect_texts(first: str, second: str) -> TextDataset:
        ...     return TextDataset({'first': first, 'second': second})

        >>> collect_texts.run(first='hello', second='bye') == TextDataset({
        ...     'first': 'hello',
        ...     'second': 'bye',
        ... })
        True

    ### Callable-type validation

    For linear and DAG flows, the outer callable is primarily declarative:
    its signature exposes the public flow interface, while child jobs define
    the executed body.

    The outer callable type is validated against the child-job composition.
    The terminal child determines whether the flow behaves like a function
    or generator, and any async child lifts the full flow to an async
    callable type.

    As a result, a sync-function outer callable fits sync child execution,
    a generator outer callable fits generator-producing terminal children,
    and async outer callables are required when child composition is async.
    Mismatches raise ``TypeError`` when the flow template is created.

    ### Generator shorthand with ``Void``

    When the validated outer callable must be a generator or
    async-generator only to expose the correct public signature, use
    [Void][omnipy.compute.helpers.Void] in the body:

    Examples:
        >>> import omnipy as om
        >>> from collections.abc import Iterator

        >>> @om.TaskTemplate()
        ... def emit_lines() -> Iterator[str]:
        ...     yield 'first'
        ...     yield 'second'

        >>> @om.LinearFlowTemplate(emit_lines)
        ... def line_stream() -> Iterator[str]:
        ...     yield from om.Void()

    This shorthand exists only to satisfy the declared outer callable type;
    the child jobs still perform the actual flow work.

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
        True

    ### Linear orchestration

    Linear flows run child jobs strictly in declaration order.

    The first child receives the caller's positional and keyword inputs.
    Each later child receives the previous child result as its leading
    positional input, plus any matching keyword arguments from the outer
    flow call.

    ``fixed_params`` always override caller-supplied values for the child
    where they are configured. ``param_key_map`` lets later children expose
    different external keyword names than their underlying callable
    parameter names.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate(iterate_over_data_files=True)
        ... def strip_text(data_file: TextModel) -> TextModel:
        ...     return data_file.content.strip()

        >>> @om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TextDataset)
        ... def add_suffix(
        ...     data_file: TextModel,
        ...     suffix: str,
        ... ) -> TextModel:
        ...     return f'{data_file.content}{suffix}'

        >>> suffix_each = add_suffix.refine(param_key_map={'suffix': 'ending'})
        >>> @om.LinearFlowTemplate(strip_text, suffix_each)
        ... def linear_flow(
        ...     dataset: TextDataset,
        ...     ending: str,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': ' hi', 'b': 'bye '})
        >>> expected = TextDataset({'a': 'hi!', 'b': 'bye!'})
        >>> linear_flow.run(text_files, ending='!') == expected
        True

    ### Tasks and flows

    Tasks are terminal jobs: they wrap one callable and execute one compute
    step.

    Flows are orchestration jobs: they may contain child tasks and child
    flows, so larger pipelines can be assembled hierarchically from smaller
    reusable pieces.

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
        >>> revised_template = applied_job.revise()

    Instances are normally produced through the [LinearFlowTemplate][]
    decorator factory rather than by direct construction.
    """
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsLinearFlow[_CallP, _RetT]]:
        """Return the executable flow type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete job class that should be instantiated from a linear flow
        template.

        Returns:
            type[IsLinearFlow[_CallP, _RetT]]: The executable [LinearFlow][]
                subclass associated with this template.
        """
        return cast(type[IsLinearFlow[_CallP, _RetT]], LinearFlow[_CallP, _RetT])


_LinearFlowTemplateFactory = callable_decorator_cls(
    LinearFlowTemplateCore,
    single_callable_arg_is_decorator_arg=_is_data_class_decorator_arg,
)


def LinearFlowTemplate(
    *child_job_templates: ChildJobTemplateLike,
    name: str | None = None,
    iterate_over_data_files: bool = False,
    output_dataset_param: str | None = None,
    output_dataset_cls: type[IsDataset] | None = None,
    auto_async: bool = True,
    result_key: str | None = None,
    fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
    param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
    restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
    **kwargs: object,
) -> Callable[[Callable[_CallP, _RetT]], IsLinearFlowTemplate[_CallP, _RetT]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Decorator-style factory for defining sequential flows.
    #
    # {{LINEAR_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Args:
    #     {{JOB_TEMPLATE_CHILD_JOB_TEMPLATES_ARGS}}
    #     {{JOB_TEMPLATE_SHARED_KWARG_DOCS}}
    # Returns:
    #     LinearFlowTemplate: New LinearFlowTemplate instance wrapping ``job_func``.
    """Decorator-style factory for defining sequential flows.

    A linear flow template wraps a Python callable together with an ordered
    list of child job templates that run sequentially. Use this when work
    should proceed step by step in a fixed declaration order.

    ### Decorator usage

    Apply the template factory as a decorator to a Python callable.
    The wrapped callable becomes a reusable job template whose public outer
    signature is visible to template users and to the applied jobs created
    from it.

    ### Outer callable and child jobs

    The wrapped callable defines the public outer signature of the flow,
    while the child-job list defines the executed body.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TextDataset)
        ... def normalize_text(data_file: TextModel) -> TextModel:
        ...     return data_file.content.strip().lower()

        >>> @om.LinearFlowTemplate(normalize_text)
        ... def clean_texts(
        ...     dataset: TextDataset,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': ' Hi ', 'b': 'BYE '})
        >>> expected = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> clean_texts.run(text_files) == expected
        True

    ### Child jobs and data classes

    Child-job templates may be
    [TaskTemplate][omnipy.compute.task.TaskTemplate] or flow-template
    instances.
    This lets flows nest other flows as well as terminal tasks.

    In linear and DAG flows, Model and Dataset subclasses are also allowed
    as child-job entries. During apply, they are coerced into helper task
    templates that construct the requested data object from positional
    input in linear flows or from keyword-matched input in DAG flows.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.LinearFlowTemplate(TextModel)
        ... def wrap_text(raw_text: str) -> TextModel:
        ...     return TextModel(raw_text)

        >>> wrap_text.run('hello').content
        'hello'
        >>> @om.DagFlowTemplate(TextDataset)
        ... def collect_texts(first: str, second: str) -> TextDataset:
        ...     return TextDataset({'first': first, 'second': second})

        >>> collect_texts.run(first='hello', second='bye') == TextDataset({
        ...     'first': 'hello',
        ...     'second': 'bye',
        ... })
        True

    ### Callable-type validation

    For linear and DAG flows, the outer callable is primarily declarative:
    its signature exposes the public flow interface, while child jobs define
    the executed body.

    The outer callable type is validated against the child-job composition.
    The terminal child determines whether the flow behaves like a function
    or generator, and any async child lifts the full flow to an async
    callable type.

    As a result, a sync-function outer callable fits sync child execution,
    a generator outer callable fits generator-producing terminal children,
    and async outer callables are required when child composition is async.
    Mismatches raise ``TypeError`` when the flow template is created.

    ### Generator shorthand with ``Void``

    When the validated outer callable must be a generator or
    async-generator only to expose the correct public signature, use
    [Void][omnipy.compute.helpers.Void] in the body:

    Examples:
        >>> import omnipy as om
        >>> from collections.abc import Iterator

        >>> @om.TaskTemplate()
        ... def emit_lines() -> Iterator[str]:
        ...     yield 'first'
        ...     yield 'second'

        >>> @om.LinearFlowTemplate(emit_lines)
        ... def line_stream() -> Iterator[str]:
        ...     yield from om.Void()

    This shorthand exists only to satisfy the declared outer callable type;
    the child jobs still perform the actual flow work.

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
        True

    ### Linear orchestration

    Linear flows run child jobs strictly in declaration order.

    The first child receives the caller's positional and keyword inputs.
    Each later child receives the previous child result as its leading
    positional input, plus any matching keyword arguments from the outer
    flow call.

    ``fixed_params`` always override caller-supplied values for the child
    where they are configured. ``param_key_map`` lets later children expose
    different external keyword names than their underlying callable
    parameter names.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate(iterate_over_data_files=True)
        ... def strip_text(data_file: TextModel) -> TextModel:
        ...     return data_file.content.strip()

        >>> @om.TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TextDataset)
        ... def add_suffix(
        ...     data_file: TextModel,
        ...     suffix: str,
        ... ) -> TextModel:
        ...     return f'{data_file.content}{suffix}'

        >>> suffix_each = add_suffix.refine(param_key_map={'suffix': 'ending'})
        >>> @om.LinearFlowTemplate(strip_text, suffix_each)
        ... def linear_flow(
        ...     dataset: TextDataset,
        ...     ending: str,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': ' hi', 'b': 'bye '})
        >>> expected = TextDataset({'a': 'hi!', 'b': 'bye!'})
        >>> linear_flow.run(text_files, ending='!') == expected
        True

    ### Tasks and flows

    Tasks are terminal jobs: they wrap one callable and execute one compute
    step.

    Flows are orchestration jobs: they may contain child tasks and child
    flows, so larger pipelines can be assembled hierarchically from smaller
    reusable pieces.

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
        >>> revised_template = applied_job.revise()

    Args:
        *child_job_templates: Ordered templates of child jobs to be
            run as part of the parent job. Model and Dataset subclasses
            are also allowed, in which case they are converted to
            create_X_from_args (if linear flow) or create_X_from_kwargs
            (if DAG flow) job templates, respectively, when apply() is
            called on the parent job template.
        name: Name of the job template. If not provided, the name of the
            wrapped callable is used.
        iterate_over_data_files: Whether dataset inputs should be
            processed item-wise.
        output_dataset_param: Optional name of an explicit
            output-dataset parameter.
        output_dataset_cls: Optional dataset class to use for iterated
            outputs.
        auto_async: Whether coroutine jobs at the outermost level (not
            in a flow context) should be automatically run in accordance
            with context (use existing event loop, if available,
            otherwise create temporary event loop and run coroutine
            until completion).
        result_key: Optional key used to wrap the returned result in a
            dictionary. Especially useful in DAG flows to avoid name
            collisions.
        fixed_params: Fixed keyword-argument values for the job. May not
            target *args or **kwargs-style params.
        param_key_map: Mapping from callable parameter names to external
            keyword names. May not target *args or **kwargs-style
            params.
        persist_outputs: Per-job output-persistence preference.
        restore_outputs: Per-job output-restore preference.
        **kwargs: Additional constructor keyword overrides.
    Returns:
        LinearFlowTemplate: New LinearFlowTemplate instance wrapping ``job_func``."""
    ret = _LinearFlowTemplateFactory(
        *child_job_templates,
        name=name,
        iterate_over_data_files=iterate_over_data_files,
        output_dataset_param=output_dataset_param,
        output_dataset_cls=output_dataset_cls,
        auto_async=auto_async,
        result_key=result_key,
        fixed_params=fixed_params,
        param_key_map=param_key_map,
        persist_outputs=persist_outputs,
        restore_outputs=restore_outputs,
        **kwargs,
    )
    return cast(Callable[[Callable[_CallP, _RetT]], IsLinearFlowTemplate[_CallP, _RetT]], ret)


class LinearFlow(JobMixin[IsLinearFlowTemplate[_CallP, _RetT],
                          IsLinearFlow[_CallP, _RetT],
                          _CallP,
                          _RetT],
                 FlowBase,
                 ChildJobListArgJobBase[IsLinearFlowTemplate[_CallP, _RetT],
                                        IsLinearFlow[_CallP, _RetT],
                                        _CallP,
                                        _RetT],
                 Generic[_CallP, _RetT]):
    """Execute a flow whose tasks run in declaration order.

    A ``LinearFlow`` runs its constituent tasks in declaration order, making
    each step wait for the previous one to finish. Use it for pipelines where
    every stage depends on the output or side effects of the stage before it.

    Instances are typically produced by calling a ``LinearFlowTemplate``
    rather than by constructing ``LinearFlow`` directly.
    """
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        """Register the engine decorator for linear-flow execution.

        When the flow already holds a runner engine, this method asks that
        engine to wrap the flow's call function with the engine-specific
        linear-flow execution behavior.

        Args:
            self: Current linear flow instance.
            engine: Engine candidate supplied during job setup.
        """
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsLinearFlow, self)
            engine.apply_job_decorator(
                JobType.LINEAR_FLOW,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsLinearFlowTemplate[_CallP, _RetT]]:
        """Return the template type used to revise this flow.

        Revision operations use this hook to recover the decorator-backed
        template class corresponding to an executable linear flow instance.

        Returns:
            type[IsLinearFlowTemplate[_CallP, _RetT]]: The [LinearFlowTemplate][]
                class associated with this flow.
        """
        return cast(type[IsLinearFlowTemplate[_CallP, _RetT]], LinearFlowTemplateCore)


class DagFlowTemplateCore(ChildJobListArgJobBase[IsDagFlowTemplate[_CallP, _RetT],
                                                 IsDagFlow[_CallP, _RetT],
                                                 _CallP,
                                                 _RetT],
                          JobTemplateMixin[IsDagFlowTemplate[_CallP, _RetT],
                                           IsDagFlow[_CallP, _RetT],
                                           _CallP,
                                           _RetT],
                          FlowBase,
                          Generic[_CallP, _RetT]):
    _coerce_data_class_children_from_kwargs: ClassVar[bool] = True

    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Implement the core template behavior for DAG flows.
    #
    # {{DAG_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Instances are normally produced through the [DagFlowTemplate][] decorator
    # factory rather than by direct construction.
    #
    """Implement the core template behavior for DAG flows.

    A DAG flow template wraps a Python callable together with child job
    templates whose dependencies form a directed acyclic graph. Use this
    when flow steps branch and join but must not form cycles.

    ### Decorator usage

    Apply the template factory as a decorator to a Python callable.
    The wrapped callable becomes a reusable job template whose public outer
    signature is visible to template users and to the applied jobs created
    from it.

    ### Outer callable and child jobs

    The wrapped callable defines the public outer signature of the flow,
    while the child-job list defines the executed body.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate(iterate_over_data_files=True)
        ... def uppercase(data_file: TextModel) -> TextModel:
        ...     return data_file.content.upper()

        >>> @om.TaskTemplate()
        ... def join_texts(
        ...     upper: TextDataset,
        ...     original: TextDataset,
        ... ) -> TextDataset:
        ...     merged = TextDataset()
        ...     for title in upper:
        ...         merged[title] = f'{upper[title].content}|{original[title].content}'
        ...     return merged

        >>> @om.DagFlowTemplate(
        ...     uppercase.refine(result_key='upper'),
        ...     join_texts.refine(param_key_map={'upper': 'upper', 'original': 'dataset'}),
        ... )
        ... def my_dag(
        ...     dataset: TextDataset,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> expected = TextDataset({'a': 'HI|hi', 'b': 'BYE|bye'})
        >>> my_dag.run(text_files) == expected
        True

    ### Child jobs and data classes

    Child-job templates may be
    [TaskTemplate][omnipy.compute.task.TaskTemplate] or flow-template
    instances.
    This lets flows nest other flows as well as terminal tasks.

    In linear and DAG flows, Model and Dataset subclasses are also allowed
    as child-job entries. During apply, they are coerced into helper task
    templates that construct the requested data object from positional
    input in linear flows or from keyword-matched input in DAG flows.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.LinearFlowTemplate(TextModel)
        ... def wrap_text(raw_text: str) -> TextModel:
        ...     return TextModel(raw_text)

        >>> wrap_text.run('hello').content
        'hello'
        >>> @om.DagFlowTemplate(TextDataset)
        ... def collect_texts(first: str, second: str) -> TextDataset:
        ...     return TextDataset({'first': first, 'second': second})

        >>> collect_texts.run(first='hello', second='bye') == TextDataset({
        ...     'first': 'hello',
        ...     'second': 'bye',
        ... })
        True

    ### Callable-type validation

    For linear and DAG flows, the outer callable is primarily declarative:
    its signature exposes the public flow interface, while child jobs define
    the executed body.

    The outer callable type is validated against the child-job composition.
    The terminal child determines whether the flow behaves like a function
    or generator, and any async child lifts the full flow to an async
    callable type.

    As a result, a sync-function outer callable fits sync child execution,
    a generator outer callable fits generator-producing terminal children,
    and async outer callables are required when child composition is async.
    Mismatches raise ``TypeError`` when the flow template is created.

    ### Generator shorthand with ``Void``

    When the validated outer callable must be a generator or
    async-generator only to expose the correct public signature, use
    [Void][omnipy.compute.helpers.Void] in the body:

    Examples:
        >>> import omnipy as om
        >>> from collections.abc import Iterator

        >>> @om.TaskTemplate()
        ... def emit_lines() -> Iterator[str]:
        ...     yield 'first'
        ...     yield 'second'

        >>> @om.LinearFlowTemplate(emit_lines)
        ... def line_stream() -> Iterator[str]:
        ...     yield from om.Void()

    This shorthand exists only to satisfy the declared outer callable type;
    the child jobs still perform the actual flow work.

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
        True

    ### DAG orchestration

    DAG flows route values by keyword name instead of chaining every child
    result positionally.

    The outer flow call first binds its arguments to the outer callable
    signature. Each child then receives the matching keyword subset from the
    accumulated named results.

    By default, a non-dictionary child result is stored under the child job
    name. ``result_key`` stores it under a custom key instead, which is the
    usual way to make one branch feed another. Dictionary results merge
    directly into the accumulated named result set.

    ``param_key_map`` lets a child read from externally visible DAG keys
    using different internal callable parameter names, and ``fixed_params``
    pins selected child inputs regardless of what earlier branches produce.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate()
        ... def uppercase(data_file: TextModel) -> TextModel:
        ...     return data_file.content.upper()

        >>> @om.TaskTemplate()
        ... def append_suffix(
        ...     data_file: TextModel,
        ...     suffix: str,
        ... ) -> TextModel:
        ...     return f'{data_file.content}{suffix}'

        >>> @om.TaskTemplate()
        ... def combine_texts(
        ...     left_dataset: TextDataset,
        ...     right_dataset: TextDataset,
        ... ) -> TextDataset:
        ...     merged = TextDataset()
        ...     for title in left_dataset:
        ...         merged[title] = (
        ...             f'{left_dataset[title].content}|'
        ...             f'{right_dataset[title].content}'
        ...         )
        ...     return merged

        >>> @om.DagFlowTemplate(
        ...     uppercase.refine(
        ...         iterate_over_data_files=True,
        ...         result_key='upper',
        ...     ),
        ...     append_suffix.refine(
        ...         iterate_over_data_files=True,
        ...         result_key='suffixed',
        ...         param_key_map={'suffix': 'ending'},
        ...     ),
        ...     combine_texts.refine(
        ...         param_key_map={
        ...             'left_dataset': 'upper',
        ...             'right_dataset': 'suffixed',
        ...         },
        ...     ),
        ... )
        ... def dag_flow(
        ...     dataset: TextDataset,
        ...     ending: str,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> expected = TextDataset({
        ...     'a': 'HI|hi!',
        ...     'b': 'BYE|bye!',
        ... })
        >>> dag_flow.run(text_files, ending='!') == expected
        True

    ### Tasks and flows

    Tasks are terminal jobs: they wrap one callable and execute one compute
    step.

    Flows are orchestration jobs: they may contain child tasks and child
    flows, so larger pipelines can be assembled hierarchically from smaller
    reusable pieces.

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
        >>> revised_template = applied_job.revise()

    Instances are normally produced through the [DagFlowTemplate][] decorator
    factory rather than by direct construction.
    """
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsDagFlow[_CallP, _RetT]]:
        """Return the executable DAG flow type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete flow class to instantiate from a DAG flow template.

        Returns:
            type[IsDagFlow[_CallP, _RetT]]: The executable [DagFlow][] subclass
                associated with this template.
        """
        return cast(type[IsDagFlow[_CallP, _RetT]], DagFlow[_CallP, _RetT])


_DagFlowTemplateFactory = callable_decorator_cls(
    DagFlowTemplateCore,
    single_callable_arg_is_decorator_arg=_is_data_class_decorator_arg,
)


def DagFlowTemplate(
    *child_job_templates: ChildJobTemplateLike,
    name: str | None = None,
    iterate_over_data_files: bool = False,
    output_dataset_param: str | None = None,
    output_dataset_cls: type[IsDataset] | None = None,
    auto_async: bool = True,
    result_key: str | None = None,
    fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
    param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
    restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
    **kwargs: object,
) -> Callable[[Callable[_CallP, _RetT]], IsDagFlowTemplate[_CallP, _RetT]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Decorator-style factory for defining directed acyclic graph flows.
    #
    # {{DAG_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Args:
    #     {{JOB_TEMPLATE_CHILD_JOB_TEMPLATES_ARGS}}
    #     {{JOB_TEMPLATE_SHARED_KWARG_DOCS}}
    # Returns:
    #     DagFlowTemplate: New DagFlowTemplate instance wrapping ``job_func``.
    """Decorator-style factory for defining directed acyclic graph flows.

    A DAG flow template wraps a Python callable together with child job
    templates whose dependencies form a directed acyclic graph. Use this
    when flow steps branch and join but must not form cycles.

    ### Decorator usage

    Apply the template factory as a decorator to a Python callable.
    The wrapped callable becomes a reusable job template whose public outer
    signature is visible to template users and to the applied jobs created
    from it.

    ### Outer callable and child jobs

    The wrapped callable defines the public outer signature of the flow,
    while the child-job list defines the executed body.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate(iterate_over_data_files=True)
        ... def uppercase(data_file: TextModel) -> TextModel:
        ...     return data_file.content.upper()

        >>> @om.TaskTemplate()
        ... def join_texts(
        ...     upper: TextDataset,
        ...     original: TextDataset,
        ... ) -> TextDataset:
        ...     merged = TextDataset()
        ...     for title in upper:
        ...         merged[title] = f'{upper[title].content}|{original[title].content}'
        ...     return merged

        >>> @om.DagFlowTemplate(
        ...     uppercase.refine(result_key='upper'),
        ...     join_texts.refine(param_key_map={'upper': 'upper', 'original': 'dataset'}),
        ... )
        ... def my_dag(
        ...     dataset: TextDataset,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> expected = TextDataset({'a': 'HI|hi', 'b': 'BYE|bye'})
        >>> my_dag.run(text_files) == expected
        True

    ### Child jobs and data classes

    Child-job templates may be
    [TaskTemplate][omnipy.compute.task.TaskTemplate] or flow-template
    instances.
    This lets flows nest other flows as well as terminal tasks.

    In linear and DAG flows, Model and Dataset subclasses are also allowed
    as child-job entries. During apply, they are coerced into helper task
    templates that construct the requested data object from positional
    input in linear flows or from keyword-matched input in DAG flows.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.LinearFlowTemplate(TextModel)
        ... def wrap_text(raw_text: str) -> TextModel:
        ...     return TextModel(raw_text)

        >>> wrap_text.run('hello').content
        'hello'
        >>> @om.DagFlowTemplate(TextDataset)
        ... def collect_texts(first: str, second: str) -> TextDataset:
        ...     return TextDataset({'first': first, 'second': second})

        >>> collect_texts.run(first='hello', second='bye') == TextDataset({
        ...     'first': 'hello',
        ...     'second': 'bye',
        ... })
        True

    ### Callable-type validation

    For linear and DAG flows, the outer callable is primarily declarative:
    its signature exposes the public flow interface, while child jobs define
    the executed body.

    The outer callable type is validated against the child-job composition.
    The terminal child determines whether the flow behaves like a function
    or generator, and any async child lifts the full flow to an async
    callable type.

    As a result, a sync-function outer callable fits sync child execution,
    a generator outer callable fits generator-producing terminal children,
    and async outer callables are required when child composition is async.
    Mismatches raise ``TypeError`` when the flow template is created.

    ### Generator shorthand with ``Void``

    When the validated outer callable must be a generator or
    async-generator only to expose the correct public signature, use
    [Void][omnipy.compute.helpers.Void] in the body:

    Examples:
        >>> import omnipy as om
        >>> from collections.abc import Iterator

        >>> @om.TaskTemplate()
        ... def emit_lines() -> Iterator[str]:
        ...     yield 'first'
        ...     yield 'second'

        >>> @om.LinearFlowTemplate(emit_lines)
        ... def line_stream() -> Iterator[str]:
        ...     yield from om.Void()

    This shorthand exists only to satisfy the declared outer callable type;
    the child jobs still perform the actual flow work.

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
        True

    ### DAG orchestration

    DAG flows route values by keyword name instead of chaining every child
    result positionally.

    The outer flow call first binds its arguments to the outer callable
    signature. Each child then receives the matching keyword subset from the
    accumulated named results.

    By default, a non-dictionary child result is stored under the child job
    name. ``result_key`` stores it under a custom key instead, which is the
    usual way to make one branch feed another. Dictionary results merge
    directly into the accumulated named result set.

    ``param_key_map`` lets a child read from externally visible DAG keys
    using different internal callable parameter names, and ``fixed_params``
    pins selected child inputs regardless of what earlier branches produce.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.TaskTemplate()
        ... def uppercase(data_file: TextModel) -> TextModel:
        ...     return data_file.content.upper()

        >>> @om.TaskTemplate()
        ... def append_suffix(
        ...     data_file: TextModel,
        ...     suffix: str,
        ... ) -> TextModel:
        ...     return f'{data_file.content}{suffix}'

        >>> @om.TaskTemplate()
        ... def combine_texts(
        ...     left_dataset: TextDataset,
        ...     right_dataset: TextDataset,
        ... ) -> TextDataset:
        ...     merged = TextDataset()
        ...     for title in left_dataset:
        ...         merged[title] = (
        ...             f'{left_dataset[title].content}|'
        ...             f'{right_dataset[title].content}'
        ...         )
        ...     return merged

        >>> @om.DagFlowTemplate(
        ...     uppercase.refine(
        ...         iterate_over_data_files=True,
        ...         result_key='upper',
        ...     ),
        ...     append_suffix.refine(
        ...         iterate_over_data_files=True,
        ...         result_key='suffixed',
        ...         param_key_map={'suffix': 'ending'},
        ...     ),
        ...     combine_texts.refine(
        ...         param_key_map={
        ...             'left_dataset': 'upper',
        ...             'right_dataset': 'suffixed',
        ...         },
        ...     ),
        ... )
        ... def dag_flow(
        ...     dataset: TextDataset,
        ...     ending: str,
        ... ) -> TextDataset:
        ...     return dataset

        >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> expected = TextDataset({
        ...     'a': 'HI|hi!',
        ...     'b': 'BYE|bye!',
        ... })
        >>> dag_flow.run(text_files, ending='!') == expected
        True

    ### Tasks and flows

    Tasks are terminal jobs: they wrap one callable and execute one compute
    step.

    Flows are orchestration jobs: they may contain child tasks and child
    flows, so larger pipelines can be assembled hierarchically from smaller
    reusable pieces.

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
        >>> revised_template = applied_job.revise()

    Args:
        *child_job_templates: Ordered templates of child jobs to be
            run as part of the parent job. Model and Dataset subclasses
            are also allowed, in which case they are converted to
            create_X_from_args (if linear flow) or create_X_from_kwargs
            (if DAG flow) job templates, respectively, when apply() is
            called on the parent job template.
        name: Name of the job template. If not provided, the name of the
            wrapped callable is used.
        iterate_over_data_files: Whether dataset inputs should be
            processed item-wise.
        output_dataset_param: Optional name of an explicit
            output-dataset parameter.
        output_dataset_cls: Optional dataset class to use for iterated
            outputs.
        auto_async: Whether coroutine jobs at the outermost level (not
            in a flow context) should be automatically run in accordance
            with context (use existing event loop, if available,
            otherwise create temporary event loop and run coroutine
            until completion).
        result_key: Optional key used to wrap the returned result in a
            dictionary. Especially useful in DAG flows to avoid name
            collisions.
        fixed_params: Fixed keyword-argument values for the job. May not
            target *args or **kwargs-style params.
        param_key_map: Mapping from callable parameter names to external
            keyword names. May not target *args or **kwargs-style
            params.
        persist_outputs: Per-job output-persistence preference.
        restore_outputs: Per-job output-restore preference.
        **kwargs: Additional constructor keyword overrides.
    Returns:
        DagFlowTemplate: New DagFlowTemplate instance wrapping ``job_func``."""
    ret = _DagFlowTemplateFactory(
        *child_job_templates,
        name=name,
        iterate_over_data_files=iterate_over_data_files,
        output_dataset_param=output_dataset_param,
        output_dataset_cls=output_dataset_cls,
        auto_async=auto_async,
        result_key=result_key,
        fixed_params=fixed_params,
        param_key_map=param_key_map,
        persist_outputs=persist_outputs,
        restore_outputs=restore_outputs,
        **kwargs,
    )
    return cast(Callable[[Callable[_CallP, _RetT]], IsDagFlowTemplate[_CallP, _RetT]], ret)


class DagFlow(
        JobMixin[IsDagFlowTemplate[_CallP, _RetT], IsDagFlow[_CallP, _RetT], _CallP, _RetT],
        FlowBase,
        ChildJobListArgJobBase[
            IsDagFlowTemplate[_CallP, _RetT],
            IsDagFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        Generic[_CallP, _RetT],
):
    """Execute a flow whose child jobs exchange data through named DAG keys.

    A ``DagFlow`` routes values between child jobs by accumulated keyword name
    rather than by one strict positional chain. Use it for branching and
    joining pipelines whose dependencies form a directed acyclic graph.

    Instances are typically produced by calling a ``DagFlowTemplate`` rather
    than by constructing ``DagFlow`` directly.
    """
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        """Register the engine decorator for DAG-flow execution.

        When a runner engine is bound to the flow, this method asks that
        engine to wrap the flow's call function with DAG-specific execution
        behavior.

        Args:
            self: Current DAG flow instance.
            engine: Engine candidate supplied during job setup.
        """
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsDagFlow, self)
            engine.apply_job_decorator(
                JobType.DAG_FLOW,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsDagFlowTemplate[_CallP, _RetT]]:
        """Return the template type used to revise this flow.

        Revision operations use this hook to recover the decorator-backed DAG
        flow template class corresponding to an executable DAG flow instance.

        Returns:
            type[IsDagFlowTemplate[_CallP, _RetT]]: The [DagFlowTemplate][]
                class associated with this flow.
        """
        return cast(type[IsDagFlowTemplate[_CallP, _RetT]], DagFlowTemplateCore)


class FuncFlowTemplateCore(
        FuncArgJobBase[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        JobTemplateMixin[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        FlowBase,
        Generic[_CallP, _RetT],
):
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Implement the core template behavior for function flows.
    #
    # {{FUNC_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Instances are normally produced through the [FuncFlowTemplate][] decorator
    # factory rather than by direct construction.
    #
    """Implement the core template behavior for function flows.

    A function flow template wraps a Python callable that orchestrates
    work as a flow. Use this when the control flow is easiest to
    express directly in Python instead of as an explicit task list or
    dependency graph.

    ### Decorator usage

    Apply the template factory as a decorator to a Python callable.
    The wrapped callable becomes a reusable job template whose public outer
    signature is visible to template users and to the applied jobs created
    from it.

    ### Wrapped callable

    The wrapped callable defines both the implementation and the public
    outer signature of the flow.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.FuncFlowTemplate()
        ... def append_suffix_to_all(
        ...     dataset: TextDataset,
        ...     suffix: str,
        ... ) -> TextDataset:
        ...     output_dataset = TextDataset()
        ...     for title, data_file in dataset.items():
        ...         output_dataset[title] = f'{data_file.content}{suffix}'
        ...     return output_dataset

        >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> expected = TextDataset({'a': 'hi!', 'b': 'bye!'})
        >>> append_suffix_to_all.run(text_files, '!') == expected
        True

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
        True

    ### Tasks and flows

    Tasks are terminal jobs: they wrap one callable and execute one compute
    step.

    Flows are orchestration jobs: they may contain child tasks and child
    flows, so larger pipelines can be assembled hierarchically from smaller
    reusable pieces.

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
        >>> revised_template = applied_job.revise()

    Instances are normally produced through the [FuncFlowTemplate][] decorator
    factory rather than by direct construction.
    """
    @classmethod
    def _get_job_subcls_for_apply(cls) -> type[IsFuncFlow[_CallP, _RetT]]:
        """Return the executable function flow type produced by this template.

        The template/application machinery calls this hook when it needs the
        concrete flow class that should be instantiated from a function flow
        template.

        Returns:
            type[IsFuncFlow[_CallP, _RetT]]: The executable [FuncFlow][]
                subclass associated with this template.
        """
        return cast(type[IsFuncFlow[_CallP, _RetT]], FuncFlow[_CallP, _RetT])


_FuncFlowTemplateFactory = callable_decorator_cls(FuncFlowTemplateCore)


def FuncFlowTemplate(
    *,
    name: str | None = None,
    iterate_over_data_files: bool = False,
    output_dataset_param: str | None = None,
    output_dataset_cls: type[IsDataset] | None = None,
    auto_async: bool = True,
    result_key: str | None = None,
    fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
    param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
    restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
    **kwargs: object,
) -> Callable[[Callable[_CallP, _RetT]], IsFuncFlowTemplate[_CallP, _RetT]]:
    # %% Original docstring (managed by expand_docstr_macros.py) %%
    # Decorator-style factory for defining callable-backed coordinating flows.
    #
    # {{FUNC_FLOW_TEMPLATE_DESCRIPTION}}
    #
    # Args:
    #     {{JOB_TEMPLATE_SHARED_KWARG_DOCS}}
    # Returns:
    #     FuncFlowTemplate: New FuncFlowTemplate instance wrapping ``job_func``.
    """Decorator-style factory for defining callable-backed coordinating flows.

    A function flow template wraps a Python callable that orchestrates
    work as a flow. Use this when the control flow is easiest to
    express directly in Python instead of as an explicit task list or
    dependency graph.

    ### Decorator usage

    Apply the template factory as a decorator to a Python callable.
    The wrapped callable becomes a reusable job template whose public outer
    signature is visible to template users and to the applied jobs created
    from it.

    ### Wrapped callable

    The wrapped callable defines both the implementation and the public
    outer signature of the flow.

    Examples:
        >>> import omnipy as om
        >>> class TextModel(om.Model[str]):
        ...     ...

        >>> class TextDataset(om.Dataset[TextModel]):
        ...     ...

        >>> @om.FuncFlowTemplate()
        ... def append_suffix_to_all(
        ...     dataset: TextDataset,
        ...     suffix: str,
        ... ) -> TextDataset:
        ...     output_dataset = TextDataset()
        ...     for title, data_file in dataset.items():
        ...         output_dataset[title] = f'{data_file.content}{suffix}'
        ...     return output_dataset

        >>> text_files = TextDataset({'a': 'hi', 'b': 'bye'})
        >>> expected = TextDataset({'a': 'hi!', 'b': 'bye!'})
        >>> append_suffix_to_all.run(text_files, '!') == expected
        True

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
        True

    ### Tasks and flows

    Tasks are terminal jobs: they wrap one callable and execute one compute
    step.

    Flows are orchestration jobs: they may contain child tasks and child
    flows, so larger pipelines can be assembled hierarchically from smaller
    reusable pieces.

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
        >>> revised_template = applied_job.revise()

    Args:
        name: Name of the job template. If not provided, the name of the
            wrapped callable is used.
        iterate_over_data_files: Whether dataset inputs should be
            processed item-wise.
        output_dataset_param: Optional name of an explicit
            output-dataset parameter.
        output_dataset_cls: Optional dataset class to use for iterated
            outputs.
        auto_async: Whether coroutine jobs at the outermost level (not
            in a flow context) should be automatically run in accordance
            with context (use existing event loop, if available,
            otherwise create temporary event loop and run coroutine
            until completion).
        result_key: Optional key used to wrap the returned result in a
            dictionary. Especially useful in DAG flows to avoid name
            collisions.
        fixed_params: Fixed keyword-argument values for the job. May not
            target *args or **kwargs-style params.
        param_key_map: Mapping from callable parameter names to external
            keyword names. May not target *args or **kwargs-style
            params.
        persist_outputs: Per-job output-persistence preference.
        restore_outputs: Per-job output-restore preference.
        **kwargs: Additional constructor keyword overrides.
    Returns:
        FuncFlowTemplate: New FuncFlowTemplate instance wrapping ``job_func``."""
    ret = _FuncFlowTemplateFactory(
        name=name,
        iterate_over_data_files=iterate_over_data_files,
        output_dataset_param=output_dataset_param,
        output_dataset_cls=output_dataset_cls,
        auto_async=auto_async,
        result_key=result_key,
        fixed_params=fixed_params,
        param_key_map=param_key_map,
        persist_outputs=persist_outputs,
        restore_outputs=restore_outputs,
        **kwargs,
    )
    return cast(Callable[[Callable[_CallP, _RetT]], IsFuncFlowTemplate[_CallP, _RetT]], ret)


class FuncFlow(
        JobMixin[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        FlowBase,
        FuncArgJobBase[
            IsFuncFlowTemplate[_CallP, _RetT],
            IsFuncFlow[_CallP, _RetT],
            _CallP,
            _RetT,
        ],
        Generic[_CallP, _RetT],
):
    """Execute a flow backed by one coordinating callable.

    A ``FuncFlow`` runs the wrapped callable itself as the flow body instead of
    orchestrating an explicit child-job list. Use it when one callable already
    captures the desired control flow and runtime behavior.

    Instances are typically produced by calling a ``FuncFlowTemplate`` rather
    than by constructing ``FuncFlow`` directly.
    """
    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        """Register the engine decorator for callable-backed flow execution.

        When a runner engine is bound to the flow, this method asks that
        engine to wrap the coordinating callable with function-flow execution
        behavior.

        Args:
            self: Current function flow instance.
            engine: Engine candidate supplied during job setup.
        """
        if self.engine:
            engine = cast(IsJobRunnerEngine, self.engine)
            self_with_mixins = cast(IsFuncFlow, self)
            engine.apply_job_decorator(
                JobType.FUNC_FLOW,
                self_with_mixins,
                self._accept_call_func_decorator,
            )

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> type[IsFuncFlowTemplate[_CallP, _RetT]]:
        """Return the template type used to revise this flow.

        Revision operations use this hook to recover the decorator-backed
        function flow template class corresponding to an executable function
        flow instance.

        Returns:
            type[IsFuncFlowTemplate[_CallP, _RetT]]: The [FuncFlowTemplate][]
                class associated with this flow.
        """
        return cast(type[IsFuncFlowTemplate[_CallP, _RetT]], FuncFlowTemplateCore)


LinearFlow.accept_mixin(FlowContextJobMixin)
DagFlow.accept_mixin(FlowContextJobMixin)
FuncFlow.accept_mixin(FlowContextJobMixin)

# TODO: Recursive replace - *args: Any -> *args: object, *kwargs: Any -> *kwargs: object
