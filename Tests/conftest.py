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
        self.wait_counter = 0

    def run(self, args, **kwargs):
        args = [AHK, EMBED_PYTHON, *args]
        return subprocess.run(args, text=True, capture_output=True, **kwargs)

    def run_code(self, code, *, quiet=False, **kwargs):
        args = ["-"]
        if quiet:
            args.insert(0, "-q")
        return self.run(args, input=dedent(code), **kwargs)

    def popen(self, args, **kwargs):
        args = [AHK, EMBED_PYTHON, *args]
        self.proc = subprocess.Popen(
            args, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, **kwargs)
        return self.proc

    def popen_code(self, code, *, quiet=False, **kwargs):
        args = ["-"]
        if quiet:
            args.insert(0, "-q")
        self.popen(args, **kwargs)
        self.proc.stdin.write(dedent(code))
        self.proc.stdin.close()

    def wait(self):
        line = self.proc.stdout.readline()
        assert line == f"ok{self.wait_counter:02}\n"
        self.wait_counter += 1

    def close(self):
        if self.proc is not None:
            self.proc.terminate()
