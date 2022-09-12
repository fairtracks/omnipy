import pandas as pd
import pytest

from unifair.modules.json.models import JsonDataset
from unifair.modules.pandas.models import PandasDataset
from unifair.old.tasks.transform import convert_json_to_pandas


@pytest.mark.skip(reason='Outdated')
def test_convert_to_pandas():
    json_data = JsonDataset()
    json_data['obj_type_1'] = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 34}]'
    json_data['obj_type_2'] = \
        '[{"c": 12, "d": "aaa", "e": "xyz"}, {"c": 23, "d": "bbb", "e": "zyx"}]'  # yapf: disable
    pandas_data = convert_json_to_pandas(json_data)

    assert isinstance(pandas_data, PandasDataset)
    pd.testing.assert_frame_equal(
        pandas_data['obj_type_1'],
        pd.DataFrame({
            'a': ['abc', 'bcd'], 'b': [12, 34]
        }),
        check_dtype=False,
    )
    pd.testing.assert_frame_equal(
        pandas_data['obj_type_2'],
        pd.DataFrame({
            'c': [12, 23], 'd': ['aaa', 'bbb'], 'e': ['xyz', 'zyx']
        }),
        check_dtype=False,
    )


@pytest.mark.skip(reason='Outdated')
def test_convert_to_pandas_no_records():
    json_data = JsonDataset()
    json_data['obj_type'] = '[]'

    pandas_data = convert_json_to_pandas(json_data)

    assert isinstance(pandas_data, PandasDataset)

    pd.testing.assert_frame_equal(
        pandas_data['obj_type'],
        pd.DataFrame(),
    )