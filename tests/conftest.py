import inspect
import os
import subprocess
from textwrap import dedent

import pytest


AHK = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"
EMBED_PYTHON = os.path.abspath("EmbedPython.ahk")


@pytest.fixture()
def child_ahk():
    unbuffered = os.getenv("PYTHONUNBUFFERED")
    if not unbuffered:
        os.environ["PYTHONUNBUFFERED"] = "1"
    instance = ChildAHK()
    try:
        yield instance
    finally:
        instance.close()
        if not unbuffered:
            del os.environ["PYTHONUNBUFFERED"]


class ChildAHK:
    def __init__(self):
        self.proc = None

    def run(self, args, **kwargs):
        args = [AHK, EMBED_PYTHON, *args]
        return subprocess.run(args, text=True, capture_output=True, **kwargs)

    def run_code(self, code, *, quiet=False, **kwargs):
        args = ["-"]
        if quiet:
            args.insert(0, "-q")
        return self.run(args, input=self._extract_code(code), **kwargs)

    def popen(self, args, **kwargs):
        args = [AHK, EMBED_PYTHON, *args]
        self.proc = subprocess.Popen(
            args, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, **kwargs)
        return self.proc

    def popen_code(self, code, *, args=(), quiet=False, **kwargs):
        args = ["-", *args]
        if quiet:
            args.insert(0, "-q")
        self.popen(args, **kwargs)
        self.proc.stdin.write(self._extract_code(code))
        self.proc.stdin.close()

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
            self.proc.terminate()
