__version__ = '0.9.0'

import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

runtime = None

if 'pytest' not in sys.modules:
    from omnipy.hub.runtime import Runtime
    runtime = Runtime()
