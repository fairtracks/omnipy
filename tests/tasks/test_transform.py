import pandas as pd

from unifair.data.json import JsonDataset
from unifair.data.pandas import PandasDataset
from unifair.tasks.transform import convert_json_to_pandas


def test_convert_to_pandas():
    json_data = JsonDataset()
    json_data['obj_1'] = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 34}]'
    json_data['obj_2'] = '[{"c": 12, "d": "aaa", "e": "xyz"}, {"c": 23, "d": "bbb", "e": "zyx"}]'

    pandas_data = convert_json_to_pandas(json_data)

    assert isinstance(pandas_data, PandasDataset)
    assert pandas_data['obj_1'].equals(pd.DataFrame({'a': ['abc', 'bcd'], 'b': [12, 34]}))
    assert pandas_data['obj_2'].equals(pd.DataFrame({'c': [12, 23], 'd': ['aaa', 'bbb'], 'e': ['xyz', 'zyx']}))


def test_convert_to_pandas_no_records():
    json_data = JsonDataset()
    json_data['obj'] = '[]'

    pandas_data = convert_json_to_pandas(json_data)

    assert isinstance(pandas_data, PandasDataset)
    assert pandas_data['obj'].equals(pd.DataFrame())


