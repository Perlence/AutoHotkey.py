"""Switch between the windows of the active application.

Pressing the Escape key repeatedly while the Alt key is held down switches
through all application windows in MRU order.
"""

import ahkpy as ahk


app_win_index = 0


@ahk.hotkey("!Escape")  # Alt+Escape
def switch_between_app_windows():
    process_name = ahk.windows.get_active().process_name
    app_windows = list(ahk.windows.filter(exe=process_name))
    if len(app_windows) < 2:
        return

    global app_win_index
    app_win_index = min(app_win_index + 1, len(app_windows) - 1)
    app_windows[app_win_index].activate()


@ahk.hotkey("~Alt Up")  # Listen to the "Alt key released" event without inhibiting its function
def reset_app_win_index():
    global app_win_index
    app_win_index = 0
