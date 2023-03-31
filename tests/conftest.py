from datetime import datetime
import gc
import itertools
import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Annotated, Callable, Iterator, Type
from unittest import mock

import pytest
import pytest_cases as pc

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.api.typedefs import TypeForm
from omnipy.compute.job_creator import JobBaseMeta, JobCreator
from omnipy.config.data import DataConfig
from omnipy.config.root_log import RootLogConfig
from omnipy.data.data_class_creator import DataClassBaseMeta, DataClassCreator

from .helpers.functions import assert_model, assert_val
from .helpers.protocols import AssertModelOrValFunc


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
) -> Iterator[IsRuntime]:
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

        def now(self, tz=None) -> datetime:  # type: ignore[override]
            return self._now

    return MockDatetime(2000, 1, 1)


@pytest.fixture(scope='function')
def assert_empty_snapshot_holder_and_deepcopy_memo(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> Callable[[], None]:
    snapshot_holder = runtime.objects.data_class_creator.snapshot_holder

    NOT_EMPTY_ERROR = 'Snapshot_holder and/or deepcopy_memo objects are{} not empty. '

    def _assert_empty_snapshot_holder_and_deepcopy_memo():
        snapshot_holder.delete_scheduled_deepcopy_content_ids()
        try:
            assert snapshot_holder.all_are_empty()
        except AssertionError:
            try:
                print(f"\n{NOT_EMPTY_ERROR.format('')}"
                      f'Running garbage collection and trying again...')
                gc.collect()
                snapshot_holder.delete_scheduled_deepcopy_content_ids()
            except AssertionError:
                print(f"\n{NOT_EMPTY_ERROR.format(' still')}"
                      f'Running garbage collection and trying last time...')
                gc.collect()
                snapshot_holder.delete_scheduled_deepcopy_content_ids()

                try:
                    assert snapshot_holder.all_are_empty()
                except AssertionError:
                    assert snapshot_holder.all_are_empty(debug=True)
            finally:
                snapshot_holder.clear()

    return _assert_empty_snapshot_holder_and_deepcopy_memo


@pytest.fixture(scope='function')
def assert_empty_snapshot_holder_and_deepcopy_memo_before_and_after(
        assert_empty_snapshot_holder_and_deepcopy_memo: Callable[[], None]) -> Iterator[None]:

    assert_empty_snapshot_holder_and_deepcopy_memo()

    yield

    assert_empty_snapshot_holder_and_deepcopy_memo()


@pc.fixture(scope='function')
@pc.parametrize(interactive=[True, False], dyn_convert=[False, True])
def runtime_data_config_variants(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_empty_snapshot_holder_and_deepcopy_memo_before_and_after: Annotated[Callable[[], None],
                                                                               pytest.fixture],
    interactive: bool,
    dyn_convert: bool,
) -> IsRuntime:
    runtime.config.data.interactive_mode = interactive
    runtime.config.data.dynamically_convert_elements_to_models = dyn_convert

    return runtime


@pytest.fixture(scope='function')
def skip_test_if_interactive_mode(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    pass
    if runtime.config.data.interactive_mode:
        pytest.skip('This test only runs without `interactive_mode`')


@pytest.fixture(scope='function')
def skip_test_if_not_interactive_mode(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    pass
    if not runtime.config.data.interactive_mode:
        pytest.skip('This test only runs with `interactive_mode`')


@pytest.fixture(scope='function')
def skip_test_if_dynamically_convert_elements_to_models(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    pass
    if runtime.config.data.dynamically_convert_elements_to_models:
        pytest.skip('This test only runs without `dynamically_convert_elements_to_models`')


@pytest.fixture(scope='function')
def skip_test_if_not_dynamically_convert_elements_to_models(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    pass
    if not runtime.config.data.dynamically_convert_elements_to_models:
        pytest.skip('This test only runs with `dynamically_convert_elements_to_models`')


@pytest.fixture(scope='function')
def skip_test_if_not_default_data_config_values(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    if any(
            getattr(runtime.config.data, attr) != getattr(DataConfig, attr)
            for attr in ('interactive_mode', 'dynamically_convert_elements_to_models')):
        pytest.skip('This test only runs with default data config values')


@pytest.fixture(scope='function')
def assert_model_if_dyn_conv_else_val(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> AssertModelOrValFunc:
    def _assert_model_if_dyn_convert_else_val(
        model_or_val: object,
        target_type: TypeForm,
        contents: object,
    ):
        if runtime.config.data.dynamically_convert_elements_to_models:
            assert_model(model_or_val, target_type, contents)
        else:
            assert_val(model_or_val, target_type, contents)

    return _assert_model_if_dyn_convert_else_val


def pytest_collection_modifyitems(items):
    integration_tests = []
    mypy_tests = []
    other_tests = []

    def _is_mypy_test(item):
        return item.__class__.__module__.startswith('pytest_mypy_plugins')

    def _module_name(item):
        return item.module.__name__

    for mypy_test, tests_per_type in itertools.groupby(items, key=_is_mypy_test):
        if mypy_test:
            for test in tests_per_type:
                test._nodeid = test.nodeid.replace('tests/', 'tests/@mypy-tests/')
                mypy_tests.append(test)
        else:
            for module, tests_per_module in itertools.groupby(tests_per_type, key=_module_name):
                if module.startswith('tests.integration'):
                    for test in tests_per_module:
                        test._nodeid = test.nodeid.replace('tests/', 'tests/@integration-tests/')
                        integration_tests.append(test)
                else:
                    other_tests.extend(tests_per_module)

    # For some unknown reason, pytest_mypy_plugins tests are much slower when running after other
    # tests, in particular integration tests. Running time to be correlated to the number of
    # previously run tests. Running pytest_mypy_plugins tests in the middle represents a tradeoff
    # between total running time and the need to run unit tests first for optimal feedback loop
    # when developing.
    items[:] = other_tests + mypy_tests + integration_tests


@pc.fixture(scope='function')
def mock_windows_linesep() -> Iterator[None]:
    with mock.patch('os.linesep', new='\r\n'):
        yield


@pc.fixture(scope='function')
def mock_unix_mac_linesep() -> Iterator[None]:
    with mock.patch('os.linesep', new='\n'):
        yield


@pc.fixture(scope='function')
@pc.parametrize(
    'linesep_variant',
    [mock_unix_mac_linesep, mock_windows_linesep],
    ids=['unix_mac_linesep', 'windows_linesep'],
)
def mock_linesep_variants(linesep_variant: Annotated[Iterator[None], pc.fixture]) -> Iterator[None]:
    yield
