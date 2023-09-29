from math import nan
import os

from deepdiff import DeepDiff
import numpy as np
from pydantic import ValidationError
import pytest

from omnipy.modules.pandas import pd
from omnipy.modules.pandas.models import PandasDataset

from .util import assert_pandas_frame_dtypes


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
    assert_pandas_frame_dtypes(pandas_data['obj_type'], ('string', 'Int64'))
    assert pandas_data.to_data() == data


def test_pandas_dataset_json_list_of_objects_same_keys():
    pandas_data = PandasDataset()
    json_data = {'obj_type': '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'}
    pandas_data.from_json(json_data)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'a': 'abc', 'b': 12
        }, {
            'a': 'bcd', 'b': 23
        }]),
        check_dtype=False,
    )
    assert_pandas_frame_dtypes(pandas_data['obj_type'], ('string', 'Int64'))
    assert pandas_data.to_json() == json_data


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
    assert_pandas_frame_dtypes(pandas_data['obj_type'], ('string', 'Int64', 'string'))
    assert pandas_data.to_data() == {
        'obj_type': [{
            'a': 'abc', 'b': 12, 'c': None
        }, {
            'a': None, 'b': None, 'c': 'bcd'
        }]
    }


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Pandas converts 'a' column into 'Int64' since all values can be cast into integers.
 Should remain floats.
""")
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
    assert_pandas_frame_dtypes(pandas_data['obj_type'], ('Float64', 'Float64'))
    assert not DeepDiff(
        pandas_data.to_data(), {'obj_type': [{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': np.nan
        }]},
        significant_digits=3)


def test_pandas_dataset_list_of_objects_float_numbers_and_missing_values():
    pandas_data = PandasDataset()
    data = {
        'obj_type': [
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
    }
    pandas_data.from_data(data)

    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame([{
            'int': 12, 'float': 12.1, 'bool': True, 'str': 'abc'
        }, {
            'int': -3, 'float': pd.NA, 'bool': False, 'str': pd.NA
        }, {
            'int': pd.NA, 'float': 14.3, 'bool': pd.NA, 'str': 'def'
        }],),
        check_dtype=False,
    )

    assert_pandas_frame_dtypes(pandas_data['obj_type'], ('Int64', 'Float64', 'boolean', 'string'))

    assert pandas_data.to_data() == {
        'obj_type': [{
            'int': 12, 'float': 12.1, 'bool': True, 'str': 'abc'
        }, {
            'int': -3, 'float': None, 'bool': False, 'str': None
        }, {
            'int': None, 'float': 14.3, 'bool': None, 'str': 'def'
        }]
    }


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
        check_dtype=False)
    assert_pandas_frame_dtypes(pandas_data['obj_type'], ('string', 'object'))
    assert pandas_data.to_data() == data
    assert pandas_data['obj_type'].loc[0, 'b'] == {'c': [1, 3]}


@pytest.mark.skipif(os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1', reason='To be implemented later')
def test_pandas_dataset_missing_values():
    pandas_data = PandasDataset()
    pandas_data.from_data(
        {'obj_type': [dict(a=1, b='a', c=1.0, d=True), dict(a=None, b=None, c=None, d=None)]})
    assert pandas_data.to_data() == {
        'obj_type': [dict(a=1, b='a', c=1.0, d=True), dict(a=None, b='', c=nan, d=None)]
    }


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
