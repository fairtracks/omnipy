"""Test interactions between compute task mixins."""

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Generator
from inspect import isawaitable, Parameter
from typing import cast

import pytest

from omnipy.compute.flow import DagFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..cases.raw.functions import (all_int_dataset_plus_int_return_str_dataset_func,
                                   async_single_int_model_plus_int_return_str_model_func,
                                   power_m1_func,
                                   single_int_model_plus_int_return_str_model_func)
from ..helpers.classes import CustomStrDataset


def test_iterate_over_data_files_func_signature() -> None:
    all_plus_no_iter_template = TaskTemplate(iterate_over_data_files=False)(
        all_int_dataset_plus_int_return_str_dataset_func)

    all_plus_iter_template = TaskTemplate(iterate_over_data_files=True)(
        single_int_model_plus_int_return_str_model_func)

    for task_template in (all_plus_no_iter_template, all_plus_iter_template):
        for task_obj in task_template, task_template.apply():
            assert task_obj.param_signatures == {
                'dataset':
                    Parameter(
                        'dataset', Parameter.POSITIONAL_OR_KEYWORD, annotation=Dataset[Model[int]]),
                'number':
                    Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            }
            assert task_obj.return_type is Dataset[Model[str]]


def test_iterate_over_data_files_func_signature_output_dataset_cls() -> None:
    all_plus_iter_template = TaskTemplate(
        iterate_over_data_files=True, output_dataset_cls=CustomStrDataset)(
            single_int_model_plus_int_return_str_model_func)

    for task_obj in all_plus_iter_template, all_plus_iter_template.apply():
        assert task_obj.param_signatures == {
            'dataset':
                Parameter(
                    'dataset', Parameter.POSITIONAL_OR_KEYWORD, annotation=Dataset[Model[int]]),
            'number':
                Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        }
        assert task_obj.return_type is CustomStrDataset


def test_iterate_over_data_files_func_signature_output_dataset_param() -> None:
    all_plus_iter_template = TaskTemplate(
        iterate_over_data_files=True,
        output_dataset_param='output_dataset',
    )(
        single_int_model_plus_int_return_str_model_func)

    for task_obj in all_plus_iter_template, all_plus_iter_template.apply():
        assert task_obj.param_signatures == {
            'dataset':
                Parameter(
                    'dataset', Parameter.POSITIONAL_OR_KEYWORD, annotation=Dataset[Model[int]]),
            'number':
                Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            'output_dataset':
                Parameter(
                    'output_dataset',
                    Parameter.KEYWORD_ONLY,
                    default=None,
                    annotation=Dataset[Model[str]])
        }
        assert task_obj.return_type is Dataset[Model[str]]


def test_iterate_over_data_files_func_signature_output_dataset_param_and_cls() -> None:
    all_plus_iter_template = TaskTemplate(
        iterate_over_data_files=True,
        output_dataset_param='output_dataset',
        output_dataset_cls=CustomStrDataset,
    )(
        single_int_model_plus_int_return_str_model_func)

    for task_obj in all_plus_iter_template, all_plus_iter_template.apply():
        assert task_obj.param_signatures == {
            'dataset':
                Parameter(
                    'dataset', Parameter.POSITIONAL_OR_KEYWORD, annotation=Dataset[Model[int]]),
            'number':
                Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            'output_dataset':
                Parameter(
                    'output_dataset',
                    Parameter.KEYWORD_ONLY,
                    default=None,
                    annotation=CustomStrDataset)
        }
        assert task_obj.return_type is CustomStrDataset


def test_iterate_over_data_files() -> None:
    task_template_cls = TaskTemplate(iterate_over_data_files=True)
    single_data_file_plus_str_template = task_template_cls(
        single_int_model_plus_int_return_str_model_func)

    dataset = Dataset[Model[int]]({'a': 5, 'b': -2})
    assert single_data_file_plus_str_template.run(
        dataset, number=2) == Dataset[Model[str]]({  # type: ignore[arg-type]
            'a': '7', 'b': '0'
        })


