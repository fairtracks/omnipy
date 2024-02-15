from typing import IO, Type

from omnipy.api.protocols.public.data import IsDataset
from omnipy.data.serializer import TarFileSerializer

from .datasets import JsonBaseDataset, JsonDataset
from .models import JsonModel


class JsonDatasetToTarFileSerializer(TarFileSerializer):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        from ..isa.datasets import IsaJsonDataset
        return isinstance(dataset, JsonBaseDataset) or isinstance(dataset, IsaJsonDataset)

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        return JsonDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'json'

    @classmethod
    def serialize(cls, json_dataset: JsonBaseDataset) -> bytes | memoryview:
        def json_encode_func(json_data: JsonModel) -> bytes:
            return json_data.json(indent=2).encode('utf8')

        return cls.create_tarfile_from_dataset(json_dataset, data_encode_func=json_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes, any_file_suffix=False) -> JsonDataset:
        json_dataset = JsonDataset()

        def json_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def json_dictify_object(data_file: str, obj_val: str) -> dict[str, str]:
            return {f'{data_file}': f'{obj_val}'}

        cls.create_dataset_from_tarfile(
            json_dataset,
            tarfile_bytes,
            data_decode_func=json_decode_func,
            dictify_object_func=json_dictify_object,
            import_method='from_json',
            any_file_suffix=any_file_suffix,
        )

        return json_dataset
