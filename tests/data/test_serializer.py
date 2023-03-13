import sys

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import SerializerRegistry

from .helpers.functions import assert_tar_file_contents
from .helpers.mocks import MockNumberSerializer, MockNumberToTarFileSerializer, NumberDataset


def test_number_dataset_serializer():
    number_data = Dataset[Model[int]]()

    number_data['obj_type1'] = 35
    number_data['obj_type2'] = 12

    serializer = MockNumberSerializer()

    assert serializer.get_dataset_cls_for_new() is NumberDataset

    serialized_bytes = serializer.serialize(number_data)
    assert serialized_bytes == b'obj_type1:35,obj_type2:12'

    deserialized_obj = serializer.deserialize(serialized_bytes)
    assert deserialized_obj.to_data() == number_data.to_data()
    assert type(deserialized_obj) is NumberDataset


def test_number_dataset_to_tar_file_serializer():
    number_data = NumberDataset()

    number_data['obj_type1'] = 35
    number_data['obj_type2'] = 12

    serializer = MockNumberToTarFileSerializer()

    assert serializer.get_dataset_cls_for_new() is NumberDataset

    tarfile_bytes = serializer.serialize(number_data)
    decode_func = lambda x: int.from_bytes(x, byteorder=sys.byteorder)  # noqa

    assert_tar_file_contents(tarfile_bytes, 'obj_type1', 'num', decode_func, 35)
    assert_tar_file_contents(tarfile_bytes, 'obj_type2', 'num', decode_func, 12)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == number_data


def test_serializer_registry():
    registry = SerializerRegistry()

    registry.register(MockNumberToTarFileSerializer)
    registry.register(MockNumberSerializer)

    assert registry.serializers == (MockNumberToTarFileSerializer, MockNumberSerializer)
    assert registry.tar_file_serializers == (MockNumberToTarFileSerializer,)
    assert registry.detect_tar_file_serializers_from_file_suffix('num') == \
           (MockNumberToTarFileSerializer,)
