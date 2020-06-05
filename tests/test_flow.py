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

        ahk.hotkey("^t", lambda: None)  # Make the script persistent

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

        ahk.hotkey("^t", lambda: None)  # Make the script persistent

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