def test_iterate_over_data_files_output_dataset_cls() -> None:
    task_template_cls = TaskTemplate(
        iterate_over_data_files=True,
        output_dataset_cls=CustomStrDataset,
    )
    single_data_file_plus_str_template = task_template_cls(
        single_int_model_plus_int_return_str_model_func)

    dataset = Dataset[Model[int]]({'a': 5, 'b': -2})
    assert single_data_file_plus_str_template.run(
        dataset, number=2) == CustomStrDataset({  # type: ignore[arg-type]
            'a': '7', 'b': '0'
        })


def test_iterate_over_data_files_param() -> None:
    task_template_cls = TaskTemplate(
        fixed_params=dict(number=2),
        param_key_map=dict(dataset='data_numbers'),
        iterate_over_data_files=True,
    )

    single_data_file_plus_str_template = task_template_cls(
        single_int_model_plus_int_return_str_model_func)

    dataset = Dataset[Model[int]]({'a': 5, 'b': -2})
    assert single_data_file_plus_str_template.run(
        data_numbers=dataset,) == Dataset[Model[str]]({  # type: ignore[call-arg]
            'a': '7', 'b': '0'
        })


def test_refine_task_template_with_other_properties_task() -> None:
    # Plain task template
    power_m1_template = TaskTemplate()(power_m1_func)
    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15

    # Refine task template with all properties (update=True)
    my_power_template = power_m1_template.refine(
        name='magic_power',
        param_key_map=dict(number='num', exponent='exp'),
        result_key='by_the_power_of_grayskull',
        fixed_params=dict(exponent=3),
    )
    assert my_power_template != power_m1_template
    for my_power_obj in my_power_template, my_power_template.apply():
        assert my_power_obj.name == 'magic_power'
        assert my_power_obj.param_key_map == dict(number='num', exponent='exp')
        assert my_power_obj.result_key == 'by_the_power_of_grayskull'
        assert my_power_obj.fixed_params == {'exponent': 3}

    my_power = my_power_template.apply()
    assert my_power != power_m1
    assert my_power(num=3) == {'by_the_power_of_grayskull': 26}  # type: ignore[call-arg]

    # Refine task template with two properties (update=True)
    my_power_template_2 = my_power_template.refine(
        param_key_map=[('number', 'numb'), ('minus_one', 'min')],)  # noqa
    assert my_power_template_2 != my_power_template
    for my_power_obj_2 in my_power_template_2, my_power_template_2.apply():
        assert my_power_obj_2.name == 'magic_power'
        assert my_power_obj_2.param_key_map == dict(number='numb', exponent='exp', minus_one='min')
        assert my_power_obj_2.result_key == 'by_the_power_of_grayskull'
        assert my_power_obj_2.fixed_params == {'exponent': 3}

    my_power_2 = my_power_template_2.apply()
    assert my_power_2 != my_power
    exp_result = {'by_the_power_of_grayskull': 27}
    assert my_power_2(numb=3, min=False) == exp_result  # type: ignore[call-arg]

    # Refine task template with single property (update=False)
    my_power_template_3 = my_power_template_2.refine(
        fixed_params=dict(number=3, minus_one=False), update=False)
    assert my_power_template_3 != my_power_template_2
    for my_power_obj_3 in my_power_template_3, my_power_template_3.apply():
        assert my_power_obj_3.name == 'power_m1_func'
        assert my_power_obj_3.param_key_map == {}
        assert my_power_obj_3.result_key is None
        assert my_power_obj_3.fixed_params == dict(number=3, minus_one=False)

    my_power_3 = my_power_template_3.apply()
    assert my_power_3 != my_power_2
    assert my_power_3(exponent=3) == 27  # type: ignore[call-arg]

    # One-liner to reset properties to default values
    my_power_4 = my_power_3.revise().refine(update=False).apply()
    assert my_power_4 == power_m1
    assert my_power_4(number=3, exponent=3, minus_one=False) == 27


async def _resolve_maybe_awaitable(result: object) -> object:
    if isinstance(result, asyncio.Task):
        return await result

    if isawaitable(result):
        awaitable_result = cast(Awaitable[object], result)
        return await awaitable_result

    return result


