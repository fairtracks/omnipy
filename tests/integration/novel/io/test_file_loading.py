"""Public Model and Dataset loading of local files and archives."""

from io import BytesIO
import tarfile

import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.data.dataset import is_dataset_instance
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError


@pc.parametrize_with_cases('source, expected_model, expected_dataset', cases='.cases.files')
@pytest.mark.parametrize('target_cls', [Model[object], JsonDataset])
@pytest.mark.parametrize('entry_point', ['load', 'load_into'])
@pytest.mark.parametrize('by_file_suffix', [False, True])
def test_model_and_dataset_file_inputs(
    source, expected_model, expected_dataset, target_cls, entry_point, by_file_suffix
) -> None:
    if entry_point == 'load':
        result = target_cls.load(source, by_file_suffix=by_file_suffix)
    else:
        result = target_cls()
        assert result.load_into(source, by_file_suffix=by_file_suffix) is result
    expected = expected_dataset if is_dataset_instance(result) else expected_model
    assert result.to_data() == expected


@pytest.mark.parametrize('target_cls', [Model[object], JsonDataset])
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


def test_failed_file_validation_preserves_model_contents(tmp_path) -> None:
    path = tmp_path / 'invalid.json'
    path.write_text('["not an integer"]')
    model = Model[list[int]]([7])

    with pytest.raises(ValidationError):
        model.load_into(path)
    assert model.content == [7]


@pytest.mark.parametrize('by_file_suffix', [False, True])
def test_dataset_file_loading_retains_existing_entries(tmp_path, by_file_suffix) -> None:
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')
    dataset = JsonDataset(existing=7)

    assert dataset.load_into(path, by_file_suffix=by_file_suffix) is dataset
    assert dataset.to_data() == {'existing': 7, 'first': [1, 2]}


@pytest.mark.parametrize('target_cls', [Model[object], JsonDataset])
@pytest.mark.parametrize('as_keywords', [False, True])
def test_keyed_local_paths_remain_unsupported(tmp_path, target_cls, as_keywords) -> None:
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')

    with pytest.raises(NotImplementedError, match='Loading files with specified keys'):
        if as_keywords:
            target_cls.load(first=path)
        else:
            target_cls.load({'first': path})
