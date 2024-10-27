import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import pytest_cases as pc

from .raw.functions import (all_int_dataset_plus_int_return_str_dataset_func,
                            async_all_int_dataset_plus_int_return_str_dataset_func,
                            async_single_int_model_plus_int_return_str_model_func,
                            async_single_int_plus_future_int_return_str_func,
                            async_single_int_plus_int_return_str_func,
                            async_single_int_plus_int_return_str_model_with_output_str_dataset_func,
                            single_int_model_plus_int_return_str_model_func,
                            single_int_plus_int_return_str_func,
                            single_int_plus_int_return_str_model_with_output_str_dataset_func,
                            single_int_plus_int_return_str_with_output_int_dataset_func)


@dataclass
class IterateDataFilesCase:
    task_func: Callable | Awaitable
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    func_is_async: bool
    func_second_arg_is_future: bool
    func_has_output_dataset_param: bool
    iterate_over_data_files: bool
    fail_with_output_dataset_param: bool
    fail_with_output_dataset_cls_is_int: bool
    fail_with_output_dataset_param_and_cls_is_int: bool


@pc.case(
    id='sync_all_data_files_plus_str_func',
    tags=['sync', 'function', 'all_data', 'no_output_dataset'],
)
def case_sync_all_int_dataset_plus_int_return_str_dataset_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=all_int_dataset_plus_int_return_str_dataset_func,
        args=(2,),
        kwargs={},
        func_is_async=False,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=False,
        iterate_over_data_files=False,
        fail_with_output_dataset_param=True,
        fail_with_output_dataset_cls_is_int=True,
        fail_with_output_dataset_param_and_cls_is_int=True,
    )


@pc.case(
    id='async_all_int_dataset_plus_int_return_str_dataset_func',
    tags=['async', 'function', 'all_data', 'no_output_dataset'],
)
def case_async_all_int_dataset_plus_int_return_str_dataset_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=async_all_int_dataset_plus_int_return_str_dataset_func,
        args=(2,),
        kwargs={},
        func_is_async=True,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=False,
        iterate_over_data_files=False,
        fail_with_output_dataset_param=True,
        fail_with_output_dataset_cls_is_int=True,
        fail_with_output_dataset_param_and_cls_is_int=True,
    )


@pc.case(
    id='sync_single_int_model_plus_int_return_str_model_func',
    tags=[
        'sync',
        'function',
        'iterate',
        'no_output_dataset',
        'str_output_dataset',
        'int_output_dataset'
    ],
)
def case_sync_single_int_model_plus_int_return_str_model_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=single_int_model_plus_int_return_str_model_func,
        args=(2,),
        kwargs={},
        func_is_async=False,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=False,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=False,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=False,
    )


@pc.case(
    id='sync_single_int_plus_int_return_str_func',
    tags=[
        'sync',
        'function',
        'iterate',
        'no_output_dataset',
        'str_output_dataset',
        'int_output_dataset'
    ],
)
def case_sync_single_int_plus_int_return_str_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=single_int_plus_int_return_str_func,
        args=(2,),
        kwargs={},
        func_is_async=False,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=False,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=False,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=False,
    )


@pc.case(
    id='sync_single_int_plus_int_return_str_model_with_output_str_dataset_func',
    tags=['sync', 'function', 'iterate', 'str_output_dataset'],
)
def case_sync_single_int_plus_int_return_str_model_with_output_str_dataset_func(
) -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=single_int_plus_int_return_str_model_with_output_str_dataset_func,
        args=(2,),
        kwargs={},
        func_is_async=False,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=True,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=False,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=True,
    )


@pc.case(
    id='sync_single_int_plus_int_return_str_with_output_int_dataset_func',
    tags=['sync', 'function', 'iterate', 'int_output_dataset'],
)
def case_sync_single_int_plus_int_return_str_with_output_int_dataset_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=single_int_plus_int_return_str_with_output_int_dataset_func,
        args=(2,),
        kwargs={},
        func_is_async=False,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=True,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=True,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=False,
    )


@pc.case(
    id='async_single_int_model_plus_int_return_str_model_func',
    tags=[
        'async',
        'function',
        'iterate',
        'no_output_dataset',
        'str_output_dataset',
        'int_output_dataset'
    ],
)
def case_async_single_int_model_plus_int_return_str_model_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=async_single_int_model_plus_int_return_str_model_func,
        args=(2,),
        kwargs={},
        func_is_async=True,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=False,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=False,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=False,
    )


@pc.case(
    id='async_single_int_plus_int_return_str_func',
    tags=[
        'async',
        'function',
        'iterate',
        'no_output_dataset',
        'str_output_dataset',
        'int_output_dataset'
    ],
)
def case_async_single_int_plus_int_return_str_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=async_single_int_plus_int_return_str_func,
        args=(2,),
        kwargs={},
        func_is_async=True,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=False,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=False,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=False,
    )


@pc.case(
    id='async_single_int_plus_int_return_str_model_with_output_str_dataset_func',
    tags=['async', 'function', 'iterate'],
)
def case_async_single_int_plus_int_return_str_model_with_output_str_dataset_func(
) -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=async_single_int_plus_int_return_str_model_with_output_str_dataset_func,
        args=(2,),
        kwargs={},
        func_is_async=True,
        func_second_arg_is_future=False,
        func_has_output_dataset_param=True,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=True,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=True,
    )


@pc.case(
    id='async_single_int_plus_future_int_return_str_func',
    tags=['async', 'function', 'iterate', 'await_number_future'],
)
def case_async_single_int_plus_future_int_return_str_func() -> IterateDataFilesCase:
    loop = asyncio.get_event_loop()
    number_future = loop.create_future()
    return IterateDataFilesCase(
        task_func=async_single_int_plus_future_int_return_str_func,
        args=(number_future,),
        kwargs={},
        func_is_async=True,
        func_second_arg_is_future=True,
        func_has_output_dataset_param=False,
        iterate_over_data_files=True,
        fail_with_output_dataset_param=False,
        fail_with_output_dataset_cls_is_int=False,
        fail_with_output_dataset_param_and_cls_is_int=False,
    )
