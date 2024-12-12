from typing import Annotated, Callable

import pytest

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.modules.json.datasets import JsonDataset
from omnipy.modules.pandas.models import PandasDataset
from omnipy.modules.raw.datasets import StrDataset

from .models import PydanticModel, TwoLevelPydanticModel


@pytest.fixture
def pandas_func(
        pandas_dataset: Annotated[PandasDataset, pytest.fixture]) -> Callable[[], PandasDataset]:
    def _pandas_func() -> PandasDataset:
        return pandas_dataset

    return _pandas_func


@pytest.fixture
def json_table_func(
        json_table_dataset: Annotated[JsonDataset, pytest.fixture]) -> Callable[[], JsonDataset]:
    def _json_table_func() -> JsonDataset:
        return json_table_dataset

    return _json_table_func


@pytest.fixture
def json_nested_table_func(
    json_nested_table_dataset: Annotated[JsonDataset,
                                         pytest.fixture],) -> Callable[[], JsonDataset]:
    def _json_nested_table_func() -> JsonDataset:
        return json_nested_table_dataset

    return _json_nested_table_func


@pytest.fixture
def json_table_as_str_func(
        json_table_as_str_dataset: Annotated[StrDataset,
                                             pytest.fixture]) -> Callable[[], StrDataset]:
    def _json_table_as_str_func() -> StrDataset:
        return json_table_as_str_dataset

    return _json_table_as_str_func


@pytest.fixture
def json_func(json_dataset: Annotated[JsonDataset, pytest.fixture]) -> Callable[[], JsonDataset]:
    def _json_dataset() -> JsonDataset:
        return json_dataset

    return _json_dataset


@pytest.fixture
def json_str_func(
        json_str_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    def _json_str_dataset() -> StrDataset:
        return json_str_dataset

    return _json_str_dataset


@pytest.fixture
def csv_func(csv_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    def _csv_dataset() -> StrDataset:
        return csv_dataset

    return _csv_dataset


@pytest.fixture
def str_func(str_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    def _str_dataset() -> StrDataset:
        return str_dataset

    return _str_dataset


@pytest.fixture
def str_unicode_func(
        str_unicode_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    def _str_unicode_dataset() -> StrDataset:
        return str_unicode_dataset

    return _str_unicode_dataset


@pytest.fixture
def python_func(
    python_dataset: Annotated[Dataset[Model[object]], pytest.fixture]
) -> Callable[[], Dataset[Model[object]]]:
    def _python_dataset() -> Dataset[Model[object]]:
        return python_dataset

    return _python_dataset


@pytest.fixture
def pydantic_func(
    pydantic_dataset: Annotated[Dataset[Model[PydanticModel]], pytest.fixture]
) -> Callable[[], Dataset[Model[PydanticModel]]]:
    def _pydantic_dataset() -> Dataset[Model[PydanticModel]]:
        return pydantic_dataset

    return _pydantic_dataset


@pytest.fixture
def two_level_pydantic_func(
    two_level_pydantic_dataset: Annotated[Dataset[Model[TwoLevelPydanticModel]], pytest.fixture]
) -> Callable[[], Dataset[Model[TwoLevelPydanticModel]]]:
    def _two_level_pydantic_dataset() -> Dataset[Model[TwoLevelPydanticModel]]:
        return two_level_pydantic_dataset

    return _two_level_pydantic_dataset
