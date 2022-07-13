import sys
from typing import Dict, IO, Union

from tests.dataset.test_common import _assert_tar_file_contents
from unifair.dataset.dataset import Dataset
from unifair.dataset.model import Model
from unifair.dataset.serializer import (create_dataset_from_tarfile,
                                        create_tarfile_from_dataset,
                                        Serializer)


class NumberDataset(Dataset[Model[int]]):
    ...


class MockNumberSerializer(Serializer):
    @staticmethod
    def serialize(number_dataset: NumberDataset) -> Union[bytes, memoryview]:
        return ','.join(':'.join([k, str(v)]) for (k, v) in number_dataset.items()).encode('utf8')

    @staticmethod
    def deserialize(serialized_bytes: bytes) -> NumberDataset:
        number_dataset = NumberDataset()
        for key, val in [_.split(':') for _ in serialized_bytes.decode('utf8').split(',')]:
            number_dataset[key] = int(val)
        return number_dataset


class MockNumberToTarFileSerializer(Serializer):
    @staticmethod
    def serialize(number_dataset: NumberDataset) -> Union[bytes, memoryview]:
        def number_encode_func(number_data: int) -> bytes:
            return bytes([number_data])

        return create_tarfile_from_dataset(
            number_dataset, file_suffix='num', data_encode_func=number_encode_func)

    @staticmethod
    def deserialize(tarfile_bytes: bytes) -> NumberDataset:
        number_dataset = NumberDataset()

        def number_decode_func(file_stream: IO[bytes]) -> int:
            return int.from_bytes(file_stream.read(), byteorder=sys.byteorder)

        create_dataset_from_tarfile(
            number_dataset,
            tarfile_bytes,
            file_suffix='num',
            data_decode_func=number_decode_func,
        )

        return number_dataset


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

    _assert_tar_file_contents(tarfile_bytes, 'obj_type1', 'num', decode_func, 35)
    _assert_tar_file_contents(tarfile_bytes, 'obj_type2', 'num', decode_func, 12)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == number_data
