from inspect import Parameter

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..cases.raw.functions import (all_int_dataset_plus_int_return_str_dataset_func,
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
    assert my_power_2(
        numb=3,  # type: ignore[call-arg]
        min=False,
    ) == {
        'by_the_power_of_grayskull': 27
    }

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
