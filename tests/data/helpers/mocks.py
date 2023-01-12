import sys
from typing import Any, Dict, IO, Type, Union

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import Serializer, TarFileSerializer


class NumberDataset(Dataset[Model[int]]):
    ...


class MockNumberSerializer(Serializer):
    @property
    def supported_dataset_type(self) -> Type[Dataset]:
        return NumberDataset

    @classmethod
    def serialize(cls, number_dataset: NumberDataset) -> Union[bytes, memoryview]:
        return ','.join(':'.join([k, str(v)]) for (k, v) in number_dataset.items()).encode('utf8')

    @classmethod
    def deserialize(cls, serialized_bytes: bytes) -> NumberDataset:
        number_dataset = NumberDataset()
        for key, val in [_.split(':') for _ in serialized_bytes.decode('utf8').split(',')]:
            number_dataset[key] = int(val)
        return number_dataset


class MockNumberToTarFileSerializer(TarFileSerializer):
    @property
    def supported_dataset_type(self) -> Type[Dataset]:
        return NumberDataset

    @classmethod
    def serialize(cls, number_dataset: NumberDataset) -> Union[bytes, memoryview]:
        def number_encode_func(number_data: int) -> bytes:
            return bytes([number_data])

        return cls.create_tarfile_from_dataset(
            number_dataset, file_suffix='num', data_encode_func=number_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes) -> NumberDataset:
        number_dataset = NumberDataset()

        def number_decode_func(file_stream: IO[bytes]) -> int:
            return int.from_bytes(file_stream.read(), byteorder=sys.byteorder)

        def python_dictify_object(obj_type: str, obj_val: Any) -> Dict:
            return {obj_type: obj_val}

        cls.create_dataset_from_tarfile(
            number_dataset,
            tarfile_bytes,
            file_suffix='num',
            data_decode_func=number_decode_func,
            dictify_object_func=python_dictify_object,
        )

        return number_dataset
