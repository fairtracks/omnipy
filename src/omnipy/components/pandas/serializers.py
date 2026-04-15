from io import BytesIO
from typing import Any, IO, Type

from omnipy.data.serializer import TarFileSerializer
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lazy_import import pd

from .datasets import PandasDataset


class PandasDatasetToTarFileSerializer(TarFileSerializer[PandasDataset]):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        return isinstance(dataset, PandasDataset)

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        return PandasDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'csv'

    @classmethod
    def serialize(cls, dataset: PandasDataset) -> bytes | memoryview:
        assert isinstance(dataset, PandasDataset)

        def pandas_encode_func(pandas_data: 'pd.DataFrame') -> memoryview:
            csv_bytes = BytesIO()
            pandas_data.to_csv(csv_bytes, encoding='utf8', mode='wb', index=False)
            return csv_bytes.getbuffer()

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=pandas_encode_func)

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> PandasDataset:
        pandas_dataset = PandasDataset()

        def csv_decode_func(file_stream: IO[bytes]) -> 'pd.DataFrame':
            from .lazy_import import pd
            return pd.read_csv(file_stream, encoding='utf8')

        def python_dictify_object(data_file: str, obj_val: Any) -> dict:
            return {data_file: obj_val}

        cls.create_dataset_from_tarfile(
            pandas_dataset,
            serialized,
            data_decode_func=csv_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data',
            any_file_suffix=any_file_suffix,
        )  # noqa

        return pandas_dataset
