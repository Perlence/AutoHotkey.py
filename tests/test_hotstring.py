import pytest

import ahkpy as ahk
from .conftest import assert_equals_eventually


class TestHotstring:
    @pytest.fixture(autouse=True)
    def send_level(self, settings):
        settings.send_level = 10
        # Typing via the default "input" mode doesn't trigger hotstrings because
        # hotstrings use keyboard hook to monitor key strokes and SendInput
        # temporarily deactivates that hook.
        settings.send_mode = "event"

    @pytest.fixture
    def edit(self, notepad):
        edit = notepad.get_control("Edit1")
        edit.text = ""
        assert edit.text == ""
        yield edit
        edit.text = ""
        assert edit.text == ""

    def test_simple(self, request, edit):
        dashes = ahk.hotstring("nepotism", "msitopen")
        request.addfinalizer(dashes.disable)
        ahk.send_event("nepotism")
        assert_equals_eventually(lambda: edit.text, "nepotism")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "msitopen ")

    def test_wait_for_and_omit_end_char(self, request, edit):
        hs = ahk.hotstring("j@", "j2", wait_for_end_char=False)
        request.addfinalizer(hs.disable)
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        hs.update(wait_for_end_char=False, omit_end_char=False)
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        hs.update(wait_for_end_char=False, omit_end_char=True)
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        hs.update(omit_end_char=False)  # wait_for_end_char=False implied
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        hs.update(omit_end_char=True)
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        hs.update(wait_for_end_char=True)  # omit_end_char implied
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        hs.update(wait_for_end_char=True, omit_end_char=False)
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "j2 ")

        edit.text = ""
        hs.update(wait_for_end_char=True, omit_end_char=True)
        ahk.send_event("j@")
        assert_equals_eventually(lambda: edit.text, "j@")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "j2")

        edit.text = ""
        dashes = ahk.hotstring("crabwise", "esiwbarc")
        request.addfinalizer(dashes.disable)
        dashes.update(wait_for_end_char=False)
        ahk.send_event("crabwise")
        assert_equals_eventually(lambda: edit.text, "esiwbarc")

        edit.text = ""
        dashes.update(wait_for_end_char=True)
        ahk.send_event("crabwise")
        assert_equals_eventually(lambda: edit.text, "crabwise")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "esiwbarc ")

    def test_on_off(self, request, edit):
        beep = ahk.hotstring("beep", "boop")
        request.addfinalizer(beep.disable)
        ahk.send_event("Beep ")
        assert_equals_eventually(lambda: edit.text, "Boop ")

        edit.text = ""
        beep.disable()
        ahk.send_event("Beep ")
        assert_equals_eventually(lambda: edit.text, "Beep ")

        edit.text = ""
        beep.enable()
        ahk.send_event("Beep ")
        assert_equals_eventually(lambda: edit.text, "Boop ")

        edit.text = ""
        beep.toggle()
        ahk.send_event("Beep ")
        assert_equals_eventually(lambda: edit.text, "Beep ")

    def test_case_sensitive(self, request, edit):
        case = ahk.hotstring("CaSe", "EsAc", case_sensitive=True)
        request.addfinalizer(case.disable)
        ahk.send_event("case ")
        assert_equals_eventually(lambda: edit.text, "case ")
        ahk.send_event("CaSe ")
        assert_equals_eventually(lambda: edit.text, "case EsAc ")

    def test_decorator(self, request, edit):
        @ahk.hotstring("blarp")
        def blarp():
            ahk.send_event("boop ")

        request.addfinalizer(blarp.disable)
        ahk.send_event("blarp")
        assert_equals_eventually(lambda: edit.text, "blarp")
        ahk.send_event(" ")
        assert_equals_eventually(lambda: edit.text, "boop ")

    def test_replace_inside_word(self, request, edit):
        airline = ahk.hotstring("al", "airline", replace_inside_word=True)
        request.addfinalizer(airline.disable)
        ahk.send_event("practical ")
        assert_equals_eventually(lambda: edit.text, "practicairline ")

    def test_no_backspacing(self, request, edit):
        em = ahk.hotstring("<em>", "</em>{left 5}", wait_for_end_char=False, backspacing=False)
        request.addfinalizer(em.disable)
        ahk.send_event("hello <em>world")
        assert_equals_eventually(lambda: edit.text, "hello <em>world</em>")

    def test_conform_to_case(self, request, edit):
        pillow = ahk.hotstring("pillow", "wollip", conform_to_case=False)
        request.addfinalizer(pillow.disable)
        ahk.send_event("pillow ")
        assert_equals_eventually(lambda: edit.text, "wollip ")

        edit.text = ""
        ahk.send_event("PILLOW ")
        assert_equals_eventually(lambda: edit.text, "wollip ")

        edit.text = ""
        ahk.send_event("PiLLoW ")
        assert_equals_eventually(lambda: edit.text, "wollip ")

    def test_reset_recognizer(self, request, edit):
        @ahk.hotstring("11", backspacing=False, wait_for_end_char=False, replace_inside_word=True)
        def eleven():
            ahk.send_event("xx", level=0)

        request.addfinalizer(eleven.disable)
        ahk.send_event("11")
        assert_equals_eventually(lambda: edit.text, "11xx")
        ahk.send_event("1 ")
        assert_equals_eventually(lambda: edit.text, "11xx1 xx")

        edit.text = ""
        eleven.update(reset_recognizer=True)
        ahk.send_event("11")
        assert_equals_eventually(lambda: edit.text, "11xx")
        ahk.send_event("1 ")
        assert_equals_eventually(lambda: edit.text, "11xx1 ")

    def test_text(self, request, edit):
        gyre = ahk.hotstring("gyre", "{F13}eryg", text=True)
        request.addfinalizer(gyre.disable)
        ahk.send_event("gyre ")
        assert_equals_eventually(lambda: edit.text, "{F13}eryg ")

    def test_active_window_context(self, request, edit):
        notepad_ctx = ahk.windows.active_window_context(class_name="Notepad")
        padnote = notepad_ctx.hotstring("notepad", "padnote")
        request.addfinalizer(padnote.disable)
        ahk.send_event("notepad ")
        assert_equals_eventually(lambda: edit.text, "padnote ")

    def test_reset_hotstring(self, request, edit):
        malaise = ahk.hotstring("malaise", "redacted")
        request.addfinalizer(malaise.disable)
        ahk.send_event("malaise ")
        assert_equals_eventually(lambda: edit.text, "redacted ")

        edit.text = ""
        ahk.send_event("mala")
        ahk.reset_hotstring()
        ahk.send_event("ise ")
        assert_equals_eventually(lambda: edit.text, "malaise ")

    def test_end_chars(self, request, edit):
        vivacious = ahk.hotstring("vivacious", "redacted")
        request.addfinalizer(vivacious.disable)
        prior_end_chars = ahk.get_hotstring_end_chars()
        request.addfinalizer(lambda: ahk.set_hotstring_end_chars(prior_end_chars))
        ahk.set_hotstring_end_chars(".")
        assert ahk.get_hotstring_end_chars() == "."

        ahk.send_event("vivacious ")
        assert_equals_eventually(lambda: edit.text, "vivacious ")

        edit.text = ""
        ahk.send_event("vivacious.")
        assert_equals_eventually(lambda: edit.text, "redacted.")

    def test_mouse_reset(self, request, edit):
        ferret = ahk.hotstring("ferret", "redacted")
        request.addfinalizer(ferret.disable)
        prior_mouse_reset = ahk.get_hotstring_mouse_reset()
        request.addfinalizer(lambda: ahk.set_hotstring_mouse_reset(prior_mouse_reset))

        ahk.set_hotstring_mouse_reset(True)
        ahk.get_hotstring_mouse_reset() is True
        ahk.send_event("fer")
        ahk.mouse_move(x=0, y=0)
        ahk.click(mode="event")
        ahk.send_event("ret ")
        assert_equals_eventually(lambda: edit.text, "ferret ")

        edit.text = ""
        ahk.set_hotstring_mouse_reset(False)
        ahk.get_hotstring_mouse_reset() is False
        ahk.send_event("fer")
        ahk.mouse_move(x=0, y=0)
        ahk.click(mode="event")
        ahk.send_event("ret ")
        assert_equals_eventually(lambda: edit.text, "redacted ")

    def test_hotstring_returns(self, child_ahk):
        def hotstrings():
            import ahkpy as ahk
            import sys
            ahk.hotkey("F24", sys.exit)
            ahk.hotstring("517", object)
            print("ok00")

        child_ahk.popen_code(hotstrings)
        child_ahk.wait(0)

        ahk.send_event("517 ")
        assert not ahk.windows.wait(
            title="Python.ahk",
            text="Error:  cannot convert '<object object",
            timeout=0.1,
        )

        ahk.send("{F24}")
