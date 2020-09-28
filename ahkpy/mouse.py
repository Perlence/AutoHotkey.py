from typing import Tuple

from .flow import ahk_call, global_ahk_lock
from .keys import send
from .settings import _set_coord_mode
from .window import Control, Window
from .unset import UNSET

__all__ = [
    "click",
    "double_click",
    "get_control_under_mouse",
    "get_mouse_pos",
    "get_window_under_mouse",
    "mouse_press",
    "mouse_release",
    "mouse_scroll",
    "right_click",
]


KEY_DOWN = 0
KEY_UP = 1
KEY_DOWN_AND_UP = 2


def click(
    button="left", *, times=1, modifier: str = None, blind=True,
    x=None, y=None, relative_to="window", mode=None, level=None, delay=None,
):
    _click(
        button, times, KEY_DOWN_AND_UP, modifier=modifier, blind=blind,
        x=x, y=y, relative_to=relative_to, mode=mode, level=level, delay=delay,
    )


def right_click(
    *, times=1, modifier: str = None, blind=True,
    x=None, y=None, relative_to="window", mode=None, level=None, delay=None,
):
    _click(
        "right", times, KEY_DOWN_AND_UP, modifier=modifier, blind=blind,
        x=x, y=y, relative_to=relative_to, mode=mode, level=level, delay=delay,
    )


def double_click(
    button="left", *, modifier: str = None, blind=True,
    x=None, y=None, relative_to="window", mode=None, level=None, delay=None,
):
    _click(
        button, 2, KEY_DOWN_AND_UP, modifier=modifier, blind=blind,
        x=x, y=y, relative_to=relative_to, mode=mode, level=level, delay=delay,
    )


def mouse_press(
    button="left", *, times=1, modifier: str = None, blind=True,
    x=None, y=None, relative_to="window", mode=None, level=None, delay=None,
):
    _click(
        button, times, KEY_DOWN, modifier=modifier, blind=blind,
        x=x, y=y, relative_to=relative_to, mode=mode, level=level, delay=delay,
    )


def mouse_release(
    button="left", *, times=1, modifier: str = None, blind=True,
    x=None, y=None, relative_to="window", mode=None, level=None, delay=None,
):
    _click(
        button, times, KEY_UP, modifier=modifier, blind=blind,
        x=x, y=y, relative_to=relative_to, mode=mode, level=level, delay=delay,
    )


def _click(
    button, times, event_type, modifier: str = None, blind=True,
    x=None, y=None, relative_to="window", mode=None, level=None, delay=None,
):
    args = []

    if x is not None:
        args.append(str(int(x)))
    if y is not None:
        args.append(str(int(y)))

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

    if relative_to == "pointer":
        args.append("relative")

    with global_ahk_lock:
        if relative_to != "pointer":
            _set_coord_mode("mouse", relative_to)
        _send_click(*args, modifier=modifier, blind=blind, mode=mode, level=level, delay=delay)


def mouse_scroll(direction, times=1, *, modifier: str = None, blind=True, mode=None, level=None):
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError(f"{direction!r} is not a valid mouse scroll direction")
    if times < 0:
        raise ValueError("times must be positive")
    _send_click("wheel"+direction, str(times), modifier=modifier, blind=blind, mode=mode, level=level, delay=UNSET)


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
