import pytest

from unifair.compute.flow import Flow, FlowTemplate


def test_init() -> None:
    flow_template = FlowTemplate()
    assert isinstance(flow_template, FlowTemplate)

    with pytest.raises(TypeError):
        FlowTemplate('extra_positional_argument')

    with pytest.raises(RuntimeError):
        Flow()

    flow = flow_template.apply()
    assert isinstance(flow, Flow)


#
# def test_flow_run_action_func_no_params(action_func_no_params: Callable[[], None]) -> None:
#     flow_template = FlowTemplate(action_func_no_params)
#     with pytest.raises(TypeError):
#         flow_template()  # noqa
#
#     flow = flow_template.apply()
#     assert flow() is None
#
#
# def test_flow_run_action_func_with_params(
#         action_func_with_params: Callable[[str, bool], None]) -> None:
#     flow_template = FlowTemplate(action_func_with_params)
#     with pytest.raises(TypeError):
#         flow_template('rm -rf *', verbose=True)  # noqa
#
#     flow = flow_template.apply()
#     assert flow('rm -rf *', verbose=True) is None
#
#
# def test_flow_run_data_import_func(data_import_func: Callable[[], str]) -> None:
#     flow_template = FlowTemplate(data_import_func)
#     with pytest.raises(TypeError):
#         flow_template()  # noqa
#
#     flow = flow_template.apply()
#     json_data = flow()
#     assert type(json_data) is str
#     assert json.loads(json_data) == dict(my_data=[123, 234, 345, 456])
#
#
# def test_flow_run_format_to_string_func(format_to_string_func: Callable[[str, int], str]) -> None:
#     flow_template = FlowTemplate(format_to_string_func)
#     with pytest.raises(TypeError):
#         flow_template('Number', 12)  # noqa
#
#     flow = flow_template.apply()
#     assert flow('Number', 12) == 'Number: 12'
#
#
# def test_flow_run_parameter_variants(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1 = FlowTemplate(power_m1_func).apply()
#
#     assert power_m1(4, 3) == 63
#     assert power_m1(4, exponent=3) == 63
#     assert power_m1(number=4, exponent=3) == 63
#     assert power_m1(4, 3, False) == 64
#     assert power_m1(4, 3, minus_one=False) == 64
#     assert power_m1(4, exponent=3, minus_one=False) == 64
#     assert power_m1(number=4, exponent=3, minus_one=False) == 64
#
#
# def test_error_missing_flow_run_parameters(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1 = FlowTemplate(power_m1_func).apply()
#
#     with pytest.raises(TypeError):
#         power_m1()
#
#     with pytest.raises(TypeError):
#         power_m1(5)
#
#     with pytest.raises(TypeError):
#         power_m1(4, minus_one=False)
#
#
# def test_property_param_signature_and_return_type_action_func_no_params(
#         action_func_no_params: Callable[[], None]) -> None:
#     flow_template = FlowTemplate(action_func_no_params)
#     for flow_obj in flow_template, flow_template.apply():
#         assert flow_obj.param_signatures == {}
#         assert flow_obj.return_type is None
#
#
# def test_property_param_signature_and_return_type_data_import_func(
#         data_import_func: Callable[[], str]) -> None:
#     flow_template = FlowTemplate(data_import_func)
#     for flow_obj in flow_template, flow_template.apply():
#         assert flow_obj.param_signatures == {}
#         assert flow_obj.return_type is str
#
#
# def test_property_param_signature_and_return_type_format_to_string_funcs(
#         format_to_string_func: Callable[[str, int], str]) -> None:
#     flow_template = FlowTemplate(format_to_string_func)
#     for flow_obj in flow_template, flow_template.apply():
#         assert flow_obj.param_signatures == {
#             'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
#             'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
#         }
#         assert flow_obj.return_type is str
#
#
# def test_property_param_signature_and_return_type_immutable(
#         format_to_string_func: Callable[[str, int], str]) -> None:
#     flow_template = FlowTemplate(format_to_string_func)
#     for flow_obj in flow_template, flow_template.apply():
#         with pytest.raises(AttributeError):
#             flow_obj.param_signatures = {}  # noqa
#
#         with pytest.raises(TypeError):
#             flow_obj.param_signatures['new'] = Parameter(  # noqa
#                 'new', Parameter.POSITIONAL_OR_KEYWORD, annotation=bool)
#
#         with pytest.raises(AttributeError):
#             flow_obj.return_type = int
#
#
# def test_property_name_default(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func)
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.name == 'power_m1_func'
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.name = 'cool_func'
#
#
# def test_property_name_change(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func, name='power_m1')
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.name == 'power_m1'
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.name = 'cool_func'
#
#
# def test_property_name_validation(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func, name=None)
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.name == 'power_m1_func'
#
#     with pytest.raises(ValueError):
#         FlowTemplate(power_m1_func, name='')
#
#     with pytest.raises(TypeError):
#         FlowTemplate(power_m1_func, name=123)  # noqa
#
#
# def test_property_fixed_params_default(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func)
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.fixed_params == {}
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.fixed_params = {'number': 'num'}
#
#         with pytest.raises(TypeError):
#             power_m1_obj.fixed_params['number'] = 'num'  # noqa
#
#     power_m1 = power_m1_template.apply()
#     assert power_m1(number=4, exponent=3) == 63
#
#
# def test_property_fixed_params_last_args(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     square_template = FlowTemplate(power_m1_func, fixed_params=dict(exponent=2, minus_one=False))
#     for square_obj in square_template, square_template.apply():
#         assert square_obj.fixed_params == {'exponent': 2, 'minus_one': False}
#
#         with pytest.raises(AttributeError):
#             square_obj.fixed_params = {'number': 'num'}
#
#         with pytest.raises(TypeError):
#             square_obj.fixed_params['minus_one'] = True  # noqa
#
#         with pytest.raises(TypeError):
#             del square_obj.fixed_params['minus_one']  # noqa
#
#     square = square_template.apply()
#
#     assert square(4) == 16
#     assert square(number=5) == 25
#
#     with pytest.raises(TypeError):
#         square()
#
#     with pytest.raises(TypeError):
#         square(exponent=5)
#
#     with pytest.raises(TypeError):
#         square(minus_one=True)
#
#     with pytest.raises(TypeError):
#         square(4, 3)
#
#         with pytest.raises(TypeError):
#             square(4, minus_one=True)
#
#
# def test_property_fixed_params_first_arg(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     two_power_m1_template = FlowTemplate(power_m1_func, fixed_params=dict(number=2))  # noqa
#     for two_power_m1_obj in two_power_m1_template, two_power_m1_template.apply():
#         assert two_power_m1_obj.fixed_params == {'number': 2}
#
#     two_power_m1 = two_power_m1_template.apply()
#     assert two_power_m1(exponent=4) == 15
#     assert two_power_m1(exponent=4, minus_one=False) == 16
#
#     with pytest.raises(TypeError):
#         two_power_m1()
#
#     with pytest.raises(TypeError):
#         two_power_m1(3)
#
#     with pytest.raises(TypeError):
#         two_power_m1(3, False)
#
#     with pytest.raises(TypeError):
#         two_power_m1(3, minus_one=False)
#
#     with pytest.raises(TypeError):
#         two_power_m1(minus_one=False)
#
#
# def test_property_fixed_params_all_args(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     seven_template = FlowTemplate(power_m1_func, fixed_params=dict(number=2, exponent=3))  # noqa
#     for seven_obj in seven_template, seven_template.apply():
#         assert seven_obj.fixed_params == {'number': 2, 'exponent': 3}
#
#     seven = seven_template.apply()
#     assert seven() == 7
#     assert seven(minus_one=False) == 8
#
#     with pytest.raises(TypeError):
#         seven(False)
#
#     with pytest.raises(TypeError):
#         seven(number=3)
#
#     with pytest.raises(TypeError):
#         seven(3, 4)
#
#     with pytest.raises(TypeError):
#         seven(3, 4, False)
#
#     with pytest.raises(TypeError):
#         seven(number=3, exponent=4)
#
#     with pytest.raises(TypeError):
#         seven(number=3, exponent=4, minus_one=False)
#
#
# def test_property_fixed_params_validation(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     seven_template = FlowTemplate(
#         power_m1_func, fixed_params=[('number', 4), ('exponent', 2)])  # noqa
#     for seven_obj in seven_template, seven_template.apply():
#         assert seven_obj.fixed_params == {'number': 4, 'exponent': 2}
#
#     for val in ({}, [], None):
#         power_m1_template = FlowTemplate(power_m1_func, fixed_params=val)  # noqa
#         for power_m1_obj in power_m1_template, power_m1_template.apply():
#             assert power_m1_obj.fixed_params == {}
#
#
# def test_property_param_key_map_default(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func)
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.param_key_map == {}
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.param_key_map = {'text': 'title'}
#
#         with pytest.raises(TypeError):
#             power_m1_obj.param_key_map['text'] = 'title'  # noqa
#
#     power_m1 = power_m1_template.apply()
#
#     assert power_m1(number=4, exponent=3) == 63
#
#
# def test_property_param_key_map_change(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func, param_key_map=dict(number='n', minus_one='m'))
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.param_key_map == {'number': 'n', 'minus_one': 'm'}
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.param_key_map = {}
#
#         with pytest.raises(TypeError):
#             power_m1_obj.param_key_map['number'] = 'n2'  # noqa
#
#         with pytest.raises(TypeError):
#             del power_m1_obj.param_key_map['minus_one']  # noqa
#
#     power_m1 = power_m1_template.apply()
#
#     assert power_m1(4, 3) == 63
#     assert power_m1(n=4, exponent=3) == 63
#     assert power_m1(4, exponent=3) == 63
#     assert power_m1(4, 3, m=False) == 64
#     assert power_m1(4, 3, False) == 64
#
#     with pytest.raises(TypeError):
#         power_m1(5)
#
#     with pytest.raises(TypeError):
#         power_m1(number=5, exponent=3)
#
#     with pytest.raises(TypeError):
#         power_m1(n=5, number=5, exponent=3)
#
#     with pytest.raises(TypeError):
#         power_m1(n=5, exponent=3, minus_one=False)
#
#     with pytest.raises(TypeError):
#         power_m1(n=5, exponent=3, m=False, minus_one=False)
#
#     with pytest.raises(TypeError):
#         power_m1(5, 3, extra_attr=123)
#
#
# def test_property_param_key_map_validation(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(
#         power_m1_func, param_key_map=[('number', 'n'), ('exponent', 'e')])  # noqa
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.param_key_map == {'number': 'n', 'exponent': 'e'}
#
#     for val in ({}, [], None):
#         power_m1_template = FlowTemplate(power_m1_func, param_key_map=val)
#         for power_m1_obj in power_m1_template, power_m1_template.apply():
#             assert power_m1_obj.param_key_map == {}
#
#     with pytest.raises(ValueError):
#         FlowTemplate(power_m1_func, param_key_map={'number': 'same', 'exponent': 'same'})
#
#
# def test_property_result_key_default(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func)
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.result_key is None
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.result_key = 'i_have_the_power'
#
#     power_m1 = power_m1_template.apply()
#     assert power_m1(4, 2) == 15
#
#
# def test_property_result_key_change(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func, result_key='i_have_the_power')
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.result_key == 'i_have_the_power'
#
#         with pytest.raises(AttributeError):
#             power_m1_obj.result_key = None
#
#     power_m1 = power_m1_template.apply()
#     assert power_m1(4, 2) == {'i_have_the_power': 15}
#
#
# def test_property_result_key_validation(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func, result_key=None)
#     for power_m1_obj in power_m1_template, power_m1_template.apply():
#         assert power_m1_obj.result_key is None
#
#     with pytest.raises(ValueError):
#         FlowTemplate(power_m1_func, result_key='')
#
#     with pytest.raises(TypeError):
#         FlowTemplate(power_m1_func, result_key=123)  # noqa
#
#
# def test_equal(format_to_string_func: Callable[[str, int], str],
#                power_m1_func: Callable[[int, int, bool], int]) -> None:
#     fts_tmpl = FlowTemplate(format_to_string_func)
#     fts_tmpl_2 = FlowTemplate(format_to_string_func)
#     for (fts_obj, fts_obj_2) in [(fts_tmpl, fts_tmpl_2), (fts_tmpl.apply(), fts_tmpl_2.apply())]:
#         assert fts_obj == fts_obj_2
#
#     pm1_tmpl = FlowTemplate(power_m1_func)
#     for (fts_obj, pm1_obj) in [(fts_tmpl, pm1_tmpl), (fts_tmpl.apply(), pm1_tmpl.apply())]:
#         assert fts_obj != pm1_obj
#
#     pm1_tmpl_2 = FlowTemplate(power_m1_func, name='other')
#     for (pm1_obj, pm1_obj_2) in [(pm1_tmpl, pm1_tmpl_2), (pm1_tmpl.apply(), pm1_tmpl_2.apply())]:
#         assert pm1_obj != pm1_obj_2
#
#     pm1_tmpl_3 = FlowTemplate(power_m1_func, fixed_params={'number': 2})
#     for (pm1_obj, pm1_obj_3) in [(pm1_tmpl, pm1_tmpl_3), (pm1_tmpl.apply(), pm1_tmpl_3.apply())]:
#         assert pm1_obj != pm1_obj_3
#
#     pm1_tmpl_4 = FlowTemplate(power_m1_func, param_key_map={'number': 'num'})
#     for (pm1_obj, pm1_obj_4) in [(pm1_tmpl, pm1_tmpl_4), (pm1_tmpl.apply(), pm1_tmpl_4.apply())]:
#         assert pm1_obj != pm1_obj_4
#
#     pm1_tmpl_5 = FlowTemplate(power_m1_func, result_key='result')
#     for (pm1_obj, pm1_obj_5) in [(pm1_tmpl, pm1_tmpl_5), (pm1_tmpl.apply(), pm1_tmpl_5.apply())]:
#         assert pm1_obj != pm1_obj_5
#
#
# def test_refine_flow_template_with_fixed_params(
#         power_m1_func: Callable[[int, int, bool], int]) -> None:
#     # Plain flow template
#     power_m1_template = FlowTemplate(power_m1_func)
#     power_m1 = power_m1_template.apply()
#     assert power_m1(3, 2) == 8
#
#     # Refine flow template (update=True)
#     square_template = power_m1_template.refine(fixed_params=dict(exponent=2, minus_one=False))
#     assert square_template != power_m1_template
#     for square_obj in square_template, square_template.apply():
#         assert square_obj.fixed_params == dict(exponent=2, minus_one=False)
#         assert square_obj.fixed_params.get('minus_one') is False
#
#     square = square_template.apply()
#     assert square != power_m1
#     assert square(3) == 9
#
#     # Refine flow template with list of tuples format (update=True)
#     cube_template = square_template.refine(fixed_params=[('exponent', 3)])  # noqa
#     assert cube_template != square_template
#     for cube_obj in cube_template, cube_template.apply():
#         assert cube_obj.fixed_params == dict(exponent=3, minus_one=False)
#         assert cube_obj.fixed_params.get('minus_one') is False
#
#     cube = cube_template.apply()
#     assert cube != square
#     assert cube(3) == 27
#
#     # Refine flow template with update=False
#     hypercube_template = cube_template.refine(fixed_params=dict(exponent=4), update=False)
#     assert hypercube_template != cube_template
#     for hypercube_obj in hypercube_template, hypercube_template.apply():
#         assert hypercube_obj.fixed_params == dict(exponent=4)
#         assert hypercube_obj.fixed_params.get('minus_one') is None
#
#     hypercube = hypercube_template.apply()
#     assert hypercube != cube
#     assert hypercube(3) == 80
#
#     # Resetting fixed_params does not work with update=True
#     reset_power_m1_template = hypercube_template.refine(fixed_params={})
#     assert reset_power_m1_template == hypercube_template
#     assert reset_power_m1_template.fixed_params == dict(exponent=4)
#
#     # Reset fixed_params with update=False
#     for val in ({}, [], None):
#         reset_power_m1_template = hypercube_template.refine(fixed_params=val, update=False)
#         assert reset_power_m1_template == power_m1_template
#         for reset_power_m1_obj in reset_power_m1_template, reset_power_m1_template.apply():
#             assert reset_power_m1_obj.fixed_params == {}
#             assert reset_power_m1_obj.fixed_params.get('minus_one') is None
#
#     reset_power_m1 = reset_power_m1_template.apply()
#     assert reset_power_m1 == power_m1
#     assert reset_power_m1(3, 2) == 8
#
#
# def test_refine_flow_template_with_other_properties(
#         power_m1_func: Callable[[int, int, bool], int]) -> None:
#     # Plain flow template
#     power_m1_template = FlowTemplate(power_m1_func)
#     power_m1 = power_m1_template.apply()
#     assert power_m1(4, 2) == 15
#
#     # Refine flow template with all properties (update=True)
#     my_power_template = power_m1_template.refine(
#         name='magic_power',
#         param_key_map=dict(number='num', exponent='exp'),
#         result_key='by_the_power_of_grayskull',
#     )
#     assert my_power_template != power_m1_template
#     for my_power_obj in my_power_template, my_power_template.apply():
#         assert my_power_obj.name == 'magic_power'
#         assert my_power_obj.param_key_map == dict(number='num', exponent='exp')
#         assert my_power_obj.result_key == 'by_the_power_of_grayskull'
#
#     my_power = my_power_template.apply()
#     assert my_power != power_m1
#     assert my_power(num=3, exp=3) == {'by_the_power_of_grayskull': 26}
#
#     # Refine flow template with single property (update=True)
#     my_power_template_2 = my_power_template.refine(
#         param_key_map=[('exponent', 'expo'), ('minus_one', 'min')],)  # noqa
#     assert my_power_template_2 != my_power_template
#     for my_power_obj_2 in my_power_template_2, my_power_template_2.apply():
#         assert my_power_obj_2.name == 'magic_power'
#         assert my_power_obj_2.param_key_map == dict(number='num', exponent='expo', minus_one='min')
#         assert my_power_obj_2.result_key == 'by_the_power_of_grayskull'
#
#     my_power_2 = my_power_template_2.apply()
#     assert my_power_2 != my_power
#     assert my_power_2(num=3, expo=3, min=False) == {'by_the_power_of_grayskull': 27}
#
#     # Refine flow template with single property (update=False)
#     my_power_template_3 = my_power_template_2.refine(
#         param_key_map=dict(exponent='expo', minus_one='min'), update=False)
#     assert my_power_template_3 != my_power_template_2
#     for my_power_obj_3 in my_power_template_3, my_power_template_3.apply():
#         assert my_power_obj_3.name == 'power_m1_func'
#         assert my_power_obj_3.param_key_map == dict(exponent='expo', minus_one='min')
#         assert my_power_obj_3.result_key is None
#
#     my_power_3 = my_power_template_3.apply()
#     assert my_power_3 != my_power_2
#     assert my_power_3(number=3, expo=3, min=False) == 27
#
#     # Resetting param_key_map does not work with update=True
#     my_power_template_4 = my_power_template_3.refine(param_key_map={})
#     assert my_power_template_4 == my_power_template_3
#     for my_power_obj_4 in my_power_template_4, my_power_template_4.apply():
#         assert my_power_obj_4.param_key_map == dict(exponent='expo', minus_one='min')
#
#     # Reset param_key_map with update=False
#     for val in ({}, [], None):
#         my_power_template_4 = my_power_template_3.refine(param_key_map=val, update=False)
#         assert my_power_template_4 == power_m1_template
#         for my_power_obj_4 in my_power_template_4, my_power_template_4.apply():
#             assert my_power_obj_4.param_key_map == {}
#
#     my_power_4 = my_power_template_4.apply()
#     assert my_power_4 == power_m1
#     assert my_power_4(number=3, exponent=3, minus_one=False) == 27
#
#
# def test_revise_refine_flow_template_with_fixed_params_and_other_properties(
#         power_m1_func: Callable[[int, int, bool], int]) -> None:
#     # New flow template with fixed params and other properties set
#     square_template = FlowTemplate(power_m1_func).refine(
#         name='square',
#         param_key_map=dict(number='num', exponent='exp'),
#         fixed_params=dict(exponent=2, minus_one=False),
#     )
#     for square_obj in square_template, square_template.apply():
#         assert square_obj.name == 'square'
#         assert square_obj.param_key_map == dict(number='num', exponent='exp')
#         assert square_obj.result_key is None
#         assert square_obj.fixed_params == {'exponent': 2, 'minus_one': False}
#
#     square = square_template.apply()
#     assert square(num=3) == 9
#
#     # Revise flow into flow_template
#     square_revised_template = square.revise()
#     assert isinstance(square_revised_template, FlowTemplate)
#     assert square_revised_template == square_template
#
#     for square_revised_obj in square_revised_template, square_revised_template.apply():
#         assert square_revised_obj.name == 'square'
#         assert square_revised_obj.param_key_map == dict(number='num', exponent='exp')
#         assert square_revised_obj.result_key is None
#         assert square_revised_obj.fixed_params == {'exponent': 2, 'minus_one': False}
#
#     # Refine revised flow_template with update=False to reset param_key_map
#     square_refined = square_revised_template.refine(
#         name=square_revised_template.name,
#         fixed_params=square_revised_template.fixed_params,
#         update=False).apply()
#
#     assert square_refined.name == 'square'
#     assert square_refined.param_key_map == {}
#     assert square_refined.result_key is None
#     assert square_refined.fixed_params == {'exponent': 2, 'minus_one': False}
#
#     assert square_refined(number=3) == 9
#
#     # One-liner to reset flow to original template
#     power_reset = square_refined.revise().refine(update=False).apply()
#     assert power_reset == FlowTemplate(power_m1_func).apply()
#     assert power_reset.name == 'power_m1_func'
#     assert power_reset.param_key_map == {}
#     assert power_reset.result_key is None
#     assert power_reset.fixed_params == {}
#
#
# def test_revise_refine_dicts_are_copied(power_m1_func: Callable[[int, int, bool], int]) -> None:
#     square_template = FlowTemplate(
#         power_m1_func,
#         name='square',
#         param_key_map=dict(number='num'),
#         fixed_params=dict(exponent=2),
#     )
#
#     square_refined_template = square_template.refine(
#         param_key_map=dict(exponent='exp'),
#         fixed_params=dict(minus_one=False),
#     )
#
#     assert len(square_template.param_key_map) == 1
#     assert len(square_template.fixed_params) == 1
#     assert len(square_refined_template.param_key_map) == 2
#     assert len(square_refined_template.fixed_params) == 2
#
#     square = square_template.apply()
#     square_revised_template = square.revise()
#     square_revised_refined_template = square_revised_template.refine(
#         param_key_map=dict(exponent='exp'),
#         fixed_params=dict(minus_one=False),
#     )
#
#     assert len(square_template.param_key_map) == 1
#     assert len(square_template.fixed_params) == 1
#     assert len(square.param_key_map) == 1
#     assert len(square.fixed_params) == 1
#     assert id(square.param_key_map) != id(square_template.param_key_map)
#     assert id(square.fixed_params) != id(square_template.fixed_params)
#
#     assert len(square_revised_template.param_key_map) == 1
#     assert len(square_revised_template.fixed_params) == 1
#     assert id(square_revised_template.param_key_map) != id(square.param_key_map)
#     assert id(square_revised_template.fixed_params) != id(square.fixed_params)
#
#     assert len(square_revised_refined_template.param_key_map) == 2
#     assert len(square_revised_refined_template.fixed_params) == 2
#
#
# def test_error_properties_param_key_map_and_fixed_params_unmatched_params(
#         power_m1_func: Callable[[int, int, bool], int]) -> None:
#     power_m1_template = FlowTemplate(power_m1_func)
#     assert 'engine' not in power_m1_template.param_signatures
#
#     with pytest.raises(KeyError):
#         FlowTemplate(power_m1_func, param_key_map=dict(engine='motor'))
#
#     with pytest.raises(KeyError):
#         power_m1_template.refine(param_key_map=dict(engine='horsepower'))
#
#     with pytest.raises(KeyError):
#         FlowTemplate(power_m1_func, fixed_params=dict(engine='hyperdrive'))
#
#     with pytest.raises(KeyError):
#         power_m1_template.refine(fixed_params=dict(engine='antigravity'))
#
#
# def test_flow_template_as_decorator() -> None:
#     @FlowTemplate
#     def plus_one(number: int) -> int:
#         return number + 1
#
#     assert isinstance(plus_one, FlowTemplate)
#
#     plus_one = plus_one.apply()
#     assert isinstance(plus_one, Flow)
#
#     assert plus_one(3) == 4
#
#
# def test_flow_template_as_decorator_with_keyword_arguments() -> None:
#     @FlowTemplate(
#         name='plus_one',
#         param_key_map=dict(number_a='number'),
#         fixed_params=dict(number_b=1),
#         result_key='plus_one',
#     )
#     def plus_func(number_a: int, number_b: int) -> int:
#         return number_a + number_b
#
#     plus_one_template = plus_func
#
#     assert isinstance(plus_one_template, FlowTemplate)
#
#     plus_one = plus_one_template.apply()
#     assert isinstance(plus_one, Flow)
#
#     assert plus_one(3) == {'plus_one': 4}
#
#
# def test_error_flow_template_decorator_with_func_argument() -> None:
#
#     with pytest.raises(TypeError):
#
#         def myfunc(a: Callable) -> Callable:
#             return a
#
#         @FlowTemplate(myfunc)
#         def plus_one(number: int) -> int:
#             return number + 1
#
#         assert isinstance(plus_one, FlowTemplate)

