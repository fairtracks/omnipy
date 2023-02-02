from abc import ABC, abstractmethod
from io import BytesIO
import tarfile
from tarfile import TarInfo
from typing import Any, Callable, Dict, IO, Tuple, Type, Union

from pydantic import ValidationError

from omnipy.data.dataset import Dataset


class Serializer(ABC):
    @classmethod
    @abstractmethod
    def is_dataset_directly_supported(cls, dataset: Dataset) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_dataset_cls_for_new(cls) -> Type[Dataset]:
        pass

    @classmethod
    @abstractmethod
    def get_output_file_suffix(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def serialize(cls, dataset: Dataset) -> Union[bytes, memoryview]:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, serialized: bytes) -> Dataset:
        pass


class TarFileSerializer(Serializer, ABC):
    @classmethod
    def create_tarfile_from_dataset(cls,
                                    dataset: Dataset,
                                    data_encode_func: Callable[[Any], Union[bytes, memoryview]]):
        bytes_io = BytesIO()
        with tarfile.open(fileobj=bytes_io, mode='w:gz') as tarfile_stream:
            for obj_type, data_obj in dataset.items():
                json_data_bytestream = BytesIO(data_encode_func(data_obj))
                json_data_bytestream.seek(0)
                tarinfo = TarInfo(name=f'{obj_type}.{cls.get_output_file_suffix()}')
                tarinfo.size = len(json_data_bytestream.getbuffer())
                tarfile_stream.addfile(tarinfo, json_data_bytestream)
        return bytes_io.getbuffer().tobytes()

    @classmethod
    def create_dataset_from_tarfile(cls,
                                    dataset: Dataset,
                                    tarfile_bytes: bytes,
                                    data_decode_func: Callable[[IO[bytes]], Any],
                                    dictify_object_func: Callable[[str, Any], Union[Dict, str]],
                                    import_method='from_data'):
        with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
            for filename in tarfile_stream.getnames():
                obj_type_file = tarfile_stream.extractfile(filename)
                assert filename.endswith(f'.{cls.get_output_file_suffix()}')
                obj_type = '.'.join(filename.split('.')[:-1])
                getattr(dataset, import_method)(
                    dictify_object_func(obj_type, data_decode_func(obj_type_file)))


class SerializerRegistry:
    def __init__(self) -> None:
        self._serializer_classes: list[Type[Serializer]] = []

    def register(self, serializer_cls: Type[Serializer]) -> None:
        self._serializer_classes.append(serializer_cls)

    @property
    def serializers(self) -> Tuple[Type[Serializer], ...]:
        return tuple(self._serializer_classes)

    @property
    def tar_file_serializers(self) -> Tuple[Type[TarFileSerializer], ...]:
        return tuple(cls for cls in self._serializer_classes if issubclass(cls, TarFileSerializer))

    def auto_detect(self, dataset: Dataset):
        return self._autodetect_serializer(dataset, self.serializers)

    def auto_detect_tar_file_serializer(self, dataset: Dataset):
        return self._autodetect_serializer(dataset, self.tar_file_serializers)

    @classmethod
    def _autodetect_serializer(cls, dataset, serializers):
        # def _direct(dataset: Dataset, serializer: Serializer):
        #     new_dataset_cls = serializer.get_dataset_cls_for_new()
        #     new_dataset = new_dataset_cls(dataset)
        #     return new_dataset

        def _to_data_from_json(dataset: Dataset, serializer: Serializer):
            new_dataset_cls = serializer.get_dataset_cls_for_new()
            new_dataset = new_dataset_cls()
            new_dataset.from_json(dataset.to_data())
            return new_dataset

        def _to_data_from_data(dataset: Dataset, serializer: Serializer):
            new_dataset_cls = serializer.get_dataset_cls_for_new()
            new_dataset = new_dataset_cls()
            new_dataset.from_data(dataset.to_data())
            return new_dataset

        def _to_data_from_data_if_direct(dataset, serializer: Serializer):
            assert serializer.is_dataset_directly_supported(dataset)
            return _to_data_from_data(dataset, serializer)

        # def _to_json_from_json(dataset: Dataset, serializer: Serializer):
        #     new_dataset_cls = serializer.get_dataset_cls_for_new()
        #     new_dataset = new_dataset_cls()
        #     new_dataset.from_json(dataset.to_json())
        #     return new_dataset

        for func in (_to_data_from_data_if_direct, _to_data_from_json, _to_data_from_data):
            for serializer in serializers:
                try:
                    new_dataset = func(dataset, serializer)
                    return new_dataset, serializer
                except (TypeError, ValueError, ValidationError, AssertionError) as e:
                    pass

        return None, None

    def detect_tar_file_serializers_from_file_suffix(self, file_suffix: str):
        return tuple(serializer_cls for serializer_cls in self.tar_file_serializers
                     if serializer_cls.get_output_file_suffix() == file_suffix)
