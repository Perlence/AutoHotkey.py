import contextvars
import dataclasses as dc
from typing import ContextManager

from .flow import ahk_call

__all__ = [
    "Settings",
    "default_settings",
    "get_settings",
    "local_settings",
    "set_settings",
]


_current_settings = contextvars.ContextVar("script_settings")


@dc.dataclass
class Settings:
    control_delay: float = 0.02
    key_delay: float = 0.01
    key_duration: float = -1
    key_delay_play: float = -1
    key_duration_play: float = -1
    mouse_delay: float = 0.01
    mouse_delay_play: float = -1
    mouse_speed: int = 2
    send_level: int = 0
    send_mode: str = "input"
    win_delay: float = 0.1

    # Should CoordMode also be here? I don't think so, because the above
    # settings change only some aspects like speed and delay and don't change
    # the overall behavior. For example, the function that moves the mouse
    # cursor or types a word is expected to mostly do the same regardless of
    # these settings.
    #
    # CoordMode on the other hand completely changes the behavior of the
    # affected functions.

    def __delattr__(self, name):
        raise AttributeError(f"{name} cannot be deleted")


def get_settings() -> Settings:
    try:
        return _current_settings.get()
    except LookupError:
        settings = dc.replace(default_settings)
        _current_settings.set(settings)
        return settings


def set_settings(settings):
    _current_settings.set(settings)


def local_settings(settings=None) -> ContextManager[Settings]:
    if settings is None:
        settings = get_settings()
    return _SettingsManager(settings)


class _SettingsManager:
    """Context manager class to support local_settings().

    Sets a copy of the supplied context in __enter__() and restores the previous
    settings in __exit__().
    """
    def __init__(self, new_settings):
        self.new_settings = dc.replace(new_settings)

    def __enter__(self) -> Settings:
        self.prior_settings = get_settings()
        set_settings(self.new_settings)
        return self.new_settings

    def __exit__(self, t, v, tb):
        set_settings(self.prior_settings)


default_settings = Settings()
set_settings(default_settings)


def optional_ms(value):
    if value is None or value < 0:
        return -1
    else:
        return int(value * 1000)


COORD_TARGETS = {"tooltip", "pixel", "mouse", "caret", "menu"}
COORD_MODES = {"screen", "window", "client"}


def _set_coord_mode(target, relative_to):
    if target not in COORD_TARGETS:
        raise ValueError(f"{target!r} is not a valid coord target")
    if relative_to not in COORD_MODES:
        raise ValueError(f"{relative_to!r} is not a valid coord mode")
    ahk_call("CoordMode", target, relative_to)
