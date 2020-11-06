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


def click(button="left", *, times=1, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    _click(button, times, KEY_DOWN_AND_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def right_click(*, times=1, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    _click("right", times, KEY_DOWN_AND_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def double_click(button="left", *, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    _click(button, 2, KEY_DOWN_AND_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def mouse_press(button="left", *, times=1, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    _click(button, times, KEY_DOWN, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def mouse_release(button="left", *, times=1, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    _click(button, times, KEY_UP, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def _click(button, times, event_type, modifier: str = None, blind=True, mode=None, level=None, delay=None):
    args = []

    if button not in {"left", "right", "middle", "x1", "x2"}:
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


def mouse_scroll(direction, times=1, *, modifier: str = None, blind=True, mode=None, level=None):
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError(f"{direction!r} is not a valid mouse scroll direction")
    if times < 0:
        raise ValueError("times must be positive")
    _send_click("wheel"+direction, str(times), modifier=modifier, blind=blind, mode=mode, level=level, delay=UNSET)


def mouse_move(x, y, *, relative_to="window", mode=None, speed=None, delay=None):
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
        unknown_modifiers = set(modifier) - set("!+^#")
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
    with global_ahk_lock:
        _set_coord_mode("mouse", relative_to)
        result = ahk_call("MouseGetPos")
    return (result["X"], result["Y"])


def get_window_under_mouse():
    win_id = ahk_call("MouseGetWin")
    if not win_id:
        return Window(None)
    return Window(win_id)


def get_control_under_mouse(simple=False):
    flag = 2 if not simple else 3
    win_id = ahk_call("MouseGetControl", flag)
    if not win_id:
        return Control(None)
    return Control(win_id)
