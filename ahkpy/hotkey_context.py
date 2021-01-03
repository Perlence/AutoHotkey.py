import dataclasses as dc
import functools
from contextlib import contextmanager
from typing import Callable, Optional, Union

from .hotkey import hotkey as _hotkey
from .hotstring import hotstring as _hotstring
from .remap_key import remap_key as _remap_key
from .flow import ahk_call, global_ahk_lock, _wrap_callback

__all__ = [
    "HotkeyContext",
    "default_context",
    "hotkey",
    "hotstring",
    "remap_key",
]


@dc.dataclass(frozen=True)
class HotkeyContext:
    """The hotkey, hotstring, and key remappings immutable factory.

    If the *active_when* argument is a callable, it is executed every time the
    user triggers the hotkey or hotstring. The callable takes either zero
    arguments or a *hot_id* argument. The argument is the identifier of the
    triggered utility. For hotkeys, the identifier will be the *key_name* of the
    :class:`~ahkpy.Hotkey` that was pressed by the user. For hotstrings, the
    identifier will be the full AutoHotkey hotstring with packed options. The
    hotkey/hotstring action is executed only if the callable returns ``True``.

    The optional positional *args* will be passed to the *active_when* when it
    is called. If you want the *active_when* to be called with keyword arguments
    use :func:`functools.partial`.

    In the following example pressing the :kbd:`F1` key shows the message only
    when the mouse cursor is over the taskbar::

        def is_mouse_over_taskbar():
            return ahkpy.get_window_under_mouse().class_name == "Shell_TrayWnd"

        ctx = ahkpy.HotkeyContext(is_mouse_over_taskbar)
        ctx.hotkey("F1", ahkpy.message_box, "Pressed F1 over the taskbar.")

    :command: `Hotkey, If, % FunctionObject
       <https://www.autohotkey.com/docs/commands/Hotkey.htm#IfFn>`_
    """

    active_when: Optional[Callable]
    __slots__ = ("active_when",)

    # TODO: Consider adding context options: MaxThreadsBuffer,
    # MaxThreadsPerHotkey, and InputLevel.

    def __init__(self, active_when: Callable = None, *args):
        if active_when is None:
            object.__setattr__(self, "active_when", None)
            return

        active_when = _wrap_callback(
            functools.partial(active_when, *args),
            ("hotkey",),
            _bare_predicate,
            _predicate,
        )
        object.__setattr__(self, "active_when", active_when)

    # Copy arguments verbatim to make Pylance's suggestions work. Use
    # functools.wraps so that the API docs are generated.

    @functools.wraps(_hotkey)
    def hotkey(
        self,
        key_name: str,
        func: Callable = None,
        *args,
        buffer=False,
        priority=0,
        max_threads=1,
        input_level=0,
    ):
        return _hotkey(
            self,
            key_name,
            func,
            *args,
            buffer=buffer,
            priority=priority,
            max_threads=max_threads,
            input_level=input_level,
        )

    @functools.wraps(_remap_key)
    def remap_key(self, origin_key, destination_key, *, mode=None, level=None):
        return _remap_key(self, origin_key, destination_key, mode=mode, level=level)

    @functools.wraps(_hotstring)
    def hotstring(
        self,
        trigger: str,
        repl: Union[str, Callable] = None,
        *args,
        case_sensitive=False,
        conform_to_case=True,
        replace_inside_word=False,
        wait_for_end_char=True,
        omit_end_char=False,
        backspacing=True,
        priority=0,
        text=False,
        mode=None,
        key_delay=None,
        reset_recognizer=False,
    ):
        return _hotstring(
            self,
            trigger,
            repl,
            *args,
            case_sensitive=case_sensitive,
            conform_to_case=conform_to_case,
            replace_inside_word=replace_inside_word,
            wait_for_end_char=wait_for_end_char,
            omit_end_char=omit_end_char,
            backspacing=backspacing,
            priority=priority,
            text=text,
            mode=mode,
            key_delay=key_delay,
            reset_recognizer=reset_recognizer,
        )

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
        if self.active_when is not None:
            ahk_call("HotkeyContext", self.active_when)

    def _exit(self):
        if self.active_when is not None:
            ahk_call("HotkeyExitContext")


def _bare_predicate(func, *_):
    return bool(func())


def _predicate(func, hot_id):
    return bool(func(hot_id=hot_id))


default_context = HotkeyContext()
hotkey = default_context.hotkey
remap_key = default_context.remap_key
hotstring = default_context.hotstring
