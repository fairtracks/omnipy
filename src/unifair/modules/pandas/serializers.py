from io import BytesIO
from typing import Any, Dict, IO, Union

from unifair.data.serializer import create_dataset_from_tarfile, create_tarfile_from_dataset

from . import pd
from .models import PandasDataset


class PandasDatasetToTarFileSerializer:
    @staticmethod
    def serialize(pandas_dataset: PandasDataset) -> Union[bytes, memoryview]:
        def pandas_encode_func(pandas_data: pd.DataFrame) -> memoryview:
            csv_bytes = BytesIO()
            pandas_data.to_csv(csv_bytes, encoding='utf8', mode='b', index=False)
            return csv_bytes.getbuffer()

        return create_tarfile_from_dataset(
            pandas_dataset, file_suffix='csv', data_encode_func=pandas_encode_func)

    @staticmethod
    def deserialize(tarfile_bytes: bytes) -> PandasDataset:
        pandas_dataset = PandasDataset()

        def csv_decode_func(file_stream: IO[bytes]) -> pd.DataFrame:
            return pd.read_csv(file_stream, encoding='utf8')

        def python_dictify_object(obj_type: str, obj_val: Any) -> Dict:
            return {obj_type: obj_val}

        create_dataset_from_tarfile(
            pandas_dataset,
            tarfile_bytes,
            file_suffix='csv',
            data_decode_func=csv_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data')  # noqa

        return pandas_dataset
