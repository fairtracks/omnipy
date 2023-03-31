import asyncio
from dataclasses import dataclass
from typing import Any, Callable

import pytest_cases as pc

from .raw.functions import (all_int_dataset_plus_int_return_str_dataset_func,
                            async_all_int_dataset_plus_int_return_str_dataset_func,
                            async_single_int_model_plus_int_return_str_model_func,
                            async_single_int_plus_future_int_fail_func,
                            async_single_int_plus_future_int_return_str_func,
                            async_single_int_plus_future_return_alphanum_string_func,
                            async_single_int_plus_int_return_str_func,
                            async_single_int_plus_int_return_str_model_with_output_str_dataset_func,
                            single_int_model_plus_default_int_pair_return_str_model_func,
                            single_int_model_plus_int_return_str_model_func,
                            single_int_plus_int_return_str_func,
                            single_int_plus_int_return_str_model_with_output_str_dataset_func,
                            single_int_plus_int_return_str_with_output_int_dataset_func)


@dataclass
class IterateDataFilesCase:
    task_func: Callable
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    func_is_async: bool
    iterate_over_data_files: bool
    func_second_arg_is_future: bool = False
    func_has_output_dataset_param: bool = False
    fail_with_output_dataset_param: bool = False
    fail_with_output_dataset_cls_is_int: bool = False
    fail_with_output_dataset_param_and_cls_is_int: bool = False
    fail_after_awaiting_future_int: bool = False
    fail_parsing_when_output_dataset_is_int: bool = False


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
        iterate_over_data_files=True,
    )


@pc.case(
    id='sync_single_int_model_plus_default_int_pair_return_str_model_func',
    tags=[
        'sync',
        'function',
        'iterate',
        'no_output_dataset',
        'str_output_dataset',
        'int_output_dataset'
    ],
)
def case_sync_single_int_model_plus_default_int_pair_return_str_model_func(
) -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=single_int_model_plus_default_int_pair_return_str_model_func,
        args=(1,),
        kwargs={'other_number': 1},
        func_is_async=False,
        iterate_over_data_files=True,
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
        iterate_over_data_files=True,
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
        iterate_over_data_files=True,
        func_has_output_dataset_param=True,
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
        iterate_over_data_files=True,
        func_has_output_dataset_param=True,
        fail_with_output_dataset_param=True,
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
        iterate_over_data_files=True,
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
        iterate_over_data_files=True,
    )


@pc.case(
    id='async_single_int_plus_future_return_alphanum_string_func',
    tags=[
        'async',
        'function',
        'iterate',
        'no_output_dataset',
        'str_output_dataset',
        'int_output_dataset'
    ],
)
def case_async_single_int_plus_future_return_alphanum_string_func() -> IterateDataFilesCase:
    return IterateDataFilesCase(
        task_func=async_single_int_plus_future_return_alphanum_string_func,
        args=(2,),
        kwargs={},
        func_is_async=True,
        iterate_over_data_files=True,
        fail_parsing_when_output_dataset_is_int=True)


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
        iterate_over_data_files=True,
        func_has_output_dataset_param=True,
        fail_with_output_dataset_param=True,
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
        iterate_over_data_files=True,
        func_second_arg_is_future=True,
    )


@pc.case(
    id='async_single_int_plus_future_int_fail_func',
    tags=['async', 'function', 'iterate', 'await_number_future'],
)
def case_async_single_int_plus_future_int_fail_func() -> IterateDataFilesCase:
    loop = asyncio.get_event_loop()
    number_future = loop.create_future()
    return IterateDataFilesCase(
        task_func=async_single_int_plus_future_int_fail_func,
        args=(number_future,),
        kwargs={},
        func_is_async=True,
        iterate_over_data_files=True,
        func_second_arg_is_future=True,
        fail_after_awaiting_future_int=True,
    )
