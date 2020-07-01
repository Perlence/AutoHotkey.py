import inspect
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from typing import Callable, Optional

import _ahk  # noqa

from .exceptions import Error

__all__ = [
    "Hotkey",
    "Hotstring",
    "SendMode",
    "get_key_state",
    "get_physical_key_state",
    "hotkey",
    "hotkey_context",
    "hotstring",
    "is_key_toggled",
    "key_wait_pressed",
    "key_wait_released",
    "remap_key",
    "reset_hotstring",
    "send_level",
    "send_mode",
    "send",
    "set_caps_lock_state",
    "set_num_lock_state",
    "set_scroll_lock_state",
]


def DEFAULT(value):
    return None


class SendMode:
    INPUT = "input"
    PLAY = "play"
    EVENT = "event"


def get_key_state(key_name):
    return _get_key_state(key_name)


def get_physical_key_state(key_name):
    return _get_key_state(key_name, "P")


def is_key_toggled(key_name):
    if key_name.lower() not in ("capslock", "numlock", "scrolllock", "insert", "ins"):
        raise ValueError("key_name must be one of CapsLock, NumLock, ScrollLock, or Insert")
    return _get_key_state(key_name, "T")


def _get_key_state(key_name, mode=None):
    result = _ahk.call("GetKeyState", key_name, mode)
    if result == "":
        raise ValueError("key_name is invalid or the state of the key could not be determined")
    return bool(result)


def set_caps_lock_state(state):
    _set_key_state("SetCapsLockState", state)


def set_num_lock_state(state):
    _set_key_state("SetNumLockState", state)


def set_scroll_lock_state(state):
    _set_key_state("SetScrollLockState", state)


def _set_key_state(cmd, state):
    if isinstance(state, str) and state.lower() in ("always_on", "alwayson"):
        state = "AlwaysOn"
    elif isinstance(state, str) and state.lower() in ("always_off", "alwaysoff"):
        state = "AlwaysOff"
    elif state:
        state = "On"
    else:
        state = "Off"
    _ahk.call(cmd, state)


def hotkey(
    key_name: str,
    func: Callable = None,
    *,
    buffer: Optional[bool] = DEFAULT(False),
    priority: Optional[int] = DEFAULT(0),
    max_threads: Optional[int] = DEFAULT(1),
    input_level: Optional[int] = DEFAULT(0),
):

    if key_name == "":
        raise Error("invalid key name")

    if func is None:
        # Return the decorator.
        return partial(hotkey, key_name, buffer=buffer, priority=priority,
                       max_threads=max_threads, input_level=input_level)

    if not callable(func):
        raise TypeError(f"object {func!r} must be callable")

    # TODO: Handle case when func == "AltTab" or other substitutes.
    # TODO: Hotkey command may set ErrorLevel. Raise an exception.

    hk = Hotkey(key_name)
    hk.update(func=func, buffer=buffer, priority=priority, max_threads=max_threads, input_level=input_level)
    return hk


@dataclass(frozen=True)
class Hotkey:
    # TODO: key_name is not enough to identify the Hotkey instance, because
    # hotkeys may exist in a context.
    key_name: str

    def enable(self):
        _ahk.call("HotkeySpecial", self.key_name, "On")

    def disable(self):
        _ahk.call("HotkeySpecial", self.key_name, "Off")

    def toggle(self):
        _ahk.call("HotkeySpecial", self.key_name, "Toggle")

    def update(self, *, func=None, buffer=None, priority=None, max_threads=None, input_level=None):
        options = []

        if buffer:
            options.append("B")
        elif buffer is not None:
            options.append("B0")

        if priority is not None:
            options.append(f'P{priority}')

        if max_threads is not None:
            options.append(f"T{max_threads}")

        if input_level is not None:
            options.append(f"I{input_level}")

        option_str = "".join(options)

        # TODO: id(self) is not reliable. The Hotkey instance may be freed
        # immediately after creation if it's not assigned to a var, and then the
        # same memory address may be used for another Hotkey instance. Using
        # context+key_name is a much better option.
        _ahk.call("Hotkey", id(self), self.key_name, func or "", option_str)


@contextmanager
def hotkey_context(predicate):
    signature = inspect.signature(predicate)
    if len(signature.parameters) == 0:
        def wrapper(*args):
            return bool(predicate())
    else:
        def wrapper(*args):
            return bool(predicate(*args))

    # TODO: Add a threading lock.
    _ahk.call("HotkeyContext", wrapper)
    yield
    _ahk.call("HotkeyExitContext")


