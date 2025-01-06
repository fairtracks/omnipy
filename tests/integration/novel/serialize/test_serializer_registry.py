from typing import Annotated

import pytest

from omnipy import Dataset, JsonDataset, Model, PandasDataset, StrDataset
from omnipy.components.json.serializers import JsonDatasetToTarFileSerializer
from omnipy.components.pandas.serializers import PandasDatasetToTarFileSerializer
from omnipy.components.raw.serializers import RawStrDatasetToTarFileSerializer
from omnipy.data.serializer import SerializerRegistry
from omnipy.shared.protocols.public.data import IsSerializerRegistry
from omnipy.shared.protocols.public.hub import IsRuntime


@pytest.fixture
def registry(runtime: Annotated[IsRuntime, pytest.fixture]) -> IsSerializerRegistry:

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