@pytest.mark.anyio
async def test_async_linear_flow_iterate_and_auto_async_dataset_transform() -> None:
    async_iterate_task = TaskTemplate(
        iterate_over_data_files=True,
        auto_async=True,
    )(
        async_single_int_model_plus_int_return_str_model_func)

    @LinearFlowTemplate(async_iterate_task)
    async def async_linear_flow_tmpl(dataset: Dataset[Model[int]],
                                     number: int) -> Dataset[Model[str]]:
        ...

    dataset = Dataset[Model[int]]({'a': 3, 'b': 5, 'c': -2})
    flow_result = await _resolve_maybe_awaitable(async_linear_flow_tmpl.run(dataset, number=2))

    assert isinstance(flow_result, Dataset)
    assert flow_result.to_data() == {'a': '5', 'b': '7', 'c': '0'}


@pytest.mark.anyio
async def test_async_dag_flow_params_and_result_key_preserve_public_non_dataset_shape() -> None:
    @TaskTemplate()
    async def async_seed(number: int) -> int:
        await asyncio.sleep(0)
        return number + 1

    @TaskTemplate(
        fixed_params={'multiplier': 3},
        param_key_map={
            'multiplier': 'factor', 'offset': 'step'
        },
        result_key='computed',
    )
    def transform(seed: int, multiplier: int, offset: int) -> int:
        return seed * multiplier + offset

    @DagFlowTemplate(async_seed.refine(result_key='seed'), transform)
    async def async_dag_flow_tmpl(number: int, factor: int, step: int) -> dict[str, int]:
        ...

    flow_result = await _resolve_maybe_awaitable(
        async_dag_flow_tmpl.run(number=4, factor=99, step=2))

    assert flow_result == {'computed': 17}


def test_dense_async_task_mixin_stack_with_iterate_auto_async_and_result_key() -> None:
    @TaskTemplate(
        iterate_over_data_files=True,
        output_dataset_param='output_dataset',
        output_dataset_cls=CustomStrDataset,
        auto_async=True,
        fixed_params={'other_number': 2},
        param_key_map={
            'number': 'step', 'other_number': 'bonus'
        },
        result_key='wrapped_dataset',
    )
    async def async_dense_transform(
        data_number: Model[int],
        number: int = 0,
        other_number: int = 0,
    ) -> Model[str]:
        await asyncio.sleep(0)
        return str(data_number.content + number + other_number)  # type: ignore[return-value]

    dataset = Dataset[Model[int]]({'a': 3, 'b': -2})
    output_dataset = CustomStrDataset()

    wrapped_result = async_dense_transform.run(
        dataset,
        step=1,  # type: ignore[call-arg]
        output_dataset=output_dataset,  # type: ignore[call-arg]
    )

    assert isinstance(wrapped_result, dict)
    assert set(wrapped_result.keys()) == {'wrapped_dataset'}
    assert wrapped_result['wrapped_dataset'] is output_dataset
    assert output_dataset.to_data() == {'a': '6', 'b': '1'}


@pytest.mark.anyio
@pytest.mark.parametrize('generator_kind', ['sync', 'async'])
async def test_result_key_preserves_sync_and_async_generator_shapes(generator_kind: str) -> None:
    if generator_kind == 'sync':

        @TaskTemplate(result_key='values')
        def sync_emit_values(start: int) -> Generator[int, None, None]:
            for value in range(start, start + 3):
                yield value

        wrapped_result = cast(dict[str, object], sync_emit_values.run(start=2))
        values = cast(Generator[int, None, None], wrapped_result['values'])
        assert list(values) == [2, 3, 4]

    else:

        @TaskTemplate(result_key='values')
        async def async_emit_values(start: int) -> AsyncGenerator[int, None]:
            for value in range(start, start + 3):
                await asyncio.sleep(0)
                yield value

        wrapped_result = cast(dict[str, object], async_emit_values.run(start=2))
        values = cast(AsyncGenerator[int, None], wrapped_result['values'])
        assert [value async for value in values] == [2, 3, 4]
