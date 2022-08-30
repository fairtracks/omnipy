from abc import ABC, abstractmethod
from io import BytesIO
import tarfile
from tarfile import TarInfo
from typing import Any, Callable, Dict, IO, Union

from unifair.data.dataset import Dataset


class Serializer(ABC):
    @staticmethod
    @abstractmethod
    def serialize(dataset: Dataset):
        pass

    @staticmethod
    @abstractmethod
    def deserialize(serialized) -> Dataset:
        pass


def create_tarfile_from_dataset(dataset: Dataset,
                                file_suffix: str,
                                data_encode_func: Callable[[Any], Union[bytes, memoryview]]):
    bytes_io = BytesIO()
    with tarfile.open(fileobj=bytes_io, mode='w:gz') as tarfile_stream:
        for obj_type, data_obj in dataset.items():
            json_data_bytestream = BytesIO(data_encode_func(data_obj))
            json_data_bytestream.seek(0)
            tarinfo = TarInfo(name=f'{obj_type}.{file_suffix}')
            tarinfo.size = len(json_data_bytestream.getbuffer())
            tarfile_stream.addfile(tarinfo, json_data_bytestream)
    return bytes_io.getbuffer().tobytes()


def create_dataset_from_tarfile(dataset: Dataset,
                                tarfile_bytes: bytes,
                                file_suffix: str,
                                data_decode_func: Callable[[IO[bytes]], Any],
                                dictify_object_func: Callable[[str, Any], Union[Dict, str]],
                                import_method='from_data'):
    with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
        for filename in tarfile_stream.getnames():
            obj_type_file = tarfile_stream.extractfile(filename)
            assert filename.endswith(f'.{file_suffix}')
            obj_type = '.'.join(filename.split('.')[:-1])
            getattr(dataset, import_method)(
                dictify_object_func(obj_type, data_decode_func(obj_type_file)))


class CsvSerializer:
    pass


class PythonSerializer:
    pass