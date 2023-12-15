__version__ = '0.12.2'

import importlib
import os
import sys
from typing import Optional

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.hub.runtime import Runtime
from omnipy.util.helpers import recursive_module_import

# from omnipy.util.helpers import recursive_module_import

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


def __getattr__(attr_name: str) -> object:
    omnipy = importlib.import_module(__name__)
    all_modules = []
    recursive_module_import(omnipy, all_modules)
    print(all_modules)


#
#
# print(__file__)
# print(__name__)
# print(list(globals().keys()))
