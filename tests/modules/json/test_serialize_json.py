from omnipy.data.serializer import TarFileSerializer
from omnipy.modules.json.datasets import JsonDataset
from omnipy.modules.json.serializers import JsonDatasetToTarFileSerializer

from ...data.helpers.functions import assert_tar_file_contents


def test_json_dataset_serializer_to_tar_file():
    json_data = JsonDataset()
    obj_type_1_json = """
[
  {
    "a": "abc",
    "b": 12
  },
  {
    "a": "bcd",
    "b": 23
  }
]"""[1:]
    obj_type_2_json = """
[
  {
    "a": "abc",
    "b": 12
  },
  {
    "c": "bcd"
  }
]"""[1:]
    json_data.from_json({'obj_type.1': f'{obj_type_1_json}', 'obj_type.2': f'{obj_type_2_json}'})

    serializer = JsonDatasetToTarFileSerializer()
    assert serializer.get_dataset_cls_for_new() is JsonDataset
    assert isinstance(serializer, TarFileSerializer)

    tarfile_bytes = serializer.serialize(json_data)
    decode_func = lambda x: x.decode('utf8')  # noqa

    assert_tar_file_contents(tarfile_bytes, 'obj_type.1', 'json', decode_func, obj_type_1_json)
    assert_tar_file_contents(tarfile_bytes, 'obj_type.2', 'json', decode_func, obj_type_2_json)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == json_data
