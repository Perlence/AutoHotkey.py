import os

import pytest

import _ahk  # noqa
import ahk


# TODO: sys.stdout is not in utf-8.


def test_call():
    with pytest.raises(TypeError, match="missing 1 required"):
        _ahk.call()

    with pytest.raises(ahk.Error, match="unknown function"):
        _ahk.call("NoSuchFunction")

    os.environ["HELLO"] = "Привет"
    hello = _ahk.call("EnvGet", "HELLO")
    assert hello == os.environ["HELLO"]

    temp = _ahk.call("EnvGet", "TEMP")
    assert isinstance(temp, str), "EnvGet result must be a string"

    rnd = _ahk.call("Random", 42, "42")
    assert isinstance(rnd, int), "Random result must be an integer"
    assert rnd == 42, f"Result must be 42, got {rnd}"

    assert _ahk.call("Random", 1, True) == 1, "Result must be 1"

    val = _ahk.call("Max", 9223372036854775807)
    assert val == 9223372036854775807, f"Result must be 9223372036854775807, got {val}"

    val = _ahk.call("Min", -9223372036854775806)
    assert val == -9223372036854775806, f"Result must be -9223372036854775806, got {val}"

    with pytest.raises(OverflowError, match="too big to convert"):
        val = _ahk.call("Max", 9223372036854775808)

    val = _ahk.call("Min", 0.5)
    assert val == 0.5, f"Result must be 0.5, got {val}"

    with pytest.raises(ahk.Error, match="cannot convert '<object object"):
        _ahk.call("Min", object())

    assert _ahk.call("Array", 1, 2, 3) == {1: 1, 2: 2, 3: 3}
    assert _ahk.call("Object", "a", 1, "b", 2, "c", 3) == {"a": 1, "b": 2, "c": 3}
