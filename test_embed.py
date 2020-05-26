import os
import subprocess

import pytest


AHK = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"
EMBED_PYTHON = os.path.abspath("EmbedPython.ahk")


def test_stdin():
    code = "import sys; print(__name__, sys.argv)"
    res = run_embed_python(['-'], input=code)
    assert res.stdout == "__main__ ['-']\n"

    res = run_embed_python(['-', 'beep.py', '2', '3'], input=code)
    assert res.stdout == "__main__ ['-', 'beep.py', '2', '3']\n"


def test_script(tmpdir):
    code = "import sys; print(__name__, sys.argv)"
    script = tmpdir / "beep.py"
    script.write_text(code, encoding="utf-8")
    res = run_embed_python([str(script)])
    assert res.stdout == f"__main__ [{repr(str(script))}]\n"

    beep = tmpdir / "beep.py"
    beep.write_text("import sys; print(sys.argv); import boop", encoding="utf-8")
    boop = tmpdir / "boop.py"
    boop.write_text("print('boop')", encoding="utf-8")
    res = run_embed_python([str(beep)])
    assert res.stdout == f"[{repr(str(beep))}]\nboop\n", (
        "module 'beep' must be able to load the module 'boop' because they are "
        "in the same directory"
    )


@pytest.mark.skip(reason="must search for modules starting from the working directory")
def test_module(tmpdir):
    code = "import sys; print(__name__, sys.argv)"
    script = tmpdir / "beep.py"
    script.write_text(code, encoding="utf-8")
    res = run_embed_python(["-m", "beep", "ahk.py", "1", "2"], cwd=tmpdir)
    assert res.stdout == f"__main__ [{repr(str(script))}, 'ahk.py', '1', '2']\n"


def test_system_exit():
    res = run_from_input("import sys; sys.exit()")
    assert res.returncode == 0

    res = run_from_input("import sys; sys.exit(1)")
    assert res.returncode == 1

    res = run_from_input("import sys; sys.exit(2)")
    assert res.returncode == 2

    res = run_from_input("import sys; sys.exit('bye')")
    assert res.returncode == 1
    assert res.stderr == 'bye\n'

    res = run_from_input("raise SystemExit")
    assert res.returncode == 0

    res = run_from_input("raise SystemExit(None)")
    assert res.returncode == 0

    res = run_from_input("raise SystemExit(1)")
    assert res.returncode == 1


def run_embed_python(args, **kwargs):
    args = [AHK, EMBED_PYTHON, *args]
    return subprocess.run(args, text=True, capture_output=True, **kwargs)


def run_from_input(code):
    return run_embed_python(['-'], input=code)
