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

from prefect import flow, Flow, State, task, Task
from prefect.tasks import task_input_hash
from prefect.utilities.names import generate_slug
