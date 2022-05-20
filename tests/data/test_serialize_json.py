from tests.data.test_common import _assert_tar_file_contents
from unifair.data.json import JsonDataset
from unifair.data.json import JsonDatasetToTarFileSerializer


def test_json_dataset_to_tar_file_serializer_single_obj_type():
    json_data = JsonDataset()
    obj_type_json = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'
    json_data['obj_type'] = obj_type_json

    serializer = JsonDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(json_data)

    _assert_tar_file_contents(tarfile_bytes, 'obj_type', 'json', obj_type_json)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == json_data


def test_json_dataset_serializer_to_tar_file_multiple_obj_types():
    json_data = JsonDataset()
    obj_type_1_json = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'
    obj_type_2_json = '[{"a": "abc", "b": 12}, {"c": "bcd"}]'
    json_data['obj_type.1'] = obj_type_1_json
    json_data['obj_type.2'] = obj_type_2_json

    serializer = JsonDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(json_data)

    _assert_tar_file_contents(tarfile_bytes, 'obj_type.1', 'json', obj_type_1_json)
    _assert_tar_file_contents(tarfile_bytes, 'obj_type.2', 'json', obj_type_2_json)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == json_data
