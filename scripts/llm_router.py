"""Shim: re-exports the Kerala PSC project's llm_router in place.

Avoids duplicating API keys/.env into this repo — the real module and its
.env live in keralapscprep/scripts/, and Python's __file__ still resolves
there when loaded this way, so its own ROOT/.env loading works unchanged.

Loaded under an alias (not plain sys.path + import) because this shim file
is itself named llm_router.py, which would otherwise collide with the real
module name and re-import itself instead.
"""
import importlib.util
import sys
from pathlib import Path

_PSC_MODULE_PATH = Path(r"C:\Users\Dell\Projects\keralapscprep\scripts\llm_router.py")
_spec = importlib.util.spec_from_file_location("_psc_llm_router", _PSC_MODULE_PATH)
_psc = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _psc  # dataclass() needs the module registered to resolve annotations
_spec.loader.exec_module(_psc)

# Re-export the public API
call_llm = _psc.call_llm
PROVIDERS = _psc.PROVIDERS
TASK_ORDER = _psc.TASK_ORDER
