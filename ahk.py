import sys
import traceback
from contextlib import contextmanager
from functools import partial

import _ahk  # noqa


# TODO: Write an __all__.


Error = _ahk.Error


def excepthook(type, value, tb):
    tblines = traceback.format_exception(type, value, tb)
    # TODO: Replace the invocation with Python-wrapped msg_box.
    MB_ICONSTOP = 0x10
    options = hex(MB_ICONSTOP)
    title = ""
    text = "".join(tblines)
    _ahk.call_cmd("MsgBox", options, title, text)


sys.excepthook = excepthook


def hotkey(key_name, func=None, buffer=None, priority=0, max_threads=None,
           input_level=None):
    if key_name == "":
        raise Error("invalid key name")
    
    if func is None:
        # Return the decorator.
        return partial(hotkey, key_name, buffer=buffer, priority=priority,
                       max_threads=max_threads, input_level=input_level)

    # TODO: Handle case when func == "AltTab" or other substitutes.
    _ahk.set_callback(f"Hotkey {key_name}", func)
    # TODO: Set the options.
    # TODO: Change options of the existing hotkeys.
    _ahk.call_cmd("Hotkey", key_name, "HotkeyLabel")
    # TODO: Return a Hotkey object.


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
