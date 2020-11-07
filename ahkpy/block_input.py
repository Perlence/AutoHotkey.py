from contextlib import contextmanager

from .flow import ahk_call

__all__ = [
    "block_input_while_sending",
    "block_input",
    "block_mouse_move",
]


@contextmanager
def block_input():
    """Block all user input unconditionally."""
    ahk_call("BlockInput", "On")
    yield
    ahk_call("BlockInput", "Off")


@contextmanager
def block_input_while_sending():
    """Block user input while a :func:`ahkpy.send` is in progress.

    This also blocks user input during mouse automation because mouse clicks and
    movements are implemented using the :func:`ahkpy.send` function.
    """
    ahk_call("BlockInput", "Send")
    yield
    ahk_call("BlockInput", "Default")


@contextmanager
def block_mouse_move():
    """Block the mouse cursor movement."""
    ahk_call("BlockInput", "MouseMove")
    yield
    ahk_call("BlockInput", "MouseMoveOff")
