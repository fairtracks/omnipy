"""Public loading of local files and archives."""

from io import BytesIO
import tarfile

import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.data.dataset import is_dataset_instance


@pc.parametrize_with_cases('source, expected_model, expected_dataset', cases='.cases.files')
@pytest.mark.parametrize('target_cls', [JsonDataset])
@pytest.mark.parametrize('entry_point', ['load', 'load_into'])
@pytest.mark.parametrize('by_file_suffix', [False, True])
def test_file_inputs(
    source, expected_model, expected_dataset, target_cls, entry_point, by_file_suffix
) -> None:
    if entry_point == 'load':
        result = target_cls.load(source, by_file_suffix=by_file_suffix)
    else:
        result = target_cls()
        assert result.load_into(source, by_file_suffix=by_file_suffix) is result
    expected = expected_dataset if is_dataset_instance(result) else expected_model
    assert result.to_data() == expected


@pytest.mark.parametrize('target_cls', [JsonDataset])
def test_load_archive_ignores_directory_members(tmp_path, target_cls) -> None:
    path = tmp_path / 'directory.tar.gz'
    with tarfile.open(path, 'w:gz') as archive:
        directory = tarfile.TarInfo('folder')
        directory.type = tarfile.DIRTYPE
        archive.addfile(directory)
        member = tarfile.TarInfo('first.json')
        content = b'[1, 2]'
        member.size = len(content)
        archive.addfile(member, BytesIO(content))

    result = target_cls.load(path, by_file_suffix=True, ignore_dirs=True)
    assert result.to_data() == ({'first': [1, 2]} if is_dataset_instance(result) else [1, 2])


@pytest.mark.parametrize('target_cls', [JsonDataset])
@pytest.mark.parametrize('as_keywords', [False, True])
def test_keyed_local_paths_remain_unsupported(tmp_path, target_cls, as_keywords) -> None:
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')

    with pytest.raises(NotImplementedError, match='Loading files with specified keys'):
        if as_keywords:
            target_cls.load(first=path)
        else:
            target_cls.load({'first': path})
