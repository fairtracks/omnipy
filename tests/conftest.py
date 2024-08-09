from datetime import datetime
import gc
import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Annotated, Callable, Iterator, Type

import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.compute.job_creator import JobBaseMeta, JobCreator
from omnipy.config.root_log import RootLogConfig
from omnipy.data.data_class_creator import DataClassBaseMeta, DataClassCreator


@pytest.fixture(scope='function')
def teardown_rm_default_root_log_dir() -> Iterator[None]:
    root_log_config = RootLogConfig()
    log_file_path = root_log_config.file_log_path
    yield
    log_dir_path = os.path.dirname(log_file_path)
    if os.path.exists(log_dir_path):
        shutil.rmtree(log_dir_path)


@pytest.fixture(scope='function')
def teardown_remove_root_log_handlers() -> Iterator[None]:
    root_logger = logging.root
    num_root_log_handlers = len(root_logger.handlers)
    yield
    assert len(root_logger.handlers[num_root_log_handlers:]) <= 3
    for handler in root_logger.handlers[num_root_log_handlers:]:
        root_logger.removeHandler(handler)


@pytest.fixture(scope='function')
def tmp_dir_path() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as _tmp_dir_path:
        yield Path(_tmp_dir_path)


@pytest.fixture(scope='function')
def teardown_reset_job_creator() -> Iterator[None]:
    yield None
    JobBaseMeta._job_creator_obj = JobCreator()


@pytest.fixture(scope='function')
def teardown_reset_data_class_creator() -> Iterator[None]:
    yield None
    DataClassBaseMeta._data_class_creator_obj = DataClassCreator()


@pytest.fixture(scope='function')
def runtime_cls(
    teardown_rm_default_root_log_dir: Annotated[None, pytest.fixture],
    teardown_remove_root_log_handlers: Annotated[None, pytest.fixture],
    teardown_reset_job_creator: Annotated[None, pytest.fixture],
    teardown_reset_data_class_creator: Annotated[None, pytest.fixture],
) -> Type[IsRuntime]:
    from omnipy.hub.runtime import Runtime
    return Runtime


@pytest.fixture(scope='function')
def runtime(
    runtime_cls: Annotated[Type[IsRuntime], pytest.fixture],
    tmp_dir_path: Annotated[Path, pytest.fixture],
) -> Iterator[None]:
    runtime = runtime_cls()

    runtime.config.reset_to_defaults()
    runtime.config.job.output_storage.local.persist_data_dir_path = str(tmp_dir_path / 'outputs')
    runtime.config.root_log.file_log_path = str(tmp_dir_path / 'logs' / 'omnipy.log')

    yield runtime


@pytest.fixture(scope='function')
def mock_datetime() -> datetime:
    class MockDatetime(datetime):
        def __init__(self, *args: object, **kwargs: object):
            self._now = datetime.now()

        def now(self, tz=None):
            return self._now

    return MockDatetime(2000, 1, 1)


@pytest.fixture(scope='function')
def assert_snapshot_holder_and_deepcopy_memo_are_empty(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> Callable[[], None]:
    snapshot_holder = runtime.objects.data_class_creator.snapshot_holder

    def _assert_snapshot_holder_and_deepcopy_memo_are_empty():
        snapshot_holder.delete_scheduled_deepcopy_content_ids()
        try:
            print('\nChecking if snapshot_holder and deepcopy_memo objects are empty...')
            assert snapshot_holder.all_are_empty()
        except AssertionError:
            try:
                print('Not empty. Running garbage collection and trying again...')
                gc.collect()
                snapshot_holder.delete_scheduled_deepcopy_content_ids()
            except AssertionError:
                print('Not empty again. Running garbage collection and trying last time...')
                gc.collect()
                snapshot_holder.delete_scheduled_deepcopy_content_ids()

                try:
                    assert snapshot_holder.all_are_empty()
                except AssertionError:
                    assert snapshot_holder.all_are_empty(debug=True)
            finally:
                snapshot_holder.clear()

    return _assert_snapshot_holder_and_deepcopy_memo_are_empty


@pytest.fixture(scope='function')
def assert_snapshot_holder_and_deepcopy_memo_are_empty_before_and_after(
    assert_snapshot_holder_and_deepcopy_memo_are_empty: Annotated[Callable[[], None],
                                                                  pytest.fixture]
) -> Iterator[None]:

    assert_snapshot_holder_and_deepcopy_memo_are_empty()

    yield

    assert_snapshot_holder_and_deepcopy_memo_are_empty()
