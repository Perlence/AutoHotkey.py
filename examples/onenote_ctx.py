import ahkpy as ahk


onenote_ctx = ahk.windows.active_window_context(title="- OneNote for Windows 10$", match="regex")
# Send em dash when typing double dashes
onenote_ctx.hotstring("--", "—", wait_for_end_char=False)
# Add line before
onenote_ctx.hotkey("^+Enter", ahk.send, "{Home}{Enter}{Up}")
# Add line after
onenote_ctx.hotkey("^Enter", ahk.send, "{End}{Enter}")
