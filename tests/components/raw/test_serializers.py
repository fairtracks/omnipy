"""Tests for raw tar-file serializers."""

from io import BytesIO
import tarfile

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
import omnipy.data.serializer as serializer_module


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


def test_raw_bytes_serializer_encodes_models_as_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    class StrictBytesIO(BytesIO):
        def __init__(self, initial_bytes: bytes = b'') -> None:
            assert isinstance(initial_bytes, bytes)
            super().__init__(initial_bytes)

    monkeypatch.setattr(serializer_module, 'BytesIO', StrictBytesIO)
    dataset = StrictBytesDataset(first=b'\x00\xff\x01', second=b'123', empty=b'')

    serialized = RawBytesDatasetToTarFileSerializer.serialize(dataset)

    with tarfile.open(fileobj=BytesIO(serialized), mode='r:gz') as archive:
        for name, expected in dataset.to_data().items():
            member = archive.extractfile(f'{name}.bytes')
            assert member is not None
            assert member.read() == expected

    assert RawBytesDatasetToTarFileSerializer.deserialize(bytes(serialized)).to_data() == (
        dataset.to_data()
    )
