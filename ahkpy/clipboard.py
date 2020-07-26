from dataclasses import dataclass
from functools import partial
from typing import Callable

import _ahk  # noqa

__all__ = [
    "ClipboardHandler",
    "get_clipboard",
    "on_clipboard_change",
    "set_clipboard",
    "wait_clipboard",
]


def get_clipboard():
    return _ahk.call("GetClipboard")


def set_clipboard(value):
    return _ahk.call("SetClipboard", str(value))


def wait_clipboard(timeout=None):
    # TODO: Implement WaitForAnyData argument.
    if timeout is not None:
        timeout = float(timeout)
    timed_out = _ahk.call("ClipWait", timeout)
    if timed_out:
        return ""
    return get_clipboard()


def on_clipboard_change(func=None, *, prepend_handler=False):
    option = 1 if not prepend_handler else -1

    def on_clipboard_change_decorator(func):
        wrapper = partial(_clipboard_handler, func)
        _ahk.call("OnClipboardChange", wrapper, option)
        return ClipboardHandler(wrapper)

    if func is None:
        return on_clipboard_change_decorator
    return on_clipboard_change_decorator(func)


def _clipboard_handler(func, typ):
    if typ == 0:
        return func("")
    elif typ == 1:
        return func(get_clipboard())
    elif typ == 2:
        # TODO: Return ClipboardAll.
        return func(get_clipboard())


@dataclass(frozen=True)
class ClipboardHandler:
    func: Callable
    __slots__ = tuple(__annotations__.keys())

    def disable(self):
        # TODO: Remove self.func from CALLBACKS and WRAPPED_PYTHON_FUNCTIONS in AHK.
        _ahk.call("OnClipboardChange", self.func, 0)


# TODO: Implement ClipboardAll.
