from typing import Tuple

from .flow import ahk_call, global_ahk_lock
from .sending import send
from .settings import _set_coord_mode, get_settings
from .unset import UNSET
from .window import Control, Window

__all__ = [
    "click",
    "double_click",
    "get_control_under_mouse",
    "get_cursor_type",
    "get_mouse_pos",
    "get_window_under_mouse",
    "mouse_move",
    "mouse_press",
    "mouse_release",
    "mouse_scroll",
    "right_click",
]

# Not implementing MouseClickDrag and passing coordinates in Click because it
# complicates the signature. Use separate commands instead.
#
# MouseClickDrag:
#
#     ahkpy.mouse_move(x=x1, y=y1)
#     ahkpy.mouse_press(which_button)
#     ahkpy.mouse_move(x=x2, y=y2, speed=speed, relative_to=...)
#     ahkpy.mouse_release()
#
# Click with coordinates:
#
#     ahkpy.mouse_move(x=x, y=y, speed=speed)
#     ahkpy.click()


KEY_DOWN = 0
KEY_UP = 1
KEY_DOWN_AND_UP = 2
BUTTONS = {"left", "right", "middle", "x1", "x2"}
SCROLL_DIRECTIONS = {"up", "down", "left", "right"}
MODIFIERS = set("!+^#")


