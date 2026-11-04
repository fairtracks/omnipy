"""Local file, directory, and archive inputs to public loading."""

import json
import tarfile
from zipfile import ZipFile

import pytest_cases as pc


@pc.parametrize('kind', ['file', 'directory', 'tar', 'zip'])
@pc.parametrize('count', [1, 2])
def case_local_source(tmp_path, kind, count):
    directory = tmp_path / 'payloads'
    directory.mkdir()
    expected = {key: [index, index + 1] for index, key in enumerate(('first', 'second')[:count])}
    for key, value in expected.items():
        (directory / f'{key}.json').write_text(json.dumps(value))

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

    model_expected = [0, 1] if kind == 'file' and count == 1 else expected
    return source, model_expected, expected


@pc.parametrize('wrapper', [list, tuple, iter])
def case_multiple_archives(tmp_path, wrapper):
    sources = []
    for key, value in [('first', [1, 2]), ('second', [3, 4])]:
        path = tmp_path / f'{key}.json'
        path.write_text(json.dumps(value))
        archive_path = tmp_path / f'{key}.tar.gz'
        with tarfile.open(archive_path, 'w:gz') as archive:
            archive.add(path, arcname=path.name)
        sources.append(archive_path)
    expected = {'first': [1, 2], 'second': [3, 4]}
    return wrapper(sources), expected, expected


def case_path_object(tmp_path):
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')
    return path, [1, 2], {'first': [1, 2]}


def case_empty_archive(tmp_path):
    path = tmp_path / 'empty.tar.gz'
    with tarfile.open(path, 'w:gz'):
        pass
    return path, {}, {}


def case_single_file_list(tmp_path):
    path = tmp_path / 'first.json'
    path.write_text('[1, 2]')
    return [str(path)], {'first': [1, 2]}, {'first': [1, 2]}
