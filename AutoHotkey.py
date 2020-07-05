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
    python_ahk_path = Path(__file__).parent / "Python.ahk"
    ahk_exe_path = get_ahk_by_assoc() or AHK
    args = [ahk_exe_path, python_ahk_path] + sys.argv[1:]
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONNOUSERSITE"] = "1"
    os.environ["PYTHONFULLPATH"] = ';'.join(sys.path)
    os.environ["PYTHONDLL"] = python_dll_path()
    ahk = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    th = threading.Thread(target=read_loop, args=(ahk.stderr, sys.stdout.buffer), daemon=True)
    th.start()
    read_loop(ahk.stdout, sys.stdout.buffer)
    th.join()


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


def python_dll_path():
    dllpath_size = 1024
    dllpath = ctypes.create_unicode_buffer(dllpath_size)
    dllpath_len = ctypes.windll.kernel32.GetModuleFileNameW(HMODULE(sys.dllhandle), dllpath, dllpath_size)
    if not dllpath_len:
        return ""
    return dllpath[:dllpath_len]


def read_loop(src, dest):
    try:
        while True:
            line = src.read(io.DEFAULT_BUFFER_SIZE)
            if not line:
                break
            dest.write(line)
            dest.flush()
    except IOError as err:
        sys.stderr.write(Path(sys.argv[0]).name + ": " + err.strerror + "\n")
        sys.exit(0)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
