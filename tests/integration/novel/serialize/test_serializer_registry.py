"""Tests for serializer registry."""

from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

import pytest

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.json.serializers import JsonDatasetToTarFileSerializer
from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.pandas.serializers import PandasDatasetToTarFileSerializer
from omnipy.components.raw.datasets import StrDataset
from omnipy.components.raw.serializers import (
    RawBytesDatasetToTarFileSerializer,
    RawStrDatasetToTarFileSerializer,
)
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import SerializerRegistry
from omnipy.shared.protocols.data import IsSerializerRegistry
from omnipy.shared.protocols.hub.runtime import IsRuntime

from .helpers.functions import write_tar_gz

_SILENT_LOG = SimpleNamespace(log_message=lambda _msg: None)


@pytest.fixture
def registry(runtime: Annotated[IsRuntime, pytest.fixture]) -> IsSerializerRegistry:
    """Provide registry."""
    registry = SerializerRegistry()

    registry.register(RawStrDatasetToTarFileSerializer)
    registry.register(JsonDatasetToTarFileSerializer)
    registry.register(PandasDatasetToTarFileSerializer)

    return registry


def test_serializer_registry_auto_detect_pandas_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    pandas_dataset: Annotated[PandasDataset, pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(pandas_dataset)
    assert serializer is PandasDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_table_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    json_table_dataset: Annotated[JsonDataset, pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_table_dataset)
    assert serializer is JsonDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    json_dataset: Annotated[JsonDataset, pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_dataset)
    assert serializer is JsonDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_table_as_str_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    json_table_as_str_dataset: Annotated[Dataset[Model[str]], pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_table_as_str_dataset)
    assert serializer is RawStrDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_str_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    json_str_dataset: Annotated[Dataset[Model[str]], pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_str_dataset)
    assert serializer is RawStrDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_csv_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    csv_dataset: Annotated[StrDataset, pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(csv_dataset)
    assert serializer is RawStrDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_str_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    str_dataset: Annotated[StrDataset, pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(str_dataset)
    assert serializer is RawStrDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_python_dataset(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    python_dataset: Annotated[Dataset[Model[object]], pytest.fixture],
):
    dataset, serializer = registry.auto_detect_tar_file_serializer(python_dataset)
    assert serializer is None


def test_serializer_registry_load_by_file_suffix_ignores_directory_members(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    tmp_path: Path,
) -> None:
    tar_path = write_tar_gz(tmp_path / 'data.tar.gz', {'folder': None, 'first.json': b'[1, 2]'})

    loaded = registry.load_from_tar_file_path_based_on_file_suffix(
        _SILENT_LOG, str(tar_path), JsonDataset(), ignore_dirs=True
    )
    assert loaded is not None
    assert loaded.to_data() == {'first': [1, 2]}


def test_serializer_registry_load_by_file_suffix_empty_archive(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    tmp_path: Path,
) -> None:
    tar_path = write_tar_gz(tmp_path / 'empty.tar.gz', {})
    to_dataset = JsonDataset()

    loaded = registry.load_from_tar_file_path_based_on_file_suffix(
        _SILENT_LOG, str(tar_path), to_dataset
    )
    assert loaded is to_dataset
    assert loaded.to_data() == {}


@pytest.mark.usefixtures('runtime')
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_dataset_load_into_keeps_existing_entries(
    tmp_path: Path, select_serializer_by: str
) -> None:
    tar_path = write_tar_gz(tmp_path / 'data.tar.gz', {'first.json': b'[1, 2]'})
    dataset = JsonDataset(existing=7)

    dataset.load_into(str(tar_path), select_serializer_by=select_serializer_by)
    assert dataset.to_data() == {'existing': 7, 'first': [1, 2]}


@pytest.mark.usefixtures('runtime')
@pytest.mark.parametrize(
    'value, expected_serializer',
    [
        ('123', RawStrDatasetToTarFileSerializer),
        ('"quoted"', RawStrDatasetToTarFileSerializer),
        (b'123', RawBytesDatasetToTarFileSerializer),
        ([1, 2], JsonDatasetToTarFileSerializer),
    ],
)
def test_serializer_registry_auto_detect_keeps_untyped_values(
    value: object, expected_serializer: type
) -> None:
    registry = SerializerRegistry()
    for serializer_cls in (
        RawStrDatasetToTarFileSerializer,
        RawBytesDatasetToTarFileSerializer,
        JsonDatasetToTarFileSerializer,
        PandasDatasetToTarFileSerializer,
    ):
        registry.register(serializer_cls)

    dataset, serializer = registry.auto_detect_tar_file_serializer(Dataset[Model[object]](a=value))
    assert serializer is expected_serializer
    assert dataset is not None
    assert dataset.to_data() == {'a': value}


def test_serializer_registry_load_by_file_suffix_keeps_text(
    registry: Annotated[IsSerializerRegistry, pytest.fixture],
    tmp_path: Path,
) -> None:
    tar_path = write_tar_gz(tmp_path / 'text.tar.gz', {'a.txt': b'"quoted"'})

    loaded = registry.load_from_tar_file_path_based_on_file_suffix(
        _SILENT_LOG, str(tar_path), Dataset[Model[object]]()
    )
    assert loaded is not None
    assert loaded.to_data() == {'a': '"quoted"'}
