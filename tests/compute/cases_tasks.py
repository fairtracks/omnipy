from dataclasses import dataclass
from inspect import Parameter
import json
from types import NoneType
from typing import Any, Callable, Dict, Generic, Tuple, TypeVar, Union

import pytest_cases as pc

from compute.cases_functions import (action_func_no_params,
                                     action_func_with_params,
                                     data_import_func,
                                     format_to_string_func,
                                     power_m1_func)
from unifair.compute.task import Task, TaskTemplate

ArgT = TypeVar('ArgT')
ReturnT = TypeVar('ReturnT')


@dataclass
class Case(Generic[ArgT, ReturnT]):
    name: str
    func: Callable[[ArgT], ReturnT]
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    assert_func: Callable[[Any], None]
    assert_signature_and_return_type_func: Callable[[Any], None]


@pc.case(
    id='sync-function-action_func_no_params()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_action_func_no_params() -> Case[[], None]:
    def assert_results(result: NoneType) -> None:
        assert result is None

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is None

    return Case(
        name='action_func_no_params',
        func=action_func_no_params,
        args=(),
        kwargs={},
        assert_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id="sync-function-action_func_with_params('rm -rf *', verbose=True)",
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_action_func_with_params() -> Case[[int, bool], None]:
    def assert_results(result: NoneType) -> None:
        assert result is None

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        print(task_obj.param_signatures)
        assert task_obj.param_signatures == {
            'command': Parameter('command', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            'verbose': Parameter('verbose', Parameter.KEYWORD_ONLY, annotation=bool, default=False),
        }
        assert task_obj.return_type is None

    return Case(
        name='action_func_with_params',
        func=action_func_with_params,
        args=('rm -rf *',),
        kwargs=dict(verbose=True),
        assert_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-data_import_func()',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_data_import_func() -> Case[[], str]:
    def assert_results(json_data: str) -> None:
        assert type(json_data) is str
        assert json.loads(json_data) == dict(my_data=[123, 234, 345, 456])

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is str

    return Case(
        name='data_import_func',
        func=data_import_func,
        args=(),
        kwargs={},
        assert_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id="sync-function-format_to_string_func('Number', 12)",
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_format_to_string_func() -> Case[[str, int], str]:
    def assert_results(result: str) -> None:
        assert result == 'Number: 12'

    def assert_param_signature_and_return_type(task_obj: Union[TaskTemplate, Task]):
        assert task_obj.param_signatures == {
            'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        }
        assert task_obj.return_type is str

    return Case(
        name='format_to_string_func',
        func=format_to_string_func,
        args=('Number', 12),
        kwargs={},
        assert_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )


@pc.case(
    id='sync-function-power_m1_func(4, 3, minus_one=False)',
    tags=['sync', 'function', 'singlethread', 'success'],
)
def case_sync_power_m1_func() -> Case[[int, int, bool], int]:
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

    return Case(
        name='power_m1_func',
        func=power_m1_func,
        args=(4, 3),
        kwargs=dict(minus_one=False),
        assert_func=assert_results,
        assert_signature_and_return_type_func=assert_param_signature_and_return_type,
    )
