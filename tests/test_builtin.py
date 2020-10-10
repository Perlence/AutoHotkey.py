import os

import pytest

import _ahk
import ahkpy as ahk


def test_call():
    with pytest.raises(TypeError, match="missing 1 required"):
        _ahk.call()

    with pytest.raises(ahk.Error, match="unknown function"):
        _ahk.call("NoSuchFunction")

    os.environ["HELLO"] = "Привет 世界"
    hello = _ahk.call("EnvGet", "HELLO")
    assert hello == os.environ["HELLO"]

    temp = _ahk.call("EnvGet", "TEMP")
    assert isinstance(temp, str)

    rnd = _ahk.call("Min", -1, "-1")
    assert isinstance(rnd, int)
    assert rnd == -1

    rnd = _ahk.call("Min", 42, "42")
    assert isinstance(rnd, int)
    assert rnd == 42

    assert _ahk.call("Min", 1, True) == 1

    val = _ahk.call("Max", 9223372036854775807)
    assert val == 9223372036854775807

    val = _ahk.call("Min", -9223372036854775806)
    assert val == -9223372036854775806

    with pytest.raises(OverflowError, match="too big to convert"):
        val = _ahk.call("Max", 9223372036854775808)

    val = _ahk.call("Min", 0.5)
    assert val == 0.5

    with pytest.raises(ahk.Error, match="cannot convert '<object object"):
        _ahk.call("Min", object())

    assert _ahk.call("Array", 1, 2, 3) == {1: 1, 2: 2, 3: 3}
    assert _ahk.call("Object", "a", 1, "b", 2, "c", 3) == {"a": 1, "b": 2, "c": 3}
