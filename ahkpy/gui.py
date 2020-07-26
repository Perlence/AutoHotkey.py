from dataclasses import dataclass
from typing import Callable

import _ahk  # noqa

__all__ = [
    "MessageHandler",
    "message_box",
    "on_message",
]


def message_box(text=None, title="", options=0, timeout=None):
    if text is None:
        # Show "Press OK to continue."
        return _ahk.call("MsgBox")

    return _ahk.call("MsgBox", options, title, str(text), timeout)
    # XXX: Return result of IfMsgBox?


def on_message(msg_number, func=None, *, max_threads=1, prepend_handler=False):
    if max_threads is not None and max_threads <= 0:
        raise ValueError("max_threads must be positive")

    if prepend_handler:
        max_threads *= -1

    def on_message_decorator(func):
        _ahk.call("OnMessage", int(msg_number), func, max_threads)
        return MessageHandler(msg_number, func)

    if func is None:
        return on_message_decorator
    return on_message_decorator(func)


@dataclass(frozen=True)
class MessageHandler:
    msg_number: int
    func: Callable
    __slots__ = tuple(__annotations__.keys())

    def disable(self):
        _ahk.call("OnMessage", self.msg_number, self.func, 0)


def tooltip():
    # TODO: Implement tooltips.
    raise NotImplementedError()
