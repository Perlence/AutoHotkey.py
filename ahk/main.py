import argparse
import io
import os
import runpy
import sys
import traceback
from pkgutil import read_code

import _ahk  # noqa

from . import api


quiet = False


def main():
    sys.excepthook = excepthook
    try:
        run_from_args()
    except SystemExit as exc:
        _ahk.call("ExitApp", handle_system_exit(exc))


def handle_system_exit(value):
    # Reference implementation: pythonrun.c/_Py_HandleSystemExit
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

    show_error(value)
    return 1


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
        sys.argv = [module, *rest]
        cwd = os.path.abspath(os.getcwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        run_module(module)
    elif file == "-":
        del sys.argv[0]
        code = sys.stdin.read()
        run_source(code)
    elif file:
        sys.argv = [file, *rest]
        script_dir = os.path.abspath(os.path.dirname(file))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        run_path(file)
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


def run_path(filename):
    try:
        # runpy._get_code_from_file:
        with io.open_code(filename) as f:
            code = read_code(f)
        if code is None:
            # That didn't work, so try it as normal source code
            with io.open_code(filename) as f:
                code = compile(f.read(), filename, "exec")
    except FileNotFoundError as err:
        show_error(f"Can't open file: {err}")
        sys.exit(2)
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error(filename)
    else:
        run_code(code)


def run_source(source, filename="<stdin>"):
    try:
        code = compile(source, filename, "exec")
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error(filename)
    else:
        run_code(code)


def run_code(code):
    try:
        globs = {"__name__": "__main__", "__doc__": None}
        exec(code, globs)
    except SystemExit:
        raise
    except:
        show_traceback()
        sys.exit(1)


def run_module(mod_name):
    try:
        runpy.run_module(mod_name, run_name="__main__", alter_sys=True)
    except SystemExit:
        raise
    except:
        show_traceback()
        sys.exit(1)


def show_syntax_error(filename=None):
    type, value, tb = sys.exc_info()
    if filename and type is SyntaxError:
        # Work hard to stuff the correct filename in the exception
        try:
            msg, (dummy_filename, lineno, offset, line) = value.args
        except ValueError:
            # Not the format we expect; leave it alone
            pass
        else:
            # Stuff in the right filename
            value = SyntaxError(msg, (filename, lineno, offset, line))
    sys.excepthook(type, value, tb.tb_next)
    sys.exit(1)


def show_traceback():
    _, _, last_tb = ei = sys.exc_info()
    try:
        sys.excepthook(ei[0], ei[1], last_tb.tb_next)
    finally:
        last_tb = ei = None


def excepthook(type, value, tb):
    show_error("".join(traceback.format_exception(type, value, tb)), end="")


def show_error(text, end="\n"):
    if sys.stderr is not None:
        print(text, end=end, file=sys.stderr, flush=True)
    if not quiet:
        # TODO: Add more MB_* constants to the module?
        MB_ICONERROR = 0x10
        api.message_box(text, options=MB_ICONERROR)
