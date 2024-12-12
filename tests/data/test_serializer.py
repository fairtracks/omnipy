from dataclasses import dataclass
from io import BytesIO
import os
from pathlib import Path
import sys
from typing import Annotated, cast, Generic, Type, TypeVar

import pytest
import pytest_cases as pc

from omnipy.api.protocols.public.data import IsDataset, IsModel, IsSerializer
from omnipy.data.dataset import Dataset, MultiModelDataset
from omnipy.data.model import Model
from omnipy.data.serializer import DatasetToTarFileSerializer, SerializerRegistry

from .helpers.functions import assert_directory_in_tar_file, assert_tar_file_contents
from .helpers.mocks import (MockNumberSerializer,
                            MockNumberToTarFileSerializer,
                            MockTextSerializer,
                            NumberDataset,
                            TextDataset)

RootT = TypeVar('RootT')


@dataclass
class DatasetSerializationCase(Generic[RootT]):
    dataset: IsDataset[IsModel[RootT]]
    serializer: IsSerializer[RootT]
    decoded_dataset_cls: type[IsDataset[IsModel[RootT]]]
    data_files_encoded: dict[str, bytes]
    dataset_encoded: bytes


def populate_number_dataset(dataset_cls: Type[IsDataset[IsModel[int]]]) -> IsDataset[IsModel[int]]:
    number_data = dataset_cls()

    number_data['data_file_æ'] = 35
    number_data['data_file_ø'] = 12

    return number_data


def populate_text_dataset(dataset_cls: Type[IsDataset[IsModel[str]]]) -> IsDataset[IsModel[str]]:
    str_data = dataset_cls()

    str_data['data_file_å'] = 'thirty-five æ'
    str_data['data_file_ß'] = 'twelve ø'

    return str_data


@pc.fixture
def number_data_files_encoded() -> Annotated[dict[str, bytes], pc.fixture]:
    return {'data_file_æ': b'#', 'data_file_ø': b'\x0c'}


@pc.fixture
def number_dataset_encoded() -> Annotated[bytes, pc.fixture]:
    return b"{'data_file_\xc3\xa6': '#', 'data_file_\xc3\xb8': '\\x0c'}"


@pc.case(id='MockNumberSerializer', tags=['dataset'])
@pc.parametrize('number_dataset_cls', [NumberDataset, Dataset[Model[int]]])
def case_mock_number_serializer(
    number_dataset_cls: Annotated[Type[IsDataset[IsModel[int]]], pc.case],
    number_data_files_encoded: Annotated[dict[str, bytes], pc.fixture],
    number_dataset_encoded: Annotated[bytes, pc.fixture],
) -> Annotated[DatasetSerializationCase[int], pc.case]:
    return DatasetSerializationCase(
        dataset=populate_number_dataset(number_dataset_cls),
        serializer=MockNumberSerializer(),
        decoded_dataset_cls=NumberDataset,
        data_files_encoded=number_data_files_encoded,
        dataset_encoded=number_dataset_encoded,
    )


@pc.fixture
def text_data_files_encoded() -> Annotated[dict[str, bytes], pc.fixture]:
    return {'data_file_å': b'thirty-five \xc3\xa6', 'data_file_ß': b'twelve \xc3\xb8'}


@pc.fixture
def text_dataset_encoded() -> Annotated[bytes, pc.fixture]:
    return (b"{'data_file_\xc3\xa5': 'thirty-five \xc3\xa6', "
            b"'data_file_\xc3\x9f': 'twelve \xc3\xb8'}")


@pc.case(id='MockTextSerializer', tags=['dataset'])
@pc.parametrize('text_dataset_cls', [TextDataset, Dataset[Model[str]]])
def case_mock_text_serializer(
    text_dataset_cls: Annotated[Type[IsDataset[IsModel[str]]], pc.case],
    text_data_files_encoded: Annotated[dict[str, bytes], pc.fixture],
    text_dataset_encoded: Annotated[bytes, pc.fixture],
) -> Annotated[DatasetSerializationCase[str], pc.case]:
    return DatasetSerializationCase(
        dataset=populate_text_dataset(text_dataset_cls),
        serializer=MockTextSerializer(),
        decoded_dataset_cls=TextDataset,
        data_files_encoded=text_data_files_encoded,
        dataset_encoded=text_dataset_encoded,
    )


# @pc.case(id='SerializerRegistry', tags=['dataset'])
# def case_multi_model_dataset(
#     text_data_files_encoded: Annotated[dict[str, bytes], pc.fixture],
#     text_dataset_encoded: Annotated[bytes, pc.fixture],
# ) -> Annotated[DatasetSerializationCase, pc.case]:
#     dataset = MultiModelDataset[Model[int | str]]()
#     dataset.set_model('number', Model[int])
#     dataset.set_model('text', Model[str])
#     return DatasetSerializationCase(
#         dataset=populate_text_dataset(text_dataset_cls),
#         serializer=MockTextSerializer,
#         decoded_dataset_cls=TextDataset,
#         data_files_encoded=text_data_files_encoded,
#         dataset_encoded=text_dataset_encoded,
#     )


@pc.parametrize_with_cases('case', has_tag='dataset', cases='.')
def test_mock_serializers(case: Annotated[DatasetSerializationCase, pc.case],) -> None:
    assert case.serializer.get_dataset_cls_for_new() is case.decoded_dataset_cls
    assert case.serializer.is_dataset_directly_supported(case.dataset)


