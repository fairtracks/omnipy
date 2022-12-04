from typing import Annotated

import pytest
import pytest_cases as pc

from unifair.compute.flow import (DagFlow,
                                  DagFlowTemplate,
                                  Flow,
                                  FlowTemplate,
                                  FuncFlow,
                                  FuncFlowTemplate)
from unifair.compute.task import TaskTemplate

from .cases.flows import FlowCase
from .cases.raw.functions import format_to_string_func
from .helpers.functions import assert_updated_wrapper
from .helpers.mocks import MockLocalRunner


def test_init(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    for class_info in [{
            'template_cls': DagFlowTemplate, 'flow_cls': DagFlow
    }, {
            'template_cls': FuncFlowTemplate, 'flow_cls': FuncFlow
    }]:
        template_cls = class_info['template_cls']
        flow_cls = class_info['flow_cls']

        flow_template = template_cls(format_to_string_func)
        assert isinstance(flow_template, FlowTemplate)
        assert isinstance(flow_template, template_cls)
        assert_updated_wrapper(flow_template, format_to_string_func)

        with pytest.raises(RuntimeError):
            flow_cls(format_to_string_func)

        flow = flow_template.apply()  # noqa  # Pycharm static type checker bug
        assert isinstance(flow, flow_cls)
        assert_updated_wrapper(flow, format_to_string_func)


def test_fail_init(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    with pytest.raises(TypeError):
        FlowTemplate()

    with pytest.raises(TypeError):
        Flow()

    with pytest.raises(TypeError):
        FuncFlowTemplate('extra_positional_argument')(lambda x: x)


@pc.parametrize_with_cases('case', cases='.cases.flows')
def test_flow_run(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
                  case: FlowCase) -> None:
    assert mock_local_runner.finished is False

    assert_updated_wrapper(case.flow_template, case.flow_func)

    with pytest.raises(TypeError):
        case.flow_template(*case.args, **case.kwargs)  # noqa

    flow = case.flow_template.apply()
    assert_updated_wrapper(flow, case.flow_func)

    results = flow(*case.args, **case.kwargs)

    assert flow.name == case.name
    case.assert_results_func(results)

    assert mock_local_runner.finished is True


# TODO: Tests to add:
#       - engine not supporting dag_flow_decorator
#       - engine not supporting func_flow_decorator
#       - dag_flow.tasks (should be a tuple, not a list, for immutability)


def test_func_flow_context(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:
    @TaskTemplate
    def task_tmpl() -> int:
        return 42

    with pytest.raises(TypeError):
        task_tmpl()

    @TaskTemplate
    def double_tmpl(number: int) -> int:
        return number * 2

    @DagFlowTemplate(task_tmpl.refine(result_key='number'), double_tmpl)
    def dag_flow_tmpl() -> int:
        ...

    with pytest.raises(TypeError):
        dag_flow_tmpl()

    dag_flow = dag_flow_tmpl.apply()
    assert dag_flow() == 84

    @FuncFlowTemplate
    def func_flow_tmpl(number: int) -> int:
        return dag_flow_tmpl() + number

    with pytest.raises(TypeError):
        func_flow_tmpl(16)

    func_flow = func_flow_tmpl.apply()
    assert func_flow(16) == 100

    @FuncFlowTemplate
    def func_flow_2_tmpl() -> int:
        return int(func_flow_tmpl(16) / 2)

    with pytest.raises(TypeError):
        func_flow_2_tmpl()

    func_flow_2 = func_flow_2_tmpl.apply()
    assert func_flow_2() == 50


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
# def test_run_dag_flow_single_task(mock_dag_func_engine, plus_one_dict_func):
# def test_run_dag_flow_single_task():
#
#     plus_one_dict = mock_dag_func_engine.task_decorator()(plus_one_dict_func)
#
#     @mock_dag_func_engine.dag_flow_decorator(plus_one_dict)
#     def my_flow(number: int) -> int:
#         pass
#
#     assert isinstance(my_flow, Flow)
#     assert my_flow(1) == {'number': 2}
#     assert my_flow.name == 'my_flow'
#     assert my_flow._mock_backend_flow.engine_param_passthrough == 0
#     assert my_flow._mock_backend_flow.backend_flow_kwargs == {}
#     assert my_flow._mock_backend_flow.finished

# def test_run_dag_flow_with_engine_and_backend_parameters(mock_dag_flow_engine_cls,
#                                                          plus_one_dict_func):
#     my_dag_flow_engine = mock_dag_flow_engine_cls(engine_param=2)
#     my_plus_one_dict = my_dag_flow_engine.task_decorator()(plus_one_dict_func)
#
#     @my_dag_flow_engine.dag_flow_decorator(
#         my_plus_one_dict,), cfg_flow={'backend_flow_parameter': 'hello'})
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
#     @mock_dag_func_engine.dag_flow_decorator(power_dag_flow_task.
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
#     @mock_dag_func_engine.dag_flow_decorator(my_power.
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == {'my_power': 16}
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
#     @mock_dag_func_engine.dag_flow_decorator(my_power.
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
#
#             plus_one_dict_dag_flow_task,  # matches 'number' from __init__, returns new 'number'
#             power_dag_flow_task,  # matches 'number' from first task and 'exponent' from __init__
#         ))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == 25

#
# def test_task_run_parameter_variants() -> None:
#     power_m1 = TaskTemplate(power_m1_func).apply()
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
# def test_error_missing_task_run_parameters() -> None:
#     power_m1 = TaskTemplate(power_m1_func).apply()
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
#         @mock_dag_func_engine.dag_flow_decorator(plus_one_dict_func.
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
#         @mock_task_runner_engine.dag_flow_decorator(plus_one_dict.
#         def my_flow(number: int) -> int:
#             pass
#
# def test_error_run_dag_flow_single_task_different_param_name(mock_dag_func_engine,
#                                                              power_dag_flow_task):
#     @mock_dag_func_engine.dag_flow_decorator(power_dag_flow_task.
#     def my_flow(n: int, e: int) -> int:
#         pass
#
#     with pytest.raises(AttributeError):
#         assert my_flow(4, 2) == 16
#
#
# def test_error_run_dag_flow_two_tasks_no_dict_first_task(mock_dag_func_engine,
#                                                          power_dag_flow_task,
#                                                          plus_one_dict_dag_flow_task):
#     @mock_dag_func_engine.dag_flow_decorator(
#
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
#     @mock_dag_func_engine.dag_flow_decorator(my_power, plus_one_dict_dag_flow_task))
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
#     @mock_dag_func_engine.dag_flow_decorator(my_power, my_plus_one))
#     def my_flow(number: int, exponent: int) -> int:
#         pass
#
#     assert my_flow(4, 2) == {'plus_one': {'number': 17}}

#
# def test_refine_task_template_with_other_properties() -> None:
#
#     # Plain task template
#     power_m1_template = TaskTemplate(power_m1_func)
#     power_m1 = power_m1_template.apply()
#     assert power_m1(4, 2) == 15
#
#     # Refine task template with all properties (update=True)
#     my_power_template = power_m1_template.refine(
#         name='magic_power',
#         param_key_map=dict(number='num', exponent='exp'),
#         result_key='by_the_power_of_grayskull',
#         fixed_params=dict(exponent=3),
#     )
#     assert my_power_template != power_m1_template
#     for my_power_obj in my_power_template, my_power_template.apply():
#         assert my_power_obj.name == 'magic_power'
#         assert my_power_obj.param_key_map == dict(number='num', exponent='exp')
#         assert my_power_obj.result_key == 'by_the_power_of_grayskull'
#         assert my_power_obj.fixed_params == {'exponent': 3}
#
#     my_power = my_power_template.apply()
#     assert my_power != power_m1
#     assert my_power(num=3) == {'by_the_power_of_grayskull': 26}
#
#     # Refine task template with two properties (update=True)
#     my_power_template_2 = my_power_template.refine(
#         param_key_map=[('number', 'numb'), ('minus_one', 'min')],)  # noqa
#     assert my_power_template_2 != my_power_template
#     for my_power_obj_2 in my_power_template_2, my_power_template_2.apply():
#         assert my_power_obj_2.name == 'magic_power'
#         assert my_power_obj_2.param_key_map == dict(number='numb', exponent='exp', minus_one='min')
#         assert my_power_obj_2.result_key == 'by_the_power_of_grayskull'
#         assert my_power_obj_2.fixed_params == {'exponent': 3}
#
#     my_power_2 = my_power_template_2.apply()
#     assert my_power_2 != my_power
#     assert my_power_2(numb=3, min=False) == {'by_the_power_of_grayskull': 27}
#
#     # Refine task template with single property (update=False)
#     my_power_template_3 = my_power_template_2.refine(
#         fixed_params=dict(number=3, minus_one=False), update=False)
#     assert my_power_template_3 != my_power_template_2
#     for my_power_obj_3 in my_power_template_3, my_power_template_3.apply():
#         assert my_power_obj_3.name == 'power_m1_func'
#         assert my_power_obj_3.param_key_map == {}
#         assert my_power_obj_3.result_key is None
#         assert my_power_obj_3.fixed_params == dict(number=3, minus_one=False)
#
#     my_power_3 = my_power_template_3.apply()
#     assert my_power_3 != my_power_2
#     assert my_power_3(exponent=3) == 27
#
#     # One-liner to reset properties to default values
#     my_power_4 = my_power_3.revise().refine(update=False).apply()
#     assert my_power_4 == power_m1
#     assert my_power_4(number=3, exponent=3, minus_one=False) == 27
#
