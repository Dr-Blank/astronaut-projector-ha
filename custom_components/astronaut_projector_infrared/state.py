"""Assumed state shared by the projector's entities."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, callback

from .codes import DEFAULT_POWER_ON_REPEATS


class NebulaColor(StrEnum):
    """Nebula colours, in the order the colour button steps through them."""

    GREEN = "green"
    BLUE = "blue"
    RED = "red"
    BLUE_GREEN = "blue_green"
    RED_BLUE = "red_blue"
    RED_GREEN = "red_green"
    AUTO_CYCLE = "auto_cycle"
    RED_BLUE_GREEN = "red_blue_green"


NEBULA_COLORS = list(NebulaColor)


class PowerOnMethod(StrEnum):
    """How power-on is sent; units differ in which one they take reliably.

    Some units sleep deeply a few seconds after switching off and spend the
    first press waking up, so they need a double press. Others take the first
    press, so a double press turns them on and straight off again.
    """

    SINGLE = "single"
    DOUBLE = "double"


@dataclass
class ProjectorState:
    """What Home Assistant last told the projector to do.

    Infrared is one-way, so nothing here is read back. Power-on always comes
    up with the stars on and the nebula on in auto-cycle, whatever the
    projector was doing before, which puts this back in step.
    """

    power: bool = False
    stars: bool = False
    nebula: bool = False
    nebula_color: NebulaColor | None = None
    power_on_repeats: int = DEFAULT_POWER_ON_REPEATS
    power_on_method: PowerOnMethod = PowerOnMethod.SINGLE
    _listeners: list[Callable[[], None]] = field(default_factory=list, repr=False)

    def power_on(self) -> None:
        """Record the state the projector always powers on in."""
        self.power = True
        self.stars = True
        self.nebula = True
        self.nebula_color = NebulaColor.AUTO_CYCLE

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        """Call listener whenever the state changes."""
        self._listeners.append(listener)

        @callback
        def remove() -> None:
            self._listeners.remove(listener)

        return remove

    @callback
    def async_notify(self) -> None:
        """Tell every listener the state changed."""
        for listener in list(self._listeners):
            listener()


type AstronautProjectorConfigEntry = ConfigEntry[ProjectorState]
