from contextlib import contextmanager
from functools import partial

import _ahk  # noqa

from .exceptions import Error

__all__ = [
    "get_key_state", "hotkey", "hotkey_context", "remap_key",
    "key_wait_pressed", "key_wait_released", "send", "send_mode",
]


def get_key_state(key_name, mode=None):
    return _ahk.call("GetKeyState", key_name, mode)


def hotkey(key_name, func=None, buffer=None, priority=0, max_threads=None,
           input_level=None):
    if key_name == "":
        raise Error("invalid key name")

    if func is None:
        # Return the decorator.
        return partial(hotkey, key_name, buffer=buffer, priority=priority,
                       max_threads=max_threads, input_level=input_level)

    if not callable(func):
        raise TypeError(f"object {func!r} must be callable")

    # TODO: Handle case when func == "AltTab" or other substitutes.
    # TODO: Set the options.
    # TODO: Change options of the existing hotkeys.
    # TODO: Return a Hotkey object.
    _ahk.call("Hotkey", key_name, func)


@contextmanager
def hotkey_context():
    # TODO: Implement `Hotkey, If` commands.
    raise NotImplementedError()


def key_wait_pressed(key_name, logical_state=False, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical_state=logical_state, timeout=timeout)


def key_wait_released(key_name, logical_state=False, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical_state=logical_state, timeout=timeout)


def _key_wait(key_name, down=False, logical_state=False, timeout=None) -> bool:
    options = []
    if down:
        options.append("D")
    if logical_state:
        options.append("L")
    if timeout is not None:
        options.append(f"T{timeout}")
    result = _ahk.call("KeyWait", str(key_name), "".join(options))
    # Return False if KeyWait timed out, True otherwise.
    return not result


def remap_key(origin_key, destination_key):
    # TODO: Implement key remapping, e.g. Esc::CapsLock.
    raise NotImplementedError()


def send(keys):
    # TODO: Consider adding `mode` keyword?
    _ahk.call("Send", keys)


def send_mode(mode):
    _ahk.call("SendMode", mode)
