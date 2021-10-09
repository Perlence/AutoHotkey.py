import sys

import pytest

import ahkpy as ahk


def test_validation():
    t = ahk.Timer(func=None)
    with pytest.raises(TypeError, match="must not be None"):
        t.update()


def test_refcounts(request):
    func = lambda: None  # noqa: E731
    timer = ahk.set_countdown(1, func)
    request.addfinalizer(timer.stop)
    func_refcount = sys.getrefcount(func)
    timer.stop()
    assert sys.getrefcount(func) == func_refcount - 1

    timer = ahk.set_countdown(0.01, func)
    func_refcount = sys.getrefcount(func)
    ahk.sleep(0.02)
    assert sys.getrefcount(func) == func_refcount - 1


def test_timer(child_ahk):
    def code():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F24", lambda: None)  # Make the script persistent

        @ahk.set_countdown(0.1)
        def dong():
            print("Dong!")
            sys.exit()

        print("Ding!")

    res = child_ahk.run_code(code)
    assert res.stderr == ""
    assert res.stdout == "Ding!\nDong!\n"
    assert res.returncode == 0


def test_timer_stop(child_ahk):
    def code():
        import ahkpy as ahk
        import sys

        ahk.hotkey("F24", lambda: None)  # Make the script persistent

        @ahk.set_timer(0.1)
        def ding():
            print("Ding!")
            ding.stop()

        @ahk.set_countdown(0.5)
        def exit():
            sys.exit()

    res = child_ahk.run_code(code)
    assert res.stderr == ""
    assert res.stdout == "Ding!\n"
    assert res.returncode == 0


def test_timer_update(request):
    times = []

    timer = ahk.set_timer(1, times.append, 1)
    request.addfinalizer(timer.stop)

    timer.update(interval=0.1)
    ahk.sleep(0.59)
    timer.stop()
    assert len(times) == 5

    times.clear()
    assert timer.interval == 0.1
    timer.start()
    ahk.sleep(0.06)
    timer.update(priority=40)  # Updating priority should not restart the timer
    ahk.sleep(0.06)
    assert len(times) == 1


def test_countdown_start(request):
    times = []

    timer = ahk.set_countdown(1, times.append, 1)
    request.addfinalizer(timer.stop)

    timer.start(interval=0.1)  # Restart a non-finished countdown
    ahk.sleep(0.11)
    assert len(times) == 1

    timer.start()  # Start a finished countdown with its previous interval
    ahk.sleep(0.11)
    assert len(times) == 2


def test_change_periodic(request):
    times = []

    timer = ahk.set_timer(0.1, times.append, 1)
    request.addfinalizer(timer.stop)

    ahk.sleep(0.29)
    assert len(times) == 2

    times.clear()
    timer.update(periodic=False)
    ahk.sleep(0.29)
    assert len(times) == 1


def test_timer_returns(child_ahk):
    def timers():
        import ahkpy as ahk
        import sys
        ahk.hotkey("F24", sys.exit)
        ahk.set_countdown(0.01, object)
        print("ok00")

    child_ahk.popen_code(timers)
    child_ahk.wait(0)

    assert not ahk.windows.wait(
        title="Python.ahk",
        text="Error:  cannot convert '<object object",
        timeout=0.1,
    )

    ahk.send("{F24}")
