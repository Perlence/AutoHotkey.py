"""Switch between the windows of the active application.

Pressing the Escape key repeatedly while the Alt key is held down switches
through all application windows in MRU order.
"""

from ctypes import windll

import ahkpy as ahk


app_win_index = 0


@ahk.hotkey("!Escape")  # Alt+Escape
def switch_between_app_windows():
    active_win = ahk.windows.get_active()
    if active_win.class_name == "MultitaskingViewFrame":
        # Alt+Tab window is active. Pressing Alt+Escape should close it without
        # switching the windows.
        ahk.send("!{Escape}")
        return

    process_name = active_win.process_name
    app_windows = [
        win
        # Filter all windows to find windows on all virtual desktops.
        for win in ahk.all_windows.filter(exe=process_name)
        if is_alt_tab_window(win)
    ]
    if len(app_windows) < 2:
        return

    global app_win_index
    app_win_index = min(app_win_index + 1, len(app_windows) - 1)
    app_windows[app_win_index].activate()


@ahk.hotkey("~Alt Up")  # Listen to the "Alt key released" event without inhibiting its function
def reset_app_win_index():
    global app_win_index
    app_win_index = 0


def is_alt_tab_window(win):
    if not win.is_visible:
        return False
    if not win.title:
        return False

    style = win.style
    ex_style = win.ex_style
    if style is None or ex_style is None:
        return False
    if ahk.ExWindowStyle.APPWINDOW in ex_style:
        return True
    if ahk.ExWindowStyle.TOOLWINDOW in ex_style:
        return False
    if ahk.ExWindowStyle.NOACTIVATE in ex_style:
        return False

    if win.class_name == "Windows.UI.Core.CoreWindow":
        return False
    if is_uwp_app_cloaked(win):
        return False

    return True


def is_uwp_app_cloaked(win):
    if win.class_name != "ApplicationFrameWindow":
        return False
    cloak_type = windll.user32.GetPropW(win.id, "ApplicationViewCloakType")
    return cloak_type == 1
