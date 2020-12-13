"""Hotkeys to set the keyboard layouts.

Press CapsLock to switch to English (US) layout. Press Shift+CapsLock to switch
to Russian layout.
"""

from ctypes import windll

import ahkpy as ahk


def set_keyboard_layout(language_code):
    # This depends on having only two layouts in the Windows language list.
    # Inspired by GetCurrentLocale and ActiveWindow functions
    # https://github.com/BladeMight/Mahou/blob/9423423163/Mahou/Classes/Locales.cs#L20.
    # TODO: Handle Command Prompt windows.

    active_win = ahk.windows.get_active()
    focused_control = active_win.get_focused_control() or active_win
    if not focused_control:
        return

    thread_id = windll.user32.GetWindowThreadProcessId(focused_control.id, 0)
    if not thread_id:
        return

    current_layout = windll.user32.GetKeyboardLayout(thread_id)
    current_layout &= 0xffff
    if current_layout != language_code:
        ahk.send("#{Space}")


LANGID_ENGLISH_US = 0x0409
LANGID_RUSSIAN = 0x0419
# See more codes in the "Language Codes" article in AHK docs.

ahk.hotkey("CapsLock", set_keyboard_layout, LANGID_ENGLISH_US)
ahk.hotkey("+CapsLock", set_keyboard_layout, LANGID_RUSSIAN)
