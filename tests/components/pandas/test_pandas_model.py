"""Tests for pandas model conversions and operations."""

from typing import Annotated

import pytest

from omnipy.components.json.typedefs import JsonDictOfListsOfScalars, JsonListOfDictsOfScalars
from omnipy.components.pandas.models import PandasModel
from omnipy.shared.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnipy.components.pandas.lazy_import import pd


@pytest.fixture
def list_of_dicts_data_with_missing() -> Annotated[JsonListOfDictsOfScalars, pytest.fixture]:
    """Return list-of-dict data with missing fields across rows."""
    return [
        {
            'int': 12, 'float': 12.1, 'bool': True, 'str': 'abc'
        },
        {
            'int': -3, 'bool': False
        },
        {
            'float': 14.3, 'str': 'def'
        },
    ]


@pytest.fixture
def dataframe_of_list_of_dicts_data() -> 'Annotated[pd.DataFrame, pytest.fixture]':
    """Return the dataframe equivalent of the shared list-of-dict fixture."""
    from omnipy.components.pandas.lazy_import import pd

    int_col = pd.Series([12, -3, pd.NA], dtype='Int64')
    float_col = pd.Series([12.1, pd.NA, 14.3], dtype='Float64')
    bool_col = pd.Series([True, False, pd.NA], dtype='boolean')
    str_col = pd.Series(['abc', pd.NA, 'def'], dtype='string')
    df = pd.concat([int_col, float_col, bool_col, str_col], axis=1)
    df.columns = ('int', 'float', 'bool', 'str')
    return df


@pytest.fixture
def dict_of_lists_data_with_nones() -> Annotated[JsonDictOfListsOfScalars, pytest.fixture]:
    return {
        'bool': [True, False, None],
        'float': [12.1, None, 14.3],
        'int': [12, -3, None],
        'str': ['abc', None, 'def']
    }


def test_pandas_model_from_data_to_data(
    list_of_dicts_data_with_missing: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
    dataframe_of_list_of_dicts_data: 'Annotated[pd.DataFrame, pytest.fixture]',
    dict_of_lists_data_with_nones: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
) -> None:
    """Test converting pandas model data from and back to Python data."""
    from omnipy.components.pandas.lazy_import import pd

    pandas_model = PandasModel()
    pandas_model.from_data(list_of_dicts_data_with_missing)
    pd.testing.assert_frame_equal(
        pandas_model.content,  # type: ignore
        dataframe_of_list_of_dicts_data,
    )
    assert pandas_model.to_data() == dict_of_lists_data_with_nones


def test_pandas_model_init_to_data(
    list_of_dicts_data_with_missing: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
    dataframe_of_list_of_dicts_data: 'Annotated[pd.DataFrame, pytest.fixture]',
    dict_of_lists_data_with_nones: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
) -> None:
    """Test initializing a pandas model from Python data."""
    from omnipy.components.pandas.lazy_import import pd

    pandas_model = PandasModel(list_of_dicts_data_with_missing)
    pd.testing.assert_frame_equal(
        pandas_model.content,  # type: ignore
        dataframe_of_list_of_dicts_data,
    )
    assert pandas_model.to_data() == dict_of_lists_data_with_nones


def test_pandas_model_init_dataframe_to_data(
    dataframe_of_list_of_dicts_data: 'Annotated[pd.DataFrame, pytest.fixture]',
    dict_of_lists_data_with_nones: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
) -> None:
    """Test initializing a pandas model directly from a dataframe."""
    from omnipy.components.pandas.lazy_import import pd

    pandas_model = PandasModel(dataframe_of_list_of_dicts_data)

    pd.testing.assert_frame_equal(
        pandas_model.content,  # type: ignore
        dataframe_of_list_of_dicts_data,
    )
    assert pandas_model.to_data() == dict_of_lists_data_with_nones


def test_pandas_model_from_json_to_json():
    """Test pandas model JSON round-tripping."""
    ...


def test_operation_pandas():
    """Test pandas model arithmetic returning a pandas model."""
    a = PandasModel()
    a.from_data([{'x': 2, 'y': 3}, {'x': 3, 'y': -1}])

    assert type(a) is PandasModel

    b = a + 1

    assert type(b) is PandasModel


def test_method_pandas():
    """Test pandas model methods returning a pandas model."""
    a = PandasModel()
    a.from_data([{'x': 2, 'y': 3}, {'x': 3, 'y': -1}])

    assert type(a) is PandasModel

    b = a.abs()

    assert type(b) is PandasModel


def test_col_select_pandas():
    """Test selecting pandas model columns preserves model type."""
    a = PandasModel()
    a.from_data([{'x': 2, 'y': 3, 'z': 2}, {'x': 3, 'y': -1, 'z': 3}])

    assert type(a) is PandasModel

    b = a[['x', 'y']]

    assert type(b) is PandasModel
