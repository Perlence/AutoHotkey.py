import ctypes
import os
import sys
import unittest

import _ahk  # noqa
import ahk

# TODO: sys.stdout is not in utf-8.


class TestEmbedPython(unittest.TestCase):

    def test_call(self):
        with self.assertRaises(ahk.Error, msg="_ahk.call() without arguments must raise an error"):
            _ahk.call()

        with self.assertRaises(ahk.Error, msg="_ahk.call() to a non-existent function must raise an error"):
            _ahk.call("NoSuchFunction")

        os.environ["HELLO"] = "Привет"
        hello = _ahk.call("EnvGet", "HELLO")
        self.assertEqual(hello, os.environ["HELLO"])

        temp = _ahk.call("EnvGet", "TEMP")
        self.assertIsInstance(temp, str, "EnvGet result must be a string")

        rnd = _ahk.call("Random", 42, "42")
        self.assertIsInstance(rnd, int, "Random result must be an integer")
        self.assertEqual(rnd, 42, f"Result must be 42, got {rnd}")

        self.assertEqual(_ahk.call("Random", 1, True), 1, "Result must be 1")

        val = _ahk.call("Max", 9223372036854775807)
        self.assertEqual(val, 9223372036854775807, f"Result must be 9223372036854775807, got {val}")

        val = _ahk.call("Min", -9223372036854775806)
        self.assertEqual(val, -9223372036854775806, f"Result must be -9223372036854775806, got {val}")

        with self.assertRaises(OverflowError):
            val = _ahk.call("Max", 9223372036854775808)

        val = _ahk.call("Min", 0.5)
        self.assertEqual(val, 0.5, f"Result must be 0.5, got {val}")

        with self.assertRaisesRegex(ahk.Error, "cannot convert '<object object"):
            _ahk.call("Min", object())

    def test_message_box(self):
        result = ahk.message_box()
        self.assertEqual(result, "", "MsgBox result must be an empty string")
        ahk.message_box("Hello, мир!")
        ahk.message_box("Do you want to continue? (Press YES or NO)", options=4)

    def test_hotkey(self):
        with self.assertRaises(ahk.Error):
            ahk.hotkey("")

        with self.assertRaises(ahk.Error, msg="passing a non-callable to ahk.hotkey must raise an error"):
            ahk.hotkey("^t", func="not callable")

        @ahk.hotkey("AppsKey & t")
        def show_msgbox():
            ahk.message_box("Hello from hotkey.")

        ahk.message_box("Press AppsKey & t now.")

        @ahk.hotkey("AppsKey & y")
        def show_bang():
            1 / 0

        ahk.message_box("Press AppsKey & y to see an exception.")

    def test_get_key_state(self):
        ahk.message_box("Press LShift.")
        if ahk.get_key_state("LShift"):
            ahk.message_box("LShift is pressed")
        else:
            ahk.message_box("LShift is not pressed")


if __name__ == "__main__":
    unittest.main(exit=False)
    _ahk.call("ExitApp")
