from textwrap import dedent

from omnipy.modules.pandas.models import PandasDataset
from omnipy.modules.pandas.serializers import PandasDatasetToTarFileSerializer

from ...data.helpers.functions import assert_tar_file_contents
from .helpers.asserts import assert_pandas_dataset_equals


def test_pandas_dataset_serializer_to_tar_file():
    pandas_data = PandasDataset()
    pandas_data.from_data({'data_file_1': [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]})
    pandas_data.from_data({'data_file_2': [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]})
    # fmt: off
    data_file_1_csv = dedent("""\
        a,b
        abc,12
        bcd,23
        """)

    data_file_2_csv = dedent("""\
        a,b,c
        abc,12,
        ,,bcd
        """)

    serializer = PandasDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(pandas_data)
    decode_func = lambda x: x.decode('utf8')  # noqa

    assert_tar_file_contents(tarfile_bytes, 'data_file_1', 'csv', decode_func, data_file_1_csv)
    assert_tar_file_contents(tarfile_bytes, 'data_file_2', 'csv', decode_func, data_file_2_csv)

    deserialized_pandas_data = serializer.deserialize(tarfile_bytes)

    assert_pandas_dataset_equals(deserialized_pandas_data, pandas_data)
