__version__ = '0.1.0'

import os
import sys

from unifair.config.runtime import Runtime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

runtime = Runtime() if "pytest" not in sys.modules else None
