import re
from setuptools import setup

with open("ahkpy/__init__.py", encoding="utf-8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="AutoHotkey.py",
    version=version,
)
