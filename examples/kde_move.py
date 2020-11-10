"""Based on Easy Window Dragging -- KDE style (requires XP/2k/NT) -- by Jonny"""

import ahkpy as ahk


@ahk.hotkey("!LButton")
def kde_move():
    """Move the window under the cursor by pressing Alt and moving the mouse."""
    settings = ahk.local_settings().activate()  # Activate the copy of the current settings.
    settings.win_delay = 0
    x1, y1 = ahk.get_mouse_pos(relative_to="screen")
    win = ahk.get_window_under_mouse()
    if win.is_maximized:
        win.restore()
        win.x = x1
        win.y = y1
    while ahk.is_key_pressed("LButton") and win:
        x2, y2 = ahk.get_mouse_pos(relative_to="screen")
        win.x += x2 - x1
        win.y += y2 - y1
        x1, y1 = x2, y2
