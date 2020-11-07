import dataclasses as dc
import functools
import queue
from typing import Callable, Optional

from .flow import ahk_call, global_ahk_lock
from .settings import COORD_MODES, _set_coord_mode
from .timer import Timer, set_countdown
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
    """The utility object to reuse and show message boxes.

    For information about the arguments refer to :func:`ahkpy.message_box`.

    The object can be used by setting the message box attributes and calling the
    :func:`~ahkpy.MessageBox.show` method::

        mb = ahkpy.MessageBox(text="hello")  # Doesn't show the message box yet
        mb.text = "hello from attribute"
        mb.show()  # Shows a message box with the text "hello from attribute"
        mb.show(text="hello from keyword argument")
        # ^^ Shows a message box with the text "hello from keyword argument"

    Also, the class can be used by calling its static methods::

        ahkpy.MessageBox.info("hello from the static method")
        # ^^ Shows a message box with the "info" icon
    """

    # Inspired by Python's tkinter.messagebox module and Qt's QMessageBox class.

    text: Optional = None
    title: Optional = None
    buttons: str = "ok"
    icon: Optional[str] = None
    default_button: int = 1
    options: list = dc.field(default_factory=list)
    timeout: Optional[int] = None

    def show(self, text=None, title=None, **attrs):
        """Show the message box with the given attributes."""
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
    def info(text, title=None, *, buttons="ok", default_button=1, options=[], timeout=None) -> Optional[str]:
        """info(text, title=None, *, buttons="ok", default_button=1, **attrs)

        Show an info message.
        """
        return _message_box(text, title, buttons, "info", default_button, options, timeout)

    @staticmethod
    def warning(text, title=None, *, buttons="ok", default_button=1, options=[], timeout=None) -> Optional[str]:
        """warning(text, title=None, *, buttons="ok", default_button=1, **attrs)

        Show a warning message.
        """
        return _message_box(text, title, buttons, "warning", default_button, options, timeout)

    @staticmethod
    def error(text, title=None, *, buttons="ok", default_button=1, options=[], timeout=None) -> Optional[str]:
        """error(text, title=None, *, buttons="ok", default_button=1, **attrs)

        Show an error message.
        """
        return _message_box(text, title, buttons, "error", default_button, options, timeout)

    @staticmethod
    def ok_cancel(text, title=None, *, icon="info", default_button=1, options=[], timeout=None) -> Optional[bool]:
        """ok_cancel(text, title=None, *, icon="info", default_button=1, **attrs)

        Ask if operation should proceed; return ``True`` if the answer is ok.
        """
        # Not using the "question" icon because it's no longer recommended.
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox
        result = _message_box(text, title, "ok_cancel", icon, default_button, options, timeout)
        if result is None:
            return None
        return result == "ok"

    @staticmethod
    def yes_no(text, title=None, *, icon="info", default_button=1, options=[], timeout=None) -> Optional[bool]:
        """yes_no(text, title=None, *, icon="info", default_button=1, **attrs)

        Ask a question; return ``True`` if the answer is yes.
        """
        result = _message_box(text, title, "yes_no", icon, default_button, options, timeout)
        if result is None:
            return None
        return result == "yes"

    @staticmethod
    def yes_no_cancel(text, title=None, *, icon="info", default_button=1, options=[], timeout=None) -> Optional[str]:
        """yes_no_cancel(text, title=None, *, icon="info", default_button=1, **attrs)

        Ask a question; return ``"yes"``, ``"no"``, or ``"cancel"``.
        """
        return _message_box(text, title, "yes_no_cancel", icon, default_button, options, timeout)

    @staticmethod
    def retry_cancel(text, title=None, *, icon="warning", default_button=1, options=[], timeout=None) -> Optional[bool]:
        """retry_cancel(text, title=None, *, icon="warning", default_button=1, **attrs)

        Ask if operation should be retried; return ``True`` if the answer is
        yes.
        """
        result = _message_box(text, title, "retry_cancel", icon, default_button, options, timeout)
        if result is None:
            return None
        return result == "retry"

    @staticmethod
    def cancel_try_continue(text, title=None, *,
                            icon="warning", default_button=2, options=[], timeout=None) -> Optional[str]:
        """cancel_try_continue(text, title=None, *, icon="warning", default_button=2, **attrs)

        Ask a question; return ``"cancel"``, ``"try"``, or ``"continue"``.
        """
        # Using "cancel_try_continue" instead of "abort_retry_cancel" because
        # it's more user-friendly.
        return _message_box(text, title, "cancel_try_continue", icon, default_button, options, timeout)


