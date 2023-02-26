try:
    executable: str
    script_full_path: str
    from _ahk import executable, script_full_path  # noqa: F401
except ModuleNotFoundError:
    import sys as _sys

    class _shim:
        def __getattr__(self, name):
            quoted_args = " ".join(
                f'"{arg}"' if " " in arg else arg
                for arg in _sys.argv
            )
            raise RuntimeError(
                f"AHK interop is not available. Please start your code as 'py -m ahkpy {quoted_args}'.",
            )

    _sys.modules["_ahk"] = _shim()
    del _shim


from .hotkey_context import *  # noqa: F401 F403

from .block_input import *  # noqa: F401 F403
from .clipboard import *  # noqa: F401 F403
from .exceptions import *  # noqa: F401 F403
from .flow import *  # noqa: F401 F403
from .hotkey import *  # noqa: F401 F403
from .hotstring import *  # noqa: F401 F403
from .key_state import *  # noqa: F401 F403
from .menu import *  # noqa: F401 F403
from .message_box import *  # noqa: F401 F403
from .mouse import *  # noqa: F401 F403
from .remap_key import *  # noqa: F401 F403
from .sending import *  # noqa: F401 F403
from .settings import *  # noqa: F401 F403
from .timer import *  # noqa: F401 F403
from .tooltip import *  # noqa: F401 F403
from .window import *  # noqa: F401 F403
from .window_message import *  # noqa: F401 F403

# Override modules with functions
hotkey = default_context.hotkey  # noqa: F405
remap_key = default_context.remap_key  # noqa: F405
hotstring = default_context.hotstring  # noqa: F405

__version__ = "0.2"
