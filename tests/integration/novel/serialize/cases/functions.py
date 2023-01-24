from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.modules.json.models import JsonDataset
from omnipy.modules.pandas.models import PandasDataset

from .datasets import (csv_dataset,
                       json_dataset,
                       json_str_dataset,
                       json_table_dataset,
                       pandas_dataset,
                       python_dataset,
                       str_dataset)


def pandas_func() -> PandasDataset:
    return pandas_dataset


def json_table_func() -> JsonDataset:
    return json_table_dataset


def json_func() -> JsonDataset:
    return json_dataset


def json_str_func() -> Dataset[Model[str]]:
    return json_str_dataset


def csv_func() -> Dataset[Model[str]]:
    return csv_dataset


def str_func() -> Dataset[Model[str]]:
    return str_dataset


def python_func() -> Dataset[Model[object]]:
    return python_dataset
