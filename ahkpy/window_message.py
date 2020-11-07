import dataclasses as dc
from typing import Callable

from .flow import ahk_call

__all__ = [
    "MessageHandler",
    "on_message",
]


def on_message(msg_number: int, func=None, *, max_threads=1, prepend_handler=False):
    """Register *func* to be called on window message *msg_number*.

    Upon receiving a window message, the *func* will be called with the
    following positional arguments:

    :param w_param: the message's *wParam* value

    :param l_param: the message's *lParam* value

    :param msg: the message number, which is useful in cases where a function
       monitors more than one message

    :param hwnd: the HWND (unique ID) of the window or control to which the
       message was sent

    The optional *max_threads* argument sets the number of messages AHK can
    handle concurrently.

    If the optional *prepend_handler* argument is set to ``True``, the *func*
    will be registered to be called before any other functions previously
    registered for *msg_number*.

    If *func* is given, returns an instance of :class:`ahkpy.MessageHandler`.
    Otherwise, the function works as a decorator::

        WM_CLOSE = 0x0010

        @ahkpy.on_message(WM_CLOSE)
        def handler(w_param, l_param, msg, hwnd):
            print("was asked to close")

        assert isinstance(handler, ahkpy.MessageHandler)

    AutoHotkey function: `OnMessage
    <https://www.autohotkey.com/docs/commands/OnMessage.htm>`_.
    """
    if max_threads is not None and max_threads <= 0:
        raise ValueError("max_threads must be positive")

    if prepend_handler:
        max_threads *= -1

    def on_message_decorator(func):
        ahk_call("OnMessage", int(msg_number), func, max_threads)
        return MessageHandler(msg_number, func)

    if func is None:
        return on_message_decorator
    return on_message_decorator(func)


@dc.dataclass(frozen=True)
class MessageHandler:
    """This object holds a function registered to be called upon receiving a
    window message.

    Creating an instance of :class:`~!ahkpy.MessageHandler` doesn't register the
    function as a handler. Use the :func:`ahkpy.on_message` function instead.
    """

    # There's no point in making MessageHandler mutable like the Timer. It's
    # complicated and doesn't add any usability points.
    msg_number: int
    func: Callable
    __slots__ = ("msg_number", "func")

    def unregister(self):
        """Unregister the message handler."""
        ahk_call("OnMessage", self.msg_number, self.func, 0)
