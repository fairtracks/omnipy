"""Tar-file serializer for Omnipy JSON datasets."""

from typing import IO, Type

from omnipy.data.serializer import TarFileSerializer
from omnipy.shared.protocols.data import IsDataset

from .datasets import JsonBaseDataset, JsonDataset
from .models import JsonModel


class JsonDatasetToTarFileSerializer(TarFileSerializer[JsonBaseDataset]):
    """Serialize JSON datasets to and from gzipped tar archives."""

    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        """Return whether a dataset can be serialized as JSON files."""

        from ..isa.datasets import IsaJsonDataset
        return isinstance(dataset, JsonBaseDataset) or isinstance(dataset, IsaJsonDataset)

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        """Return the dataset class created during deserialization."""

        return JsonDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        """Return the file suffix used for serialized dataset members."""

        return 'json'

    @classmethod
    def serialize(cls, dataset: JsonBaseDataset) -> bytes | memoryview:
        """Serialize a JSON dataset into a gzipped tar archive."""

        def json_encode_func(json_data: JsonModel) -> bytes:
            return json_data.to_json().encode('utf8')

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=json_encode_func)

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> JsonDataset:
        """Deserialize a gzipped tar archive into a JSON dataset."""

        json_dataset = JsonDataset()

        def json_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def json_dictify_object(data_file: str, obj_val: str) -> dict[str, str]:
            return {f'{data_file}': f'{obj_val}'}

        cls.create_dataset_from_tarfile(
            json_dataset,
            serialized,
            data_decode_func=json_decode_func,
            dictify_object_func=json_dictify_object,
            import_method='from_json',
            any_file_suffix=any_file_suffix,
        )

        return json_dataset
