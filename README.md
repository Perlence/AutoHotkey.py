# Python.ahk

Embed Python into AutoHotkey.

## Quickstart

Create a virtual environment for your script and activate it:

```bat
> py -m venv env
> env\Scripts\activate.bat
```

Install the package from the URL:

```bat
> py -m pip install git+https://github.com/Perlence/Python.ahk
```

Run the sample code:

```bat
> type con > playground.py
import ahk
ahk.message_box("Hello!")
^Z

> py -m ahk playground.py
```

## Supported Versions

- AutoHotkey 1.1
- Python 3.7 or greater

Python.ahk was tested on Windows 10 v2004, AutoHotkey v1.1.30.03, Python v3.8.1.
