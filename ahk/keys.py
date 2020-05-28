from contextlib import contextmanager
from functools import partial

import _ahk  # noqa

__all__ = [
    "get_key_state", "hotkey", "hotkey_context", "remap_key", "send",
    "send_mode",
]


def get_key_state(key_name, mode=None):
    return _ahk.call("GetKeyState", key_name, mode)


def hotkey(key_name, func=None, buffer=None, priority=0, max_threads=None,
           input_level=None):
    if key_name == "":
        raise _ahk.Error("invalid key name")

    if func is None:
        # Return the decorator.
        return partial(hotkey, key_name, buffer=buffer, priority=priority,
                       max_threads=max_threads, input_level=input_level)

    # TODO: Handle case when func == "AltTab" or other substitutes.
    # TODO: Set the options.
    # TODO: Change options of the existing hotkeys.
    # TODO: Return a Hotkey object.
    _ahk.call("Hotkey", key_name, func)


@contextmanager
def hotkey_context():
    # TODO: Implement `Hotkey, If` commands.
    raise NotImplementedError()


def remap_key(origin_key, destination_key):
    # TODO: Implement key remapping, e.g. Esc::CapsLock.
    raise NotImplementedError()


def send(keys):
    # TODO: Consider adding `mode` keyword?
    _ahk.call("Send", keys)


def send_mode(mode):
    _ahk.call("SendMode", mode)
