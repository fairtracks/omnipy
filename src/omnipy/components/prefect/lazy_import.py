import os
from pathlib import Path
import socket
import sys

import prefect.testing.utilities


def set_prefect_config_path():
    prefect_module_dir = Path(__file__).resolve().parent

    os.environ['PREFECT_LOGGING_SETTINGS_PATH'] = \
        f"{prefect_module_dir.joinpath('settings', 'logging.yml')}"


def use_ephemeral_mode_for_tests():
    """Force Prefect into ephemeral local mode when running under ``pytest``.

    The test suite should not depend on external Prefect Cloud or server settings, so
    this helper clears remote-API settings and enables ephemeral mode when ``pytest``
    has been imported.
    """
    if 'pytest' in sys.modules:
        os.environ['PREFECT_SERVER_ALLOW_EPHEMERAL_MODE'] = 'True'
        os.environ['PREFECT_API_KEY'] = ''
        os.environ['PREFECT_API_URL'] = ''


def insert_mock_test_harness_port_finder_for_tests():
    if 'pytest' in sys.modules:
        from prefect.server.api.server import SubprocessASGIServer  # pyright: ignore
        from prefect.testing.utilities import _find_available_port  # pyright: ignore

        def _find_available_port_with_env_override() -> int:
            prefect_test_port = os.getenv('PREFECT_TEST_PORT')
            if prefect_test_port:
                return int(prefect_test_port)
            else:
                return _find_available_port()

        class MockSubprocessASGIServer(SubprocessASGIServer):
            @property
            def address(self) -> str:
                return f'http://0.0.0.0:{self.port}'

            @property
            def api_url(self) -> str:
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                return f'http://{ip_address}/api'

        prefect.testing.utilities._find_available_port = (  # pyright: ignore
            _find_available_port_with_env_override)

        use_nono_workaround = os.getenv('PREFECT_TEST_NONO_WORKAROUND')
        if use_nono_workaround:
            prefect.testing.utilities.SubprocessASGIServer = (  # pyright: ignore
                MockSubprocessASGIServer)


set_prefect_config_path()
use_ephemeral_mode_for_tests()
insert_mock_test_harness_port_finder_for_tests()

from prefect import cache_policies  # noqa
from prefect import State  # noqa
from prefect import Flow as PrefectFlow  # noqa
from prefect import flow as prefect_flow  # noqa
from prefect import Task as PrefectTask  # noqa
from prefect import task as prefect_task  # noqa
from prefect.cache_policies import CachePolicy, Inputs, RUN_ID, TASK_SOURCE  # noqa
from prefect.context import TaskRunContext  # noqa
from prefect.server.api.server import replace_placeholder_string_in_files  # noqa
from prefect.tasks import task_input_hash  # noqa
from prefect.testing.utilities import prefect_test_harness  # noqa
from prefect.utilities.annotations import NotSet  # noqa
