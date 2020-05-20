from contextlib import contextmanager
from functools import partial

import _ahk  # noqa


# TODO: Write an __all__.


class AHKError(Exception):
    pass


def hotkey(key_name, func=None, buffer=None, priority=0, max_threads=None,
           input_level=None):
    if key_name == "":
        raise AHKError("invalid key name")
    
    if func is None:
        # Return the decorator.
        return partial(hotkey, key_name, buffer=buffer, priority=priority,
                       max_threads=max_threads, input_level=input_level)

    # TODO: Handle case when func == "AltTab" or other substitutes.
    _ahk.set_callback(f"Hotkey {key_name}", func)
    # TODO: Set the options.
    # TODO: Change options of the existing hotkeys.
    _ahk.call_cmd("Hotkey", key_name, "HotkeyLabel")


def remap_key(origin_key, destination_key):
    # TODO: Implement key remapping, e.g. Esc::CapsLock.
    raise NotImplementedError()


@contextmanager
def hotkey_context():
    # TODO: Implement `Hotkey, If` commands.
    raise NotImplementedError()


def send(keys):
    # TODO: Consider adding `mode` keyword?
    _ahk.call_cmd("Send", keys)
