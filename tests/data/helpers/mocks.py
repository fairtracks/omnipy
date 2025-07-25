import sys
from typing import Any, IO, Type

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import Serializer, TarFileSerializer
from omnipy.shared.protocols.data import IsDataset


class MockDataset(DataClassBase):
    ...


class MockModel(DataClassBase):
    ...


class NumberDataset(Dataset[Model[int]]):
    ...


class MockNumberSerializer(Serializer):
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        return isinstance(dataset, NumberDataset)

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        return NumberDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'num'

    @classmethod
    def serialize(cls, number_dataset: NumberDataset) -> bytes | memoryview:
        return ','.join(
            ':'.join([k, str(v.content)]) for (k, v) in number_dataset.items()).encode('utf8')

    @classmethod
    def deserialize(cls, serialized_bytes: bytes, any_file_suffix=False) -> NumberDataset:
        number_dataset = NumberDataset()
        for key, val in [_.split(':') for _ in serialized_bytes.decode('utf8').split(',')]:
            number_dataset[key] = int(val)
        return number_dataset


class MockNumberToTarFileSerializer(TarFileSerializer):
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        return isinstance(dataset, NumberDataset)

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        return NumberDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'num'

    @classmethod
    def serialize(cls, number_dataset: NumberDataset) -> bytes | memoryview:
        def number_encode_func(number_data: int) -> bytes:
            return bytes([number_data])

        return cls.create_tarfile_from_dataset(number_dataset, data_encode_func=number_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes, any_file_suffix=False) -> NumberDataset:
        number_dataset = NumberDataset()

        def number_decode_func(file_stream: IO[bytes]) -> int:
            return int.from_bytes(file_stream.read(), byteorder=sys.byteorder)

        def python_dictify_object(data_file: str, obj_val: Any) -> dict:
            return {data_file: obj_val}

        cls.create_dataset_from_tarfile(
            number_dataset,
            tarfile_bytes,
            data_decode_func=number_decode_func,
            dictify_object_func=python_dictify_object,
            any_file_suffix=any_file_suffix,
        )

        return number_dataset
