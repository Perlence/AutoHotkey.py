import argparse
import os
import runpy
import sys
import traceback
from contextlib import contextmanager

import _ahk  # noqa

from . import api


quiet = False


def main():
    sys.excepthook = excepthook
    try:
        run_from_args()
    except SystemExit as exc:
        _ahk.call("ExitApp", handle_system_exit(exc))


def run_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="supress message boxes with errors")
    program = parser.add_mutually_exclusive_group()
    program.add_argument("-m", "--module",
                        help="run library module as a script")
    program.add_argument("FILE", nargs="?",
                         help="program read from script file")
    parser.add_argument("ARGS", nargs="*",
                        help="arguments passed to program in sys.argv[1:]")

    args = parse_args()
    if args is None:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    global quiet
    help, quiet, module, file, rest = args

    if help:
        parser.print_help()
        sys.exit()

    if module:
        # TODO: Handle exception in the module.
        sys.argv = [module, *rest]
        cwd = os.path.abspath(os.getcwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        runpy.run_module(module, run_name="__main__", alter_sys=True)
    elif file == "-":
        file = "<string>"
        code = sys.stdin.read()
        del sys.argv[0]
        globs = {"__name__": "__main__"}
        with handle_exception(file):
            exec(code, globs)
    elif file:
        sys.argv = [file, *rest]
        script_dir = os.path.abspath(os.path.dirname(file))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        with handle_exception(file):
            runpy.run_path(file, run_name="__main__")
    else:
        # TODO: Implement interactive mode.
        # TODO: Show usage in a message box.
        parser.print_usage()
        sys.exit()


def parse_args():
    # Parse arguments manually instead of using ArgumentParser.parse_args,
    # because I want to keep the strict order of arguments.
    if len(sys.argv) < 2:
        return

    args = sys.argv[1:]

    help = False
    quiet = False
    module = None
    file = None
    rest = []

    if args[0] in ("-h", "--help"):
        help = True
        return help, quiet, module, file, rest

    if args[0] in ("-q", "--quiet"):
        quiet = True
        del args[0]

    if len(args) < 1:
        return

    if args[0] == "-m":
        if len(args) < 2:
            return
        module, *rest = args[1:]
    else:
        file, *rest = args

    return help, quiet, module, file, rest


@contextmanager
def handle_exception(entry_filename):
    """Drop auxiliary traceback frames and show the exception."""
    try:
        yield
    except (SyntaxError, Exception) as err:
        tbe = traceback.TracebackException.from_exception(err)
        skip_frames = 0
        for i, frame in enumerate(tbe.stack):
            if frame.filename == entry_filename:
                skip_frames = i
                break
        if (isinstance(err, SyntaxError) and err.filename == entry_filename and
                skip_frames == 0):
            skip_frames = len(tbe.stack)
        tbe.stack = traceback.StackSummary.from_list(tbe.stack[skip_frames:])
        print_exception("".join(tbe.format()))
        sys.exit(1)


def excepthook(type, value, tb):
    print_exception("".join(traceback.format_exception(type, value, tb)))


def print_exception(text):
    if sys.stderr is not None:
        print(text, end="", file=sys.stderr, flush=True)
    if not quiet:
        # TODO: Add more MB_* constants to the module?
        MB_ICONERROR = 0x10
        api.message_box(text, options=MB_ICONERROR)


def handle_system_exit(value):
    # Reference implementation: pythonrun.c/_Py_HandleSystemExit
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
