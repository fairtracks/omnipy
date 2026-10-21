"""Shared fixtures for integration novel serialization tests."""

from .cases.datasets import (
    csv_dataset,
    json_dataset,
    json_nested_table_dataset,
    json_str_dataset,
    json_table_as_str_dataset,
    json_table_dataset,
    pandas_dataset,
    python_dataset,
    str_dataset,
    str_unicode_dataset,
)
from .cases.functions import (
    csv_func,
    json_func,
    json_nested_table_func,
    json_str_func,
    json_table_as_str_func,
    json_table_func,
    pandas_func,
    python_func,
    str_func,
    str_unicode_func,
)

__all__ = [
    'csv_dataset',
    'csv_func',
    'json_dataset',
    'json_func',
    'json_nested_table_dataset',
    'json_nested_table_func',
    'json_str_dataset',
    'json_str_func',
    'json_table_as_str_dataset',
    'json_table_as_str_func',
    'json_table_dataset',
    'json_table_func',
    'pandas_dataset',
    'pandas_func',
    'python_dataset',
    'python_func',
    'str_dataset',
    'str_func',
    'str_unicode_dataset',
    'str_unicode_func',
]
