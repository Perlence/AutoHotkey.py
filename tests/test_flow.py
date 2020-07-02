import subprocess
from dataclasses import FrozenInstanceError

import pytest

import ahk


def test_sleep(child_ahk):
    def code():
        import ahk
        ahk.set_timer(lambda: print(1), countdown=0.1)
        ahk.sleep(0.2)  # sleep longer than the countdown
        print(2)
        # sys.exit()
        # ahk.message_box(2)
        # 1/0

    proc = child_ahk.run_code(code)
    assert proc.stdout == "1\n2\n"
    assert proc.stderr == ""
    assert proc.returncode == 0

    def code():
        import ahk
        import threading
        ahk.set_timer(lambda: print(1), countdown=0.1)
        threading.Timer(0.2, lambda: print(2)).start()
        ahk.sleep(0.3)
        print(3)

    proc = child_ahk.run_code(code)
    assert proc.stdout == "1\n2\n3\n"
    assert proc.stderr == ""
    assert proc.returncode == 0


def test_timer(child_ahk):
    timer = ahk.set_timer(lambda: None, countdown=1)
    with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
        timer.func = None

    timer.cancel()
    del timer

    def code():
        import ahk
        import sys

        ahk.hotkey("F24", lambda: None)  # Make the script persistent

        @ahk.set_timer(countdown=0.1)
        def dong():
            print("Dong!")
            sys.exit()

        print("Ding!")

    res = child_ahk.run_code(code)
    assert res.stdout == "Ding!\nDong!\n"
    assert res.stderr == ""
    assert res.returncode == 0

    def code():
        import ahk
        import sys

        ahk.hotkey("F24", lambda: None)  # Make the script persistent

        @ahk.set_timer(period=0.1)
        def ding():
            print("Ding!")
            ding.stop()

        @ahk.set_timer(countdown=0.5)
        def exit():
            sys.exit()

    res = child_ahk.run_code(code)
    assert res.stdout == "Ding!\n"
    assert res.stderr == ""
    assert res.returncode == 0


def test_suspend(child_ahk):
    def code():
        import ahk
        import sys

        ahk.hotkey("F13", lambda: print("ok01"))

        @ahk.hotkey("F14")
        def sus():
            ahk.suspend()
            print("ok02")

        ahk.set_timer(sys.exit, countdown=0.5)
        print("ok00")

    proc = child_ahk.popen_code(code)
    child_ahk.wait(0)

    ahk.send("{F13}")
    child_ahk.wait(1)

    ahk.send("{F14}")
    child_ahk.wait(2)

    ahk.send("{F13}")

    proc.wait()
    assert proc.stdout.read() == ""


def test_callback_after_error(child_ahk):
    def code():
        import ahk
        import sys
        ahk.hotkey("F24", sys.exit)

        @ahk.hotkey("F13")
        def _():
            # This executes after SystemExit was raised, but have not been
            # handled yet.
            pass

        ahk.send("{F13}")
        for _ in range(1_000_000):
            pass
        raise SystemExit()

    proc = child_ahk.popen_code(code)
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        ahk.send("{F24}")
    assert proc.stdout.read() == ""
    assert proc.stderr.read() == ""
    assert proc.returncode == 0


def test_reload(child_ahk, tmpdir):
    def code():
        import ahk
        import sys
        ahk.hotkey('F24', sys.exit)
        ahk.hotkey('F13', ahk.reload)
        ahk.message_box("ok00")

    script = tmpdir / "code.py"
    script.write(child_ahk._extract_code(code))
    child_ahk.popen([script])
    assert ahk.windows.wait(title="Python.ahk", text="ok00", timeout=1)

    ahk.send("{F13}")
    # ahk.sleep(0)
    assert ahk.windows.wait_close(title="Python.ahk", text="ok00", timeout=1)
    assert ahk.windows.wait(title="Python.ahk", text="ok00", timeout=1)

    ahk.send("{F24}")
