import inspect
import os
from pathlib import Path
import sys


def set_prefect_config_path():
    prefect_module_dir = os.path.dirname(inspect.getabsfile(inspect.currentframe()))

    os.environ['PREFECT_LOGGING_SETTINGS_PATH'] = \
        f"{Path(prefect_module_dir).joinpath('settings', 'logging.yml')}"


def use_local_api_for_tests():
    if 'pytest' in sys.modules:
        os.environ['PREFECT_API_KEY'] = ''
        os.environ['PREFECT_API_URL'] = ''


set_prefect_config_path()
use_local_api_for_tests()

from prefect import Flow as PrefectFlow  # noqa
from prefect import flow as prefect_flow  # noqa
from prefect import State  # noqa
from prefect import Task as PrefectTask  # noqa
from prefect import task as prefect_task  # noqa
from prefect.tasks import task_input_hash  # noqa
from prefect.utilities.names import generate_slug  # noqa
