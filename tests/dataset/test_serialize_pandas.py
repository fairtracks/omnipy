from tests.dataset.test_common import (_assert_pandas_dataset_equals, _assert_tar_file_contents)
from unifair.dataset.pandas import (PandasDataset, PandasDatasetToTarFileSerializer)


def test_pandas_dataset_serializer_to_tar_file():
    pandas_data = PandasDataset()
    pandas_data['obj_type_1'] = [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]
    pandas_data['obj_type_2'] = [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]

    # fmt: off
    obj_type_1_csv = """
,a,b
0,abc,12
1,bcd,23
"""[1:]

    obj_type_2_csv = """
,a,b,c
0,abc,12,
1,,,bcd
"""[1:]

    serializer = PandasDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(pandas_data)
    decode_func = lambda x: x.decode('utf8')  # noqa

    _assert_tar_file_contents(tarfile_bytes, 'obj_type_1', 'csv', decode_func, obj_type_1_csv)
    _assert_tar_file_contents(tarfile_bytes, 'obj_type_2', 'csv', decode_func, obj_type_2_csv)

    deserialized_pandas_data = serializer.deserialize(tarfile_bytes)

    _assert_pandas_dataset_equals(deserialized_pandas_data, pandas_data)
