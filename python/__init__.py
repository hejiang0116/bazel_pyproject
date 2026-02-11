import os
import sys

# This allows 'import xla' inside the library to find the 'xla' subfolder
_pkg_root = os.path.dirname(os.path.abspath(__file__))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from .main import *