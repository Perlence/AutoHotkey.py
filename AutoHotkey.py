import ctypes
import io
import os
import subprocess
import sys
import threading
from ctypes.wintypes import HMODULE
from pathlib import Path


# TODO: Get programs associated with the .ahk extension instead of hardcoding.
AHK = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"


def main():
    python_ahk_path = Path(__file__).parent / "Python.ahk"
    args = [AHK, python_ahk_path] + sys.argv[1:]
    os.environ["PYTHONUNBUFFERED"] = "1"
    export_python_dll_path()
    ahk = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    th = threading.Thread(target=read_loop, args=(ahk.stderr, sys.stdout.buffer), daemon=True)
    th.start()
    read_loop(ahk.stdout, sys.stdout.buffer)
    th.join()


def export_python_dll_path():
    dllpath_size = 1024
    dllpath = ctypes.create_unicode_buffer(dllpath_size)
    dllpath_len = ctypes.windll.kernel32.GetModuleFileNameW(HMODULE(sys.dllhandle), dllpath, dllpath_size)
    if dllpath_len:
        os.environ["PYTHONDLL"] = dllpath[:dllpath_len]


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
