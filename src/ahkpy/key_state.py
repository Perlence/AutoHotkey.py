import functools

from .flow import ahk_call, _wait_for

__all__ = [
    "get_caps_lock_state",
    "get_insert_state",
    "get_key_name_from_sc",
    "get_key_name_from_vk",
    "get_key_name",
    "get_key_sc",
    "get_key_vk",
    "get_num_lock_state",
    "get_scroll_lock_state",
    "is_key_pressed_logical",
    "is_key_pressed",
    "set_caps_lock_state",
    "set_num_lock_state",
    "set_scroll_lock_state",
    "wait_key_pressed_logical",
    "wait_key_pressed",
    "wait_key_released_logical",
    "wait_key_released",
]


def is_key_pressed(key_name: str) -> bool:
    """Return whether the key is pressed down physically.

    :command: `GetKeyState
       <https://www.autohotkey.com/docs/commands/GetKeyState.htm>`_
    """
    return _get_key_state(key_name, "P")


def is_key_pressed_logical(key_name: str) -> bool:
    """Return the logical state of the key.

    This is the state that the OS and the active window believe the key to be
    in, but is not necessarily the same as the physical state, that is, whether
    the user is physically holding it down.

    :command: `GetKeyState
       <https://www.autohotkey.com/docs/commands/GetKeyState.htm>`_
    """
    return _get_key_state(key_name)


def get_caps_lock_state() -> bool:
    return _get_key_state("CapsLock", "T")


def get_num_lock_state() -> bool:
    return _get_key_state("NumLock", "T")


def get_scroll_lock_state() -> bool:
    return _get_key_state("ScrollLock", "T")


def get_insert_state() -> bool:
    return _get_key_state("Insert", "T")


def _get_key_state(key_name, mode=None):
    result = ahk_call("GetKeyState", key_name, mode)
    if result == "":
        raise ValueError(f"{key_name!r} is not a valid key or the state of the key could not be determined")
    return bool(result)


def set_caps_lock_state(state: bool, always=False):
    _set_key_state("SetCapsLockState", state, always)


def set_num_lock_state(state: bool, always=False):
    _set_key_state("SetNumLockState", state, always)


def set_scroll_lock_state(state: bool, always=False):
    _set_key_state("SetScrollLockState", state, always)


def _set_key_state(cmd, state, always):
    if state:
        state = "On"
    else:
        state = "Off"
    if always:
        state = f"Always{state}"
    ahk_call(cmd, state)


def wait_key_pressed(key_name, timeout: float = None) -> bool:
    """Wait for a key or mouse/joystick button to be pressed down physically.

    Returns ``True`` when the user presses the key. If there is no user input
    after *timeout* seconds, then ``False`` will be returned. If *timeout* is
    not specified or ``None``, there is no limit to the wait time.
    """
    return _wait_for(timeout, functools.partial(is_key_pressed, key_name)) or False


def wait_key_released(key_name, timeout: float = None) -> bool:
    """Wait for a key or mouse/joystick button to be released physically."""
    return _wait_for(timeout, lambda: not is_key_pressed(key_name)) or False


def wait_key_pressed_logical(key_name, timeout: float = None) -> bool:
    """Wait for a key or mouse/joystick button logical state to be pressed."""
    return _wait_for(timeout, functools.partial(is_key_pressed_logical, key_name)) or False


def wait_key_released_logical(key_name, timeout: float = None) -> bool:
    """Wait for a key or mouse/joystick button logical state to be released."""
    return _wait_for(timeout, lambda: not is_key_pressed_logical(key_name)) or False


def get_key_name(key_name: str) -> str:
    """Return the name of a key.

        >>> ahkpy.get_key_name("vk70")
        'F1'
        >>> ahkpy.get_key_name(f"vk{112:x}")
        'F1'
        >>> ahkpy.get_key_name("sc3b")
        'F1'

    :command: `GetKeyName
       <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
    """
    return str(_get_key("GetKeyName", key_name))


def get_key_name_from_vk(vk: int) -> str:
    """Return the name of a key given its virtual key code.

        >>> ahkpy.get_key_name_from_vk(112)
        'F1'

    :command: `GetKeyName
       <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
    """
    return get_key_name(f"vk{vk}")


def get_key_name_from_sc(sc: int) -> str:
    """Return the name of a key given its scan code.

        >>> ahkpy.get_key_name_from_sc(59)
        'F1'

    :command: `GetKeyName
       <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
    """
    return get_key_name(f"sc{sc}")


def get_key_vk(key_name: str) -> int:
    """Return the virtual key code of a key.

        >>> ahkpy.get_key_vk("F1")
        112

    :command: `GetKeyVK <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
    """
    return _get_key("GetKeyVK", key_name)


def get_key_sc(key_name: str) -> int:
    """Return the scan code of a key.

        >>> ahkpy.get_key_sc("F1")
        59

    :command: `GetKeySC <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
    """
    return _get_key("GetKeySC", key_name)


def _get_key(cmd, key):
    result = ahk_call(cmd, str(key))
    if not result:
        raise ValueError(f"{key!r} is not a valid key")
    return result
