import dataclasses as dc

from .hotkeys import Hotkey
from .key_state import is_key_pressed
from .sending import send

__all__ = [
    "RemappedKey",
]


def remap_key(ctx, origin_key, destination_key, *, mode=None, level=None):
    """Remap *origin_key* to *destination_key*.

    For valid keys refer to `List of Keys
    <https://www.autohotkey.com/docs/KeyList.htm>`_.

    The optional keyword-only *mode* and *level* arguments are passed to the
    :func:`~ahkpy.send` function that will send the *destination_key* when the
    user presses the *origin_key*.

    For more information refer to `Remapping Keys
    <https://www.autohotkey.com/docs/misc/Remap.htm>`_.
    """
    mouse = destination_key.lower() in {"lbutton", "rbutton", "mbutton", "xbutton1", "xbutton2"}
    if mouse:
        def wildcard_origin():
            if not is_key_pressed(destination_key):
                send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level, mouse_delay=-1)

        def wildcard_origin_up():
            send("{Blind}{%s Up}" % destination_key, mode=mode, level=level, mouse_delay=-1)
    else:
        ctrl_to_alt = (
            origin_key.lower() in {"ctrl", "lctrl", "rctrl"} and
            destination_key.lower() in {"alt", "lalt", "ralt"}
        )
        if ctrl_to_alt:
            def wildcard_origin():
                send(
                    "{Blind}{%s Up}{%s DownR}" % (origin_key, destination_key),
                    mode=mode,
                    level=level,
                    key_delay=-1,
                )
        else:
            def wildcard_origin():
                send("{Blind}{%s DownR}" % destination_key, mode=mode, level=level, key_delay=-1)

        def wildcard_origin_up():
            send("{Blind}{%s Up}" % destination_key, mode=mode, level=level, key_delay=-1)

    wildcard_origin = ctx.hotkey(f"*{origin_key}", wildcard_origin)
    wildcard_origin_up = ctx.hotkey(f"*{origin_key} Up", wildcard_origin_up)
    return RemappedKey(wildcard_origin, wildcard_origin_up)


@dc.dataclass(frozen=True)
class RemappedKey:
    """The object that represents a remapped key.

    Creating an instance of :class:`!RemappedKey` doesn't register it in AHK.
    Use :meth:`~ahkpy.keys.BaseHotkeyContext.remap_key` instead.
    """

    wildcard_origin: Hotkey
    wildcard_origin_up: Hotkey
    __slots__ = ("wildcard_origin", "wildcard_origin_up")

    def enable(self):
        """Enable the key remapping."""
        self.wildcard_origin.enable()
        self.wildcard_origin_up.enable()

    def disable(self):
        """Disable the key remapping."""
        self.wildcard_origin.disable()
        self.wildcard_origin_up.disable()

    def toggle(self):
        """Enable the key remapping if it's disabled or do the opposite."""
        self.wildcard_origin.toggle()
        self.wildcard_origin_up.toggle()
