from dataclasses import dataclass
from functools import partial
from typing import Callable

from .flow import ahk_call

__all__ = [
    "ClipboardHandler",
    "get_clipboard",
    "on_clipboard_change",
    "set_clipboard",
    "wait_clipboard",
]


def get_clipboard() -> str:
    """Get text from the Windows clipboard."""
    return ahk_call("GetClipboard")


def set_clipboard(value):
    """Put text into the Windows clipboard."""
    return ahk_call("SetClipboard", str(value))


def wait_clipboard(timeout: float = None) -> str:
    """Wait until the clipboard contains text and return it.

    If the optional *timeout* argument is given, then wait no longer than this
    many seconds. If the wait period expires and there's no text, return an
    empty string. If omitted, the function will wait indefinitely. Specifying 0
    is the same as specifying 0.5.
    """
    # TODO: Implement WaitForAnyData argument.
    if timeout is not None:
        timeout = float(timeout)
    timed_out = ahk_call("ClipWait", timeout)
    if timed_out:
        return ""
    return get_clipboard()


def on_clipboard_change(func: Callable = None, *args, prepend_handler=False):
    """Register *func* to be called on clipboard change.

    An instance of :class:`ClipboardHandler` is returned which can be used to
    unregister the function.

    The optional positional *args* will be passed to the *func* when it is
    called. If you want the callback to be called with keyword arguments use
    :func:`functools.partial`.

    An optional keyword-only *prepend_handler* argument registers the function
    before any previously registered functions.

    This function can be used as a decorator:

    .. code-block:: python

        @ahkpy.on_clipboard_change()
        def handler(clipboard):
            print(clipboard.upper())
    """
    option = 1 if not prepend_handler else -1

    def on_clipboard_change_decorator(func):
        wrapper = partial(_clipboard_handler, func, *args)
        ahk_call("OnClipboardChange", wrapper, option)
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
    __slots__ = ("func",)

    def unregister(self):
        """Unregister the clipboard handler and stop calling the function on
        clipboard change.
        """
        ahk_call("OnClipboardChange", self.func, 0)


# TODO: Implement ClipboardAll.
