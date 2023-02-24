import dataclasses as dc
import functools
from typing import Optional

from .flow import ahk_call

__all__ = [
    "MessageBox",
    "message_box",
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
    """MessageBox(text=None, title=None, buttons="ok", icon=None, default_button=1, options=[], timeout=None)

    The utility object to reuse and show message boxes.

    For information about the arguments refer to :func:`message_box`.

    The object can be used by setting the message box attributes and calling the
    :meth:`show` method::

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

    text: Optional[str] = None
    title: Optional[str] = None
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

    :param str text: the text to display in the message box. Defaults to "Press
       OK to continue.".

    :param str title: the title of the message box window. Defaults to the name
       of the AHK script (without path), that is, "Python.ahk".

    :param str buttons: the buttons to display in the message box. Defaults to
       OK button. Takes one of the following values:

       - ``"ok"``
       - ``"ok_cancel"``
       - ``"yes_no_cancel"``
       - ``"yes_no"``
       - ``"retry_cancel"``
       - ``"cancel_try_continue"``

    :param str icon: the icon to display. Defaults to no icon. Takes one of the
       following values:

       - ``None`` – no icon
       - ``"info"``, ``"information"``, ``"asterisk"`` – a symbol consisting of
         a lowercase letter *i* in a circle
       - ``"warning"``, ``"exclamation"`` – a symbol consisting of an
         exclamation point in a triangle with a yellow background
       - ``"error"``, ``"hand"``, ``"stop"`` – a symbol consisting of a white X
         in a circle with a red background

    :param int default_button: which button should be focused when the message
       box is shown. Defaults to the first button in the reading order. Takes
       integer values from 1 to 3.

    :param list[str] options: a list of zero or many of the following options:

       - ``"right"`` – the message box text is right-aligned
       - ``"rtl_reading"`` – specifies that the message box text is displayed
         with right to left reading order
       - ``"service_notification"`` – the message box is displayed on the active
         desktop
       - ``"default_desktop_only"`` – the message box is displayed on the active
         desktop. This is similar to ``"service_notification"``, except that the
         system displays the message box only on the default desktop of the
         interactive window station

    :param float timeout: specifies time in seconds to wait for user's response.
       After the timeout elapses, the message box will be automatically
       closed. If *timeout* is not specified or ``None``, there is no limit to
       the wait time.

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

    :command: `MsgBox <https://www.autohotkey.com/docs/commands/MsgBox.htm>`_
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
