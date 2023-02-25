import ctypes
import os
import struct
import subprocess
import sys
from ctypes.wintypes import DWORD, HMODULE
from pathlib import Path


AHK = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"
EXIT_CODE_RESTART = 65530


def main():
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONEXECUTABLE"] = sys.executable
    os.environ["PYTHONDLL"] = python_dll_path()

    ahk_exe_path = fix_ahk_platform(get_ahk_exe_path())
    python_ahk_path = Path(__file__).parent / "Python.ahk"
    args = [ahk_exe_path, python_ahk_path] + sys.argv[1:]

    while True:
        ahk = subprocess.Popen(args, stdin=sys.stdin)

        while True:
            try:
                code = ahk.wait()
                if code is not None:
                    break
            except KeyboardInterrupt:
                # KeyboardInterrupt is automatically propagated to the subprocess.
                pass

        if ahk.returncode == EXIT_CODE_RESTART:
            print("Restarting AHK...", file=sys.stderr)
            continue

        # On Windows, Popen.returncode is unsigned int, while the sys.exit
        # function expects a signed int.
        signed_status = ctypes.c_int32(ahk.returncode)
        sys.exit(signed_status.value)


def python_dll_path():
    dllpath_size = 1024
    dllpath = ctypes.create_unicode_buffer(dllpath_size)
    dllpath_len = ctypes.windll.kernel32.GetModuleFileNameW(HMODULE(sys.dllhandle), dllpath, dllpath_size)
    if not dllpath_len:
        return ""
    return dllpath[:dllpath_len]


def get_ahk_exe_path():
    env_path = os.getenv("AUTOHOTKEY")
    if env_path:
        return env_path

    ahk_assoc = get_ahk_by_assoc()
    if ahk_assoc and Path(ahk_assoc).name.lower().startswith("autohotkey"):
        return ahk_assoc

    return AHK


def get_ahk_by_assoc():
    S_OK = 0
    S_FALSE = 1
    ASSOCF_NONE = 0
    ASSOCSTR_EXECUTABLE = 2
    out_len = DWORD(0)
    res = ctypes.windll.Shlwapi.AssocQueryStringW(
        ASSOCF_NONE,
        ASSOCSTR_EXECUTABLE,
        ".ahk",
        None,
        None,
        ctypes.byref(out_len),
    )
    if res != S_FALSE:
        return ""

    out = ctypes.create_unicode_buffer(1024)
    res = ctypes.windll.Shlwapi.AssocQueryStringW(
        ASSOCF_NONE,
        ASSOCSTR_EXECUTABLE,
        ".ahk",
        None,
        out,
        ctypes.byref(out_len),
    )
    if res != S_OK:
        return ""

    ahk_exe_path = out[:out_len.value].rstrip("\x00")
    return ahk_exe_path


def fix_ahk_platform(ahk_exe_path):
    p = Path(ahk_exe_path)
    if p.name.lower() == "autohotkey.exe":
        # Get the AHK binary of the same architecture as the Python interpreter.
        arch = struct.calcsize("P") * 8
        return f"{p.parent}\\{p.stem}U{arch}{p.suffix}"
    return ahk_exe_path


if __name__ == "__main__":
    main()
