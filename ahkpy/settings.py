import dataclasses as dc
import contextvars
from typing import ContextManager

__all__ = [
    "Settings",
    "get_settings",
    "local_settings",
    "set_settings",
]


COORD_MODES = {"screen", "window", "client"}

_current_settings = contextvars.ContextVar("script_settings")


@dc.dataclass
class Settings:
    control_delay: float = 0.02
    key_delay: float = 0.01
    key_duration: float = -1
    key_delay_play: float = -1
    key_duration_play: float = -1
    mouse_delay: float = 0.01  # TODO: Implement mouse_delay.
    mouse_delay_play: float = -1  # TODO: Implement mouse_delay_play.
    mouse_speed: int = 2  # TODO: Implement mouse_speed.
    send_level: int = 0
    send_mode: str = "input"
    win_delay: float = 0.1

    def __delattr__(self, name):
        raise AttributeError(f"{name} cannot be deleted")


def get_settings() -> Settings:
    try:
        return _current_settings.get()
    except LookupError:
        settings = Settings()
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
    decimal context in __exit__().
    """
    def __init__(self, new_settings):
        self.new_settings = dc.replace(new_settings)

    def __enter__(self) -> Settings:
        self.prior_settings = get_settings()
        set_settings(self.new_settings)
        return self.new_settings

    def __exit__(self, t, v, tb):
        set_settings(self.prior_settings)
