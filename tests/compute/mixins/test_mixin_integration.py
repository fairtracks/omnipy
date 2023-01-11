from inspect import Parameter

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model

from ..cases.raw.functions import (all_data_files_plus_str_func,
                                   power_m1_func,
                                   single_data_file_plus_str_func)


def test_iterate_over_data_files_func_signature() -> None:
    all_plus_no_iter_template = TaskTemplate(
        all_data_files_plus_str_func,
        iterate_over_data_files=False,
    )

    all_plus_iter_template = TaskTemplate(
        single_data_file_plus_str_func,
        iterate_over_data_files=True,
    )

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


def test_refine_task_template_with_other_properties_task() -> None:
    # Plain task template
    power_m1_template = TaskTemplate(power_m1_func)
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
    assert my_power(num=3) == {'by_the_power_of_grayskull': 26}

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
    assert my_power_2(numb=3, min=False) == {'by_the_power_of_grayskull': 27}

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
    assert my_power_3(exponent=3) == 27

    # One-liner to reset properties to default values
    my_power_4 = my_power_3.revise().refine(update=False).apply()
    assert my_power_4 == power_m1
    assert my_power_4(number=3, exponent=3, minus_one=False) == 27