def message_box(text=None, title=None, *,
                buttons="ok", icon=None, default_button=1, options=[], timeout=None) -> Optional[str]:
    """Display the specified *text* in a small window containing one or more
    buttons.

    :param text: the text to display in the message box. Defaults to "Press OK
       to continue.".

    :param title: the title of the message box window. Defaults to the name of
       the AHK script (without path), that is, "Python.ahk".

    :param buttons: the buttons to display in the message box. Defaults to OK
       button. The following values are allowed:

       - ``"ok"``
       - ``"ok_cancel"``
       - ``"yes_no_cancel"``
       - ``"yes_no"``
       - ``"retry_cancel"``
       - ``"cancel_try_continue"``

    :param icon: the icon to display. Defaults to no icon. The following values
       are allowed:

       - ``None``: no icon
       - ``"info"``, ``"information"``, ``"asterisk"``: a symbol consisting of a
         lowercase letter *i* in a circle
       - ``"warning"``, ``"exclamation"``: a symbol consisting of an exclamation
         point in a triangle with a yellow background
       - ``"error"``, ``"hand"``, ``"stop"``: a symbol consisting of a white X
         in a circle with a red background

    :param default_button: which button should be focused when the message box
       is shown. Defaults to the first button in the reading order. Takes
       :class:`int` values from 1 to 3.

    :param options: a list of zero or many additional options. The following
       values are allowed:

       - ``"right"``: the message box text is right-aligned
       - ``"rtl_reading"``: specifies that the message box text is displayed
         with right to left reading order
       - ``"service_notification"``: the message box is displayed on the active
         desktop
       - ``"default_desktop_only"``: the message box is displayed on the active
         desktop. This is similar to ``"service_notification"``, except that the
         system displays the message box only on the default desktop of the
         interactive window station

    :param timeout: specifies time in seconds to wait for user's response. After
       the timeout has elapsed, the message box will be automatically closed. If
       *timeout* is omitted, waits indefinitely.

    :return: ``None`` if the timeout has elapsed, or one of the following values
       that signify the button the user has pressed:

       - ``"ok"``
       - ``"yes"``
       - ``"no"``
       - ``"cancel"``
       - ``"abort"``
       - ``"ignore"``
       - ``"retry"``
       - ``"continue"``
       - ``"try_again"``

    AutoHotkey command: `MsgBox
    <https://www.autohotkey.com/docs/commands/MsgBox.htm>`_.
    """
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

        The *text* argument is required either to be set as the instance
        attribute, or passed as an argument.

        The optional *x* and *y* arguments set the position of the tooltip
        relative to the area, specified by the *relative_to* argument which
        defaults to ``"window"``. The valid *relative_to* arguments are the
        following:

        - ``"screen"``: coordinates are relative to the desktop (entire screen).
        - ``"window"``: coordinates are relative to the active window.
        - ``"client"``: coordinates are relative to the active window's client
          area, which excludes the window's title bar, menu (if it has a
          standard one) and borders. Client coordinates are less dependent on OS
          version and theme.

        If the *x* or *y* coordinate is omitted, the tooltip will take the
        missing coordinate from the mouse cursor.

        If the optional *timeout* argument is given, the tooltip will be hidden
        after this many seconds.

        AutoHotkey command: `ToolTip
        <https://www.autohotkey.com/docs/commands/ToolTip.htm>`_.
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
