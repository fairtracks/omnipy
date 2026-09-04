from collections.abc import Iterator
from contextlib import contextmanager
import os
from pathlib import Path


def set_prefect_config_path():
    prefect_module_dir = Path(__file__).resolve().parent

    os.environ['PREFECT_LOGGING_SETTINGS_PATH'] = \
        f"{prefect_module_dir.joinpath('settings', 'logging.yml')}"


set_prefect_config_path()


@contextmanager
def prefect_test_config_context(with_harness: bool) -> Iterator[None]:
    import prefect.settings as ps

    # Adapted from https://github.com/PrefectHQ/prefect/blob/main/tests/conftest.py
    prefect_test_settings = {
        ps.PREFECT_CLI_COLORS: False,
        ps.PREFECT_CLI_WRAP_LINES: False,
        ps.PREFECT_LOGGING_TO_API_ENABLED: False,
        ps.PREFECT_SERVER_ANALYTICS_ENABLED: False,
        ps.PREFECT_API_SERVICES_LATE_RUNS_ENABLED: False,
        ps.PREFECT_API_SERVICES_SCHEDULER_ENABLED: False,
        ps.PREFECT_API_SERVICES_PAUSE_EXPIRATIONS_ENABLED: False,
        ps.PREFECT_API_SERVICES_CANCELLATION_CLEANUP_ENABLED: False,
        ps.PREFECT_API_SERVICES_FOREMAN_ENABLED: False,
        ps.PREFECT_API_LOG_RETRYABLE_ERRORS: True,
        ps.PREFECT_MEMOIZE_BLOCK_AUTO_REGISTRATION: False,
        ps.PREFECT_API_BLOCKS_REGISTER_ON_START: False,
        ps.PREFECT_API_SERVICES_EVENT_PERSISTER_ENABLED: False,
        ps.PREFECT_API_SERVICES_TRIGGERS_ENABLED: False,
        ps.PREFECT_API_SERVICES_TASK_RUN_RECORDER_ENABLED: False,
        ps.PREFECT_FLOWS_HEARTBEAT_FREQUENCY: None,
    }

    if with_harness:
        # To ignore external server, if configured
        prefect_test_settings[ps.PREFECT_API_URL] = ''
        prefect_test_settings[ps.PREFECT_API_KEY] = ''

        # Needed for multithread/multiprocess tasks in tests/engine/cases/tasks.py
        prefect_test_settings[ps.PREFECT_SERVER_EPHEMERAL_ENABLED] = True
    else:
        # To make sure ephemeral server is not started instead of test harness
        prefect_test_settings[ps.PREFECT_SERVER_EPHEMERAL_ENABLED] = False

    with ps.temporary_settings(prefect_test_settings):
        yield


@contextmanager
def prefect_test_harness_context(port: int | None) -> Iterator[None]:
    import prefect.testing.utilities

    if port is not None:
        prefect.testing.utilities._find_available_port = lambda: port

    with prefect.testing.utilities.prefect_test_harness():
        yield


from prefect import cache_policies  # noqa
from prefect import Flow as PrefectFlow  # noqa
from prefect import flow as prefect_flow  # noqa
from prefect import State  # noqa
from prefect import Task as PrefectTask  # noqa
from prefect import task as prefect_task  # noqa
from prefect.cache_policies import CachePolicy, Inputs, RUN_ID, TASK_SOURCE  # noqa
from prefect.context import TaskRunContext  # noqa
from prefect.tasks import task_input_hash  # noqa
from prefect.utilities.annotations import NotSet  # noqa
