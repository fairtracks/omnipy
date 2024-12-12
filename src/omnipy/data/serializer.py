from abc import ABC, abstractmethod
import ast
from io import BytesIO
import os
from pathlib import Path
import tarfile
from tarfile import TarInfo
from typing import Any, BinaryIO, Callable, cast, Generic, IO, ParamSpec, Type

from typing_extensions import TypeVar

from omnipy.api.protocols.private.log import CanLog
from omnipy.api.protocols.public.data import (IsDataEncoder,
                                              IsDataset,
                                              IsModel,
                                              IsSerializer,
                                              IsTarFileSerializer,
                                              RootT,
                                              SupportsGeneralSerializerQueries)
from omnipy.data.helpers import HasData
from omnipy.util.contexts import hold_and_reset_prev_attrib_value
from omnipy.util.helpers import ensure_path_obj
from omnipy.util.pydantic import ValidationError

LogP = ParamSpec('LogP')
DatasetT = TypeVar('DatasetT', bound=IsDataset)


class Serializer(ABC):
    """"""
    @classmethod
    @abstractmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        ...

    @classmethod
    @abstractmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        ...

    @classmethod
    @abstractmethod
    def get_output_file_suffix(cls) -> str:
        ...

    # @classmethod
    # @abstractmethod
    # def serialize(cls, dataset: IsDataset) -> bytes | memoryview:
    #     ...
    #
    # @classmethod
    # @abstractmethod
    # def deserialize(cls, serialized: bytes, any_file_suffix=False) -> IsDataset:
    #     ...


class BytesSerializerMixin(IsDataEncoder[RootT], SupportsGeneralSerializerQueries, Generic[RootT]):
    @classmethod
    def serialize_to_bytes(cls, dataset: IsDataset[IsModel[RootT]]) -> BinaryIO:
        dataset_as_dict = {
            key: cls.encode_data(key, val.contents).decode('utf8') for (key, val) in dataset.items()
        }
        return BytesIO(repr(dataset_as_dict).encode('utf8'))

    @classmethod
    def deserialize_from_bytes(cls, data: BinaryIO) -> IsDataset[IsModel[RootT]]:
        dataset_cls = cls.get_dataset_cls_for_new()
        dataset = dataset_cls()

        dataset_as_dict_repr = data.read().decode('utf8')
        dataset_as_dict: dict[str, str] = ast.literal_eval(dataset_as_dict_repr)
        for key, val in dataset_as_dict.items():
            dataset[key] = cls.decode_data(key, val.encode('utf8'))

        return dataset


class DirectorySerializerMixin(IsDataEncoder[RootT],
                               SupportsGeneralSerializerQueries,
                               Generic[RootT]):
    @classmethod
    def serialize_to_directory(cls, dataset: IsDataset[IsModel[RootT]],
                               dir_path: Path | str) -> None:
        dir_path = ensure_path_obj(dir_path)
        os.makedirs(dir_path)

        for key, val in dataset.items():
            with open(dir_path / f'{key}.{cls.get_output_file_suffix()}', 'bw') as file:
                file.write(cls.encode_data(key, val.contents))

    @classmethod
    def deserialize_from_directory(cls, dir_path: Path | str) -> IsDataset[IsModel[RootT]]:
        dir_path = ensure_path_obj(dir_path)

        dataset_cls = cls.get_dataset_cls_for_new()
        dataset = dataset_cls()

        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                basename, suffix = os.path.splitext(filename)
                assert suffix == f'{os.path.extsep}{cls.get_output_file_suffix()}'
                with open(dir_path / filename, 'br') as file:
                    dataset[basename] = cls.decode_data(basename, file.read())

        return dataset


class TarFileSerializer(Serializer):
    """"""
    @classmethod
    def create_tarfile_from_dataset(cls,
                                    dataset: IsDataset,
                                    data_encode_func: Callable[..., bytes | memoryview]) -> bytes:
        bytes_io = BytesIO()
        with tarfile.open(fileobj=bytes_io, mode='w:gz') as tarfile_stream:
            for data_file, data in dataset.items():  # type: ignore[attr-defined]
                json_data_bytestream = BytesIO(data_encode_func(data.contents))
                json_data_bytestream.seek(0)
                tarinfo = TarInfo(name=f'{data_file}.{cls.get_output_file_suffix()}')
                tarinfo.size = len(json_data_bytestream.getbuffer())
                tarfile_stream.addfile(tarinfo, json_data_bytestream)
        return bytes_io.getbuffer().tobytes()

    @classmethod
    def create_dataset_from_tarfile(cls,
                                    dataset: IsDataset,
                                    tarfile_bytes: bytes,
                                    data_decode_func: Callable[[IO[bytes]], Any],
                                    dictify_object_func: Callable[[str, Any], dict | str],
                                    import_method: str = 'from_data',
                                    any_file_suffix: bool = False) -> None:
        with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tarfile_stream:
            for filename in tarfile_stream.getnames():
                data_file = tarfile_stream.extractfile(filename)
                assert data_file is not None
                if not any_file_suffix:
                    assert filename.endswith(f'.{cls.get_output_file_suffix()}')
                data_file_name = os.path.basename('.'.join(filename.split('.')[:-1]))
                getattr(dataset, import_method)({data_file_name: data_decode_func(data_file)})


class DatasetToTarFileSerializer(TarFileSerializer):
    def __init__(self, registry: 'SerializerRegistry'):
        self._registry = registry

    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        ...

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        ...

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'num'

    @classmethod
    def serialize(cls, number_dataset: IsDataset) -> bytes | memoryview:
        ...

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes, any_file_suffix=False) -> IsDataset:
        ...


