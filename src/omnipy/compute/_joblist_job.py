"""Task-list job bases used by linear and DAG flow templates.

This module extends the callable-based job hierarchy with an immutable tuple of
task-template dependencies. Concrete flow template classes compose this base with
`JobTemplateMixin`, which lets flow templates preserve both the callable entrypoint
and the ordered task list across refine/apply/revise operations.
"""

from collections.abc import AsyncGenerator, AsyncIterator, Generator, Iterator
import inspect
import os
from textwrap import dedent
from typing import (Any,
                    Callable,
                    ClassVar,
                    Generic,
                    get_args,
                    get_origin,
                    Literal,
                    NamedTuple,
                    ParamSpec)

from typing_extensions import TypeVar

from omnipy.components.general.tasks import (create_dataset_args,
                                             create_dataset_kwargs,
                                             create_model_args,
                                             create_model_kwargs)
from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute.helpers import create_data_class_task_name, is_func_arg_template_child
from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.protocols.compute.job import ChildJobTemplateLike, IsFuncArgJobTemplate
from omnipy.shared.protocols.data import IsDataset, IsModel
from omnipy.util.callable_types import callable_type_from_flags, CallableType
from omnipy.util.helpers import is_package_editable

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_JOB_TEMPLATE_CHILD_JOB_TEMPLATES_ARGS'] = dedent("""\
            *child_job_templates: Ordered templates of child jobs to be
                run as part of the parent job. Model and Dataset subclasses
                are also allowed, in which case they are converted to
                create_X_from_args (if linear flow) or create_X_from_kwargs
                (if DAG flow) job templates, respectively, when apply() is
                called on the parent job template.""")

    os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_CHILDREN_AND_DATA_CLASSES'] = dedent("""\
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
            True""")

    os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_CALLABLE_TYPE_RULES'] = dedent("""\
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
        Mismatches raise ``TypeError`` when the flow template is created.""")

    os.environ['OMNIPY_MACRO_FLOW_TEMPLATE_VOID_SHORTHAND'] = dedent("""\
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
        the child jobs still perform the actual flow work.""")

    os.environ['OMNIPY_MACRO_LINEAR_FLOW_TEMPLATE_ORCHESTRATION'] = dedent("""\
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
            True""")

    os.environ['OMNIPY_MACRO_DAG_FLOW_TEMPLATE_ORCHESTRATION'] = dedent("""\
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
            True""")


class ChildJobListArgJobBase(FuncArgJobBase[_JobTemplateT, _JobT, _CallP, _RetT],
                             Generic[_JobTemplateT, _JobT, _CallP, _RetT]):
    _coerce_data_class_children_from_kwargs: ClassVar[bool] = False

    class DataClassAndJobParentInfo(NamedTuple):
        dataset_or_model: Literal['dataset', 'model']
        parent_coerces_from_kwargs: bool

    _data_class_child_to_template_map: ClassVar[dict[
        DataClassAndJobParentInfo,
        IsFuncArgJobTemplate,
    ]] = {
        DataClassAndJobParentInfo('dataset', False): create_dataset_args,
        DataClassAndJobParentInfo('dataset', True): create_dataset_kwargs,
        DataClassAndJobParentInfo('model', False): create_model_args,
        DataClassAndJobParentInfo('model', True): create_model_kwargs,
    }

    def __init__(self,
                 job_func: Callable[_CallP, _RetT],
                 /,
                 *child_job_templates: ChildJobTemplateLike,
                 **kwargs: object) -> None:
        super().__init__(job_func, *child_job_templates, **kwargs)
        self._child_job_templates: tuple[ChildJobTemplateLike, ...] = child_job_templates
        self._validate_callable_type_against_child_job_templates()

    def _get_init_args(self) -> tuple[object, ...]:
        return self._job_func, *self._child_job_templates

    @property
    def child_job_templates(self) -> tuple[ChildJobTemplateLike, ...]:
        return self._child_job_templates

    @staticmethod
    def _child_callable_type(child_flow_component: ChildJobTemplateLike) -> CallableType.Literals:
        if inspect.isclass(child_flow_component):
            return CallableType.SYNC_FUNCTION
        else:
            return child_flow_component.callable_type

    @staticmethod
    def _child_return_type(child_flow_component: ChildJobTemplateLike) -> Any:
        if inspect.isclass(child_flow_component):
            return child_flow_component
        else:
            return child_flow_component.return_type

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
        terminal_child_callable_type = self._child_callable_type(terminal_child)
        is_generator = terminal_child_callable_type in (
            CallableType.SYNC_GENERATOR,
            CallableType.ASYNC_GENERATOR,
        )

        if (not is_generator and terminal_child_callable_type in (
                CallableType.SYNC_FUNCTION,
                CallableType.ASYNC_COROUTINE,
        )):
            is_generator = self._return_annotation_is_generator_like(
                self._child_return_type(terminal_child))

        is_async = any(
            self._child_callable_type(child_job_template) in (
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

    def _coerce_class_to_template_for_apply(
            self, child_job_like_cls: type[IsDataset] | type[IsModel]) -> IsFuncArgJobTemplate:
        from omnipy.data.dataset import is_dataset_subclass
        from omnipy.data.model import is_model_subclass

        from_kwargs = self._coerce_data_class_children_from_kwargs

        if is_dataset_subclass(child_job_like_cls):
            info = self.DataClassAndJobParentInfo('dataset', from_kwargs)
        elif is_model_subclass(child_job_like_cls):
            info = self.DataClassAndJobParentInfo('model', from_kwargs)
        else:
            raise TypeError(f'Unsupported child flow component: {child_job_like_cls!r}')

        job_template = self._data_class_child_to_template_map[info]
        return job_template.refine(
            name=create_data_class_task_name(child_job_like_cls, from_kwargs),
            fixed_params={f'{info.dataset_or_model}_cls': child_job_like_cls},
        )

    def _apply(self) -> _JobT:
        if all(is_func_arg_template_child(child) for child in self._child_job_templates):
            return super()._apply()

        coerced_child_job_templates = tuple(
            self._coerce_class_to_template_for_apply(child) if inspect.isclass(child) else child
            for child in self._child_job_templates)

        coerced_template = self._refine(*coerced_child_job_templates)
        return super(
            ChildJobListArgJobBase,
            coerced_template,  # pyright: ignore[reportArgumentType]
        )._apply()

    def _refine(self,
                *child_job_templates: ChildJobTemplateLike,
                update: bool = True,
                **kwargs: object) -> _JobTemplateT:

        refined_template = super()._refine(
            *child_job_templates,
            update=update,
            **kwargs,
        )
        return refined_template
