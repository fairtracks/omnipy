"""Save/load round trips through the shared public archive methods."""

import asyncio
from pathlib import Path
import tarfile

import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.shared.enums.data import SelectSerializerBy

from .cases.saving import SaveCase


@pc.parametrize_with_cases('case', cases='.cases.saving')
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_save_and_load_round_trip(
    tmp_path: Path,
    case: SaveCase,
    select_serializer_by: SelectSerializerBy.Literals,
) -> None:
    before = case.value.to_data()
    case.value.save(tmp_path / 'saved')

    archive_path = tmp_path / 'saved.tar.gz'
    with tarfile.open(archive_path) as archive:
        assert {Path(member.name).stem for member in archive.getmembers()} == case.member_names
    assert {path.stem for path in (tmp_path / 'saved').iterdir()} == case.member_names
    assert case.value.to_data() == before

    loaded = case.value.load(archive_path, select_serializer_by=select_serializer_by)
    assert not isinstance(loaded, asyncio.Task)
    assert type(loaded) is type(case.value)
    assert loaded.to_data() == before


@pytest.mark.parametrize('with_suffix', [False, True])
@pytest.mark.parametrize('path_type', [str, Path])
def test_save_path_with_or_without_archive_suffix(
    tmp_path: Path, with_suffix: bool, path_type: type[str] | type[Path]
) -> None:
    dataset = JsonDataset(first=[1, 2])
    dataset.save(path_type(tmp_path / ('saved.tar.gz' if with_suffix else 'saved')))

    assert {path.name for path in tmp_path.iterdir()} == {'saved', 'saved.tar.gz'}
    assert [path.name for path in (tmp_path / 'saved').iterdir()] == ['first.json']

    loaded = JsonDataset.load(path_type(tmp_path / 'saved.tar.gz'))
    # Local paths given as str are loaded synchronously, even if typed as possibly URLs
    assert not isinstance(loaded, asyncio.Task)
    assert loaded.to_data() == {'first': [1, 2]}
