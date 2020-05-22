import ctypes
import os
import sys
import _ahk  # noqa

ctypes.windll.user32.MessageBoxW(0, f"Hello from Python.", "AHK", 1)
print("Hello from stdout.")

# TODO: sys.stdout is not in utf-8.

os.environ["HELLO"] = "Привет"
hello = _ahk.call_cmd("EnvGet", "HELLO")
assert hello == os.environ["HELLO"]

temp = _ahk.call_cmd("EnvGet", "TEMP")
assert isinstance(temp, str), "EnvGet result must be a string"

rnd = _ahk.call_cmd("Random", "1", "10")
assert isinstance(rnd, int), "Random result must be an integer"

result = _ahk.call_cmd("MsgBox")
assert result == "", "MsgBox result must be an empty string"
_ahk.call_cmd("MsgBox", "Hello, мир!")
_ahk.call_cmd("MsgBox", "4", "", "Do you want to continue? (Press YES or NO)")

_ahk.call_cmd("Send", "#r")

import ahk

try:
    ahk.hotkey('')
except ahk.Error:
    pass
else:
    assert False, "ahk.hotkey('') must raise an error"

try:
    ahk.hotkey('^t', func='not callable')
except ahk.Error:
    pass
else:
    assert False, "passing a non-callable to ahk.hotkey must raise an error"

@ahk.hotkey('AppsKey & t')
def show_msgbox():
    _ahk.call_cmd("MsgBox", "Hello from hotkey.")

_ahk.call_cmd("MsgBox", "Press AppsKey & t now.")

@ahk.hotkey('AppsKey & y')
def show_bang():
    1 / 0

_ahk.call_cmd("MsgBox", "Press AppsKey & y to see an exception.")

try:
    _ahk.call_cmd("NoSuchCommand", "A")
except ahk.Error:
    pass
else:
    assert False, "call_cmd must raise an error when the command is unknown"

_ahk.call_cmd("MsgBox", "Done!")
_ahk.call_cmd("ExitApp")