def hotstring(
    string,
    replacement=None,
    *,
    wait_for_end_char=DEFAULT(True),
    replace_inside_word=DEFAULT(False),
    backspacing=DEFAULT(True),
    case_sensitive=DEFAULT(False),
    conform_to_case=DEFAULT(False),
    key_delay=None,
    omit_end_char=DEFAULT(False),
    priority=DEFAULT(0),
    raw=DEFAULT(False),
    text=DEFAULT(False),
    mode=DEFAULT(SendMode.INPUT),
    reset_recognizer=DEFAULT(False),
):
    # TODO: Implement setting global options.
    # TODO: Write tests.
    if replacement is None:
        # Return the decorator.
        return partial(
            hotstring,
            string,
            wait_for_end_char=wait_for_end_char,
            replace_inside_word=replace_inside_word,
            backspacing=backspacing,
            case_sensitive=case_sensitive,
            conform_to_case=conform_to_case,
            key_delay=key_delay,
            omit_end_char=omit_end_char,
            priority=priority,
            raw=raw,
            text=text,
            mode=mode,
            reset_recognizer=reset_recognizer,
        )

    hs = Hotstring(string)
    hs.update(
        replacement=replacement,
        wait_for_end_char=wait_for_end_char,
        replace_inside_word=replace_inside_word,
        backspacing=backspacing,
        case_sensitive=case_sensitive,
        conform_to_case=conform_to_case,
        key_delay=key_delay,
        omit_end_char=omit_end_char,
        priority=priority,
        raw=raw,
        text=text,
        mode=mode,
        reset_recognizer=reset_recognizer,
    )
    return hs


@dataclass(frozen=True)
class Hotstring:
    string: str

    def set_replacement(self, replacement):
        _ahk.call("Hotstring", str(self.string), replacement)

    def disable(self):
        _ahk.call("Hotstring", str(self.string), "", "Off")

    def enable(self):
        _ahk.call("Hotstring", str(self.string), "", "On")

    def toggle(self):
        _ahk.call("Hotstring", str(self.string), "", "Toggle")

    def update(
        self,
        *,
        replacement=None,
        wait_for_end_char=None,
        replace_inside_word=None,
        backspacing=None,
        case_sensitive=None,
        conform_to_case=None,
        key_delay=None,
        omit_end_char=None,
        priority=None,
        raw=None,
        text=None,
        mode=None,
        reset_recognizer=None,
    ):
        options = []

        if wait_for_end_char is False:
            options.append("*")
        elif omit_end_char:
            options.append("*0")
            options.append("O")
        else:
            if wait_for_end_char:
                options.append("*0")
            if omit_end_char is False:
                options.append("O0")

        if replace_inside_word:
            options.append("?")
        elif replace_inside_word is not None:
            options.append("?0")

        if backspacing:
            options.append("B")
        elif backspacing is not None:
            options.append("B0")

        if conform_to_case:
            options.append("C1")
        elif case_sensitive:
            options.append("C")
        elif case_sensitive is not None or conform_to_case is not None:
            options.append("C0")

        if key_delay is not None:
            options.append(f"K{key_delay}")

        if priority is not None:
            options.append(f"P{priority}")

        if text:
            options.append("T")
        elif raw:
            options.append("R")
        elif raw is not None or text is not None:
            options.append("R0")

        if mode is not None:
            mode = mode.lower()
        if mode == SendMode.INPUT:
            options.append("SI")
        elif mode == SendMode.PLAY:
            options.append("SP")
        elif mode == SendMode.EVENT:
            options.append("SE")

        if reset_recognizer:
            options.append("Z")
        elif reset_recognizer is not None:
            options.append("Z0")

        option_str = "".join(options)

        _ahk.call("Hotstring", f":{option_str}:{self.string}", replacement or "")


def reset_hotstring():
    _ahk.call("Reset")


def key_wait_pressed(key_name, logical_state=False, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical_state=logical_state, timeout=timeout)


def key_wait_released(key_name, logical_state=False, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical_state=logical_state, timeout=timeout)


def _key_wait(key_name, down=False, logical_state=False, timeout=None) -> bool:
    options = []
    if down:
        options.append("D")
    if logical_state:
        options.append("L")
    if timeout is not None:
        options.append(f"T{timeout}")
    timed_out = _ahk.call("KeyWait", str(key_name), "".join(options))
    return not timed_out


def remap_key(origin_key, destination_key):
    # TODO: Handle LCtrl as the origin key.
    # TODO: Handle remapping keyboard key to a mouse button.
    @hotkey(f"*{origin_key}")
    def wildcard_origin():
        send("{Blind}{%s DownR}" % destination_key)

    @hotkey(f"*{origin_key} Up")
    def wildcard_origin_up():
        send("{Blind}{%s Up}" % destination_key)

    return RemappedKey(wildcard_origin, wildcard_origin_up)


@dataclass(frozen=True)
class RemappedKey:
    wildcard_origin: Hotkey
    wildcard_origin_up: Hotkey

    def enable(self):
        self.wildcard_origin.enable()
        self.wildcard_origin_up.enable()

    def disable(self):
        self.wildcard_origin.disable()
        self.wildcard_origin_up.disable()

    def toggle(self):
        self.wildcard_origin.toggle()
        self.wildcard_origin_up.toggle()


def send(keys):
    # TODO: Consider adding `mode` keyword?
    _ahk.call("Send", keys)


def send_level(level: int):
    # TODO: Make this setting thread-local.
    if not 0 <= level <= 100:
        raise ValueError("level must be between 0 and 100")
    _ahk.call("SendLevel", int(level))


def send_mode(mode):
    # TODO: Make this setting thread-local.
    _ahk.call("SendMode", mode)
