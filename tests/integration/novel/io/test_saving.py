"""Save/load round trips through the shared public archive methods."""

import asyncio
from pathlib import Path
import tarfile

import pytest
import pytest_cases as pc

from omnipy.shared.enums.data import SelectSerializerBy

from .cases.saving import SaveCase


@pc.parametrize_with_cases('case', cases='.cases.saving')
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
@pytest.mark.parametrize('with_suffix', [False, True])
@pytest.mark.parametrize('path_type', [str, Path])
def test_save_and_load_round_trip(
    tmp_path: Path,
    case: SaveCase,
    select_serializer_by: SelectSerializerBy.Literals,
    with_suffix: bool,
    path_type: type[str] | type[Path],
) -> None:
    path = tmp_path / ('saved.tar.gz' if with_suffix else 'saved')
    before = case.value.to_data()
    case.value.save(path_type(path))

    archive_path = tmp_path / 'saved.tar.gz'
    with tarfile.open(archive_path) as archive:
        assert {Path(member.name).stem for member in archive.getmembers()} == case.member_names
    assert {path.stem for path in (tmp_path / 'saved').iterdir()} == case.member_names
    assert case.value.to_data() == before

    loaded = case.value.load(path_type(archive_path), select_serializer_by=select_serializer_by)
    # Local paths given as str are loaded synchronously, even if typed as possibly URLs
    assert not isinstance(loaded, asyncio.Task)
    assert type(loaded) is type(case.value)
    assert loaded.to_data() == before
