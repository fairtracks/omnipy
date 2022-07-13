from deepdiff import DeepDiff
import numpy as np
import pandas as pd
from pydantic import ValidationError
import pytest

from dataset.test_common import _assert_pandas_frame_dtypes
from unifair.dataset.pandas import PandasDataset


def test_pandas_dataset_list_of_objects_same_keys():
    pandas_data = PandasDataset()
    data = {'obj_type': [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 'abc', 'b': 12
        }, {
            'a': 'bcd', 'b': 23
        }]),
        check_dtype=False,
    )
    _assert_pandas_frame_dtypes(pandas_data['obj_type'], ('object', 'Int64'))
    assert pandas_data.to_data() == data


def test_pandas_dataset_list_of_objects_different_keys():
    pandas_data = PandasDataset()
    data = {'obj_type': [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 'abc', 'b': 12, 'c': None
        }, {
            'a': None, 'b': None, 'c': 'bcd'
        }]),
        check_dtype=False,
    )
    _assert_pandas_frame_dtypes(pandas_data['obj_type'], ('object', 'Int64', 'object'))
    assert pandas_data.to_data() == {
        'obj_type': [{
            'a': 'abc', 'b': 12, 'c': np.nan
        }, {
            'a': np.nan, 'b': pd.NA, 'c': 'bcd'
        }]
    }


def test_pandas_dataset_list_of_objects_float_numbers():
    pandas_data = PandasDataset()
    data = {'obj_type': [{'a': 12.0, 'b': 12.1}, {'a': 3.0}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': None
        }]),
    )
    _assert_pandas_frame_dtypes(pandas_data['obj_type'], ('float64', 'float64'))
    assert not DeepDiff(
        pandas_data.to_data(), {'obj_type': [{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': np.nan
        }]},
        significant_digits=3)


@pytest.mark.skip(reason="""
Currently, columns of dtype=float64 are currently changed into the 'nullable integer' dtype `Int64`
if all values in the column are either whole numbers or nan. This might be incorrect in relation
to the data model imported from. Prior knowledge of the imported data model (before pandas import)
is required to do better. This should be handled in the planned refactoring of imports/exports. """)
def test_pandas_dataset_list_of_objects_float_numbers():
    pandas_data = PandasDataset()
    data = {
        'obj_type': [
            {
                'a': 12.0, 'b': 12.1
            },
            {
                'a': 3.0
            },
            {
                'b': 14.3
            },
        ]
    }
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': None
        }, {
            'a': None, 'b': 14.3
        }]),
    )
    _assert_pandas_frame_dtypes(pandas_data['obj_type'], ('float64', 'float64'))
    assert not DeepDiff(
        pandas_data.to_data(),
        {'obj_type': [{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': np.nan
        }, {
            'a': np.nan, 'b': 14.3
        }]},
        significant_digits=3)


def test_pandas_dataset_list_of_nested_objects():
    pandas_data = PandasDataset()
    data = {'obj_type': [{'a': 'abc', 'b': {'c': [1, 3]}}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 'abc', 'b': {
                'c': [1, 3]
            }
        }]),
    )
    _assert_pandas_frame_dtypes(pandas_data['obj_type'], ('object', 'object'))
    assert pandas_data.to_data() == data
    assert pandas_data['obj_type'].loc[0, 'b'] == {'c': [1, 3]}


def test_pandas_dataset_empty_list():
    pandas_data = PandasDataset()
    assert pandas_data.to_data() == {}

    pandas_data.from_data({'obj_type': []})
    assert isinstance(pandas_data['obj_type'], pd.DataFrame) and pandas_data['obj_type'].empty
    assert pandas_data.to_data() == {'obj_type': []}


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
