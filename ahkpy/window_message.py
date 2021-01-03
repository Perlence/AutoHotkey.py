import dataclasses as dc
import functools
from typing import Callable

from .flow import ahk_call, _wrap_callback

__all__ = [
    "MessageHandler",
    "on_message",
]


def on_message(msg_number: int, func=None, *args, max_threads=1, prepend_handler=False):
    """Register *func* to be called on window message *msg_number*.

    Upon receiving a window message, the *func* will be called with the
    following arguments:

    :param int w_param: the message's *wParam* value

    :param int l_param: the message's *lParam* value

    :param int msg: the message number, which is useful in cases where a
       function monitors more than one message

    :param int hwnd: the HWND (unique ID) of the window or control to which the
       message was sent

    The optional positional *args* will be passed to the *func* when it is
    called. If you want the callback to be called with keyword arguments use
    :func:`functools.partial`.

    The optional *max_threads* argument sets the number of messages AHK can
    handle concurrently.

    If the optional *prepend_handler* argument is set to ``True``, the *func*
    will be registered to be called before any other functions previously
    registered for *msg_number*.

    If *func* is given, returns an instance of :class:`MessageHandler`.
    Otherwise, the function works as a decorator::

        WM_CLOSE = 0x0010

        @ahkpy.on_message(WM_CLOSE)
        def handler(w_param, l_param, msg, hwnd):
            print("was asked to close")

        assert isinstance(handler, ahkpy.MessageHandler)

    :command: `OnMessage
       <https://www.autohotkey.com/docs/commands/OnMessage.htm>`_
    """
    if max_threads is not None and max_threads <= 0:
        raise ValueError("max_threads must be positive")

    if prepend_handler:
        max_threads *= -1

    def on_message_decorator(func):
        func = _wrap_callback(
            functools.partial(func, *args),
            ("w_param", "l_param", "msg", "hwnd"),
            _bare_message_handler,
            _message_handler,
        )
        ahk_call("OnMessage", int(msg_number), func, max_threads)
        return MessageHandler(msg_number, func)

    if func is None:
        return on_message_decorator
    return on_message_decorator(func)


def _bare_message_handler(func, *_):
    return func()


def _message_handler(func, w_param, l_param, msg, hwnd):
    return func(w_param=w_param, l_param=l_param, msg=msg, hwnd=hwnd)


@dc.dataclass(frozen=True)
class MessageHandler:
    """This immutable object holds a function registered to be called upon
    receiving a window message.

    Creating an instance of :class:`!MessageHandler` doesn't register the
    function as a handler. Use the :func:`on_message` function instead.
    """

    # There's no point in making MessageHandler mutable like the Timer. It's
    # complicated and doesn't add any usability points.
    msg_number: int
    func: Callable
    __slots__ = ("msg_number", "func")

    def unregister(self):
        """Unregister the message handler."""
        ahk_call("OnMessage", self.msg_number, self.func, 0)
