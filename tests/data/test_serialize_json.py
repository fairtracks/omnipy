import tarfile
from io import BytesIO

from unifair.data.json import JsonDataset, JsonDatasetToTarFileSerializer


def _assert_tar_file_contents(tarfile_bytes: bytes, obj_type_name: str, json_str: str):
    tf = tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz')
    json_file = tf.extractfile(f'{obj_type_name}.json')
    assert json_file is not None
    assert json_file.read().decode('utf8') == json_str


def test_json_dataset_to_tar_file_serializer_single_obj_type():
    json_data = JsonDataset()
    obj_type_json = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'
    json_data['obj_type'] = obj_type_json

    serializer = JsonDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(json_data)

    _assert_tar_file_contents(tarfile_bytes, 'obj_type', obj_type_json)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == json_data


def test_json_dataset_serializer_to_tar_file_multiple_obj_types():
    json_data = JsonDataset()
    obj_type_1_json = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'
    obj_type_2_json = '[{"a": "abc", "b": 12}, {"c": "bcd"}]'
    json_data['obj_type_1'] = obj_type_1_json
    json_data['obj_type_2'] = obj_type_2_json

    serializer = JsonDatasetToTarFileSerializer()
    tarfile_bytes = serializer.serialize(json_data)

    _assert_tar_file_contents(tarfile_bytes, 'obj_type_1', obj_type_1_json)
    _assert_tar_file_contents(tarfile_bytes, 'obj_type_2', obj_type_2_json)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == json_data
