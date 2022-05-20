import pandas as pd
from pydantic import ValidationError
import pytest

from unifair.data.pandas import PandasDataset


def test_pandas_dataset_list_of_objects_same_keys():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 'abc', 'b': 12
        }, {
            'a': 'bcd', 'b': 23
        }]),
        check_dtype=False,
    )


def test_pandas_dataset_list_of_objects_different_keys():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 'abc', 'b': 12, 'c': None
        }, {
            'a': None, 'b': None, 'c': 'bcd'
        }]),
        check_dtype=False,
    )


def test_pandas_dataset_list_of_objects_float_numbers():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 12.0, 'b': 12.1}, {'a': 3.0}]
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': None
        }]),
        check_dtype=True,
    )


def test_pandas_dataset_list_of_nested_objects():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 'abc', 'b': {'c': [1, 3]}}]
    assert pandas_data['obj_type'].equals(pd.DataFrame([{'a': 'abc', 'b': {'c': [1, 3]}}]))
    assert pandas_data['obj_type'].loc[0, 'b'] == {'c': [1, 3]}


def test_pandas_dataset_empty_list():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = []
    assert pandas_data['obj_type'].equals(pd.DataFrame())


def test_pandas_dataset_error_not_list():
    pandas_data = PandasDataset()
    with pytest.raises(ValueError):
        pandas_data['obj_type'] = '1'


def test_pandas_dataset_error_list_items_not_objects():
    pandas_data = PandasDataset()
    with pytest.raises(ValidationError):
        pandas_data['obj_type'] = [123, 234]


def test_pandas_dataset_error_objects_keys_not_str():
    pandas_data = PandasDataset()
    with pytest.raises(ValidationError):
        pandas_data['obj_type'] = [{123: 'abc', 'b': 12}]


def test_pandas_dataset_error_empty_objects():
    # We might want to reevaluate how to handle empty objects later
    pandas_data = PandasDataset()
    with pytest.raises(ValidationError):
        pandas_data['obj_type'] = [{'a': 'abc', 'b': 12}, {}]
