import dataclasses as dc
import queue
from typing import Optional

from .flow import ahk_call, global_ahk_lock
from .settings import COORD_MODES, _set_coord_mode
from .timer import Timer, set_countdown
from .unset import UNSET

__all__ = [
    "ToolTip",
]


@dc.dataclass
class ToolTip:
    """The tooltip object.

    No more than 20 tooltips can be shown simultaneously.

    Example usage::

        tt = ToolTip(text="hello")  # Doesn't show the tooltip yet
        tt.text = "hello from attribute"
        tt.show()
        # ^^ Shows a tooltip with the text "hello from attribute" near the mouse
        # cursor
        tt.show(text="hello from keyword argument")
        # ^^ Hides the previous tooltip and shows a new one with the text "hello
        # from keyword argument" near the mouse cursor
    """

    text: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    relative_to: str = "window"
    timeout: Optional[float] = None

    _pool = queue.LifoQueue(maxsize=20)
    for tooltip_id in range(20, 0, -1):
        _pool.put(tooltip_id)
    del tooltip_id

    def __init__(self, text=None, *, x=None, y=None, relative_to="window", timeout=None):
        self.text = text
        self.x = x
        self.y = y
        if relative_to not in COORD_MODES:
            raise ValueError(f"{relative_to!r} is not a valid coord mode")
        self.relative_to = relative_to

        self._id: Optional[int] = None
        self._timer: Optional[Timer] = None

    def show(self, text=None, *, x=UNSET, y=UNSET, relative_to=None, timeout=UNSET):
        """Show the tooltip.

        If the method is called without the *x* and *y* arguments, the menu is
        shown at the mouse cursor.

        Otherwise, the tooltip's position depends on the *relative_to* argument.
        Valid *relative_to* values are:

        - ``"screen"`` – coordinates are relative to the desktop (entire
          screen).
        - ``"window"`` – coordinates are relative to the active window.
        - ``"client"`` – coordinates are relative to the active window's client
          area, excluding title bar, menu and borders.

        The optional *x* and *y* arguments set the tooltip's position relative
        to the area specified by the *relative_to* argument. The default
        *relative_to* value is ``"window"``. So if you call
        ``tooltip.show("hello", x=42)``, the *y* coordinate will be the mouse
        cursor's *y* coordinate, and the *x* coordinate will be 42 pixels to the
        right of the active window.

        The *text* argument is required to either be set as the instance
        attribute, or passed as an argument.

        If the optional *timeout* argument is given, the tooltip will be hidden
        after this many seconds.

        :command: `ToolTip
           <https://www.autohotkey.com/docs/commands/ToolTip.htm>`_
        """
        if not text and not self.text:
            raise ValueError("text must not be empty")
        elif not text:
            text = self.text

        if x is UNSET:
            x = self.x
        if y is UNSET:
            y = self.y
        x = x if x is not None else ""
        y = y if y is not None else ""

        if relative_to is None:
            relative_to = self.relative_to

        tooltip_id = self._acquire()
        with global_ahk_lock:
            _set_coord_mode("tooltip", relative_to)
            ahk_call("ToolTip", str(text), x, y, tooltip_id)

        if timeout is UNSET:
            timeout = self.timeout
        if timeout is not None:
            if self._timer:
                self._timer.start(timeout)
            else:
                self._timer = set_countdown(timeout, self.hide)
        elif self._timer:
            self._timer.stop()
            self._timer = None

    def hide(self):
        """Hide the tooltip."""
        if self._id is None:
            return
        ahk_call("ToolTip", "", "", "", self._id)
        if self._timer:
            self._timer.stop()
            self._timer = None
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
