"""Public loading of local files and archives."""

import asyncio
from io import BytesIO
from pathlib import Path
import tarfile
from typing import Literal

import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.raw.datasets import StrDataset, StrictStrDataset
from omnipy.components.raw.models import StrModel
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.enums.data import SelectSerializerBy
from omnipy.util.pydantic import ValidationError

from ..serialize.helpers.functions import write_tar_gz
from .cases.files import FileCase


@pc.parametrize_with_cases('case', cases='.cases.files')
@pytest.mark.parametrize('target_cls', [Model[object], JsonDataset, Model[JsonDataset]])
@pytest.mark.parametrize('entry_point', ['load', 'load_into'])
def test_file_inputs(
    case: FileCase,
    target_cls: type[Model] | type[Dataset],
    entry_point: Literal['load', 'load_into'],
) -> None:
    if entry_point == 'load':
        result = target_cls.load(case.source)
        # Local paths given as str are loaded synchronously, even if typed as possibly URLs
        assert not isinstance(result, asyncio.Task)
    else:
        result = target_cls()
        assert result.load_into(case.source) is result
    expected = case.expected_model if target_cls is Model[object] else case.expected_dataset
    assert result.to_data() == expected


@pytest.mark.parametrize('target_cls', [Model[object], JsonDataset, Model[JsonDataset]])
def test_load_archive_ignores_directory_members(
    tmp_path: Path, target_cls: type[Model] | type[Dataset]
) -> None:
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
    assert result.to_data() == {'first': [1, 2]}


@pytest.mark.parametrize('target_cls', [Model[object], JsonDataset])
@pytest.mark.parametrize('as_keywords', [False, True])
def test_keyed_local_paths_remain_unsupported(
    tmp_path: Path, target_cls: type[Model] | type[Dataset], as_keywords: bool
) -> None:
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
        ({'a.csv': b'x,y\n1,2\n'}, Dataset[Model[object]], {'a': {'x': [1], 'y': [2]}}),
        ({'a.bytes': b'\x00\xff'}, Dataset[Model[object]], {'a': b'\x00\xff'}),
        ({'a.md': b'# x'}, Dataset[Model[object]], {'a': b'# x'}),
        ({'a.png': b'\x89PNG'}, Dataset[Model[object]], {'a': b'\x89PNG'}),
        ({'a.png': b'\x89PNG'}, Dataset[Model[bytes]], {'a': b'\x89PNG'}),
    ],
)
@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_serializer_selection_falls_back_to_file_suffix_and_raw_bytes(
    tmp_path: Path,
    members: dict[str, bytes | None],
    target_cls: type[Dataset],
    expected: dict[str, object],
    select_serializer_by: SelectSerializerBy.Literals,
) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', members)
    result = target_cls.load(path, select_serializer_by=select_serializer_by)
    assert result.to_data() == expected


@pc.parametrize(
    'file_name, content, expected_by_suffix',
    [
        ('first.txt', b'hello', 'hello'),
        ('first.csv', b'x,y\n1,2\n', {'x': [1], 'y': [2]}),
        ('first.md', b'# x', '# x'),
    ],
)
@pytest.mark.parametrize('target_cls', [JsonDataset, Model[JsonDataset]])
@pytest.mark.parametrize('as_archive', [False, True])
def test_serializer_selection_of_json_dataset_for_other_file_suffixes(
    tmp_path: Path,
    file_name: str,
    content: bytes,
    expected_by_suffix: object,
    target_cls: type[Dataset] | type[Model],
    as_archive: bool,
) -> None:
    if as_archive:
        path = write_tar_gz(tmp_path / 'data.tar.gz', {file_name: content})
    else:
        path = tmp_path / file_name
        path.write_bytes(content)

    assert target_cls.load(path, select_serializer_by='suffix').to_data() == {
        'first': expected_by_suffix
    }
    # Selecting by type uses the JSON serializer, regardless of the file suffix
    with pytest.raises(ValidationError):
        target_cls.load(path, select_serializer_by='type')


def test_serializer_selection_by_type_overrides_file_suffix(tmp_path: Path) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', {'a.json': b'[1, 2]'})

    assert Dataset[Model[str]].load(path, select_serializer_by='type').to_data() == {'a': '[1, 2]'}
    with pytest.raises(ValidationError):
        Dataset[Model[str]].load(path, select_serializer_by='suffix')


def test_failed_file_validation_preserves_model_contents(tmp_path: Path) -> None:
    path = tmp_path / 'invalid.json'
    path.write_text('["not an integer"]')
    model = Model[list[int]]([7])

    with pytest.raises(ValidationError):
        model.load_into(path)
    assert model.content == [7]


def test_dataset_wrapping_model_load_into_merges(tmp_path: Path) -> None:
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')
    model = Model[JsonDataset](existing=[0])

    assert model.load_into(path) is model
    assert model.to_data() == {'existing': [0], 'first': [1, 2]}


@pytest.mark.parametrize(
    'member_name, expected',
    [
        ('__model_list_int__.json', [1, 2]),
        ('first.json', {'first': [1, 2]}),
    ],
)
def test_one_member_archive_is_keyed_unless_saved_as_single_value(
    tmp_path: Path, member_name: str, expected: object
) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', {member_name: b'[1, 2]'})
    assert Model[object].load(path).to_data() == expected


@pytest.mark.parametrize('select_serializer_by', ['type', 'suffix'])
def test_serializer_selection_by_file_suffix_rejects_mixed_suffixes(
    tmp_path: Path, select_serializer_by: SelectSerializerBy.Literals
) -> None:
    path = write_tar_gz(tmp_path / 'data.tar.gz', {'a.json': b'[1]', 'b.md': b'# x'})

    with pytest.raises(ValueError, match='different file suffixes'):
        Dataset[Model[object]].load(path, select_serializer_by=select_serializer_by)

    # A bytes target is supported directly by type, regardless of the file suffixes
    assert Dataset[Model[bytes]].load(path, select_serializer_by='type').to_data() == {
        'a': b'[1]',
        'b': b'# x',
    }


@pytest.mark.parametrize('target_cls', [JsonDataset, StrictStrDataset])
@pytest.mark.parametrize('as_archive', [False, True])
def test_loading_non_utf8_content_as_text_fails_validation(
    tmp_path: Path, target_cls: type[Dataset], as_archive: bool
) -> None:
    if as_archive:
        path = write_tar_gz(tmp_path / 'data.tar.gz', {'first.bytes': b'\x00\xff'})
    else:
        path = tmp_path / 'first.bytes'
        path.write_bytes(b'\x00\xff')

    with pytest.raises(ValidationError, match='first'):
        target_cls.load(path, select_serializer_by='type')


@pytest.mark.parametrize('as_archive', [False, True])
def test_non_utf8_text_loads_as_bytes_into_str_models_with_matching_encoding(
    tmp_path: Path, as_archive: bool
) -> None:
    content = 'blåbær'.encode('latin-1')
    if as_archive:
        path = write_tar_gz(tmp_path / 'data.tar.gz', {'first.bytes': content})
    else:
        path = tmp_path / 'first.bytes'
        path.write_bytes(content)
    str_dataset_latin1 = StrDataset.adjust('StrDatasetLatin1', 'StrModelLatin1', encoding='latin-1')

    loaded = str_dataset_latin1.load(path, select_serializer_by='suffix')
    assert loaded.to_data() == {'first': 'blåbær'}
    if not as_archive:
        str_model_latin1 = StrModel.adjust('StrModelLatin1', encoding='latin-1')
        assert str_model_latin1.load(path, select_serializer_by='suffix').to_data() == 'blåbær'
