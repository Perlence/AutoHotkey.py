"""Map LCtrl+Arrow keys to Home, End, Page Up, and Page Down.

This works with modifiers too: pressing LCtrl+Shift+Down sends Shift+PageDown.
"""

import ahkpy as ahk


def remap_ctrl_arrow(src, dest):
    if ahk.is_key_pressed("LCtrl"):
        ahk.send("{Blind}{LCtrl Up}{%s DownR}{LCtrl Down}" % dest)
    else:
        ahk.send("{Blind}{%s DownR}" % src)


ahk.hotkey("*Left", remap_ctrl_arrow, "Left", "Home")
ahk.hotkey("*Right", remap_ctrl_arrow, "Right", "End")
ahk.hotkey("*Up", remap_ctrl_arrow, "Up", "PgUp")
ahk.hotkey("*Down", remap_ctrl_arrow, "Down", "PgDn")
ahk.hotkey("*Delete", remap_ctrl_arrow, "Delete", "Insert")

# The following hotkeys resolve the stuck arrow keys in some games.
ahk.hotkey("*Left Up", ahk.send, "{Blind}{Left Up}")
ahk.hotkey("*Right Up", ahk.send, "{Blind}{Right Up}")
ahk.hotkey("*Up Up", ahk.send, "{Blind}{Up Up}")
ahk.hotkey("*Down Up", ahk.send, "{Blind}{Down Up}")
ahk.hotkey("*Delete Up", ahk.send, "{Blind}{Delete Up}")
