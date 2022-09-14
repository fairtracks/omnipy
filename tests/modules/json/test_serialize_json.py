from tests.data.helpers.functions import assert_tar_file_contents
from unifair.modules.json.models import JsonDataset
from unifair.modules.json.serializers import JsonDatasetToTarFileSerializer


def test_json_dataset_serializer_to_tar_file():
    json_data = JsonDataset()
    obj_type_1_json = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'
    obj_type_2_json = '[{"a": "abc", "b": 12}, {"c": "bcd"}]'
    json_data.from_json('{{"obj_type.1": {}, "obj_type.2": {}}}'.format(
        obj_type_1_json, obj_type_2_json))

    serializer = JsonDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(json_data)
    decode_func = lambda x: x.decode('utf8')  # noqa

    assert_tar_file_contents(tarfile_bytes, 'obj_type.1', 'json', decode_func, obj_type_1_json)
    assert_tar_file_contents(tarfile_bytes, 'obj_type.2', 'json', decode_func, obj_type_2_json)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == json_data
