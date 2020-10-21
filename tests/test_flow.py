import subprocess
import sys

import pytest

import ahkpy as ahk


def test_sleep(child_ahk):
    def code():
        import ahkpy as ahk
        ahk.set_countdown(lambda: print(1), interval=0.1)
        ahk.sleep(0.2)  # sleep longer than the countdown
        print(2)
        # sys.exit()
        # ahk.message_box(2)
        # 1/0

    proc = child_ahk.run_code(code)
    assert proc.stderr == ""
    assert proc.stdout == "1\n2\n"
    assert proc.returncode == 0

    def code():
        import ahkpy as ahk
        import threading
        ahk.set_countdown(lambda: print(1), interval=0.1)
        threading.Timer(0.2, lambda: print(2)).start()
        ahk.sleep(0.3)
        print(3)

    proc = child_ahk.run_code(code)
    assert proc.stderr == ""
    assert proc.stdout == "1\n2\n3\n"
    assert proc.returncode == 0


class TestTimer:
    def test_refcounts(self, request):
        func = lambda: None  # noqa: E731
        timer = ahk.set_countdown(func, interval=1)
        request.addfinalizer(timer.stop)
        func_refcount = sys.getrefcount(func)
        timer.stop()
        assert sys.getrefcount(func) == func_refcount - 1

        timer = ahk.set_countdown(func, interval=0.01)
        func_refcount = sys.getrefcount(func)
        ahk.sleep(0.01)
        assert sys.getrefcount(func) == func_refcount - 1

    def test_timer(self, child_ahk):
        def code():
            import ahkpy as ahk
            import sys

            ahk.hotkey("F24", lambda: None)  # Make the script persistent

            @ahk.set_countdown(interval=0.1)
            def dong():
                print("Dong!")
                sys.exit()

            print("Ding!")

        res = child_ahk.run_code(code)
        assert res.stderr == ""
        assert res.stdout == "Ding!\nDong!\n"
        assert res.returncode == 0

    def test_timer_stop(self, child_ahk):
        def code():
            import ahkpy as ahk
            import sys

            ahk.hotkey("F24", lambda: None)  # Make the script persistent

            @ahk.set_timer(interval=0.1)
            def ding():
                print("Ding!")
                ding.stop()

            @ahk.set_countdown(interval=0.5)
            def exit():
                sys.exit()

        res = child_ahk.run_code(code)
        assert res.stderr == ""
        assert res.stdout == "Ding!\n"
        assert res.returncode == 0

    def test_timer_update(self, request):
        times = []

        timer = ahk.set_timer(lambda: times.append(1), interval=1)
        request.addfinalizer(timer.stop)

        timer.update(interval=0.1)
        ahk.sleep(0.59)
        timer.stop()
        assert len(times) == 5

        times = []
        assert timer.interval == 0.1
        timer.start()
        ahk.sleep(0.06)
        timer.update(priority=40)  # Updating priority should not restart the timer
        ahk.sleep(0.06)
        assert len(times) == 1

    def test_countdown_start(self, request):
        times = []

        timer = ahk.set_countdown(lambda: times.append(1), interval=1)
        request.addfinalizer(timer.stop)

        timer.start(interval=0.1)  # Restart a non-finished countdown
        ahk.sleep(0.1)
        assert len(times) == 1

        timer.start()  # Start a finished countdown with its previous interval
        ahk.sleep(0.1)
        assert len(times) == 2

    def test_change_periodic(self, request):
        times = []

        timer = ahk.set_timer(lambda: times.append(1), interval=0.1)
        request.addfinalizer(timer.stop)

        ahk.sleep(0.29)
        assert len(times) == 2

        times = []
        timer.update(periodic=False)
        ahk.sleep(0.29)
        assert len(times) == 1


def test_suspend(child_ahk):
    def code():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F13", print, "ok01")

        @ahk.hotkey("F14")
        def sus():
            ahk.suspend()
            print("ok02")

        ahk.set_countdown(sys.exit, interval=0.5)
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
        import ahkpy as ahk
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
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", ahk.reload)
        ahk.message_box("ok00")

    script = tmpdir / "code.py"
    script.write(child_ahk._extract_code(code))
    child_ahk.popen([script])
    assert ahk.windows.wait(title="Python.ahk", text="ok00", timeout=1)

    ahk.send("{F13}")
    assert ahk.windows.wait_close(title="Python.ahk", text="ok00", timeout=1)
    assert ahk.windows.wait(title="Python.ahk", text="ok00", timeout=1)

    ahk.send("{F24}")


def test_coop(child_ahk):
    def code():
        import runpy
        import sys
        import ahkpy as ahk

        ahk.hotkey("F24", sys.exit)
        ahk.hotkey("F13", ahk.message_box, "hello")

        print("ok00")

        ahk.coop(
            runpy.run_module,
            mod_name="http.server",
            run_name="__main__",
            alter_sys=True,
        )

    proc = child_ahk.popen_code(code)
    child_ahk.wait(0)

    assert proc.stdout.readline().startswith("Serving HTTP")

    from urllib.request import urlopen
    resp = urlopen("http://localhost:8000")
    assert b"Directory listing for /" in resp.read()

    assert '"GET / HTTP/1.1" 200' in proc.stderr.readline()

    ahk.send("{F13}")
    assert ahk.windows.wait_active(title="Python.ahk", text="hello", timeout=1)

    # TODO: Test sending KeyboardInterrupt.
    ahk.send("{F24}")


@pytest.mark.xfail
def test_settings_bleed(settings):
    settings.win_delay = 0.1

    win_delays = []

    def f():
        with ahk.local_settings() as local:
            win_delays.append(ahk.get_settings().win_delay)
            local.win_delay = 0  # This must not affect other callbacks
            ahk.sleep(0.02)

    ahk.set_countdown(f, 0.01)
    ahk.set_countdown(f, 0.02)
    ahk.sleep(0.03)

    assert win_delays == [0.1, 0.1]
