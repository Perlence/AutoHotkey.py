import dataclasses as dc
import queue
from typing import Callable, Optional

from .flow import ahk_call, global_ahk_lock

__all__ = [
    "MessageHandler",
    "ToolTip",
    "message_box",
    "on_message",
]


UNSET = object()

COORD_MODES = {"screen", "window", "client"}


def message_box(text=None, title="", options=0, timeout=None):
    if text is None:
        # Show "Press OK to continue."
        return ahk_call("MsgBox")

    return ahk_call("MsgBox", options, title, str(text), timeout)
    # XXX: Return result of IfMsgBox?


def on_message(msg_number, func=None, *, max_threads=1, prepend_handler=False):
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
    msg_number: int
    func: Callable
    __slots__ = ("msg_number", "func")

    def unregister(self):
        # TODO: Remove self.func from CALLBACKS and WRAPPED_PYTHON_FUNCTIONS in AHK.
        ahk_call("OnMessage", self.msg_number, self.func, 0)


@dc.dataclass
class ToolTip:
    text: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    relative_to: str = "window"
    _id: Optional[int] = dc.field(default=None, init=False, repr=False)

    _pool = queue.LifoQueue(maxsize=20)
    for tooltip_id in range(20, 0, -1):
        _pool.put(tooltip_id)
    del tooltip_id

    def __init__(self, text=None, x=None, y=None, relative_to="window"):
        # Write the __init__ method for code suggestions.
        self.text = text
        self.x = x
        self.y = y
        if relative_to not in COORD_MODES:
            raise ValueError(f"{relative_to!r} is not a valid coord mode")
        self.relative_to = relative_to

    def show(self, text=None, x=UNSET, y=UNSET, relative_to=None):
        if not text and not self.text:
            raise ValueError("text must not be empty")
        elif text:
            self.text = text

        if x is not UNSET:
            self.x = x
        if y is not UNSET:
            self.y = y
        x = self.x if self.x is not None else ""
        y = self.y if self.y is not None else ""

        if relative_to is not None:
            self.relative_to = relative_to
        if self.relative_to not in COORD_MODES:
            raise ValueError(f"{relative_to!r} is not a valid coord mode")

        tooltip_id = self._acquire()
        with global_ahk_lock:
            ahk_call("CoordMode", "ToolTip", self.relative_to)
            ahk_call("ToolTip", str(self.text), x, y, tooltip_id)

    def hide(self):
        if self._id is None:
            return
        ahk_call("ToolTip", "", "", "", self._id)
        self._release()

    def _acquire(self):
        if self._id is None:
            try:
                self._id = ToolTip._pool.get_nowait()
            except queue.Empty:
                raise RuntimeError("cannot show more than 20 tooltips simultaneously") from None
        return self._id

    def _release(self):
        if self._id is None:
            return
        try:
            ToolTip._pool.put_nowait(self._id)
        except queue.Full:
            raise RuntimeError("tooltip pool is corrupted") from None
        self._id = None
