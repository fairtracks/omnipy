from math import nan
import os

from deepdiff import DeepDiff
import numpy as np
import pytest

from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.pandas.models import PandasModel
from omnipy.components.tables.models import RowWiseTableListOfDictsModel
from omnipy.util._pydantic import ValidationError

from .helpers.asserts import assert_pandas_frame_dtypes

# Placeholder


def test_pandas_dataset_input_variants():
    from omnipy.components.pandas.lazy_import import pd

    table = RowWiseTableListOfDictsModel([{'a': 'abc', 'b': 12}])
    df = pd.concat([
        pd.Series(['abc'], dtype='string'),
        pd.Series([12], dtype='Int64'),
    ], axis=1)
    df.columns = ('a', 'b')

    dataset_1 = PandasDataset()
    dataset_1.from_data({'data_file': [{'a': 'abc', 'b': 12}]})

    dataset_2 = PandasDataset()
    dataset_2.from_json({'data_file': '[{"a": "abc", "b": 12}]'})
    pd.testing.assert_frame_equal(dataset_1['data_file'].content, dataset_2['data_file'].content)

    dataset_3 = PandasDataset()
    dataset_3['data_file'] = [{'a': 'abc', 'b': 12}]
    pd.testing.assert_frame_equal(dataset_2['data_file'].content, dataset_3['data_file'].content)

    dataset_4 = PandasDataset()
    dataset_4['data_file'] = table
    pd.testing.assert_frame_equal(dataset_3['data_file'].content, dataset_4['data_file'].content)

    dataset_5 = PandasDataset()
    dataset_5['data_file'] = df
    pd.testing.assert_frame_equal(dataset_4['data_file'].content, dataset_5['data_file'].content)

    dataset_6 = PandasDataset()
    dataset_6['data_file'] = PandasModel([{'a': 'abc', 'b': 12}])
    pd.testing.assert_frame_equal(dataset_5['data_file'].content, dataset_6['data_file'].content)

    dataset_7 = PandasDataset(data_file=[{'a': 'abc', 'b': 12}])
    pd.testing.assert_frame_equal(dataset_6['data_file'].content, dataset_7['data_file'].content)

    dataset_8 = PandasDataset(data_file=table)
    pd.testing.assert_frame_equal(dataset_7['data_file'].content, dataset_8['data_file'].content)

    dataset_9 = PandasDataset(data_file=df)
    pd.testing.assert_frame_equal(dataset_8['data_file'].content, dataset_9['data_file'].content)

    dataset_10 = PandasDataset(data_file=PandasModel([{'a': 'abc', 'b': 12}]))
    pd.testing.assert_frame_equal(dataset_9['data_file'].content, dataset_10['data_file'].content)


