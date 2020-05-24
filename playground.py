import ctypes
import os
import sys

import _ahk  # noqa
import ahk

ctypes.windll.user32.MessageBoxW(0, f"Hello from Python.", "AHK", 0)
print("Hello from stdout.")

# TODO: sys.stdout is not in utf-8.

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

try:
    val = _ahk.call("Max", 9223372036854775808)
except OverflowError:
    pass
else:
    assert False, "Passing 9223372036854775808 must throw an OverflowError"

val = _ahk.call("Min", 0.5)
assert val == 0.5, f"Result must be 0.5, got {val}"

result = ahk.message_box()
assert result == "", "MsgBox result must be an empty string"
ahk.message_box("Hello, мир!")
ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)

_ahk.call("Send", "#r")

try:
    _ahk.call()
except _ahk.Error:
    pass
else:
    assert False, "_ahk.call() without arguments must raise an error"

try:
    _ahk.call("NoSuchFunction")
except _ahk.Error:
    pass
else:
    assert False, "_ahk.call() to a non-existent function must raise an error"

import ahk

try:
    ahk.hotkey("")
except ahk.Error:
    pass
else:
    assert False, "ahk.hotkey("") must raise an error"

try:
    ahk.hotkey("^t", func="not callable")
except ahk.Error:
    pass
else:
    assert False, "passing a non-callable to ahk.hotkey must raise an error"

@ahk.hotkey("AppsKey & t")
def show_msgbox():
    ahk.message_box("Hello from hotkey.")

ahk.message_box("Press AppsKey & t now.")

@ahk.hotkey("AppsKey & y")
def show_bang():
    1 / 0

ahk.message_box("Press AppsKey & y to see an exception.")

try:
    _ahk.call("NoSuchCommand", "A")
except ahk.Error:
    pass
else:
    assert False, "_ahk.call() must raise an error when the command is unknown"

if ahk.get_key_state("LShift"):
    ahk.message_box("LShift is pressed")
else:
    ahk.message_box("LShift is not pressed")

ahk.message_box("Done!")
_ahk.call("ExitApp")