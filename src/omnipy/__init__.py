__version__ = '0.12.3'

import os
import sys
from typing import Optional

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.hub.runtime import Runtime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# TODO: The check disabling runtime for tests also trigger for tests that are run outside of Omnipy,
#  breaking tests on the user side.
#  Find a better way to disable the global runtime object for Omnipy tests


def _get_runtime() -> Optional['Runtime']:
    if 'pytest' not in sys.modules:
        return Runtime()
    else:
        return None


runtime: Optional['Runtime'] = _get_runtime()

__all__ = [Model, Dataset]