def test_pandas_dataset_list_of_objects_same_keys():
    from omnipy.components.pandas.lazy_import import pd

    pandas_data = PandasDataset()
    data = {'data_file': [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['data_file'].content,
        pd.DataFrame([{
            'a': 'abc', 'b': 12
        }, {
            'a': 'bcd', 'b': 23
        }]),
        check_dtype=False,
    )
    assert_pandas_frame_dtypes(pandas_data['data_file'], ('string', 'Int64'))
    assert pandas_data.to_data() == data


def test_pandas_dataset_json_list_of_objects_same_keys():
    from omnipy.components.pandas.lazy_import import pd

    pandas_data = PandasDataset()
    json_data = {'data_file': '[{"a":"abc","b":12},{"a":"bcd","b":23}]'}
    pandas_data.from_json(json_data)
    pd.testing.assert_frame_equal(
        pandas_data['data_file'].content,
        pd.DataFrame([{
            'a': 'abc', 'b': 12
        }, {
            'a': 'bcd', 'b': 23
        }]),
        check_dtype=False,
    )
    assert_pandas_frame_dtypes(pandas_data['data_file'], ('string', 'Int64'))
    assert pandas_data.to_json(pretty=False) == json_data


def test_pandas_dataset_list_of_objects_different_keys():
    from omnipy.components.pandas.lazy_import import pd

    pandas_data = PandasDataset()
    data = {'data_file': [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['data_file'].content,
        pd.DataFrame([{
            'a': 'abc', 'b': 12, 'c': None
        }, {
            'a': None, 'b': None, 'c': 'bcd'
        }]),
        check_dtype=False,
    )
    assert_pandas_frame_dtypes(pandas_data['data_file'], ('string', 'Int64', 'string'))
    assert pandas_data.to_data() == {
        'data_file': [{
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
    from omnipy.components.pandas.lazy_import import pd

    pandas_data = PandasDataset()
    data = {'data_file': [{'a': 12.0, 'b': 12.1}, {'a': 3.0}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['data_file'].content,
        pd.DataFrame([{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': None
        }]),
    )
    assert_pandas_frame_dtypes(pandas_data['data_file'], ('Float64', 'Float64'))
    assert not DeepDiff(
        pandas_data.to_data(), {'data_file': [{
            'a': 12.0, 'b': 12.1
        }, {
            'a': 3.0, 'b': np.nan
        }]},
        significant_digits=3)


def test_pandas_dataset_list_of_nested_objects():
    from omnipy.components.pandas.lazy_import import pd

    pandas_data = PandasDataset()
    data = {'data_file': [{'a': 'abc', 'b': {'c': [1, 3]}}]}
    pandas_data.from_data(data)
    pd.testing.assert_frame_equal(
        pandas_data['data_file'].content,
        pd.DataFrame([{
            'a': 'abc', 'b': {
                'c': [1, 3]
            }
        }]),
        check_dtype=False)
    assert_pandas_frame_dtypes(pandas_data['data_file'], ('string', 'object'))
    assert pandas_data.to_data() == data
    assert pandas_data['data_file'].content.loc[0, 'b'] == {'c': [1, 3]}


@pytest.mark.skipif(os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1', reason='To be implemented later')
def test_pandas_dataset_missing_values():
    pandas_data = PandasDataset()
    pandas_data.from_data(
        {'data_file': [dict(a=1, b='a', c=1.0, d=True), dict(a=None, b=None, c=None, d=None)]})
    assert pandas_data.to_data() == {
        'data_file': [dict(a=1, b='a', c=1.0, d=True), dict(a=None, b='', c=nan, d=None)]
    }


def test_pandas_dataset_empty_list():
    from omnipy.components.pandas.lazy_import import pd

    pandas_data = PandasDataset()
    assert pandas_data.to_data() == {}

    pandas_data.from_data({'data_file': []})
    assert isinstance(pandas_data['data_file'].content,
                      pd.DataFrame) and pandas_data['data_file'].content.empty
    assert pandas_data.to_data() == {'data_file': []}


def test_pandas_dataset_error_not_list():
    pandas_data = PandasDataset()
    with pytest.raises(ValueError):
        pandas_data['data_file'] = '1'


def test_pandas_dataset_error_list_items_not_objects():
    pandas_data = PandasDataset()
    with pytest.raises(ValidationError):
        pandas_data['data_file'] = [123, 234]


def test_pandas_dataset_objects_keys_not_str():
    pandas_data = PandasDataset()
    pandas_data['data_file'] = [{123: 'abc', 'b': 12}]
    assert pandas_data['data_file'].columns[0] == '123'


def test_pandas_dataset_error_empty_objects():
    from omnipy.components.pandas.lazy_import import pd

    # We might want to reevaluate how to handle empty objects later
    pandas_data = PandasDataset()
    pandas_data['data_file'] = [{'a': 'abc', 'b': 12}, {}]
    assert pd.isna(pandas_data['data_file'].loc[1]).all()


# Placeholder
def test_pandas_model_input_output_json():
    ...
