import dataclasses as dc

import _ahk  # noqa

__all__ = [
    "Window", "Windows", "detect_hidden_windows", "set_title_match_mode", "windows",
]


def detect_hidden_windows(value):
    value = "On" if value else "Off"
    _ahk.call("DetectHiddenWindows", value)


def set_title_match_mode(mode=None, speed=None):
    if mode is not None:
        match_modes = {
            "startswith": "1",
            "contains": "2",
            "exact": "3",
            "1": "1",
            "2": "2",
            "3": "3",
            "regex": "regex",
        }
        ahk_mode = match_modes.get(str(mode).lower())
        if ahk_mode is None:
            raise ValueError(f"unknown match mode {mode!r}")
        _ahk.call("SetTitleMatchMode", ahk_mode)

    if speed is not None:
        speeds = ["fast", "slow"]
        if speed.lower() not in speeds:
            raise ValueError(f"unknown speed {speed!r}")
        _ahk.call("SetTitleMatchMode", speed)


class Windows:
    def __init__(self, query=None):
        if query is None:
            query = WindowQuery()
        self._query = query

    def filter(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        return Windows(dc.replace(
            self._query,
            title=default(title, self._query.title),
            class_name=default(class_name, self._query.class_name),
            id=default(id, self._query.id),
            pid=default(pid, self._query.pid),
            exe=default(exe, self._query.exe),
            text=default(text, self._query.text),
        ))

    def exclude(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        return Windows(dc.replace(
            self._query,
            exclude_title=default(title, self._query.exclude_title),
            exclude_class_name=default(class_name, self._query.exclude_class_name),
            exclude_id=default(id, self._query.exclude_id),
            exclude_pid=default(pid, self._query.exclude_pid),
            exclude_exe=default(exe, self._query.exclude_exe),
            exclude_text=default(text, self._query.exclude_text),
        ))

    def first(self):
        win_id = _ahk.call("WinExist", *self._query.pack())
        # TODO: Should this still return a null Window instance if window was not found?
        if win_id:
            return Window(win_id)

    top = first

    def last(self):
        win_id = _ahk.call("WinGet", "IDLast", *self._query.pack())
        if win_id:
            return Window(win_id)

    bottom = last

    def active(self):
        win_id = _ahk.call("WinActive", *self._query.pack())
        if win_id:
            return Window(win_id)

    def wait(self, timeout=None):
        win_title, win_text, exclude_title, exclude_text = self._query.pack()
        result = _ahk.call("WinWait", win_title, win_text, timeout or "", exclude_title, exclude_text)
        # Return False if timed out, True otherwise.
        return not result

    def wait_active(self):
        ...

    def wait_inactive(self):
        ...

    def wait_close(self):
        ...

    def close(self):
        ...

    def hide(self):
        ...

    def kill(self):
        ...

    def maximize(self):
        ...

    def minimize(self):
        ...

    def restore(self):
        ...

    def show(self):
        ...

    def __iter__(self):
        win_ids = _ahk.call("WinGet", "List", *self._query.pack())
        for win_id in win_ids.values():
            yield Window(win_id)

    def __getitem__(self, item):
        ...

    def __len__(self):
        return _ahk.call("WinGet", "Count", *self._query.pack())


@dc.dataclass
class WindowQuery:
    title: str = None
    class_name: str = None
    id: int = None
    pid: int = None
    exe: str = None
    text: str = None
    exclude_title: str = None
    exclude_class_name: str = None
    exclude_id: int = None
    exclude_pid: int = None
    exclude_exe: str = None
    exclude_text: str = None

    def pack(self):
        win_title = []
        if self.title is not None:
            win_title.append(self.title)
        if self.class_name is not None:
            win_title.append(f"ahk_class {self.class_name}")
        if self.id is not None:
            win_title.append(f"ahk_id {self.id}")
        if self.pid is not None:
            win_title.append(f"ahk_pid {self.pid}")
        if self.exe is not None:
            win_title.append(f"ahk_exe {self.exe}")

        exclude_title = []
        if self.exclude_title is not None:
            exclude_title.append(self.exclude_title)
        if self.exclude_class_name is not None:
            exclude_title.append(f"ahk_class {self.exclude_class_name}")
        if self.exclude_id is not None:
            exclude_title.append(f"ahk_id {self.exclude_id}")
        if self.exclude_pid is not None:
            exclude_title.append(f"ahk_pid {self.exclude_pid}")
        if self.exclude_exe is not None:
            exclude_title.append(f"ahk_exe {self.exclude_exe}")

        return (
            " ".join(win_title),
            self.text or "",
            " ".join(exclude_title),
            self.exclude_text or "",
        )


windows = Windows()


@dc.dataclass
class Window:
    id: int

    @property
    def title(self):
        return _ahk.call("WinGetTitle", self._ahk_id())

    def _ahk_id(self):
        return f"ahk_id {self.id}"


def default(a, b):
    if a is not None:
        return a
    return b
