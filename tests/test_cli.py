import os
import subprocess
import sys
from textwrap import dedent

import pytest

import ahkpy as ahk
from ahkpy.main import STATUS_CONTROL_C_EXIT

try:
    import winpty
except ImportError:
    winpty = None

skip_if_winpty_is_missing = pytest.mark.skipif(winpty is None, reason="winpty is missing")

# Force WinPTY backend instead of ConPTY. The latter doesn't seem to send
# SIGINTs properly when the tests are run via tox.
os.environ['PYWINPTY_BACKEND'] = '1'


def test_stdin(child_ahk):
    code = "import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)"
    res = child_ahk.run(["-q", "-"], input=code)
    assert res.stderr == ""
    assert res.stdout == "__main__ <stdin> ['-']\n"
    assert res.returncode == 0

    res = child_ahk.run(["-", "script.py", "2", "3"], input=code)
    assert res.stdout == "__main__ <stdin> ['-', 'script.py', '2', '3']\n"
    assert res.returncode == 0

    res = child_ahk.run_code("""\
        try:
            argparse
        except NameError:
            pass
        else:
            print("'argparse' is in scope")
        """)
    assert res.stderr == ""
    assert res.stdout == ""
    assert res.returncode == 0


def test_sys_parameters(tmpdir):
    script = tmpdir / "script.py"
    script.write(dedent("""\
        import sys
        import ahkpy as ahk
        print(sys._home)
        print(sys.prefix)
        print(sys.exec_prefix)
        print(sys.base_prefix)
        print(sys.base_exec_prefix)
        print(sys.executable)
        print(sys.argv)
        print(*sys.path, sep="\\n")
    """))
    ahk_res = subprocess.run([sys.executable, "-m", "ahkpy", script], capture_output=True, text=True)
    py_res = subprocess.run([sys.executable, script], capture_output=True, text=True)
    assert ahk_res.stderr == py_res.stderr == ""
    assert ahk_res.stdout == py_res.stdout


def test_script(tmpdir, child_ahk):
    script = tmpdir / "script.py"
    script.write("import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)")
    res = child_ahk.run([script])
    assert res.stderr == ""
    assert res.stdout == f"__main__ {script} [{repr(str(script))}]\n"
    assert res.returncode == 0

    beep = tmpdir / "beep.py"
    beep.write("import ahkpy as ahk, sys; print(sys.argv); import boop")
    boop = tmpdir / "boop.py"
    boop.write("print('boop')")
    res = child_ahk.run([beep])
    assert res.stderr == ""
    assert res.stdout == f"[{repr(str(beep))}]\nboop\n", (
        "module 'beep' must be able to load the module 'boop' because they are "
        "in the same directory"
    )
    assert res.returncode == 0


def test_cmd(child_ahk):
    code = "import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)"
    res = child_ahk.run(["-c", code])
    assert res.stderr == ""
    assert res.stdout == "__main__ <stdin> ['-c']\n"
    assert res.returncode == 0

    code = "import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)"
    res = child_ahk.run(["-c", code, "hello"])
    assert res.stderr == ""
    assert res.stdout == "__main__ <stdin> ['-c', 'hello']\n"
    assert res.returncode == 0


def test_module(tmpdir, child_ahk):
    script = tmpdir / "script.py"
    script.write("import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)")
    res = child_ahk.run(["-m", "script", "ahk.py", "1", "2"], cwd=tmpdir)
    assert res.stderr == ""
    assert res.stdout == f"__main__ {script} [{repr(str(script))}, 'ahk.py', '1', '2']\n"
    assert res.returncode == 0


def test_directory(tmpdir, child_ahk):
    script = tmpdir / "__main__.py"
    script.write("import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)")
    res = child_ahk.run([tmpdir, "ahk.py", "1", "2"])
    assert res.stderr == ""
    assert res.stdout == f"__main__ {script} [{repr(str(tmpdir))}, 'ahk.py', '1', '2']\n"
    assert res.returncode == 0


