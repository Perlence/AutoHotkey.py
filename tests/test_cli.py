import subprocess
from textwrap import dedent

import pytest

from ahkpy.main import STATUS_CONTROL_C_EXIT


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


def test_script(tmpdir, child_ahk):
    script = tmpdir / "script.py"
    script.write("import ahkpy as ahk, sys; print(__name__, __file__, sys.argv)")
    res = child_ahk.run([str(script)])
    assert res.stderr == ""
    assert res.stdout == f"__main__ {str(script)} [{repr(str(script))}]\n"
    assert res.returncode == 0

    beep = tmpdir / "beep.py"
    beep.write("import ahkpy as ahk, sys; print(sys.argv); import boop")
    boop = tmpdir / "boop.py"
    boop.write("print('boop')")
    res = child_ahk.run([str(beep)])
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
    assert res.stdout == f"__main__ {str(script)} [{repr(str(script))}, 'ahk.py', '1', '2']\n"
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
    res = child_ahk.run(["-q", str(script)])
    assert res.stderr == dedent(f"""\
        Traceback (most recent call last):
          File "{script}", line 1, in <module>
            1/0
        ZeroDivisionError: division by zero
        """)
    assert res.returncode == 1

    res = child_ahk.run(["-q", "script.py"], cwd=tmpdir)
    assert res.stderr == dedent("""\
        Traceback (most recent call last):
          File "script.py", line 1, in <module>
            1/0
        ZeroDivisionError: division by zero
        """)
    assert res.returncode == 1

    res = child_ahk.run_code("import", quiet=True)
    assert res.stderr == dedent("""\
          File "<stdin>", line 1
            import
                 ^
        SyntaxError: invalid syntax
        """)
    assert res.returncode == 1

    script.write("import")
    res = child_ahk.run(["-q", str(script)])
    assert res.stderr == dedent(f"""\
          File "{script}", line 1
            import
                 ^
        SyntaxError: invalid syntax
        """)
    assert res.returncode == 1

    beep = tmpdir / "beep.py"
    beep.write("import boop")
    boop = tmpdir / "boop.py"
    boop.write("import")
    res = child_ahk.run(["-q", str(beep)])
    assert res.stderr == dedent(f"""\
        Traceback (most recent call last):
          File "{beep}", line 1, in <module>
            import boop
          File "{boop}", line 1
            import
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
    res = subprocess.run(["pyw.exe", "-m", "ahkpy", str(script)])
    assert res.returncode == 0


def test_interactive_mode(request):
    from winpty import PtyProcess

    proc = PtyProcess.spawn("py.exe -m ahkpy", dimensions=(24, 120))
    request.addfinalizer(proc.terminate)

    assert "Python 3" in proc.readline()
    assert 'Type "help"' in proc.readline()
    assert "(InteractiveConsole)" in proc.readline()
    assert proc.read(3) == ">>>"

    proc.write("import sys; sys.argv\r\n")
    assert "import sys; sys.argv" in proc.readline()
    assert "['']" in proc.readline()
    assert proc.read(3) == ">>>"

    proc.write("nonexistent\r\n")
    assert "nonexistent" in proc.readline()
    assert "Traceback" in proc.readline()
    assert "  File" in proc.readline()
    assert "NameError: name 'nonexistent' is not defined" in proc.readline()
    assert proc.read(3) == ">>>"

    proc.write("!\r\n")
    assert "!" in proc.readline()
    assert '  File "<console>"' in proc.readline()
    assert "    !" in proc.readline()
    assert "    ^" in proc.readline()
    assert "SyntaxError: invalid syntax" in proc.readline()
    assert proc.read(3) == ">>>"

    proc.write("exit()\r\n")
    proc.wait()
    assert proc.exitstatus == 0


def test_interactive_exec_in_main(request):
    import time

    import ahkpy as ahk
    from winpty import PtyProcess

    proc = PtyProcess.spawn("py.exe -m ahkpy", dimensions=(24, 120))
    request.addfinalizer(proc.terminate)
    proc.read()

    proc.write("ahk.wait_key_pressed_logical('F13')\r\n")
    proc.read()
    ahk.send_event("{F13}", level=10, key_duration=0.01)
    time.sleep(0.01)
    assert proc.readline().startswith("True")

    proc.write("exit()\r\n")
    proc.wait()
    assert proc.exitstatus == 0


@pytest.mark.parametrize("proc", [
    pytest.param("", id="interrupt during no Python code"),
    pytest.param("while True: ahk.sleep(1)", id="interrupt in Python's main"),
    pytest.param("ahk.set_timer(0.1, lambda: None)", id="interrupt in callback"),
])
def test_keyboard_interrupt(request, tmpdir, child_ahk, proc):
    from winpty import PtyProcess

    def code():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        print("ok00")
        "{proc}"

    script = tmpdir / "script.py"
    code_str = child_ahk.extract_code(code).replace('"{proc}"', proc)
    script.write(code_str)

    proc = PtyProcess.spawn(f"py.exe -m ahkpy {script}", dimensions=(24, 120))
    request.addfinalizer(proc.terminate)

    assert "ok00" in proc.readline()
    proc.sendintr()
    proc.wait()
    assert proc.exitstatus == STATUS_CONTROL_C_EXIT
    assert "KeyboardInterrupt" in proc.read()


def test_keyboard_interrupt_broken_handler(request, tmpdir, child_ahk):
    from winpty import PtyProcess

    import ahkpy as ahk

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

    proc = PtyProcess.spawn(f"py.exe -m ahkpy -q {script}", dimensions=(24, 120))
    request.addfinalizer(proc.terminate)

    assert "ok00" in proc.readline()
    proc.sendintr()
    proc.read()
    assert "ZeroDivisionError" in proc.read()
    assert proc.isalive()
    ahk.send("{F24}")
    proc.wait()
