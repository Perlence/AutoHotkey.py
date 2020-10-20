"""Map LCtrl+Arrow keys to Home, End, Page Up, and Page Down.

This works with modifiers too: pressing LCtrl+Shift+Down sends Shift+PageDown.
"""

from functools import partial

import ahkpy as ahk


def remap_ctrl_arrow(src, dest):
    if ahk.is_key_pressed("LCtrl"):
        ahk.send("{Blind}{LCtrl Up}{%s DownR}{LCtrl Down}" % dest)
    else:
        ahk.send("{Blind}{%s DownR}" % src)


ahk.hotkey("*Left", partial(remap_ctrl_arrow, "Left", "Home"))
ahk.hotkey("*Right", partial(remap_ctrl_arrow, "Right", "End"))
ahk.hotkey("*Up", partial(remap_ctrl_arrow, "Up", "PgUp"))
ahk.hotkey("*Down", partial(remap_ctrl_arrow, "Down", "PgDn"))
ahk.hotkey("*Delete", partial(remap_ctrl_arrow, "Delete", "Insert"))

# The following hotkeys resolve the stuck arrow keys in some games.
ahk.hotkey("*Left Up", partial(ahk.send, "{Blind}{Left Up}"))
ahk.hotkey("*Right Up", partial(ahk.send, "{Blind}{Right Up}"))
ahk.hotkey("*Up Up", partial(ahk.send, "{Blind}{Up Up}"))
ahk.hotkey("*Down Up", partial(ahk.send, "{Blind}{Down Up}"))
ahk.hotkey("*Delete Up", partial(ahk.send, "{Blind}{Delete Up}"))
