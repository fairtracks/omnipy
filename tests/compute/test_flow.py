from typing import Dict

import pytest


@pytest.fixture
def mock_dag_func_engine(mock_dag_flow_engine_cls):
    return mock_dag_flow_engine_cls()


@pytest.fixture
def plus_one_dict_func():
    def _plus_one_dict_func(number: int) -> Dict[str, int]:
        return {'number': number + 1}

    return _plus_one_dict_func


@pytest.fixture
def plus_one_dict_dag_flow_task(mock_dag_func_engine, plus_one_dict_func):
    return mock_dag_func_engine.task_decorator()(plus_one_dict_func)


@pytest.fixture
def power_dag_flow_task(mock_dag_func_engine, power_func):
    return mock_dag_func_engine.task_decorator()(power_func)


def test_error_redecorate_task_different_engine(mock_task_runner_engine,
                                                mock_dag_func_engine,
                                                plus_one_dict_func):
    mock_task_runner_engine_task = \
        mock_task_runner_engine.task_decorator(plus_one_dict_func)

    with pytest.raises(RuntimeError):
        _mock_dag_flow_engine_task = mock_dag_func_engine.task_decorator(
            mock_task_runner_engine_task)


def test_error_no_flow_decorator_parentheses(mock_dag_func_engine):
    with pytest.raises(AttributeError):

        @mock_dag_func_engine.dag_flow_decorator
        def my_flow(number: int) -> int:
            pass

        my_flow(1)


def test_error_run_dag_flow_no_tasks(mock_dag_func_engine):
    with pytest.raises(TypeError):

        @mock_dag_func_engine.dag_flow_decorator()
        def my_flow(number: int) -> int:
            pass


def test_error_run_dag_flow_pure_func_not_task(mock_dag_func_engine, plus_one_dict_func):
    with pytest.raises(TypeError):

        @mock_dag_func_engine.dag_flow_decorator(tasks=(plus_one_dict_func,))
        def my_flow(number: int) -> int:
            pass

        # TODO: remove?
        # assert my_flow(1) == {'number': 2}


def test_error_no_dag_flow_wrapper(mock_task_runner_engine, plus_one_dict_func):
    plus_one_dict = mock_task_runner_engine.task_decorator()(plus_one_dict_func)

    with pytest.raises(NotImplementedError):

        @mock_task_runner_engine.dag_flow_decorator(tasks=(plus_one_dict,))
        def my_flow(number: int) -> int:
            pass


def test_run_dag_flow_single_task(mock_dag_func_engine, plus_one_dict_func):
    plus_one_dict = mock_dag_func_engine.task_decorator()(plus_one_dict_func)

    @mock_dag_func_engine.dag_flow_decorator(tasks=(plus_one_dict,))
    def my_flow(number: int) -> int:
        pass

    assert isinstance(my_flow, Flow)
    assert my_flow(1) == {'number': 2}
    assert my_flow.name == 'my_flow'
    assert my_flow._mock_backend_flow.engine_param_passthrough == 0
    assert my_flow._mock_backend_flow.backend_flow_kwargs == {}
    assert my_flow._mock_backend_flow.finished


def test_run_dag_flow_with_engine_and_backend_parameters(mock_dag_flow_engine_cls,
                                                         plus_one_dict_func):
    my_dag_flow_engine = mock_dag_flow_engine_cls(engine_param=2)
    my_plus_one_dict = my_dag_flow_engine.task_decorator()(plus_one_dict_func)

    @my_dag_flow_engine.dag_flow_decorator(
        tasks=(my_plus_one_dict,), cfg_flow={'backend_flow_parameter': 'hello'})
    def my_flow(number: int) -> int:
        pass

    assert my_flow(1) == {'number': 2}
    assert my_flow._mock_backend_flow.engine_param_passthrough == 2
    assert my_flow._mock_backend_flow.backend_flow_kwargs == {'backend_flow_parameter': 'hello'}
    assert my_flow._mock_backend_flow.finished


