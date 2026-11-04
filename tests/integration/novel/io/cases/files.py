"""Local file, directory, and archive inputs to public loading."""

from collections.abc import Callable, Iterable
import json
from pathlib import Path
import tarfile
from typing import Literal, NamedTuple
from zipfile import ZipFile

import pytest_cases as pc

from omnipy.shared.protocols.data import IsPathsOrUrlsOneOrMore


class FileCase(NamedTuple):
    source: IsPathsOrUrlsOneOrMore
    expected_model: object
    """Expected data when loaded into a Model"""
    expected_dataset: dict[str, object]
    """Expected data when loaded into a Dataset, or a Model wrapping one"""


@pc.parametrize('kind', ['file', 'directory', 'tar', 'zip'])
@pc.parametrize('count', [1, 2])
def case_local_source(
    tmp_path: Path, kind: Literal['file', 'directory', 'tar', 'zip'], count: int
) -> FileCase:
    directory = tmp_path / 'payloads'
    directory.mkdir()
    expected: dict[str, object] = {
        key: [index, index + 1] for index, key in enumerate(('first', 'second')[:count])
    }
    for key, value in expected.items():
        (directory / f'{key}.json').write_text(json.dumps(value))

    source: str | list[str]
    if kind == 'file':
        source = [str(directory / f'{key}.json') for key in expected]
        source = source[0] if count == 1 else source
    elif kind == 'directory':
        source = str(directory)
    elif kind == 'tar':
        source = str(tmp_path / 'payloads.tar.gz')
        with tarfile.open(source, 'w:gz') as archive:
            for path in directory.iterdir():
                archive.add(path, arcname=path.name)
    else:
        source = str(tmp_path / 'payloads.zip')
        with ZipFile(source, 'w') as archive:
            for path in directory.iterdir():
                archive.write(path, arcname=path.name)

    model_expected: object = [0, 1] if kind == 'file' and count == 1 else expected
    return FileCase(source=source, expected_model=model_expected, expected_dataset=expected)


@pc.parametrize('wrapper', [list, iter])
def case_multiple_archives(
    tmp_path: Path, wrapper: Callable[[list[Path]], Iterable[Path]]
) -> FileCase:
    sources: list[Path] = []
    for key, value in [('first', [1, 2]), ('second', [3, 4])]:
        path = tmp_path / f'{key}.json'
        path.write_text(json.dumps(value))
        archive_path = tmp_path / f'{key}.tar.gz'
        with tarfile.open(archive_path, 'w:gz') as archive:
            archive.add(path, arcname=path.name)
        sources.append(archive_path)
    expected: dict[str, object] = {'first': [1, 2], 'second': [3, 4]}
    return FileCase(source=wrapper(sources), expected_model=expected, expected_dataset=expected)


def case_path_object(tmp_path: Path) -> FileCase:
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')
    return FileCase(source=path, expected_model=[1, 2], expected_dataset={'first': [1, 2]})


def case_empty_archive(tmp_path: Path) -> FileCase:
    path = tmp_path / 'empty.tar.gz'
    with tarfile.open(path, 'w:gz'):
        pass
    return FileCase(source=path, expected_model={}, expected_dataset={})


def case_single_file_list(tmp_path: Path) -> FileCase:
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')
    return FileCase(
        source=[str(path)], expected_model={'first': [1, 2]}, expected_dataset={'first': [1, 2]}
    )