def test_system_exit(child_ahk):
    res = child_ahk.run_code("import ahkpy as ahk, sys; sys.exit()")
    assert res.returncode == 0

    res = child_ahk.run_code("import ahkpy as ahk, sys; sys.exit(1)")
    assert res.returncode == 1

    res = child_ahk.run_code("import ahkpy as ahk, sys; sys.exit(2)")
    assert res.returncode == 2

    res = child_ahk.run_code("import ahkpy as ahk, sys; sys.exit('bye')", quiet=True)
    assert res.returncode == 1
    assert res.stderr == "bye\n"

    res = child_ahk.run_code("raise SystemExit")
    assert res.returncode == 0

    res = child_ahk.run_code("raise SystemExit(None)")
    assert res.returncode == 0

    res = child_ahk.run_code("raise SystemExit(1)")
    assert res.returncode == 1


def test_tracebacks(tmpdir, child_ahk):
    res = child_ahk.run_code("1/0", quiet=True)
    assert res.stderr == dedent("""\
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        ZeroDivisionError: division by zero
        """)
    assert res.returncode == 1

    script = tmpdir / "script.py"
    script.write("1/0")
    res = child_ahk.run(["-q", script])
    if sys.version_info < (3, 11):
        assert res.stderr == dedent(f"""\
            Traceback (most recent call last):
              File "{script}", line 1, in <module>
                1/0
            ZeroDivisionError: division by zero
            """)
    else:
        assert res.stderr == dedent(f"""\
            Traceback (most recent call last):
              File "{script}", line 1, in <module>
                1/0
                ~^~
            ZeroDivisionError: division by zero
            """)
    assert res.returncode == 1

    res = child_ahk.run(["-q", "script.py"], cwd=tmpdir)
    if sys.version_info < (3, 11):
        assert res.stderr == dedent("""\
            Traceback (most recent call last):
              File "script.py", line 1, in <module>
                1/0
            ZeroDivisionError: division by zero
            """)
    else:
        assert res.stderr == dedent("""\
            Traceback (most recent call last):
              File "script.py", line 1, in <module>
                1/0
                ~^~
            ZeroDivisionError: division by zero
            """)
    assert res.returncode == 1

    res = child_ahk.run_code("!", quiet=True)
    assert res.stderr == dedent("""\
          File "<stdin>", line 1
            !
            ^
        SyntaxError: invalid syntax
        """)
    assert res.returncode == 1

    script.write("!")
    res = child_ahk.run(["-q", script])
    assert res.stderr == dedent(f"""\
          File "{script}", line 1
            !
            ^
        SyntaxError: invalid syntax
        """)
    assert res.returncode == 1

    beep = tmpdir / "beep.py"
    beep.write("import boop")
    boop = tmpdir / "boop.py"
    boop.write("!")
    res = child_ahk.run(["-q", beep])
    assert res.stderr == dedent(f"""\
        Traceback (most recent call last):
          File "{beep}", line 1, in <module>
            import boop
          File "{boop}", line 1
            !
            ^
        SyntaxError: invalid syntax
        """)
    assert res.returncode == 1

    res = child_ahk.run(["-q", "nonexistent.py"])
    assert res.stderr == "Can't open file: [Errno 2] No such file or directory: 'nonexistent.py'\n"
    assert res.returncode == 2

    res = child_ahk.run(["-q", "-m", "nonexistent"])
    assert res.returncode == 1


def test_pyw(tmpdir):
    script = tmpdir / "script.py"
    code = "print('hello')"
    script.write(code)
    res = subprocess.run(["pyw.exe", "-m", "ahkpy", script])
    assert res.returncode == 0


def test_ahk_path_envvar(tmpdir):
    spy = tmpdir / "spy.bat"
    code = "@echo %0 %*"
    spy.write(code)

    script = tmpdir / "script.py"
    code = "print('hello')"
    script.write(code)

    import os
    res = subprocess.run(
        [sys.executable, "-m", "ahkpy", script],
        env={**os.environ, "AUTOHOTKEY": str(spy)},
        encoding="utf-8",
        capture_output=True,
    )
    assert res.stderr == ""
    assert res.stdout.lower() == f"{spy} {ahk.__path__[0]}\\Python.ahk {script}\n".lower()
    assert res.returncode == 0


def test_import_ahk(tmpdir):
    script = tmpdir / "script.py"
    code = "import ahkpy; print('ok')"
    script.write(code)
    res = subprocess.run([sys.executable, script], encoding="utf-8", capture_output=True)
    assert res.stderr == ""
    assert res.stdout == "ok\n"
    assert res.returncode == 0

    code = "import ahkpy; ahkpy.poll(); print('ok')"
    script.write(code)
    res = subprocess.run([sys.executable, script], encoding="utf-8", capture_output=True)
    assert "RuntimeError: AHK interop is not available." in res.stderr
    assert res.stdout == ""
    assert res.returncode == 1


