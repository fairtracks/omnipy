from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.modules.json.datasets import JsonDataset
from omnipy.modules.pandas.models import PandasDataset
from omnipy.modules.raw.datasets import StrDataset

from .datasets import (csv_dataset,
                       json_dataset,
                       json_nested_table_dataset,
                       json_str_dataset,
                       json_table_as_str_dataset,
                       json_table_dataset,
                       pandas_dataset,
                       python_dataset,
                       str_dataset,
                       str_unicode_dataset)


def pandas_func() -> PandasDataset:
    return pandas_dataset


def json_table_func() -> JsonDataset:
    return json_table_dataset


def json_nested_table_func() -> JsonDataset:
    return json_nested_table_dataset


def json_table_as_str_func() -> StrDataset:
    return json_table_as_str_dataset


def json_func() -> JsonDataset:
    return json_dataset


def json_str_func() -> Dataset[Model[str]]:
    return json_str_dataset


def csv_func() -> StrDataset:
    return csv_dataset


def str_func() -> StrDataset:
    return str_dataset


def str_unicode_func() -> StrDataset:
    return str_unicode_dataset


def python_func() -> Dataset[Model[object]]:
    return python_dataset
