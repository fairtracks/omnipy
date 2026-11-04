"""Public loading of local files and archives."""

from io import BytesIO
import tarfile

import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.data.dataset import Dataset, is_dataset_instance
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError

from ..serialize.helpers.functions import write_tar_gz


@pc.parametrize_with_cases('source, expected_model, expected_dataset', cases='.cases.files')
@pytest.mark.parametrize('target_cls', [JsonDataset])
@pytest.mark.parametrize('entry_point', ['load', 'load_into'])
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_file_inputs(
    source, expected_model, expected_dataset, target_cls, entry_point, select_serializer_by
) -> None:
    if entry_point == 'load':
        result = target_cls.load(source, select_serializer_by=select_serializer_by)
    else:
        result = target_cls()
        assert result.load_into(source, select_serializer_by=select_serializer_by) is result
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

    result = target_cls.load(path, select_serializer_by='suffix', ignore_dirs=True)
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


@pc.parametrize(
    'members, target_cls, expected',
    [
        ({'a.json': b'[1, 2]'}, Dataset[Model[list[int]]], {'a': [1, 2]}),
        ({'a.json': b'[1, 2]'}, Dataset[Model[object]], {'a': [1, 2]}),
        ({'a.txt': b'"quoted"'}, Dataset[Model[object]], {'a': '"quoted"'}),
        ({'a.png': b'\x89PNG'}, Dataset[Model[object]], {'a': b'\x89PNG'}),
        ({'a.png': b'\x89PNG'}, Dataset[Model[bytes]], {'a': b'\x89PNG'}),
    ],
)
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_serializer_selection_falls_back_to_file_suffix_and_raw_bytes(
    tmp_path, members, target_cls, expected, select_serializer_by
) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', members)
    result = target_cls.load(path, select_serializer_by=select_serializer_by)
    assert result.to_data() == expected


def test_serializer_selection_by_type_overrides_file_suffix(tmp_path) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', {'a.json': b'[1, 2]'})

    assert Dataset[Model[str]].load(path, select_serializer_by='type').to_data() == {'a': '[1, 2]'}
    with pytest.raises(ValidationError):
        Dataset[Model[str]].load(path, select_serializer_by='suffix')


@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_serializer_selection_by_file_suffix_rejects_mixed_suffixes(
    tmp_path, select_serializer_by
) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', {'a.json': b'[1]', 'b.md': b'# x'})

    with pytest.raises(ValueError, match='different file suffixes'):
        Dataset[Model[object]].load(path, select_serializer_by=select_serializer_by)

    # A bytes target is supported directly by type, regardless of the file suffixes
    assert Dataset[Model[bytes]].load(path, select_serializer_by='type').to_data() == {
        'a': b'[1]',
        'b': b'# x',
    }