@pc.parametrize_with_cases('case', has_tag='dataset', cases='.')
def test_dataset_serialization_to_bytes(case: Annotated[DatasetSerializationCase, pc.case]) -> None:
    serialized_bytes = case.serializer.serialize_to_bytes(case.dataset)
    assert cast(BytesIO, serialized_bytes).getvalue() == case.dataset_encoded

    deserialized_obj = case.serializer.deserialize_from_bytes(serialized_bytes)
    assert deserialized_obj.to_data() == case.dataset.to_data()
    assert type(deserialized_obj) is case.decoded_dataset_cls


@pc.parametrize_with_cases('case', has_tag='dataset', cases='.')
def test_dataset_serialization_to_directory(
    case: Annotated[DatasetSerializationCase[RootT], pc.case],
    tmp_path: Annotated[Path, pytest.fixture],
) -> None:
    dir_path = tmp_path / case.dataset.__class__.__name__
    type2prefix = dict(int='num', str='txt', dict='json')

    case.serializer.serialize_to_directory(case.dataset, dir_path)

    assert os.path.exists(dir_path) and len(os.listdir(dir_path)) == len(case.dataset) == 2
    for root, dirs, files in os.walk(dir_path):
        assert len(dirs) == 0

        key: str
        val: IsModel[RootT]
        for key, val in case.dataset.items():
            data_file_name = f'{key}.{type2prefix[type(val.contents).__name__]}'
            assert data_file_name in files
            with open(dir_path / data_file_name, 'br') as file:
                assert file.read() == case.data_files_encoded[key]

    deserialized_dataset = case.serializer.deserialize_from_directory(dir_path)
    assert deserialized_dataset.to_data() == case.dataset.to_data()
    assert type(deserialized_dataset) is case.decoded_dataset_cls


#
# def test_number_dataset_serialization_to_bytes():
#     number_data = NumberDataset()
#
#     number_data['data_file_å'] = 35
#     number_data['data_file_ø'] = 12
#
#     serializer = MockNumberSerializer()
#
#     assert serializer.get_dataset_cls_for_new() is NumberDataset
#     assert serializer.is_dataset_directly_supported(number_data)
#
#     serialized_bytes = serializer.serialize_to_bytes(number_data)
#     assert serialized_bytes.getvalue() == \
#            b"{'data_file_\xc3\xa5': '#', 'data_file_\xc3\xb8': '\\x0c'}"
#
#     deserialized_obj = serializer.deserialize_from_bytes(serialized_bytes)
#     assert deserialized_obj.to_data() == number_data.to_data()
#     assert type(deserialized_obj) is NumberDataset
#


def test_number_dataset_serialization_to_tar_file():
    number_data = NumberDataset()

    number_data['data_file_1'] = 35
    number_data['data_file_2'] = 12

    serializer = MockNumberToTarFileSerializer()

    assert serializer.get_dataset_cls_for_new() is NumberDataset
    assert serializer.is_dataset_directly_supported(number_data)

    tarfile_bytes = serializer.serialize(number_data)
    decode_func = lambda x: int.from_bytes(x, byteorder=sys.byteorder)  # noqa

    assert_tar_file_contents(tarfile_bytes, 'data_file_1', 'num', decode_func, 35)
    assert_tar_file_contents(tarfile_bytes, 'data_file_2', 'num', decode_func, 12)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == number_data


def test_multi_model_dataset_of_datasets_to_bytes():
    dataset_of_datasets = MultiModelDataset[Model[Dataset[Model[int | str]]]]()

    dataset_of_datasets['data_dir_1'] = dict(data_file_1=35, data_file_2=27)
    dataset_of_datasets['data_dir_2'] = dict(data_file_2=13, data_file_3=45)

    registry = SerializerRegistry()
    registry.register(DatasetToTarFileSerializer)
    registry.register(MockNumberToTarFileSerializer)

    serializer = DatasetToTarFileSerializer(registry)

    assert serializer.get_dataset_cls_for_new() is Dataset[Model[NumberDataset]]
    assert serializer.is_dataset_directly_supported(dataset_of_datasets)

    tarfile_bytes = serializer.serialize(dataset_of_datasets)
    decode_func = lambda x: int.from_bytes(x, byteorder=sys.byteorder)  # noqa

    assert_directory_in_tar_file(tarfile_bytes, 'data_dir_1')
    assert_directory_in_tar_file(tarfile_bytes, 'data_dir_2')

    assert_tar_file_contents(tarfile_bytes, 'data_dir_1/data_file_1', 'num', decode_func, 35)
    assert_tar_file_contents(tarfile_bytes, 'data_dir_1/data_file_2', 'num', decode_func, 27)
    assert_tar_file_contents(tarfile_bytes, 'data_dir_2/data_file_2', 'num', decode_func, 13)
    assert_tar_file_contents(tarfile_bytes, 'data_dir_2/data_file_3', 'num', decode_func, 45)

    deserialized_json_data = serializer.deserialize(tarfile_bytes)

    assert deserialized_json_data == dataset_of_datasets


def test_serializer_registry():
    registry = SerializerRegistry()

    registry.register(MockNumberToTarFileSerializer)
    registry.register(MockNumberSerializer)

    assert registry.serializers == (MockNumberToTarFileSerializer, MockNumberSerializer)
    assert registry.tar_file_serializers == (MockNumberToTarFileSerializer,)
    assert registry.detect_tar_file_serializers_from_file_suffix('num') == \
           (MockNumberToTarFileSerializer,)
