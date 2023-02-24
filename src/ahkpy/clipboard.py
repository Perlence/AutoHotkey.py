import dataclasses as dc
import functools
from typing import Callable

from .flow import ahk_call, _wait_for, _wrap_callback

__all__ = [
    "ClipboardHandler",
    "get_clipboard",
    "on_clipboard_change",
    "set_clipboard",
    "wait_clipboard",
]


def get_clipboard() -> str:
    """Get text from the Windows clipboard.

    :variable: `Clipboard
       <https://www.autohotkey.com/docs/misc/Clipboard.htm>`_
    """
    return str(ahk_call("GetVar", "Clipboard"))


def set_clipboard(value):
    """Put text into the Windows clipboard.

    :variable: `Clipboard
       <https://www.autohotkey.com/docs/misc/Clipboard.htm>`_
    """
    return ahk_call("SetVar", "Clipboard", str(value))


def wait_clipboard(timeout: float = None) -> str:
    """Wait until the clipboard contains text and return it.

    If there is no text in the clipboard after *timeout* seconds, then an empty
    string will be returned. If *timeout* is not specified or ``None``, there is
    no limit to the wait time.

    :command: `ClipWait
       <https://www.autohotkey.com/docs/commands/ClipWait.htm>`_
    """
    # TODO: Implement WaitForAnyData argument.
    return _wait_for(timeout, get_clipboard) or ""


def on_clipboard_change(func: Callable = None, *args, prepend_handler=False):
    """Register *func* to be called on clipboard change.

    On clipboard change, *func* will be called with the clipboard text as the
    *clipboard* argument.

    The optional positional *args* will be passed to the *func* when it is
    called. If you want the callback to be called with keyword arguments use
    :func:`functools.partial`.

    If the optional *prepend_handler* argument is set to ``True``, the *func*
    will be registered to be called before any other previously registered
    functions.

    If *func* returns true, then the other clipboard handlers won't be called.

    If *func* is given, returns an instance of :class:`ClipboardHandler`.
    Otherwise, the function works as a decorator::

        @ahkpy.on_clipboard_change()
        def handler(clipboard):
            print(clipboard.upper())

        assert isinstance(handler, ahkpy.ClipboardHandler)

    :command: `OnClipboardChange
       <https://www.autohotkey.com/docs/commands/OnClipboardChange.htm>`_
    """
    option = 1 if not prepend_handler else -1

    def on_clipboard_change_decorator(func):
        func = _wrap_callback(
            functools.partial(func, *args),
            ("clipboard",),
            _bare_clipboard_handler,
            _clipboard_handler,
        )
        ahk_call("OnClipboardChange", func, option)
        return ClipboardHandler(func)

    if func is None:
        return on_clipboard_change_decorator
    return on_clipboard_change_decorator(func)


def _bare_clipboard_handler(func, *_):
    return bool(func())


def _clipboard_handler(func, typ):
    if typ == 0:
        return bool(func(clipboard=""))
    elif typ == 1:
        return bool(func(clipboard=get_clipboard()))
    elif typ == 2:
        # TODO: Return ClipboardAll.
        return bool(func(clipboard=get_clipboard()))


@dc.dataclass(frozen=True)
class ClipboardHandler:
    """This immutable object holds a function registered to be called on
    clipboard change.

    Creating an instance of :class:`!ClipboardHandler` doesn't register the
    function as a handler. Use the :func:`on_clipboard_change` function instead.
    """

    func: Callable
    __slots__ = ("func",)

    def unregister(self):
        """Unregister the clipboard handler and stop calling the function on
        clipboard change.
        """
        ahk_call("OnClipboardChange", self.func, 0)


# TODO: Implement ClipboardAll.