def test_run_dag_flow_param_variants(mock_dag_func_engine, power_dag_flow_task):
    @mock_dag_func_engine.dag_flow_decorator(tasks=(power_dag_flow_task,))
    def my_flow(number: int, exponent: int) -> int:
        pass

    assert my_flow(4, 2) == 16
    assert my_flow(4, exponent=3) == 64
    assert my_flow(number=3, exponent=2) == 9


def test_run_dag_flow_single_task_set_task_result_name(mock_dag_func_engine, power_func):
    my_power = mock_dag_func_engine.task_decorator(cfg_task={'result_key': 'my_power'})(power_func)

    @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power,))
    def my_flow(number: int, exponent: int) -> int:
        pass

    assert my_flow(4, 2) == {'my_power': 16}


def test_error_run_dag_flow_single_task_different_param_name(mock_dag_func_engine,
                                                             power_dag_flow_task):
    @mock_dag_func_engine.dag_flow_decorator(tasks=(power_dag_flow_task,))
    def my_flow(n: int, e: int) -> int:
        pass

    with pytest.raises(AttributeError):
        assert my_flow(4, 2) == 16


def test_run_dag_flow_single_task_map_param_name(mock_dag_func_engine, power_func):
    my_power = mock_dag_func_engine.task_decorator(cfg_task={
        'param_key_map': {
            'number': 'n', 'exponent': 'e'
        },
    })(
        power_func)

    @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power,))
    def my_flow(n: int, e: int) -> int:
        pass

    assert my_flow(4, 2) == 16
    assert my_flow(4, e=3) == 64
    assert my_flow(n=2, e=3) == 8


def test_run_dag_flow_two_tasks_param_name_match(mock_dag_func_engine,
                                                 plus_one_dict_dag_flow_task,
                                                 power_dag_flow_task):
    @mock_dag_func_engine.dag_flow_decorator(
        tasks=(
            plus_one_dict_dag_flow_task,  # matches 'number' from __init__, returns new 'number'
            power_dag_flow_task,  # matches 'number' from first task and 'exponent' from __init__
        ))
    def my_flow(number: int, exponent: int) -> int:
        pass

    assert my_flow(4, 2) == 25


def test_error_run_dag_flow_two_tasks_no_dict_first_task(mock_dag_func_engine,
                                                         power_dag_flow_task,
                                                         plus_one_dict_dag_flow_task):
    @mock_dag_func_engine.dag_flow_decorator(
        tasks=(
            power_dag_flow_task,
            plus_one_dict_dag_flow_task,
        ))
    def my_flow(number: int, exponent: int) -> int:
        pass

    with pytest.raises(RuntimeError):
        assert my_flow(4, 2) == 17


def test_run_dag_flow_incorrect_param_second_task(mock_dag_func_engine,
                                                  power_func,
                                                  plus_one_dict_dag_flow_task):
    my_power = mock_dag_func_engine.task_decorator(cfg_task={'result_key': 'my_power'})(power_func)

    @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power, plus_one_dict_dag_flow_task))
    def my_flow(number: int, exponent: int) -> int:
        pass

    assert my_flow(4, 2) == {'number': 5}  # plus_one takes 'number' as input, not 'my_power'


def test_run_dag_flow_two_tasks_mapped_params(mock_dag_func_engine, power_func, plus_one_dict_func):
    my_power = mock_dag_func_engine.task_decorator(cfg_task={'result_key': 'my_power'})(power_func)
    my_plus_one = mock_dag_func_engine.task_decorator(cfg_task={
        'param_key_map': {
            'number': 'my_power'
        },
        'result_key': 'plus_one',
    })(
        plus_one_dict_func)

    @mock_dag_func_engine.dag_flow_decorator(tasks=(my_power, my_plus_one))
    def my_flow(number: int, exponent: int) -> int:
        pass

    assert my_flow(4, 2) == {'plus_one': {'number': 17}}