def click(button="left", times=1, *, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    """click(button="left", times=1, **options)

    Click a mouse button.

    The *button* argument takes one of the following values: ``"left"``,
    ``"right"``, ``"middle"``, ``"x1"``, ``"x2"``.

    The *times* argument specifies the number of times to click the mouse.

    .. :param str button: the mouse button to click. Takes one of the following
       values: ``"left"``, ``"right"``, ``"middle"``, ``"x1"``, ``"x2"``.
       Defaults to ``"left"``.

    .. :param int times: the number of times to click the mouse. Defaults to 1.

    The following keyword-only arguments set the click *options*:

    :param str modifier: the string of AHK characters that represent the
       keyboard modifiers to press down before clicking the mouse. Takes a
       combination of the following characters: ``!+^#`` which correspond to
       :kbd:`Alt`, :kbd:`Shift`, :kbd:`Ctrl`, and :kbd:`Win`. Defaults to no
       modifiers.

    :param bool blind: if true, preserves the keyboard modifiers in the down
       position. For example, calling :func:`!click` with :kbd:`Ctrl` held down
       will send a :kbd:`Ctrl` + :kbd:`Click`. If false, releases the currently
       held keyboard modifiers before the click. Defaults to ``True``.

    :param str mode: the mode that is used to send the clicks. For more
       information refer to the *mode* argument of the :func:`send` function.

    :param int level: controls which artificial keyboard and mouse events are
       ignored by hotkeys and hotstrings. For more information refer to the
       *level* argument of the :func:`send` function.

    :param float delay: the delay after each mouse click. For more information
       refer to the *mouse_delay* argument of the :func:`send` function.

    :command: `Send, {Click}
       <https://www.autohotkey.com/docs/commands/Send.htm#Click>`_
    """
    _click(button, times, KEY_DOWN_AND_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def right_click(times=1, *, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    """right_click(times=1, **options)

    Click the right mouse button.

    For arguments refer to :func:`click`.
    """
    _click("right", times, KEY_DOWN_AND_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def double_click(button="left", *, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    """double_click(button="left", **options)

    Double-click a mouse button.

    For arguments refer to :func:`click`.
    """
    _click(button, 2, KEY_DOWN_AND_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def mouse_press(button="left", times=1, *, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    """mouse_press(button="left", times=1, **options)

    Press down and hold a mouse button.

    For arguments refer to :func:`click`.
    """
    _click(button, times, KEY_DOWN, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def mouse_release(button="left", times=1, *, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    """mouse_release(button="left", times=1, **options)

    Release a mouse button.

    For arguments refer to :func:`click`.
    """
    _click(button, times, KEY_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def _click(button, times, event_type, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    args = []

    if button not in BUTTONS:
        raise ValueError(f"{button!r} is not a valid mouse button")
    args.append(button)

    if event_type == KEY_DOWN:
        args.append("down")
    elif event_type == KEY_UP:
        args.append("up")
    elif event_type == KEY_DOWN_AND_UP:
        pass
    else:
        raise ValueError(f"{event_type!r} is not a valid event type")

    if times < 0:
        raise ValueError("times must be positive")
    args.append(str(times))

    with global_ahk_lock:
        _send_click(*args, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def mouse_scroll(direction: str, times=1, *, modifier: str = None, blind=True, mode=None, level=None):
    """mouse_scroll(direction: str, times=1, **options)

    Scroll the mouse wheel.

    The *direction* argument specifies the scroll direction. Takes one of the
    following values: ``"up"``, ``"down"``, ``"left"``, ``"right"``.

    The *times* argument specifies the number of notches to turn the wheel.
    However, some applications do not obey *times* higher than 1. Use the
    following workaround::

        for _ in range(5):
            ahkpy.mouse_scroll("up")

    For the *options* arguments refer to :func:`click`.

    :command: `Send, {Click}
       <https://www.autohotkey.com/docs/commands/Send.htm#Click>`_
    """
    if direction not in SCROLL_DIRECTIONS:
        raise ValueError(f"{direction!r} is not a valid mouse scroll direction")
    if times < 0:
        raise ValueError("times must be positive")
    _send_click("wheel"+direction, str(times), modifier=modifier, blind=blind, mode=mode, level=level, delay=UNSET)


def mouse_move(x, y, *, relative_to="window", mode=None, speed=None, delay=None):
    """Move the mouse cursor.

    .. TODO: Pasted from the ToolTip.show method. Consider referring.

    The *x* and *y* arguments set the coordinates to move the mouse relative to
    the area specified by the *relative_to* argument which defaults to
    ``"window"``. The valid *relative_to* arguments are the following:

    - ``"cursor"`` – coordinates are relative to its current position.
    - ``"screen"`` – coordinates are relative to the desktop (entire screen).
    - ``"window"`` – coordinates are relative to the active window.
    - ``"client"`` – coordinates are relative to the active window's client
      area, which excludes the window's title bar, menu (if it has a
      standard one) and borders. Client coordinates are less dependent on OS
      version and theme.

    :param str mode: the mode that is used to move the mouse. If the *speed*
       argument is given, it forces the Event mode. For more information refer
       to the *mode* argument of the :func:`send` function.

    :param int speed: the speed of mouse movement in the range 0 (fastest) to
       100 (slowest). Defaults to one currently set in
       :attr:`Settings.mouse_speed`.

    :param float delay: the delay after the mouse movement. For more information
       refer to the *mouse_delay* argument of the :func:`send` function.

    :command: `Send, {Click X, Y, 0}
       <https://www.autohotkey.com/docs/commands/Send.htm#Click>`_, `MouseMove
       <https://www.autohotkey.com/docs/commands/MouseMove.htm>`_
    """
    if speed is not None:
        if mode is None:
            # Force SendEvent if speed is given.
            mode = "event"
    else:
        speed = get_settings().mouse_speed
    if not 0 <= speed <= 100:
        raise ValueError("speed must be between 0 and 100")

    offset = ""
    if relative_to == "cursor":
        offset = "relative"

    # To move the mouse without clicking, specify 0 after the coordinates.
    no_click = "0"

    with global_ahk_lock:
        if relative_to != "cursor":
            _set_coord_mode("mouse", relative_to)
        ahk_call("SetDefaultMouseSpeed", speed)
        # I use 'Send {Click ...}' here instead of MouseMove because it lets me
        # reuse the _send_click() function.
        _send_click(str(int(x)), str(int(y)), no_click, offset, mode=mode, delay=delay)


def _send_click(*args, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    if modifier is not None:
        unknown_modifiers = set(modifier) - MODIFIERS
        if unknown_modifiers:
            raise ValueError(f"{''.join(unknown_modifiers)!r} is not a valid modifier")
    else:
        modifier = ""

    blind_str = "{Blind}" if blind else ""

    send(
        "%s%s{Click, %s}" % (blind_str, modifier, ",".join(args)),
        mode=mode,
        level=level,
        key_delay=UNSET,
        key_duration=UNSET,
        mouse_delay=delay,
    )


def get_mouse_pos(relative_to="window") -> Tuple[int, int]:
    """Get current mouse position relative to specified area.

    The valid *relative_to* arguments are the following:

    - ``"screen"`` – coordinates are relative to the desktop (entire screen).
    - ``"window"`` – coordinates are relative to the active window.
    - ``"client"`` – coordinates are relative to the active window's client
      area, which excludes the window's title bar, menu (if it has a
      standard one) and borders. Client coordinates are less dependent on OS
      version and theme.

    .. ^^ Copied from ToolTip.show().

    Returns a ``(x, y)`` tuple.

    :command: `MouseGetPos, X, Y
       <https://www.autohotkey.com/docs/commands/MouseGetPos.htm>`_
    """
    with global_ahk_lock:
        _set_coord_mode("mouse", relative_to)
        result = ahk_call("MouseGetPos")
    return (result["X"], result["Y"])


def get_window_under_mouse() -> Window:
    """get_window_under_mouse() -> ahkpy.Window

    Get the window under the mouse cursor.

    Returns a :class:`Window` instance. If the window cannot be determined,
    returns ``Window(None)``. The window does not have to be active to be
    detected.

    :command: `MouseGetPos,,, Win
       <https://www.autohotkey.com/docs/commands/MouseGetPos.htm>`_
    """
    win_id = ahk_call("MouseGetWin")
    if not win_id:
        return Window(None)
    return Window(win_id)


def get_control_under_mouse(simple=False):
    """get_control_under_mouse(simple=False) -> ahkpy.Control

    Get the control under the mouse cursor.

    If the *simple* argument is true, a simpler method of detection is used.
    This method correctly retrieves the active/topmost child window of an
    Multiple Document Interface (MDI) application such as SysEdit or TextPad.
    However, it is less accurate for other purposes such as detecting controls
    inside a GroupBox control.

    Returns a :class:`Control` instance. If the control cannot be determined,
    returns ``Control(None)``. The window does not have to be active for the
    control to be detected.

    :command: `MouseGetPos,,,, Control
       <https://www.autohotkey.com/docs/commands/MouseGetPos.htm>`_
    """
    flag = 2 | bool(simple)
    win_id = ahk_call("MouseGetControl", flag)
    if not win_id:
        return Control(None)
    return Control(win_id)


def get_cursor_type() -> str:
    """Get the type of mouse cursor currently being displayed.

    Returns one of the following words: AppStarting, Arrow, Cross, Help,
    IBeam, Icon, No, Size, SizeAll, SizeNESW, SizeNS, SizeNWSE, SizeWE, UpArrow,
    Wait, Unknown.

    The acronyms used with the size-type cursors are compass directions, e.g.
    NESW is NorthEast+SouthWest. The hand-shaped cursors (pointing and grabbing)
    are classified as Unknown.
    """
    return ahk_call("GetVar", "A_Cursor")
