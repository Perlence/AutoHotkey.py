try:
    from _ahk import script_full_path  # noqa
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

    # TODO: Write a test for this.
    _sys.modules['_ahk'] = _shim()
    del _shim

from .clipboard import *  # noqa
from .exceptions import *  # noqa
from .flow import *  # noqa
from .gui import *  # noqa
from .keys import *  # noqa
from .window import *  # noqa

__version__ = "0.1.dev"
