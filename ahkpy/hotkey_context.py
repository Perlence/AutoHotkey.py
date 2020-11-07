import dataclasses as dc
import functools
import inspect
from contextlib import contextmanager
from typing import Callable

from . import hotkeys
from . import hotstrings
from . import remap
from .flow import ahk_call, global_ahk_lock

__all__ = [
    "HotkeyContext",
    "default_context",
    "hotkey",
    "hotstring",
    "remap_key",
]


@dc.dataclass(frozen=True)
class HotkeyContext:
    """The hotkey, hotstring, and key remappings factory.

    If the *predicate* argument is a callable, it is executed every time the
    user presses the hotkey or triggers the hotstring. The predicate takes
    either zero or one positional argument. In case of latter, the predicate
    will be called with the identifier of the triggered utility: *key_name* of
    the :class:`~ahkpy.Hotkey` that was pressed by the user or the full
    AutoHotkey hotstring with packed options. If the predicate returns ``True``,
    the hotkey/hotstring is executed. Otherwise, the original key is propagated
    to the system in the case of a hotkey.

    .. TODO: ^^ Quite a mouthful.

    In the following example pressing the :kbd:`F1` key shows the message only
    when the mouse cursor is over the taskbar::

        def is_mouse_over_taskbar():
            return ahkpy.get_window_under_mouse().class_name == "Shell_TrayWnd"

        ctx = ahkpy.HotkeyContext(is_mouse_over_taskbar)
        ctx.hotkey("F1", ahkpy.message_box, "Pressed F1 over the taskbar.")

    AutoHotkey command: `Hotkey, If, % FunctionObject
    <https://www.autohotkey.com/docs/commands/Hotkey.htm#IfFn>`_.
    """

    predicate: Callable
    __slots__ = ("predicate",)

    # TODO: Consider adding context options: MaxThreadsBuffer,
    # MaxThreadsPerHotkey, and InputLevel.

    def __init__(self, predicate=None):
        if predicate is None:
            object.__setattr__(self, "predicate", None)
            return

        signature = inspect.signature(predicate)
        if len(signature.parameters) == 0:
            def wrapped_predicate(hotkey):
                return bool(predicate())
        else:
            def wrapped_predicate(hotkey):
                return bool(predicate(hotkey))

        wrapped_predicate = functools.wraps(predicate)(wrapped_predicate)
        object.__setattr__(self, "predicate", wrapped_predicate)

    hotkey = hotkeys.hotkey
    remap_key = remap.remap_key
    hotstring = hotstrings.hotstring

    @contextmanager
    def _manager(self):
        # I don't want to make HotkeyContext a Python context manager, because
        # the end users will be tempted to use it as such, e.g:
        #
        #     with hotkey_context(lambda: ...):
        #         hotkey(...)
        #
        # This approach has a number of issues that can be mitigated, but better
        # be avoided:
        #
        # 1. Current context must be stored in a thread-local storage in order
        #    to be referenced by hotkey(). This can be solved by returning the
        #    context as `with ... as ctx`.
        # 2. Nested contexts become possible, but implementing them is not
        #    trivial.
        #
        # Instead, the following is the chosen way to use the hotkey contexts:
        #
        #     ctx = hotkey_context(lambda: ...)
        #     ctx.hotkey(...)

        with global_ahk_lock:
            self._enter()
            try:
                yield
            finally:
                self._exit()

    def _enter(self):
        if self.predicate is not None:
            ahk_call("HotkeyContext", self.predicate)

    def _exit(self):
        if self.predicate is not None:
            ahk_call("HotkeyExitContext")


default_context = HotkeyContext()
hotkey = default_context.hotkey
remap_key = default_context.remap_key
hotstring = default_context.hotstring
