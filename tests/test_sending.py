import time

import pytest

import ahkpy as ahk


def test_send_level(child_ahk):
    with pytest.raises(ValueError, match="level must be between 0 and 100"):
        ahk.send("{F13}", level=-1)
    with pytest.raises(ValueError, match="level must be between 0 and 100"):
        ahk.send("{F13}", level=101)

    called = False

    @ahk.hotkey("F15", input_level=10)
    def f15():
        nonlocal called
        called = True

    # Use SendEvent here because hotkeys with input_level > 0 use keyboard hook
    # and SendInput temporarily disables that hook.
    ahk.send_event("{F15}")
    ahk.sleep(0)  # Let AHK process the hotkey.
    assert not called

    ahk.send_event("{F15}", level=20)
    ahk.sleep(0)
    assert called


def test_fallback_to_send_event_on_delay(notepad):
    start = time.perf_counter()
    ahk.send("abcdef", key_delay=0.01)
    end = time.perf_counter()
    assert end - start >= 6 * 0.01
