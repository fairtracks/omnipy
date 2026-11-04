"""Save/load round trips through the shared public archive methods."""

from pathlib import Path
import tarfile

import pytest
import pytest_cases as pc


@pc.parametrize_with_cases('value, member_names', cases='.cases.saving')
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
@pytest.mark.parametrize('with_suffix', [False, True])
@pytest.mark.parametrize('path_type', [str, Path])
def test_save_and_load_round_trip(
    tmp_path, value, member_names, select_serializer_by, with_suffix, path_type
):
    path = tmp_path / ('saved.tar.gz' if with_suffix else 'saved')
    before = value.to_data()
    value.save(path_type(path))

    archive_path = tmp_path / 'saved.tar.gz'
    with tarfile.open(archive_path) as archive:
        assert {Path(member.name).stem for member in archive.getmembers()} == member_names
    assert {path.stem for path in (tmp_path / 'saved').iterdir()} == member_names
    assert value.to_data() == before

    loaded = type(value).load(path_type(archive_path), select_serializer_by=select_serializer_by)
    assert type(loaded) is type(value)
    assert loaded.to_data() == before
