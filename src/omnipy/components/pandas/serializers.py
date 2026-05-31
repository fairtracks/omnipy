"""Tar-file serializer for pandas-backed Omnipy datasets."""

from io import BytesIO
from typing import Any, IO, Type

from omnipy.data.serializer import TarFileSerializer
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lazy_import import pd

from .datasets import PandasDataset


class PandasDatasetToTarFileSerializer(TarFileSerializer[PandasDataset]):
    """Serialize pandas datasets to and from gzipped tar archives."""

    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        """Return whether a dataset is a pandas dataset."""

        return isinstance(dataset, PandasDataset)

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        """Return the dataset class created during deserialization."""

        return PandasDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        """Return the file suffix used for serialized dataset members."""

        return 'csv'

    @classmethod
    def serialize(cls, dataset: PandasDataset) -> bytes | memoryview:
        """Serialize a pandas dataset into a gzipped tar archive."""

        assert isinstance(dataset, PandasDataset)

        def pandas_encode_func(pandas_data: 'pd.DataFrame') -> memoryview:
            csv_bytes = BytesIO()
            pandas_data.to_csv(csv_bytes, encoding='utf8', mode='wb', index=False)
            return csv_bytes.getbuffer()

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=pandas_encode_func)

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> PandasDataset:
        """Deserialize a gzipped tar archive into a pandas dataset."""

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
