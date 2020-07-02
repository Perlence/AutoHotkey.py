@echo off
"C:\Program Files\AutoHotkey\AutoHotkey.exe" "%~dp0Python.ahk" %* 2>&1 | wsl cat
