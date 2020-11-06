from .flow import ahk_call

__all__ = [
    "get_caps_lock_state",
    "get_insert_state",
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


def is_key_pressed(key_name):
    return _get_key_state(key_name, "P")


def is_key_pressed_logical(key_name):
    return _get_key_state(key_name)


def get_caps_lock_state():
    return _get_key_state("CapsLock", "T")


def get_num_lock_state():
    return _get_key_state("NumLock", "T")


def get_scroll_lock_state():
    return _get_key_state("ScrollLock", "T")


def get_insert_state():
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


def wait_key_pressed(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical=False, timeout=timeout)


def wait_key_released(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical=False, timeout=timeout)


def wait_key_pressed_logical(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=True, logical=True, timeout=timeout)


def wait_key_released_logical(key_name, timeout=None) -> bool:
    return _key_wait(key_name, down=False, logical=True, timeout=timeout)


def _key_wait(key_name, down=False, logical=False, timeout=None) -> bool:
    options = []
    if down:
        options.append("D")
    if logical:
        options.append("L")
    if timeout is not None:
        options.append(f"T{timeout}")
    timed_out = ahk_call("KeyWait", str(key_name), "".join(options))
    return not timed_out


def get_key_name(key):
    """Return the name of a key."""
    return str(_get_key("GetKeyName", key))


def get_key_vk(key):
    """Return the virtual key code of a key."""
    return _get_key("GetKeyVK", key)


def get_key_sc(key):
    """Return the scan code of a key."""
    return _get_key("GetKeySC", key)


def _get_key(cmd, key):
    result = ahk_call(cmd, str(key))
    if not result:
        raise ValueError(f"{key!r} is not a valid key")
    return result
