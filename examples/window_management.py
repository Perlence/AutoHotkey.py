import ahkpy as ahk


ahk.hotkey("AppsKey & a", lambda: ahk.windows.get_active().toggle_always_on_top())
ahk.hotkey("AppsKey & h", lambda: ahk.windows.get_active().minimize())
ahk.hotkey("AppsKey & Left", ahk.send, "#{Left}")
ahk.hotkey("AppsKey & Right", ahk.send, "#{Right}")
ahk.hotkey("AppsKey & Up", lambda: ahk.windows.get_active().toggle_maximized())
ahk.hotkey("AppsKey & Down", lambda: ahk.windows.get_active().toggle_minimized())
