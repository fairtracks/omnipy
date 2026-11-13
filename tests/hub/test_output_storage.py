"""Tests for output storage backends and persistence to S3-compatible storage.

S3 is replaced by fsspec's in-memory file system, so the tests need neither s3fs nor a network.
"""

from collections.abc import Iterator
import importlib.util
from pathlib import Path
from typing import Annotated, Any
import uuid

import fsspec
import pytest

from omnipy import Dataset, Model, TaskTemplate
import omnipy.hub.output_storage as output_storage_module
from omnipy.hub.output_storage import (
    FsspecOutputStorage,
    get_output_storage,
    LocalOutputStorage,
    s3_filesystem,
)
from omnipy.shared.enums.job import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions
from omnipy.shared.protocols.hub.runtime import IsRuntime


@pytest.fixture
def memory_fs() -> Iterator[Any]:
    """An in-memory fsspec file system, emptied after the test."""
    filesystem = fsspec.filesystem('memory')
    yield filesystem
    filesystem.store.clear()
    filesystem.pseudo_dirs[:] = ['']


@pytest.fixture
def s3_as_memory(monkeypatch: pytest.MonkeyPatch, memory_fs: Any) -> Any:
    """Make the S3 output storage use the in-memory file system."""
    monkeypatch.setattr(output_storage_module, 's3_filesystem', lambda s3_config: memory_fs)
    return memory_fs


def _exercise_storage(storage: Any) -> None:
    assert storage.list_dirs() == []
    assert storage.list_files() == []

    storage.write_bytes('run_1/00_a.tar.gz', b'a')
    storage.write_bytes('run_1/01_b.tar.gz', b'b')
    storage.write_bytes('run_2/00_c.tar.gz', b'c')
    storage.write_bytes('omnipy.log', b'log')

    assert storage.list_dirs() == ['run_1', 'run_2']
    assert storage.list_files() == ['omnipy.log']
    assert storage.list_files('run_1') == ['00_a.tar.gz', '01_b.tar.gz']
    assert storage.list_files('missing') == []

    with storage.local_copy('run_1/01_b.tar.gz') as local_path:
        assert local_path.endswith('.tar.gz')
        assert Path(local_path).read_bytes() == b'b'


def test_local_output_storage(tmp_path: Path) -> None:
    _exercise_storage(LocalOutputStorage(tmp_path / 'outputs'))


def test_fsspec_output_storage(memory_fs: Any) -> None:
    _exercise_storage(FsspecOutputStorage(memory_fs, f'bucket-{uuid.uuid4().hex}/outputs'))


def test_fsspec_upload_and_download(memory_fs: Any, tmp_path: Path) -> None:
    storage = FsspecOutputStorage(memory_fs, 'bucket/staging')
    local_file = tmp_path / 'params.json'
    local_file.write_text('{}')

    url = storage.upload_file(local_file, 'job_1/params.json')
    assert url == 's3://bucket/staging/job_1/params.json'
    assert storage.list_files('job_1') == ['params.json']

    storage.download_file('job_1/params.json', tmp_path / 'copy.json')
    assert (tmp_path / 'copy.json').read_text() == '{}'

    storage.write_bytes('job_1/outputs/run/00_x.tar.gz', b'x')
    storage.download_dir('job_1/outputs', tmp_path / 'outputs')
    assert (tmp_path / 'outputs' / 'run' / '00_x.tar.gz').read_bytes() == b'x'


def test_get_output_storage_selects_protocol(
    runtime: Annotated[IsRuntime, pytest.fixture],
    s3_as_memory: Annotated[Any, pytest.fixture],
) -> None:
    job_config = runtime.config.job
    assert isinstance(get_output_storage(job_config), LocalOutputStorage)

    with pytest.raises(ValueError, match='bucket name'):
        get_output_storage(job_config, 's3')

    job_config.output_storage.s3.bucket_name = 'my-bucket'
    storage = get_output_storage(job_config, 's3')
    assert isinstance(storage, FsspecOutputStorage)
    assert storage.root == 's3://my-bucket/omnipy/outputs'


@pytest.mark.skipif(importlib.util.find_spec('s3fs') is not None, reason='s3fs is installed')
def test_s3_without_s3fs_points_to_the_extra(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    with pytest.raises(ImportError, match=r'omnipy\[s3\]'):
        s3_filesystem(runtime.config.job.output_storage.s3)


@TaskTemplate()
def _squares(numbers: Model[list[int]]) -> Dataset[Model[int]]:
    return Dataset[Model[int]]({str(number): number * number for number in numbers.content})


def test_persist_and_restore_with_s3(
    runtime: Annotated[IsRuntime, pytest.fixture],
    s3_as_memory: Annotated[Any, pytest.fixture],
) -> None:
    output_storage = runtime.config.job.output_storage
    output_storage.protocol = 's3'
    output_storage.s3.bucket_name = f'bucket-{uuid.uuid4().hex}'
    output_storage.persist_outputs = ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS

    result = _squares.run(Model[list[int]]([1, 2, 3]))
    assert result == Dataset[Model[int]]({'1': 1, '2': 4, '3': 9})

    storage = get_output_storage(runtime.config.job)
    run_dirs = storage.list_dirs()
    assert len(run_dirs) == 1
    assert storage.list_files(run_dirs[0]) == ['00_task__squares.tar.gz']

    output_storage.persist_outputs = ConfigPersistOutputsOptions.DISABLED
    output_storage.restore_outputs = ConfigRestoreOutputsOptions.AUTO_ENABLE_IGNORE_PARAMS
    restored = _squares.run(Model[list[int]]([5]))
    assert Dataset[Model[int]](restored) == Dataset[Model[int]]({'1': 1, '2': 4, '3': 9})
