# Changelog

## Version 0.2 (2023-03-12)

### Backward-incompatible changes

- Dropped support for Python 3.7.
- The `sys.executable` attribute now holds the absolute path to the Python
  executable that was used to start AutoHotkey, and `ahk.executable` holds the
  absolute path to the AutoHotkey executable, acting as AutoHotkey's `A_AhkPath`
  global variable. Previously, `sys.executable` held the path to the AutoHotkey
  executable.

### Changes

- Add the `MonitorWorkArea` support for the `SysGet` command.
- Made AutoHotkey.py work in a conda environment.
- Made the values of sys.executable, sys.prefix, sys.base_prefix, and sys.path
  match to the corresponding values from a regular Python interpreter.

## Version 0.1.2 (2021-10-09)

### Changes

- Fixed `get_clipboard()` returning a number instead of a string.

## Version 0.1.1 (2021-08-22)

### Changes

- Fixed the app freeze when closing the console window.

## Version 0.1 (2021-01-24)

First public release.
