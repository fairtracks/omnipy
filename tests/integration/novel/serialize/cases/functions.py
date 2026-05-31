"""Helper functions for integration novel serialization tests."""

from typing import Annotated, Callable

import pytest

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.raw.datasets import StrDataset
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


@pytest.fixture
def pandas_func(
        pandas_dataset: Annotated[PandasDataset, pytest.fixture]) -> Callable[[], PandasDataset]:
    """Provide pandas func."""
    def _pandas_func() -> PandasDataset:
        """Return pandas func."""
        return pandas_dataset

    return _pandas_func


@pytest.fixture
def json_table_func(
        json_table_dataset: Annotated[JsonDataset, pytest.fixture]) -> Callable[[], JsonDataset]:
    """Provide jSON table func."""
    def _json_table_func() -> JsonDataset:
        """Return jSON table func."""
        return json_table_dataset

    return _json_table_func


@pytest.fixture
def json_nested_table_func(
    json_nested_table_dataset: Annotated[JsonDataset,
                                         pytest.fixture],) -> Callable[[], JsonDataset]:
    """Provide jSON nested table func."""
    def _json_nested_table_func() -> JsonDataset:
        """Return jSON nested table func."""
        return json_nested_table_dataset

    return _json_nested_table_func


@pytest.fixture
def json_table_as_str_func(
        json_table_as_str_dataset: Annotated[StrDataset,
                                             pytest.fixture]) -> Callable[[], StrDataset]:
    """Provide jSON table as string func."""
    def _json_table_as_str_func() -> StrDataset:
        """Return jSON table as string func."""
        return json_table_as_str_dataset

    return _json_table_as_str_func


@pytest.fixture
def json_func(json_dataset: Annotated[JsonDataset, pytest.fixture]) -> Callable[[], JsonDataset]:
    """Provide jSON func."""
    def _json_dataset() -> JsonDataset:
        """Return jSON dataset."""
        return json_dataset

    return _json_dataset


@pytest.fixture
def json_str_func(
        json_str_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    """Provide jSON string func."""
    def _json_str_dataset() -> StrDataset:
        """Return jSON string dataset."""
        return json_str_dataset

    return _json_str_dataset


@pytest.fixture
def csv_func(csv_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    """Provide cSV func."""
    def _csv_dataset() -> StrDataset:
        """Return cSV dataset."""
        return csv_dataset

    return _csv_dataset


@pytest.fixture
def str_func(str_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    """Provide string func."""
    def _str_dataset() -> StrDataset:
        """Return string dataset."""
        return str_dataset

    return _str_dataset


@pytest.fixture
def str_unicode_func(
        str_unicode_dataset: Annotated[StrDataset, pytest.fixture]) -> Callable[[], StrDataset]:
    """Provide string unicode func."""
    def _str_unicode_dataset() -> StrDataset:
        """Return string unicode dataset."""
        return str_unicode_dataset

    return _str_unicode_dataset


@pytest.fixture
def python_func(
    python_dataset: Annotated[Dataset[Model[object]], pytest.fixture]
) -> Callable[[], Dataset[Model[object]]]:
    """Provide python func."""
    def _python_dataset() -> Dataset[Model[object]]:
        """Return python dataset."""
        return python_dataset

    return _python_dataset