@skip_if_winpty_is_missing
def test_interactive_mode(request):
    proc = winpty.PtyProcess.spawn([sys.executable, "-m", "ahkpy"], dimensions=(24, 120))
    request.addfinalizer(proc.terminate)

    assert "Python 3" in proc.readline()
    assert 'Type "help"' in proc.readline()
    assert "(InteractiveConsole)" in proc.readline()
    assert ">>>" in proc.read()

    proc.write("import sys; sys.argv\r\n")
    assert "import sys; sys.argv" in proc.readline()
    assert "['']" in proc.readline()
    assert ">>>" in proc.read()

    proc.write("nonexistent\r\n")
    assert "nonexistent" in proc.readline()
    assert "Traceback" in proc.readline()
    assert "  File" in proc.readline()
    assert "NameError: name 'nonexistent' is not defined" in proc.readline()
    assert ">>>" in proc.read()

    proc.write("!\r\n")
    assert "!" in proc.readline()
    assert '  File "<console>"' in proc.readline()
    assert "    !" in proc.readline()
    assert "    ^" in proc.readline()
    if sys.version_info < (3, 11):
        assert "SyntaxError: invalid syntax" in proc.readline()
    else:
        assert "SyntaxError: incomplete input" in proc.readline()
    assert ">>>" in proc.read()

    proc.write("exit()\r\n")
    proc.wait()
    assert proc.exitstatus == 0


@skip_if_winpty_is_missing
def test_interactive_mode_persistent(request):
    proc = winpty.PtyProcess.spawn([sys.executable, "-m", "ahkpy"], dimensions=(24, 120))
    request.addfinalizer(proc.terminate)
    proc.read()

    proc.write("ahk.hotkey('F24', exit)\r\n")
    proc.read()

    proc.write("exit()\r\n")
    proc.wait()
    assert proc.exitstatus == 0


@skip_if_winpty_is_missing
def test_interactive_exec_in_main(request):
    proc = winpty.PtyProcess.spawn([sys.executable, "-m", "ahkpy"], dimensions=(24, 120))
    request.addfinalizer(proc.terminate)
    proc.read()

    proc.write("ahk.wait_key_pressed_logical('F13')\r\n")
    proc.read()
    ahk.send_event("{F13}", level=10, key_duration=0.05)
    assert "True" in proc.readline()

    proc.write("exit()\r\n")
    proc.wait()
    assert proc.exitstatus == 0


@skip_if_winpty_is_missing
@pytest.mark.parametrize("proc", [
    pytest.param("", id="interrupt during no Python code"),
    pytest.param("while True: ahk.sleep(1)", id="interrupt in Python's main"),
    pytest.param("ahk.set_timer(0.1, lambda: None)", id="interrupt in callback"),
])
def test_keyboard_interrupt(request, tmpdir, child_ahk, proc):
    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        print("ok00")
        "{proc}"

    script = tmpdir / "script.py"
    code_str = child_ahk.extract_code(code).replace('"{proc}"', proc)
    script.write(code_str)

    proc = winpty.PtyProcess.spawn([sys.executable, "-m", "ahkpy", script], dimensions=(24, 120))
    request.addfinalizer(proc.terminate)

    assert "ok00" in proc.readline()
    proc.sendintr()
    proc.wait()
    assert proc.exitstatus == STATUS_CONTROL_C_EXIT


@skip_if_winpty_is_missing
def test_keyboard_interrupt_broken_handler(request, tmpdir, child_ahk):
    def code():
        import ahkpy as ahk
        import signal
        import sys
        ahk.hotkey("F24", sys.exit)
        def handler(*args): 1/0
        signal.signal(signal.SIGINT, handler)
        print("ok00")

    script = tmpdir / "script.py"
    script.write(child_ahk.extract_code(code))

    proc = winpty.PtyProcess.spawn([sys.executable, "-m", "ahkpy", "-q", script], dimensions=(24, 120))
    request.addfinalizer(proc.terminate)

    assert "ok00" in proc.readline()
    proc.sendintr()
    proc.read()
    assert "ZeroDivisionError" in proc.read()
    assert proc.isalive()
    ahk.send("{F24}")
    proc.wait()