class SerializerRegistry:
    def __init__(self) -> None:
        self._serializer_classes: list[Type[IsSerializer]] = []

    def register(self, serializer_cls: Type[IsSerializer]) -> None:
        self._serializer_classes.append(serializer_cls)

    @property
    def serializers(self) -> tuple[Type[IsSerializer], ...]:
        return tuple(self._serializer_classes)

    @property
    def tar_file_serializers(self) -> tuple[Type[IsTarFileSerializer], ...]:
        return tuple(cls for cls in self._serializer_classes if issubclass(cls, TarFileSerializer))

    def auto_detect(self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        return self._autodetect_serializer(dataset, self.serializers)

    def auto_detect_tar_file_serializer(
            self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        return self._autodetect_serializer(dataset, self.tar_file_serializers)

    @classmethod
    def _autodetect_serializer(
        cls,
        dataset: IsDataset,
        serializers: tuple[Type[IsSerializer], ...],
    ) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:

        from omnipy.hub.runtime import runtime
        if runtime:
            with hold_and_reset_prev_attrib_value(
                    runtime.config.data,
                    'interactive_mode',
            ):
                with hold_and_reset_prev_attrib_value(
                        runtime.config.data,
                        'dynamically_convert_elements_to_models',
                ):
                    runtime.config.data.interactive_mode = False
                    runtime.config.data.dynamically_convert_elements_to_models = False

                    return cls._test_all_serializer_combos(dataset, serializers)
        else:
            return cls._test_all_serializer_combos(dataset, serializers)

    @classmethod
    def _test_all_serializer_combos(
        self,
        dataset: IsDataset,
        serializers: tuple[Type[IsSerializer], ...],
    ) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:

        # def _direct(dataset: Dataset, serializer: Serializer):
        #     new_dataset_cls = serializer.get_dataset_cls_for_new()
        #     new_dataset = new_dataset_cls(dataset)
        #     return new_dataset

        def _to_data_from_json(dataset: IsDataset, serializer: IsSerializer):
            new_dataset_cls = serializer.get_dataset_cls_for_new()
            new_dataset = new_dataset_cls()
            new_dataset.from_json(dataset.to_data())
            return new_dataset

        def _to_data_from_data(dataset: IsDataset, serializer: IsSerializer):
            new_dataset_cls = serializer.get_dataset_cls_for_new()
            new_dataset = new_dataset_cls()
            new_dataset.from_data(dataset.to_data())
            return new_dataset

        def _to_data_from_data_if_direct(dataset: IsDataset, serializer: IsSerializer):
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
                except (TypeError, ValueError, ValidationError, AssertionError):
                    ...

        return None, None

    def detect_tar_file_serializers_from_dataset_cls(
            self, dataset: IsDataset) -> tuple[Type[IsTarFileSerializer], ...]:
        serializers = tuple(
            serializer_cls for serializer_cls in self.tar_file_serializers
            if serializer_cls.is_dataset_directly_supported(dataset))
        if len(serializers) == 0:
            serializers = tuple(serializer_cls for serializer_cls in self.tar_file_serializers
                                if serializer_cls.get_output_file_suffix() == 'bytes')
        return serializers

    def detect_tar_file_serializers_from_file_suffix(
            self, file_suffix: str) -> tuple[Type[IsTarFileSerializer], ...]:
        return tuple(serializer_cls for serializer_cls in self.tar_file_serializers
                     if serializer_cls.get_output_file_suffix() == file_suffix)

    def load_from_tar_file_path_based_on_file_suffix(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        log: Callable
        if hasattr(log_obj, 'log'):
            log = log_obj.log
        else:
            log = print

        with tarfile.open(tar_file_path, 'r:gz') as tarfile_obj:
            file_suffixes = set(fn.split('.')[-1] for fn in tarfile_obj.getnames())
        if len(file_suffixes) != 1:
            log(f'Tar archive contains files with different or '
                f'no file suffixes: {file_suffixes}. Serializer '
                f'cannot be uniquely determined. Aborting '
                f'restore.')
        else:
            file_suffix = file_suffixes.pop()
            serializers = self.detect_tar_file_serializers_from_file_suffix(file_suffix)
            if len(serializers) == 0:
                log(f'No serializer for file suffix "{file_suffix}" can be'
                    f'determined. Aborting restore.')
            else:
                log(f'Reading dataset from a gzipped tarpack at'
                    f' "{os.path.abspath(tar_file_path)}"')

                serializer = serializers[0]
                with open(tar_file_path, 'rb') as tarfile_binary:
                    auto_dataset = serializer.deserialize(tarfile_binary.read())

                if to_dataset.get_model_class() is auto_dataset.get_model_class():
                    cast(HasData, to_dataset).data = cast(HasData, auto_dataset).data
                    return to_dataset
                else:
                    try:
                        if to_dataset.get_model_class().inner_type == str:
                            to_dataset.from_data(auto_dataset.to_json())
                        else:
                            to_dataset.from_json(auto_dataset.to_data())
                        return to_dataset
                    except Exception:
                        return auto_dataset

    def load_from_tar_file_path_based_on_dataset_cls(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        log: Callable
        if hasattr(log_obj, 'log'):
            log = log_obj.log
        else:
            log = print

        serializers = self.detect_tar_file_serializers_from_dataset_cls(to_dataset)
        if len(serializers) == 0:
            log(f'No serializer for Dataset with type "{type(to_dataset)}" can be '
                f'determined.')
        else:
            for serializer in serializers:
                log(f'Reading dataset from a gzipped tarpack at'
                    f' "{os.path.abspath(tar_file_path)}" with serializer type: '
                    f'"{serializer.__name__}"')

                with open(tar_file_path, 'rb') as tarfile_binary:
                    out_dataset = serializer.deserialize(tarfile_binary.read())

                return out_dataset
