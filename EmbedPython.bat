@echo off
"C:\Program Files\AutoHotkey\AutoHotkey.exe" "%~dn0.ahk" %* 2>&1 | wsl cat
