import argparse
import functools
import os
import runpy
import sys
import time
import traceback

from .message_box import MessageBox, message_box
from .exceptions import Error  # noqa: F401, used in Python.ahk


quiet = False


def main():
    sys.excepthook = sys.__excepthook__ = excepthook

    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = sys.__stdout__ = open_console("CONOUT$", "w")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8")
    else:
        sys.stderr = sys.__stderr__ = open_console("CONOUT$", "w")
    if sys.stdin:
        sys.stdin.reconfigure(encoding="utf-8")
    else:
        sys.stdin = sys.__stdin__ = open_console("CONIN$", "r")

    venv = os.getenv("VIRTUAL_ENV")
    if venv and not os.getenv("PYTHONFULLPATH"):
        import site
        # TODO: Fix the missing init.tcl. This is broken: ahkpy -m tkinter.scrolledtext
        site.addsitedir(f"{venv}\\Lib\\site-packages")

    run_from_args()


def open_console(con, mode):
    try:
        return open(con, mode, encoding="utf-8")
    except OSError:
        return None


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

    show_error(value)
    return 1


def run_from_args():
    usage = "py -m ahkpy [-h] [-q] [-c CMD | -m MOD | FILE | -] [ARGS] ..."
    parser = GUIArgumentParser(usage=usage)
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="supress message boxes with errors",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c", dest="cmd", action="store_true",
        help="program passed in as string",
    )
    group.add_argument(
        "-m", dest="module", action="store_true",
        help="run library module as a script",
    )
    parser.add_argument(
        "ARGS", nargs=argparse.REMAINDER,
        help="arguments passed to program in sys.argv[1:]",
    )

    options = parser.parse_args()
    args = options.ARGS

    global quiet
    quiet = options.quiet

    if options.cmd:
        sys.argv[:] = ["-c", *args[1:]]
        # TODO: Consider importing ahkpy.
        run_source(args[0])
    elif options.module:
        sys.argv[:] = args
        cwd = os.path.abspath(os.getcwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        run_module(args[0])
    elif sys.stdin and (not args or args[0] == "-"):
        if args:
            sys.argv[:] = ["-", *args[1:]]
        else:
            sys.argv[:] = [""]
        if sys.stdin.isatty():
            import ahkpy
            quiet = True
            ahkpy.coop(
                interact,
                exitmsg="",
                local={
                    "ahkpy": ahkpy,
                    "ahk": ahkpy,
                },
            )
        else:
            code = sys.stdin.read()
            run_source(code)
    elif args and args[0]:
        sys.argv[:] = args
        script_dir = os.path.abspath(os.path.dirname(args[0]))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        run_path(args[0])
    else:
        parser.print_usage(sys.stderr)
        sys.exit(2)


class GUIArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        if message:
            if file is None:
                file = sys.stderr
            if file is None:
                message_box(message)
                return
            file.write(message)


def interact(banner=None, local=None, exitmsg=None):
    import code
    console = code.InteractiveConsole(local)
    console.raw_input = interactive_input
    console.interact(banner, exitmsg)
    # TODO: Up and down arrow keys don't scroll the history.
    # TODO: Executing "ahk.wait_key_pressed('F1')" in the console freezes the
    # program. Tray menu doesn't respond.

    # Force close AHK if it became persistent.
    # TODO: Add a test for this.
    sys.exit(0)


def interactive_input(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        # https://bugs.python.org/issue26531
        time.sleep(0.1)
        raise


def run_path(filename):
    try:
        # runpy.run_path:
        import io
        from pkgutil import get_importer, read_code
        importer = get_importer(filename)
        is_NullImporter = False
        if type(importer).__module__ == "imp":
            if type(importer).__name__ == "NullImporter":
                is_NullImporter = True
        if isinstance(importer, type(None)) or is_NullImporter:
            # runpy._get_code_from_file:
            with io.open_code(filename) as f:
                code = read_code(f)
            if code is None:
                # That didn't work, so try it as normal source code
                with io.open_code(filename) as f:
                    code = compile(f.read(), filename, "exec")
        else:
            # TODO: Write a test for running directories.
            code = functools.partial(runpy.run_path, filename, run_name="__main__")
    except FileNotFoundError as err:
        show_error(f"Can't open file: {err}")
        sys.exit(2)
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error(filename)
    else:
        run_code(code, filename)


def run_source(source, filename="<stdin>"):
    try:
        code = compile(source, filename, "exec")
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error(filename)
    else:
        run_code(code, filename)


def run_code(code, filename):
    try:
        globs = {
            "__name__": "__main__",
            "__doc__": None,
            "__file__": filename,
        }
        if callable(code):
            code()
        else:
            exec(code, globs)
    except SystemExit:
        raise
    except:  # noqa: E722
        show_traceback()
        sys.exit(1)


def run_module(mod_name):
    try:
        runpy.run_module(mod_name, run_name="__main__", alter_sys=True)
    except SystemExit:
        raise
    except:  # noqa: E722
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
        MessageBox.error(text)
