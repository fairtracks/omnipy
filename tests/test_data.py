import os
from tempfile import TemporaryDirectory

import pandas as pd
from pandas.testing import assert_frame_equal

from unifair.core.data import JsonDocumentCollection, PandasDataFrameCollection


def test_pandas_dataframe_add():
    df_coll = PandasDataFrameCollection()

    name = 'data1'
    df = pd.DataFrame.from_dict({'a': [1, 2, 3], 'b': [2, 3, 4]})
    df_coll[name] = df
    assert_frame_equal(df_coll[name], df)


def test_pandas_dataframe_readwrite():
    df_coll_1 = PandasDataFrameCollection()
    df_coll_2 = PandasDataFrameCollection()

    name = 'data1'
    df = pd.DataFrame.from_dict({
        'A': [1, 2, 3], 'B': ["{'a': [1, 2, 3]}", "{'b': [2, 4, 6]}", "{'c': [3, 6, 9]}"]
    })
    df_coll_1[name] = df

    with TemporaryDirectory() as tmpdirname:
        df_coll_1.write_to_dir(tmpdirname)

        with open(os.path.join(tmpdirname, name + '.csv')) as out_file:
            assert out_file.read() == """
,A,B
0,1,"{'a': [1, 2, 3]}"
1,2,"{'b': [2, 4, 6]}"
2,3,"{'c': [3, 6, 9]}"
"""[1:]

        df_coll_2.read_from_dir(tmpdirname)
        assert_frame_equal(df_coll_1[name], df_coll_2[name])


def test_json_document_add():
    json_coll = JsonDocumentCollection()

    name = 'data1'
    obj = {'a': [1, 2, 3], 'b': [2, 3, 4]}
    json_coll[name] = obj
    assert json_coll[name] == obj


def test_json_document_readwrite():
    df_coll_1 = JsonDocumentCollection()
    df_coll_2 = JsonDocumentCollection()

    name = 'data1'
    obj = {'A': [1, 2, 3], 'B': [{'a': [1, 2, 3]}, {'b': [2, 4, 6]}, {'c': [3, 6, 9]}]}
    df_coll_1[name] = obj

    with TemporaryDirectory() as tmpdirname:
        df_coll_1.write_to_dir(tmpdirname)

        with open(os.path.join(tmpdirname, name + '.json')) as out_file:
            assert out_file.read() == """
{
    "A": [
        1,
        2,
        3
    ],
    "B": [
        {
            "a": [
                1,
                2,
                3
            ]
        },
        {
            "b": [
                2,
                4,
                6
            ]
        },
        {
            "c": [
                3,
                6,
                9
            ]
        }
    ]
}
"""[1:]

        df_coll_2.read_from_dir(tmpdirname)
        assert df_coll_1[name] == df_coll_2[name]


# TODO: Add tests for format validation
