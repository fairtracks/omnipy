import inspect
import os
from pathlib import Path


def set_prefect_config_path():
    prefect_module_dir = os.path.dirname(inspect.getabsfile(inspect.currentframe()))

    os.environ['PREFECT_LOGGING_SETTINGS_PATH'] = \
        f"{Path(prefect_module_dir).joinpath('settings', 'logging.yml')}"


# set_prefect_config_path()

from prefect import flow, Flow, State, task, Task
from prefect.tasks import task_input_hash
from prefect.utilities.names import generate_slug
