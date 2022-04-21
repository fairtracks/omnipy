import pandas as pd
import pytest
from pydantic import ValidationError

from unifair.data.pandas import PandasDataset


def test_pandas_dataset_list_of_objects_same_keys():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]
    assert pandas_data['obj_type'].equals(pd.DataFrame([{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]))


def test_pandas_dataset_list_of_objects_different_keys():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]
    assert pandas_data['obj_type'].equals(
        pd.DataFrame([{'a': 'abc', 'b': 12, 'c': None}, {'a': None, 'b': None, 'c': 'bcd'}])
    )


def test_pandas_dataset_list_of_nested_objects():
    pandas_data = PandasDataset()
    pandas_data['obj_type'] = [{'a': 'abc', 'b': {'c': [1, 3]}}]
    assert pandas_data['obj_type'].equals(
        pd.DataFrame([{'a': 'abc', 'b': {'c': [1, 3]}}])
    )
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
