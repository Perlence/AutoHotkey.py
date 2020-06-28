@echo off
"C:\Program Files\AutoHotkey\AutoHotkey.exe" "%~p0\EmbedPython.ahk" %* 2>&1 | wsl cat
