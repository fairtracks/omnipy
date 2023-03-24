__version__ = '0.10.0'

import os
import sys
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_runtime() -> Optional['Runtime']:
    if 'pytest' not in sys.modules:
        from omnipy.hub.runtime import Runtime
        return Runtime()
    else:
        return None


runtime: Optional['Runtime'] = _get_runtime()
