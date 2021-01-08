import pytest

import ahkpy as ahk


def test_get_key_state(child_ahk):
    with pytest.raises(ValueError, match="'beep' is not a valid key or the state of the key could not be determined"):
        ahk.is_key_pressed("beep")

    assert ahk.is_key_pressed("F13") is False
    ahk.send("{F13 Down}")
    assert ahk.is_key_pressed("F13") is True
    ahk.send("{F13 Up}")
    assert ahk.is_key_pressed("F13") is False


def test_get_key():
    key = "LWin"
    assert ahk.get_key_name(key) == "LWin"
    assert ahk.get_key_vk(key) == 0x5b
    assert ahk.get_key_sc(key) == 0x15b
    assert ahk.get_key_name("vk5b") == "LWin"
    assert ahk.get_key_name("sc15b") == "LWin"

    assert ahk.get_key_name(1) == "1"

    with pytest.raises(ValueError, match="is not a valid key"):
        ahk.get_key_vk("noooo")


def test_key_wait(child_ahk):
    def code():
        import ahkpy as ahk
        import sys

        print("ok00")
        result = ahk.wait_key_pressed("RShift")
        assert result is True, f"result must be True, got {result!r}"
        print("ok01")
        result = ahk.wait_key_released("RShift")
        assert result is True, f"result must be True, got {result!r}"
        print("ok02")

        result = ahk.wait_key_pressed("RShift", timeout=.1)
        assert result is False, f"result must be False, got {result!r}"
        print("ok03")

        sys.exit()

    proc = child_ahk.popen_code(code)

    child_ahk.wait(0)
    ahk.send("{RShift Down}")
    child_ahk.wait(1)
    ahk.send("{RShift Up}")
    child_ahk.wait(2)

    child_ahk.wait(3)
    child_ahk.close()
    assert proc.returncode == 0


def test_lock_state(request):
    initial_state = ahk.get_caps_lock_state()
    assert isinstance(initial_state, bool)
    request.addfinalizer(lambda: ahk.set_caps_lock_state(initial_state))

    ahk.set_caps_lock_state(True)
    assert ahk.get_caps_lock_state() is True
    ahk.set_caps_lock_state(False)
    assert ahk.get_caps_lock_state() is False
