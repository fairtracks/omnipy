import re
from typing import TypeGuard

from omnipy.compute._func_job import FuncArgJobBase
from omnipy.compute._job import JobTemplateMixin
from omnipy.shared.protocols.compute.job import IsFuncArgJobTemplate
from omnipy.shared.protocols.data import IsDataset, IsModel


class Void:
    """
    Empty sync/async iterable for signature-only generator flow bodies.

    Use this when a flow template body exists only to define a generator or
    async-generator callable signature, while the child jobs perform the
    actual work.

    Examples:
        @LinearFlowTemplate(task_one, generator_task_two)
        def my_sync_generator_flow(number: int) -> Generator[int, None, None]:
            yield from Void()  # For generator signature only; never run.

        @DagFlowTemplate(task_one, generator_task_two)
        async def my_async_generator_flow(number: int) -> AsyncGenerator[int, None]:
            async for _ in Void():  # For generator signature only; never run.
                yield _
    """
    def __iter__(self):
        return iter(())

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


def is_func_arg_template_child(child: object) -> TypeGuard[IsFuncArgJobTemplate]:
    return isinstance(child, FuncArgJobBase) and isinstance(child, JobTemplateMixin)


def underscore_data_class_name(data_cls: type[IsDataset] | type[IsModel]) -> str:
    import inflection

    raw_name = data_cls.__name__
    underscored_name = inflection.underscore(raw_name.replace(' ', ''))
    underscored_name = re.sub(r'[^0-9a-zA-Z]+', '_', underscored_name).strip('_').lower()
    return underscored_name if underscored_name else 'data'


def create_data_class_task_name(
    data_cls: type[IsDataset] | type[IsModel],
    from_kwargs: bool,
) -> str:
    data_cls_name = underscore_data_class_name(data_cls)

    if from_kwargs:
        return f'create_{data_cls_name}_from_kwargs'
    else:
        return f'create_{data_cls_name}_from_args'
