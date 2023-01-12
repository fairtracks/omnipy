import pytest

from omnipy.data.serializer import SerializerRegistry
from omnipy.modules.json.serializers import JsonDatasetToTarFileSerializer
from omnipy.modules.pandas.serializers import PandasDatasetToTarFileSerializer
from omnipy.modules.raw.serializers import RawDatasetToTarFileSerializer

from .cases.raw.datasets import (csv_dataset,
                                 json_dataset,
                                 json_str_dataset,
                                 json_table_dataset,
                                 pandas_dataset,
                                 python_dataset,
                                 str_dataset)


@pytest.fixture
def registry():

    registry = SerializerRegistry()

    registry.register(PandasDatasetToTarFileSerializer)
    registry.register(RawDatasetToTarFileSerializer)
    registry.register(JsonDatasetToTarFileSerializer)

    return registry


def test_serializer_registry_auto_detect_pandas_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(pandas_dataset)
    assert serializer is PandasDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_table_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_table_dataset)
    assert serializer is PandasDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_dataset)
    assert serializer is JsonDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_json_str_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(json_str_dataset)
    assert serializer is JsonDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_csv_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(csv_dataset)
    assert serializer is RawDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_str_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(str_dataset)
    assert serializer is RawDatasetToTarFileSerializer


def test_serializer_registry_auto_detect_python_dataset(registry):
    dataset, serializer = registry.auto_detect_tar_file_serializer(python_dataset)
    assert serializer is None
