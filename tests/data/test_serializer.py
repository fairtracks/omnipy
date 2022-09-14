import sys

from unifair.data.dataset import Dataset
from unifair.data.model import Model

from .helpers.functions import assert_tar_file_contents
from .helpers.mocks import MockNumberSerializer, MockNumberToTarFileSerializer, NumberDataset


def test_number_dataset_serializer():
    number_data = Dataset[Model[int]]()

    number_data['obj_type1'] = 35
    number_data['obj_type2'] = 12

    serializer = MockNumberSerializer()
    serialized_bytes = serializer.serialize(number_data)

    assert serialized_bytes == b'obj_type1:35,obj_type2:12'
    assert serializer.deserialize(serialized_bytes) == number_data


def test_number_dataset_to_tar_file_serializer():
    number_data = NumberDataset()

    number_data['obj_type1'] = 35
    number_data['obj_type2'] = 12

    serializer = MockNumberToTarFileSerializer()
    tarfile_bytes = serializer.serialize(number_data)
    decode_func = lambda x: int.from_bytes(x, byteorder=sys.byteorder)  # noqa

    assert_tar_file_contents(tarfile_bytes, 'obj_type1', 'num', decode_func, 35)
    assert_tar_file_contents(tarfile_bytes, 'obj_type2', 'num', decode_func, 12)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == number_data
