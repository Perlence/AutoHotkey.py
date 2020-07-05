import ctypes
import io
import os
import subprocess
import sys
import threading
from ctypes.wintypes import DWORD, HMODULE
from pathlib import Path


AHK = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"


def main():
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONNOUSERSITE"] = "1"
    os.environ["PYTHONFULLPATH"] = ';'.join(sys.path)
    os.environ["PYTHONDLL"] = python_dll_path()

    python_ahk_path = Path(__file__).parent / "Python.ahk"
    ahk_exe_path = get_ahk_by_assoc() or AHK
    args = [ahk_exe_path, python_ahk_path] + sys.argv[1:]
    ahk = subprocess.Popen(
        args,
        stdout=subprocess.PIPE if sys.stdout else None,
        stderr=subprocess.PIPE if sys.stderr else None,
        bufsize=0,
    )

    if sys.stderr:
        th = threading.Thread(target=read_loop, args=(ahk.stderr, sys.stderr.buffer), daemon=True)
        th.start()

    if sys.stdout:
        try:
            read_loop(ahk.stdout, sys.stdout.buffer)
        except KeyboardInterrupt:
            ahk.terminate()

    try:
        ahk.wait()
    except KeyboardInterrupt:
        ahk.terminate()
        ahk.wait()

    if sys.stderr:
        th.join()

    sys.exit(ahk.returncode)


def python_dll_path():
    dllpath_size = 1024
    dllpath = ctypes.create_unicode_buffer(dllpath_size)
    dllpath_len = ctypes.windll.kernel32.GetModuleFileNameW(HMODULE(sys.dllhandle), dllpath, dllpath_size)
    if not dllpath_len:
        return ""
    return dllpath[:dllpath_len]


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


def read_loop(src, dest):
    try:
        while True:
            buf = src.read(io.DEFAULT_BUFFER_SIZE)
            if not buf:
                break
            dest.write(buf)
            dest.flush()
    except IOError as err:
        sys.stderr.write(Path(sys.argv[0]).name + ": " + err.strerror + "\n")


if __name__ == "__main__":
    main()
