import argparse
import functools
import os
import runpy
import sys
import subprocess
import time
import traceback

import ahkpy as ahk
from .exceptions import Error  # noqa: F401, used in Python.ahk


STATUS_CONTROL_C_EXIT = 0xC000013A

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

    prepare_tray_menu()
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


def prepare_tray_menu():
    ahk_win = ahk.all_windows.first(pid=os.getpid())
    WM_COMMAND = 0x0111
    ID_TRAY_OPEN = 65300
    ID_TRAY_WINDOWSPY = 65302

    def open_docs():
        subprocess.Popen(["explorer.exe", "https://ahkpy.readthedocs.io/"])

    ahk.tray_menu._remove_standard()
    ahk.tray_menu.add("&Open", ahk_win.post_message, WM_COMMAND, ID_TRAY_OPEN, default=True)
    ahk.tray_menu.add("&Help", open_docs)
    ahk.tray_menu.add_separator()
    ahk.tray_menu.add("&Window Spy", ahk_win.post_message, WM_COMMAND, ID_TRAY_WINDOWSPY)
    ahk.tray_menu.add("&Restart This Script", ahk.restart)
    ahk.tray_menu.add_separator()
    ahk.tray_menu.add("&Suspend Hotkeys", ahk.toggle_suspend)
    ahk.tray_menu.add("E&xit", sys.exit)


def run_from_args():
    usage = "py -m ahkpy [-h] [-V] [-q] [--no-tray] [-c CMD | -m MOD | FILE | -] [ARGS] ..."
    parser = GUIArgumentParser(usage=usage, prog="ahkpy")
    parser.add_argument(
        "-V", "--version", action="version", version=version(),
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="suppress message boxes with errors",
    )
    parser.add_argument(
        "--no-tray", dest="tray", action="store_false", default=True,
        help="hide the tray icon",
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

    if options.tray:
        ahk.flow.ahk_call("Menu", "Tray", "Icon")

    if options.cmd:
        sys.argv[:] = ["-c", *args[1:]]
        # Add "ahkpy" and "ahk" to globals.
        run_source(args[0], extra_globals={"ahkpy": ahk, "ahk": ahk})
    elif options.module:
        sys.argv[:] = args
        cwd = os.path.abspath(os.getcwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        run_module(args[0])
    elif sys.stdin and (not args or args[0] == "-"):
        if args:
            sys.argv[:] = args
        else:
            sys.argv[:] = [""]
        if sys.stdin.isatty():
            quiet = True
            interact()
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
                ahk.message_box(message)
                return
            file.write(message)


def version():
    python_version, _, _ = sys.version.partition(" ")
    ahk_version = ahk.flow.ahk_call("GetVar", "A_AhkVersion")
    return f"AutoHotkey.py {ahk.__version__}, Python {python_version}, AutoHotkey {ahk_version}"


def interact():
    import code
    console = code.InteractiveConsole(locals={"ahkpy": ahk, "ahk": ahk})
    console.raw_input = lambda prompt="": ahk.coop(interactive_input, prompt)
    console.interact(exitmsg="")
    # Force close AHK if it became persistent.
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
            # Run directory.
            code = functools.partial(runpy.run_path, filename, run_name="__main__")
    except FileNotFoundError as err:
        show_error(f"Can't open file: {err}")
        sys.exit(2)
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error(filename)
    else:
        run_code(code, filename)


def run_source(source, filename="<stdin>", extra_globals=None):
    try:
        code = compile(source, filename, "exec")
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error(filename)
    else:
        run_code(code, filename, extra_globals)


def run_code(code, filename, extra_globals=None):
    try:
        globs = {
            "__name__": "__main__",
            "__doc__": None,
            "__file__": filename,
            **(extra_globals or {}),
        }
        if callable(code):
            code()
        else:
            exec(code, globs)
    except SystemExit:
        raise
    except BaseException as exc:
        show_traceback()
        status = STATUS_CONTROL_C_EXIT if isinstance(exc, KeyboardInterrupt) else 1
        sys.exit(status)


def run_module(mod_name):
    try:
        runpy.run_module(mod_name, run_name="__main__", alter_sys=True)
    except SystemExit:
        raise
    except BaseException as exc:
        show_traceback()
        status = STATUS_CONTROL_C_EXIT if isinstance(exc, KeyboardInterrupt) else 1
        sys.exit(status)


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
    text = "".join(traceback.format_exception(type, value, tb))
    silent_exc = getattr(value, "_ahk_silent_exc", False)
    if isinstance(value, KeyboardInterrupt):
        silent_exc = True
    show_error(text, end="", silent_exc=silent_exc)


def show_error(text, end="\n", silent_exc=False):
    if sys.stderr is not None:
        print(text, end=end, file=sys.stderr, flush=True)
    if not (quiet or silent_exc):
        ahk.MessageBox.error(text)