#
# @pytest.fixture
# def mock_dag_func_engine(mock_dag_flow_engine_cls):
#     return mock_dag_flow_engine_cls()
#
#
# @pytest.fixture
# def plus_one_dict_func():
#     def _plus_one_dict_func(number: int) -> Dict[str, int]:
#         return {'number': number + 1}
#
#     return _plus_one_dict_func
#
#
# @pytest.fixture
# def plus_one_dict_dag_flow_task(mock_dag_func_engine, plus_one_dict_func):
#     return mock_dag_func_engine.task_decorator()(plus_one_dict_func)
#
#
# @pytest.fixture
# def power_dag_flow_task(mock_dag_func_engine, power_func):
#     return mock_dag_func_engine.task_decorator()(power_func)
#
#
# def test_error_redecorate_task_different_engine(mock_task_runner_engine,
#                                                 mock_dag_func_engine,
#                                                 plus_one_dict_func):
#     mock_task_runner_engine_task = \
#         mock_task_runner_engine.task_decorator(plus_one_dict_func)
#
#     with pytest.raises(RuntimeError):
#         _mock_dag_flow_engine_task = mock_dag_func_engine.task_decorator(
#             mock_task_runner_engine_task)
#
#
# def test_error_no_flow_decorator_parentheses(mock_dag_func_engine):
#     with pytest.raises(AttributeError):
#
#         @mock_dag_func_engine.dag_flow_decorator
#         def my_flow(number: int) -> int:
#             pass
#
#         my_flow(1)
#
#
# def test_error_run_dag_flow_no_tasks(mock_dag_func_engine):
#     with pytest.raises(TypeError):
#
#         @mock_dag_func_engine.dag_flow_decorator()
#         def my_flow(number: int) -> int:
#             pass
#
#
# def test_error_run_dag_flow_pure_func_not_task(mock_dag_func_engine, plus_one_dict_func):
#     with pytest.raises(TypeError):
#
#         @mock_dag_func_engine.dag_flow_decorator(tasks=(plus_one_dict_func,))
#         def my_flow(number: int) -> int:
#             pass
#
#         # TODO: remove?
#         # assert my_flow(1) == {'number': 2}
#
#
# def test_error_no_dag_flow_wrapper(mock_task_runner_engine, plus_one_dict_func):
#     plus_one_dict = mock_task_runner_engine.task_decorator()(plus_one_dict_func)
#
#     with pytest.raises(NotImplementedError):
#
#         @mock_task_runner_engine.dag_flow_decorator(tasks=(plus_one_dict,))
#         def my_flow(number: int) -> int:
#             pass
#
#
# def test_run_dag_flow_single_task(mock_dag_func_engine, plus_one_dict_func):
#     plus_one_dict = mock_dag_func_engine.task_decorator()(plus_one_dict_func)
#
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(plus_one_dict,))
#     def my_flow(number: int) -> int:
#         pass
#
#     assert isinstance(my_flow, Flow)
#     assert my_flow(1) == {'number': 2}
#     assert my_flow.name == 'my_flow'
#     assert my_flow._mock_backend_flow.engine_param_passthrough == 0
#     assert my_flow._mock_backend_flow.backend_flow_kwargs == {}
#     assert my_flow._mock_backend_flow.finished
#
#
# def test_run_dag_flow_with_engine_and_backend_parameters(mock_dag_flow_engine_cls,
#                                                          plus_one_dict_func):
#     my_dag_flow_engine = mock_dag_flow_engine_cls(engine_param=2)
#     my_plus_one_dict = my_dag_flow_engine.task_decorator()(plus_one_dict_func)
#
#     @my_dag_flow_engine.dag_flow_decorator(
#         tasks=(my_plus_one_dict,), cfg_flow={'backend_flow_parameter': 'hello'})
#     def my_flow(number: int) -> int:
#         pass
#
#     assert my_flow(1) == {'number': 2}
#     assert my_flow._mock_backend_flow.engine_param_passthrough == 2
#     assert my_flow._mock_backend_flow.backend_flow_kwargs == {'backend_flow_parameter': 'hello'}
#     assert my_flow._mock_backend_flow.finished
#
#
# def test_run_dag_flow_param_variants(mock_dag_func_engine, power_dag_flow_task):
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(power_dag_flow_task,))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == 16
#     assert my_flow(4, exponent=3) == 64
#     assert my_flow(number=3, exponent=2) == 9
#
#
# def test_run_dag_flow_single_task_set_task_result_name(mock_dag_func_engine, power_func):
#     my_power = mock_dag_func_engine.task_decorator(cfg_task={'result_key': 'my_power'})(power_func)
#
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power,))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == {'my_power': 16}
#
#
# def test_error_run_dag_flow_single_task_different_param_name(mock_dag_func_engine,
#                                                              power_dag_flow_task):
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(power_dag_flow_task,))
#     def my_flow(n: int, e: int) -> int:
#         pass
#
#     with pytest.raises(AttributeError):
#         assert my_flow(4, 2) == 16
#
#
# def test_run_dag_flow_single_task_map_param_name(mock_dag_func_engine, power_func):
#     my_power = mock_dag_func_engine.task_decorator(cfg_task={
#         'param_key_map': {
#             'number': 'n', 'exponent': 'e'
#         },
#     })(
#         power_func)
#
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power,))
#     def my_flow(n: int, e: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == 16
#     assert my_flow(4, e=3) == 64
#     assert my_flow(n=2, e=3) == 8
#
#
# def test_run_dag_flow_two_tasks_param_name_match(mock_dag_func_engine,
#                                                  plus_one_dict_dag_flow_task,
#                                                  power_dag_flow_task):
#     @mock_dag_func_engine.dag_flow_decorator(
#         tasks=(
#             plus_one_dict_dag_flow_task,  # matches 'number' from __init__, returns new 'number'
#             power_dag_flow_task,  # matches 'number' from first task and 'exponent' from __init__
#         ))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == 25
#
#
# def test_error_run_dag_flow_two_tasks_no_dict_first_task(mock_dag_func_engine,
#                                                          power_dag_flow_task,
#                                                          plus_one_dict_dag_flow_task):
#     @mock_dag_func_engine.dag_flow_decorator(
#         tasks=(
#             power_dag_flow_task,
#             plus_one_dict_dag_flow_task,
#         ))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     with pytest.raises(RuntimeError):
#         assert my_flow(4, 2) == 17
#
#
# def test_run_dag_flow_incorrect_param_second_task(mock_dag_func_engine,
#                                                   power_func,
#                                                   plus_one_dict_dag_flow_task):
#     my_power = mock_dag_func_engine.task_decorator(cfg_task={'result_key': 'my_power'})(power_func)
#
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power, plus_one_dict_dag_flow_task))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == {'number': 5}  # plus_one takes 'number' as input, not 'my_power'
#
#
# def test_run_dag_flow_two_tasks_mapped_params(mock_dag_func_engine, power_func, plus_one_dict_func):
#     my_power = mock_dag_func_engine.task_decorator(cfg_task={'result_key': 'my_power'})(power_func)
#     my_plus_one = mock_dag_func_engine.task_decorator(cfg_task={
#         'param_key_map': {
#             'number': 'my_power'
#         },
#         'result_key': 'plus_one',
#     })(
#         plus_one_dict_func)
#
#     @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power, my_plus_one))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == {'plus_one': {'number': 17}}
