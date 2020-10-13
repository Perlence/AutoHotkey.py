import dataclasses as dc
import functools
import queue
from typing import Callable, Optional

from .flow import Timer, ahk_call, global_ahk_lock, set_countdown
from .settings import COORD_MODES, _set_coord_mode
from .unset import UNSET

__all__ = [
    "MessageBox",
    "MessageHandler",
    "ToolTip",
    "message_box",
    "on_message",
]


MESSAGE_BOX_BUTTONS = {
    "ok": 0x00000000,
    "ok_cancel": 0x00000001,
    "abort_retry_ignore": 0x00000002,
    "yes_no_cancel": 0x00000003,
    "yes_no": 0x00000004,
    "retry_cancel": 0x00000005,
    "cancel_try_continue": 0x00000006,
}

MESSAGE_BOX_ICON = {
    None: 0x00000000,
    "hand": 0x00000010,
    "question": 0x00000020,
    "exclamation": 0x00000030,
    "asterisk": 0x00000040,
    "warning": 0x00000030,  # exclamation
    "error": 0x00000010,  # hand
    "information": 0x00000040,  # asterisk
    "info": 0x00000040,  # asterisk
    "stop": 0x00000010,  # hand
}

MESSAGE_BOX_DEFAULT_BUTTON = {
    1: 0x00000000,
    2: 0x00000100,
    3: 0x00000200,
}

MESSAGE_BOX_OPTIONS = {
    "default_desktop_only": 0x00020000,
    "right": 0x00080000,
    "rtl_reading": 0x00100000,
    "service_notification": 0x00200000,
}


@dc.dataclass
class MessageBox:
    # Inspired by Python's tkinter.messagebox module and Qt's QMessageBox class.

    text: Optional = None
    title: Optional = None
    buttons: str = "ok"
    icon: Optional[str] = None
    default_button: int = 1
    options: list = dc.field(default_factory=list)
    timeout: Optional[int] = None

    def show(self, text=None, title=None, **attrs):
        attrs["text"] = text if text is not None else self.text
        attrs["title"] = title if title is not None else self.title
        if attrs:
            self = dc.replace(self, **attrs)
        # MessageBox().show() must act exactly as message_box().
        return message_box(
            self.text,
            self.title,
            buttons=self.buttons,
            icon=self.icon,
            default_button=self.default_button,
            options=self.options,
            timeout=self.timeout,
        )

    @staticmethod
    def info(text, title=None, *, buttons="ok", default_button=1, options=[], timeout=None):
        """Show an info message."""
        return _message_box(text, title, buttons, "info", default_button, options, timeout)

    @staticmethod
    def warning(text, title=None, *, buttons="ok", default_button=1, options=[], timeout=None):
        """Show a warning message."""
        return _message_box(text, title, buttons, "warning", default_button, options, timeout)

    @staticmethod
    def error(text, title=None, *, buttons="ok", default_button=1, options=[], timeout=None):
        """Show an error message."""
        return _message_box(text, title, buttons, "error", default_button, options, timeout)

    @staticmethod
    def ok_cancel(text, title=None, *, icon="info", default_button=1, options=[], timeout=None):
        """Ask if operation should proceed; return True if the answer is ok.

        Not using the "question" icon because it's no longer recommended.
        https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox
        """
        result = _message_box(text, title, "ok_cancel", icon, default_button, options, timeout)
        if result is None:
            return None
        return result == "ok"

    @staticmethod
    def yes_no(text, title=None, *, icon="info", default_button=1, options=[], timeout=None):
        """Ask a question; return True if the answer is yes."""
        result = _message_box(text, title, "yes_no", icon, default_button, options, timeout)
        if result is None:
            return None
        return result == "yes"

    @staticmethod
    def yes_no_cancel(text, title=None, *, icon="info", default_button=1, options=[], timeout=None):
        return _message_box(text, title, "yes_no_cancel", icon, default_button, options, timeout)

    @staticmethod
    def retry_cancel(text, title=None, *, icon="warning", default_button=1, options=[], timeout=None):
        """Ask if operation should be retried; return True if the answer is yes.
        """
        result = _message_box(text, title, "retry_cancel", icon, default_button, options, timeout)
        if result is None:
            return None
        return result == "retry"

    @staticmethod
    def cancel_try_continue(text, title=None, *, icon="warning", default_button=2, options=[], timeout=None):
        """Ask if operation should be cancelled, retried, or continued.

        Using "cancel_try_continue" instead of "abort_retry_cancel" because it's
        more user-friendly.
        """
        return _message_box(text, title, "cancel_try_continue", icon, default_button, options, timeout)


def message_box(text=None, title=None, *, buttons="ok", icon=None, default_button=1, options=[], timeout=None):
    if text is None:
        if buttons == "ok" and icon is None:
            text = "Press OK to continue."
        else:
            text = ""

    return _message_box(text, title, buttons, icon, default_button, options, timeout)


def _message_box(text, title=None, buttons="ok", icon=None, default_button=1, options=[], timeout=None):
    buttons = MESSAGE_BOX_BUTTONS[buttons]
    icon = MESSAGE_BOX_ICON[icon]
    default_button = MESSAGE_BOX_DEFAULT_BUTTON[default_button]

    def option_reducer(result, option):
        return result | MESSAGE_BOX_OPTIONS[option]

    options = functools.reduce(option_reducer, options, 0)

    result = ahk_call(
        "MsgBox",
        buttons | icon | default_button | options,
        str(title) if title is not None else "",
        str(text),
        timeout,
    )
    if result == "timeout":
        return None
    return result


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
    # There's no point in making MessageHandler mutable like the Timer. It's
    # complicated and doesn't add any usability points.
    msg_number: int
    func: Callable
    __slots__ = ("msg_number", "func")

    def unregister(self):
        ahk_call("OnMessage", self.msg_number, self.func, 0)


@dc.dataclass
class ToolTip:
    text: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    relative_to: str = "window"
    timeout: Optional[float] = None

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

        self._id: Optional[int] = None
        self._timer: Optional[Timer] = None

    def show(self, text=None, x=UNSET, y=UNSET, relative_to=None, timeout=UNSET):
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
                self._timer = set_countdown(self.hide, timeout)
        elif self._timer:
            self._timer.stop()
            self._timer = None

    def hide(self):
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
