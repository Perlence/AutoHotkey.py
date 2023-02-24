import inspect
import signal
import subprocess
import sys
import textwrap
import time

import pytest

import ahkpy as ahk


@pytest.fixture(scope="class")
def child_ahk():
    instance = ChildAHK()
    try:
        yield instance
    finally:
        instance.close()


class ChildAHK:
    def __init__(self):
        self.proc = None

    def run(self, args, **kwargs):
        args = [sys.executable, "-m", "ahkpy", *map(str, args)]
        return subprocess.run(
            args,
            capture_output=True, encoding="utf-8",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            **kwargs,
        )

    def run_code(self, code, *, quiet=False, **kwargs):
        args = ["-"]
        if quiet:
            args.insert(0, "-q")
        return self.run(args, input=self.extract_code(code), **kwargs)

    def popen(self, args, **kwargs):
        args = [sys.executable, "-m", "ahkpy", *map(str, args)]
        self.proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            **kwargs)
        return self.proc

    def popen_code(self, code, *, args=(), quiet=False, **kwargs):
        args = ["-", *args]
        if quiet:
            args.insert(0, "-q")
        self.popen(args, **kwargs)
        self.proc.stdin.write(self.extract_code(code))
        self.proc.stdin.close()
        return self.proc

    def extract_code(self, code):
        if callable(code):
            func_name = code.__name__
            source = inspect.getsource(code)
            return f"{textwrap.dedent(source)}\n{func_name}()\n"
        return textwrap.dedent(code)

    def wait(self, counter):
        line = self.proc.stdout.readline()
        assert line == f"ok{counter:02}\n"

    def close(self):
        if self.proc is None:
            return
        try:
            self.proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        else:
            return

        self.proc.send_signal(signal.CTRL_BREAK_EVENT)
        try:
            self.proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            self.proc.terminate()


@pytest.fixture(params=range(20))
def repeat():
    return


@pytest.fixture()
def settings():
    import ahkpy as ahk
    with ahk.local_settings() as settings:
        yield settings


@pytest.fixture(scope="class")
def notepad():
    import ahkpy as ahk
    notepad_proc = subprocess.Popen(["notepad.exe"])
    try:
        notepad_win = ahk.windows.wait_active(pid=notepad_proc.pid, timeout=5)
        yield notepad_win
    finally:
        notepad_proc.terminate()


def assert_equals_eventually(func, expected, timeout=1):
    stop = time.perf_counter() + timeout
    while time.perf_counter() < stop:
        actual = func()
        if actual == expected:
            return
        ahk.sleep(0.01)
    assert actual == expected
