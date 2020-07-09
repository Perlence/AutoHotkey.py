import inspect
import signal
import subprocess
import sys
from textwrap import dedent

import pytest


AHK = sys.executable


@pytest.fixture()
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
        args = ["py.exe", "-m", "ahkpy", *args]
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
        return self.run(args, input=self._extract_code(code), **kwargs)

    def popen(self, args, **kwargs):
        args = ["py.exe", "-m", "ahkpy", *args]
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
        self.proc.stdin.write(self._extract_code(code))
        self.proc.stdin.close()
        return self.proc

    def _extract_code(self, code):
        if callable(code):
            func_name = code.__name__
            source = inspect.getsource(code)
            return f"{dedent(source)}\n{func_name}()\n"
        return dedent(code)

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
def repeat(request):
    return
