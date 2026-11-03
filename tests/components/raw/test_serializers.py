"""Tests for raw tar-file serializers."""

import pytest

from omnipy.components.raw.datasets import (
    BytesDataset,
    StrDataset,
    StrictBytesDataset,
    StrictStrDataset,
)
from omnipy.components.raw.serializers import (
    RawBytesDatasetToTarFileSerializer,
    RawStrDatasetToTarFileSerializer,
)
from omnipy.data.dataset import Dataset


@pytest.mark.parametrize('dataset_cls', [StrDataset, StrictStrDataset])
def test_raw_str_serializer_supports_str_datasets(dataset_cls: type[Dataset]) -> None:
    """Support datasets of plain and strict strings directly."""
    assert RawStrDatasetToTarFileSerializer.is_dataset_directly_supported(dataset_cls())
    assert not RawBytesDatasetToTarFileSerializer.is_dataset_directly_supported(dataset_cls())


@pytest.mark.parametrize('dataset_cls', [BytesDataset, StrictBytesDataset])
def test_raw_bytes_serializer_supports_bytes_datasets(dataset_cls: type[Dataset]) -> None:
    """Support datasets of plain and strict bytes directly."""
    assert RawBytesDatasetToTarFileSerializer.is_dataset_directly_supported(dataset_cls())
    assert not RawStrDatasetToTarFileSerializer.is_dataset_directly_supported(dataset_cls())
