import os
from pathlib import Path
import sys


def set_prefect_config_path():
    prefect_module_dir = Path(__file__).resolve().parent

    os.environ['PREFECT_LOGGING_SETTINGS_PATH'] = \
        f"{prefect_module_dir.joinpath('settings', 'logging.yml')}"


def use_ephemeral_mode_for_tests():
    if 'pytest' in sys.modules:
        os.environ['PREFECT_SERVER_ALLOW_EPHEMERAL_MODE'] = 'True'
        os.environ['PREFECT_API_KEY'] = ''
        os.environ['PREFECT_API_URL'] = ''


set_prefect_config_path()
use_ephemeral_mode_for_tests()

from prefect import cache_policies  # noqa
from prefect import State  # noqa
from prefect import Flow as PrefectFlow  # noqa
from prefect import flow as prefect_flow  # noqa
from prefect import Task as PrefectTask  # noqa
from prefect import task as prefect_task  # noqa
from prefect.cache_policies import CachePolicy  # noqa
from prefect.tasks import task_input_hash  # noqa
from prefect.testing.utilities import prefect_test_harness  # noqa
from prefect.utilities.annotations import NotSet  # noqa
