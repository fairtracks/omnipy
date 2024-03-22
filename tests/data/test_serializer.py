import sys

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import DatasetToTarFileSerializer, SerializerRegistry

from .helpers.functions import assert_directory_in_tar_file, assert_tar_file_contents
from .helpers.mocks import MockNumberSerializer, MockNumberToTarFileSerializer, NumberDataset


def test_number_dataset_serializer():
    number_data = Dataset[Model[int]]()

    number_data['data_file_1'] = 35
    number_data['data_file_2'] = 12

    serializer = MockNumberSerializer()

    assert serializer.get_dataset_cls_for_new() is NumberDataset
    assert not serializer.is_dataset_directly_supported(number_data)

    serialized_bytes = serializer.serialize(number_data)
    assert serialized_bytes == b'data_file_1:35,data_file_2:12'

    deserialized_obj = serializer.deserialize(serialized_bytes)
    assert deserialized_obj.to_data() == number_data.to_data()
    assert type(deserialized_obj) is NumberDataset


def test_number_dataset_to_tar_file_serializer():
    number_data = NumberDataset()

    number_data['data_file_1'] = 35
    number_data['data_file_2'] = 12

    serializer = MockNumberToTarFileSerializer()

    assert serializer.get_dataset_cls_for_new() is NumberDataset
    assert serializer.is_dataset_directly_supported(number_data)

    tarfile_bytes = serializer.serialize(number_data)
    decode_func = lambda x: int.from_bytes(x, byteorder=sys.byteorder)  # noqa

    assert_tar_file_contents(tarfile_bytes, 'data_file_1', 'num', decode_func, 35)
    assert_tar_file_contents(tarfile_bytes, 'data_file_2', 'num', decode_func, 12)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == number_data


def test_dataset_of_number_dataset_to_tar_file_serializer():
    hierarchical_number_data = Dataset[Model[Dataset[Model[int]]]]()

    hierarchical_number_data['data_dir_1'] = dict(data_file_1=35, data_file_2=27)
    hierarchical_number_data['data_dir_2'] = dict(data_file_2=13, data_file_3=45)

    registry = SerializerRegistry()
    registry.register(DatasetToTarFileSerializer)
    registry.register(MockNumberToTarFileSerializer)

    serializer = DatasetToTarFileSerializer(registry)

    assert serializer.get_dataset_cls_for_new() is Dataset[Model[NumberDataset]]
    assert serializer.is_dataset_directly_supported(hierarchical_number_data)

    tarfile_bytes = serializer.serialize(hierarchical_number_data)
    decode_func = lambda x: int.from_bytes(x, byteorder=sys.byteorder)  # noqa

    assert_directory_in_tar_file(tarfile_bytes, 'data_dir_1')
    assert_directory_in_tar_file(tarfile_bytes, 'data_dir_2')

    assert_tar_file_contents(tarfile_bytes, 'data_dir_1/data_file_1', 'num', decode_func, 35)
    assert_tar_file_contents(tarfile_bytes, 'data_dir_1/data_file_2', 'num', decode_func, 27)
    assert_tar_file_contents(tarfile_bytes, 'data_dir_2/data_file_2', 'num', decode_func, 13)
    assert_tar_file_contents(tarfile_bytes, 'data_dir_2/data_file_3', 'num', decode_func, 45)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == hierarchical_number_data


def test_serializer_registry():
    registry = SerializerRegistry()

    registry.register(MockNumberToTarFileSerializer)
    registry.register(MockNumberSerializer)

    assert registry.serializers == (MockNumberToTarFileSerializer, MockNumberSerializer)
    assert registry.tar_file_serializers == (MockNumberToTarFileSerializer,)
    assert registry.detect_tar_file_serializers_from_file_suffix('num') == \
           (MockNumberToTarFileSerializer,)
