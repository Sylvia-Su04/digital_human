"""
Wrapper package that re-exports the real GFPGAN package from pylibs,
while providing the gfpgan/weights/ directory for facexlib model downloads.
"""
import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_comfy_root = os.path.dirname(_this_dir)

# Remove the partially-initialized wrapper from sys.modules so we can import the real one
_wrapper = sys.modules.pop('gfpgan', None)

# Temporarily remove ComfyUI root from sys.path to find the real gfpgan in PYTHONPATH
_orig_path = sys.path[:]
sys.path = [p for p in sys.path if os.path.abspath(p) != _comfy_root]

try:
    import importlib
    _real_gfpgan = importlib.import_module('gfpgan')
finally:
    sys.path = _orig_path

# Copy all public attributes from the real gfpgan into this wrapper's namespace
for _attr in dir(_real_gfpgan):
    if not _attr.startswith('_'):
        globals()[_attr] = getattr(_real_gfpgan, _attr)

# Also copy submodules so that 'from gfpgan.xxx import yyy' works
for _name, _mod in list(sys.modules.items()):
    if _name.startswith('gfpgan.'):
        globals()[_name.split('.', 1)[1]] = _mod
