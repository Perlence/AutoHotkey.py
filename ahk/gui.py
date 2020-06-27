from dataclasses import dataclass
from functools import partial
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
    # TODO: Return result of IfMsgBox?


def on_message(msg_number, func=None, *, max_threads=1, prepend_handler=False):
    if func is None:
        return partial(on_message, msg_number, max_threads=max_threads, prepend_handler=prepend_handler)

    if max_threads is not None and max_threads <= 0:
        raise ValueError("max_threads must be positive")

    if prepend_handler:
        max_threads *= -1

    _ahk.call("OnMessage", int(msg_number), func, max_threads)
    return MessageHandler(msg_number, func)


@dataclass(frozen=True)
class MessageHandler:
    msg_number: int
    func: Callable

    def disable(self):
        _ahk.call("OnMessage", self.msg_number, self.func, 0)


def tooltip():
    # TODO: Implement tooltips.
    raise NotImplementedError()
