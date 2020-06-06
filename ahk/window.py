import dataclasses as dc
import threading

import _ahk  # noqa

__all__ = [
    "Window", "Windows", "detect_hidden_windows", "set_title_match_mode", "windows",
]

last_found_window_lock = threading.RLock()


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


@dc.dataclass
class Windows:
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

    def filter(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        if title is None and class_name is None and id is None and pid is None and exe is None and text is None:
            return self
        return dc.replace(
            self,
            title=default(title, self.title),
            class_name=default(class_name, self.class_name),
            id=default(id, self.id),
            pid=default(pid, self.pid),
            exe=default(exe, self.exe),
            text=default(text, self.text),
        )

    def exclude(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        if title is None and class_name is None and id is None and pid is None and exe is None and text is None:
            return self
        return dc.replace(
            self,
            exclude_title=default(title, self.exclude_title),
            exclude_class_name=default(class_name, self.exclude_class_name),
            exclude_id=default(id, self.exclude_id),
            exclude_pid=default(pid, self.exclude_pid),
            exclude_exe=default(exe, self.exclude_exe),
            exclude_text=default(text, self.exclude_text),
        )

    def first(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        win_id = _ahk.call("WinExist", *filtered._query())
        return Window(win_id)

    top = first

    def last(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        win_id = _ahk.call("WinGet", "IDLast", *filtered._query())
        return Window(win_id)

    bottom = last

    def get_active(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        win_id = _ahk.call("WinActive", *filtered._query())
        return Window(win_id)

    def wait(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None, timeout=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        return filtered._wait("WinWait", timeout)

    def wait_active(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None, timeout=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        return filtered._wait("WinWaitActive", timeout)

    def wait_inactive(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None, timeout=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        return filtered._wait("WinWaitNotActive", timeout)

    def wait_close(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None, timeout=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        win_title, win_text, exclude_title, exclude_text = filtered._query()
        # WinWaitClose doesn't set Last Found Window, return False if the wait
        # was timed out.
        timed_out = _ahk.call("WinWaitClose", win_title, win_text, timeout or "", exclude_title, exclude_text)
        return not timed_out

    def _wait(self, cmd, timeout):
        win_title, win_text, exclude_title, exclude_text = self._query()
        # Calling WinWait[Not]Active and WinWait sets an implicit Last Found
        # Window that is local to the current AHK thread. Let's protect it from
        # being overwritten by other Python threads.
        with last_found_window_lock:
            timed_out = _ahk.call(cmd, win_title, win_text, timeout or "", exclude_title, exclude_text)
            if timed_out:
                return Window(0)
            # Return the Last Found Window.
            return windows.first()

    def close_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None, timeout=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinClose", timeout)

    def hide_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinHide")

    def kill_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None, timeout=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinKill", timeout)

    def maximize_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinMaximize")

    def minimize_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinMinimize")

    # TODO: Implement WinMinimizeAllUndo.

    def restore_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinRestore")

    def show_all(self, title=None, *, class_name=None, id=None, pid=None, exe=None, text=None):
        filtered = self.filter(title=title, class_name=class_name, id=id, pid=pid, exe=exe, text=text)
        filtered._group_action("WinShow")

    def _group_action(self, cmd, timeout=None):
        if self == Windows() and cmd == "WinMinimize":
            # If the filter matches all the windows, minimize everything except
            # the desktop window.
            _ahk.call("WinMinimizeAll")
            return

        query_hash = hash(dc.astuple(self))
        query_hash_str = str(query_hash).replace("-", "m")  # AHK doesn't allow "-" in group names
        win_title, win_text, exclude_title, exclude_text = self._query()
        label = ""
        _ahk.call("GroupAdd", query_hash_str, win_title, win_text, label, exclude_title, exclude_text)
        _ahk.call(cmd, f"ahk_group {query_hash_str}", "", timeout)

    def __iter__(self):
        """Return matching windows ordered from top to bottom."""
        win_ids = _ahk.call("WinGet", "List", *self._query())
        for win_id in win_ids.values():
            yield Window(win_id)

    def __len__(self):
        return _ahk.call("WinGet", "Count", *self._query())

    def __repr__(self):
        field_strs = [
            f"{field_name}={value!r}"
            for field_name, value in dc.asdict(self).items()
            if value is not None
        ]
        return self.__class__.__qualname__ + f"({', '.join(field_strs)})"

    def _query(self):
        win_title = []
        if self.title is not None:
            win_title.append(str(self.title))
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
            exclude_title.append(str(self.exclude_title))
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
            default(str, self.text, ""),
            " ".join(exclude_title),
            default(str, self.exclude_text, ""),
        )


windows = Windows()


@dc.dataclass
class Window:
    id: int

    def __bool__(self):
        return self.id != 0

    @property
    def rect(self):
        result = self._call("WinGetPos")
        return result["X"], result["Y"], result["Width"], result["Height"]

    @rect.setter
    def rect(self, new_rect):
        x, y, width, height = new_rect
        self.move(x, y, width, height)

    @property
    def position(self):
        x, y, _, _ = self.rect
        return x, y

    @position.setter
    def position(self, new_position):
        x, y = new_position
        self.move(x, y)

    @property
    def x(self):
        x, _, _, _ = self.rect
        return x

    @x.setter
    def x(self, new_x):
        self.move(x=new_x)

    @property
    def y(self):
        _, y, _, _ = self.rect
        return y

    @y.setter
    def y(self, new_y):
        self.move(y=new_y)

    @property
    def width(self):
        _, _, width, _ = self.rect
        return width

    @width.setter
    def width(self, new_width):
        self.move(width=new_width)

    @property
    def height(self):
        _, _, _, height = self.rect
        return height

    @height.setter
    def height(self, new_height):
        self.move(height=new_height)

    def move(self, x=None, y=None, width=None, height=None):
        self._call("WinMove",
                   default(int, x, ""),
                   default(int, y, ""),
                   default(int, width, ""),
                   default(int, height, ""))

    @property
    def active(self):
        return self._call("WinActive") != 0

    @property
    def exists(self):
        return self._call("WinExist") != 0

    @property
    def class_name(self):
        return self._call("WinGetClass")

    @property
    def text(self):
        return self._call("WinGetText")

    @property
    def title(self):
        return self._call("WinGetTitle")

    @title.setter
    def title(self, new_title):
        return self._call("WinSetTitle", str(new_title))

    @property
    def pid(self):
        return self._get("PID")

    @property
    def process_name(self):
        return self._get("ProcessName")

    @property
    def minimized(self):
        return self._get("MinMax") == -1

    @property
    def maximized(self):
        return self._get("MinMax") == 1

    # TODO: Implement ControlList and ControlListHwnd

    @property
    def transparent(self):
        result = self._get("Transparent")
        if result == "":
            return None
        return result

    @transparent.setter
    def transparent(self, value):
        if value is None:
            value = "Off"
        elif not 0 <= value <= 255:
            raise ValueError("transparency value must be between 0 and 255")
        else:
            value = int(value)
        self._set("Transparent", value)

    def activate(self):
        self._call("WinActivate")

    def close(self, timeout=None):
        self._call("WinClose", timeout)
        if timeout is not None:
            # Check if the window still exists.
            return windows.first(id=id) is None

    def _call(self, cmd, *args):
        # Call the command only if the window was found previously. This makes
        # optional chaining possible. For example,
        # `ahk.windows.first(class_name="Notepad").close()` doesn't error out
        # when there are no Notepad windows.
        if self.id != 0:
            return _ahk.call(cmd, f"ahk_id {self.id}", "", *args)

    def _get(self, subcmd):
        if self.id != 0:
            return _ahk.call("WinGet", subcmd, f"ahk_id {self.id}")

    def _set(self, subcmd, value):
        if self.id != 0:
            return _ahk.call("WinSet", subcmd, value, f"ahk_id {self.id}")


def identity(a):
    return a


def default(a, b, func=identity):
    if func is not identity:
        func, a, b = a, b, func
    if a is not None:
        return func(a)
    return b
