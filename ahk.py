import sys
import traceback
from contextlib import contextmanager
from functools import partial

import _ahk  # noqa


# TODO: Write an __all__.
Error = _ahk.Error


def message_box(text=None, title="", options=0, timeout=None):
    if text is None:
        # Show "Press OK to continue."
        return _ahk.call("MsgBox")

    return _ahk.call("MsgBox", options, title, text, timeout)
    # TODO: Return result of IfMsgBox?


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
    _ahk.call("Hotkey", key_name, "HotkeyLabel")
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
    _ahk.call("Send", keys)


def get_key_state(key_name, mode=None):
    return _ahk.call("GetKeyState", key_name, mode)


def _main():
    sys.excepthook = _excepthook
    try:
        _run_from_args()
    except SystemExit as ex:
        _ahk.call("ExitApp", _handle_system_exit(ex))


def _run_from_args():
    import runpy
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("SCRIPT", nargs="?")
    parser.add_argument("-m", "--module")
    args, rest = parser.parse_known_args()
    if args.module:
        sys.argv = [args.module, *rest]
        runpy.run_module(args.module, run_name="__main__", alter_sys=True)
    elif args.SCRIPT:
        sys.argv = [args.SCRIPT, *rest]
        runpy.run_path(args.SCRIPT, run_name="__main__")
    else:
        # TODO: Implement interactive mode.
        parser.print_usage()
        sys.exit()


def _excepthook(type, value, tb):
    tblines = traceback.format_exception(type, value, tb)
    # TODO: Add more MB_* constants to the module?
    MB_ICONERROR = 0x10
    message_box("".join(tblines), options=MB_ICONERROR)


def _handle_system_exit(value):
    if value is None:
        return 0

    if isinstance(value, BaseException):
        try:
            code = value.code
        except AttributeError:
            pass
        else:
            value = code
            if value is None:
                return 0

    if isinstance(value, int):
        return value

    if sys.stderr is not None:
        print(value, file=sys.stderr, flush=True)
    return 1
