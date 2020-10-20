import subprocess

import ahkpy as ahk
import psutil


@ahk.hotkey(">^r")  # RCtrl+R
def restart_app():
    """Restart the application by pressing the hotkey on its active window."""
    active_win = ahk.windows.get_active()
    pid = active_win.pid
    if pid is None:
        return

    ps = psutil.Process(pid)
    args = [ps.exe()] + ps.cmdline()[1:]

    all_wins = ahk.windows.filter(pid=pid)
    closed = all_wins.close_all(timeout=5)
    if not closed:
        ps.terminate()
        try:
            ps.wait(timeout=5)
        except psutil.TimeoutExpired:
            return

    subprocess.Popen(args)
