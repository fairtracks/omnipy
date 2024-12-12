from typing import Annotated

import pytest

from omnipy.modules.json.typedefs import JsonListOfDictsOfScalars
from omnipy.modules.pandas import pd
from omnipy.modules.pandas.models import PandasModel


@pytest.fixture
def list_of_dicts_data_with_missing() -> Annotated[JsonListOfDictsOfScalars, pytest.fixture]:
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
def dataframe_of_list_of_dicts_data() -> Annotated[pd.DataFrame, pytest.fixture]:
    int_col = pd.Series([12, -3, pd.NA], dtype='Int64')
    float_col = pd.Series([12.1, pd.NA, 14.3], dtype='Float64')
    bool_col = pd.Series([True, False, pd.NA], dtype='boolean')
    str_col = pd.Series(['abc', pd.NA, 'def'], dtype='string[python]')
    df = pd.concat([int_col, float_col, bool_col, str_col], axis=1)
    df.columns = ('int', 'float', 'bool', 'str')  # type: ignore[assignment]
    return df


@pytest.fixture
def list_of_dicts_data_with_nones() -> Annotated[JsonListOfDictsOfScalars, pytest.fixture]:
    return [{
        'bool': True, 'float': 12.1, 'int': 12, 'str': 'abc'
    }, {
        'bool': False, 'float': None, 'int': -3, 'str': None
    }, {
        'bool': None, 'float': 14.3, 'int': None, 'str': 'def'
    }]


def test_pandas_model_from_data_to_data(
    list_of_dicts_data_with_missing: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
    dataframe_of_list_of_dicts_data: Annotated[pd.DataFrame, pytest.fixture],
    list_of_dicts_data_with_nones: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
) -> None:
    pandas_model = PandasModel()
    pandas_model.from_data(list_of_dicts_data_with_missing)
    pd.testing.assert_frame_equal(
        pandas_model.contents,  # type: ignore
        dataframe_of_list_of_dicts_data,
    )
    assert pandas_model.to_data() == list_of_dicts_data_with_nones


def test_pandas_model_init_to_data(
    list_of_dicts_data_with_missing: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
    dataframe_of_list_of_dicts_data: Annotated[pd.DataFrame, pytest.fixture],
    list_of_dicts_data_with_nones: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
) -> None:
    pandas_model = PandasModel(list_of_dicts_data_with_missing)
    pd.testing.assert_frame_equal(
        pandas_model.contents,  # type: ignore
        dataframe_of_list_of_dicts_data,
    )
    assert pandas_model.to_data() == list_of_dicts_data_with_nones


def test_pandas_model_init_dataframe_to_data(
    dataframe_of_list_of_dicts_data: Annotated[pd.DataFrame, pytest.fixture],
    list_of_dicts_data_with_nones: Annotated[JsonListOfDictsOfScalars, pytest.fixture],
) -> None:
    pandas_model = PandasModel(dataframe_of_list_of_dicts_data)

    pd.testing.assert_frame_equal(
        pandas_model.contents,  # type: ignore
        dataframe_of_list_of_dicts_data,
    )
    assert pandas_model.to_data() == list_of_dicts_data_with_nones


def test_pandas_model_from_json_to_json():
    ...


def test_operation_pandas():
    a = PandasModel()
    a.from_data([{'x': 2, 'y': 3}, {'x': 3, 'y': -1}])

    assert type(a) is PandasModel

    b = a + 1

    assert type(b) is PandasModel


def test_method_pandas():
    a = PandasModel()
    a.from_data([{'x': 2, 'y': 3}, {'x': 3, 'y': -1}])

    assert type(a) is PandasModel

    b = a.abs()

    assert type(b) is PandasModel


def test_col_select_pandas():
    a = PandasModel()
    a.from_data([{'x': 2, 'y': 3, 'z': 2}, {'x': 3, 'y': -1, 'z': 3}])

    assert type(a) is PandasModel

    b = a[['x', 'y']]

    assert type(b) is PandasModel
