from dataclasses import dataclass
from inspect import Parameter
import json
from types import NoneType
from typing import Any, Callable, Dict, Generic, Tuple, TypeVar, Union

import pytest_cases as pc

from unifair.compute.task import Task, TaskTemplate

from .raw.functions import (action_func_no_params,
                            action_func_with_params,
                            data_import_func,
                            dict_of_squared_func,
                            empty_dict_func,
                            format_to_string_func,
                            plus_one_dict_func,
                            power_m1_func)

ArgT = TypeVar('ArgT')
ReturnT = TypeVar('ReturnT')


@dataclass
class TaskCase(Generic[ArgT, ReturnT]):
    name: str
    task_func: Callable[[ArgT], ReturnT]
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    assert_results_func: Callable[[Any], None]
    assert_signature_and_return_type_func: Callable[[Any], None]


@pc.case(
    id='sync-function-action_func_no_params()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_action_func_no_params() -> TaskCase[[], None]:
    def assert_results(result: NoneType) -> None:
        assert result is None

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is None

    return TaskCase(
        name='action_func_no_params',
        task_func=action_func_no_params,
        args=(),
        kwargs={},
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id="sync-function-action_func_with_params('rm -rf *', verbose=True)",
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_action_func_with_params() -> TaskCase[[int, bool], None]:
    def assert_results(result: NoneType) -> None:
        assert result is None

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        print(task_obj.param_signatures)
        assert task_obj.param_signatures == {
            'command': Parameter('command', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            'verbose': Parameter('verbose', Parameter.KEYWORD_ONLY, annotation=bool, default=False),
        }
        assert task_obj.return_type is None

    return TaskCase(
        name='action_func_with_params',
        task_func=action_func_with_params,
        args=('rm -rf *',),
        kwargs=dict(verbose=True),
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-data_import_func()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_data_import_func() -> TaskCase[[], str]:
    def assert_results(json_data: str) -> None:
        assert type(json_data) is str
        assert json.loads(json_data) == dict(my_data=[123, 234, 345, 456])

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is str

    return TaskCase(
        name='data_import_func',
        task_func=data_import_func,
        args=(),
        kwargs={},
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id="sync-function-format_to_string_func('Number', 12)",
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_format_to_string_func() -> TaskCase[[str, int], str]:
    def assert_results(result: str) -> None:
        assert result == 'Number: 12'

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {
            'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        }
        assert task_obj.return_type is str

    return TaskCase(
        name='format_to_string_func',
        task_func=format_to_string_func,
        args=('Number', 12),
        kwargs={},
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-power_m1_func(4, 3, minus_one=False)',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_power_m1_func() -> TaskCase[[int, int, bool], int]:
    def assert_results(result: int) -> None:
        assert result == 64

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {
            'number':
                Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            'exponent':
                Parameter('exponent', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
            'minus_one':
                Parameter(
                    'minus_one',
                    Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=bool,
                    default=True,
                )
        }
        assert task_obj.return_type is int

    return TaskCase(
        name='power_m1_func',
        task_func=power_m1_func,
        args=(4, 3),
        kwargs=dict(minus_one=False),
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-empty_dict_func()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_empty_dict_fun() -> TaskCase[[], Dict]:
    def assert_results(result: Dict) -> None:
        assert result == {}

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is Dict

    return TaskCase(
        name='empty_dict_func',
        task_func=empty_dict_func,
        args=(),
        kwargs={},
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-plus_one_dict_func()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_plus_one_dict_func() -> TaskCase[[int], Dict[str, int]]:
    def assert_results(result: Dict[str, int]) -> None:
        assert result == {'number': 4}

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {
            'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        }
        assert task_obj.return_type is Dict[str, int]

    return TaskCase(
        name='plus_one_dict_func',
        task_func=plus_one_dict_func,
        args=(3,),
        kwargs={},
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-dict_of_squared_func()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_dict_of_squared_fun() -> TaskCase[[int], Dict[int, int]]:
    def assert_results(result: Dict[int, int]) -> None:
        assert result == {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {
            'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        }
        assert task_obj.return_type is Dict[int, int]

    return TaskCase(
        name='dict_of_squared_func',
        task_func=dict_of_squared_func,
        args=(6,),
        kwargs={},
        assert_results_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )
