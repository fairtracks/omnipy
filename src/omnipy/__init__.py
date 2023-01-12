__version__ = '0.5.1'

import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

runtime = None

if 'pytest' not in sys.modules:
    from omnipy.config.runtime import Runtime
    runtime = Runtime()
