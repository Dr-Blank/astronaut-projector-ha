"""Switch platform for the Astronaut Projector Infrared integration."""

from abc import abstractmethod
from typing import Any, override

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .codes import AstronautProjectorCode, wake_command
from .entity import AstronautProjectorEntity
from .state import AstronautProjectorConfigEntry, NebulaColor

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AstronautProjectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up astronaut projector switches from a config entry."""
    async_add_entities(
        [
            AstronautProjectorPowerSwitch(entry, "power"),
            AstronautProjectorStarsSwitch(entry, "stars"),
            AstronautProjectorNebulaSwitch(entry, "nebula"),
        ]
    )


class AstronautProjectorSwitch(AstronautProjectorEntity, SwitchEntity, RestoreEntity):
    """Base for a switch whose state lives in the shared projector state."""

    _attr_assumed_state = True

    def __init__(self, entry: AstronautProjectorConfigEntry, key: str) -> None:
        """Initialize the switch."""
        super().__init__(entry, key)
        self._attr_translation_key = key

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the last state and follow changes made by sibling entities."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            self._restore(last_state.state == STATE_ON)
            self._projector.async_notify()
        self.async_on_remove(
            self._projector.async_add_listener(self.async_write_ha_state)
        )

    @abstractmethod
    def _restore(self, is_on: bool) -> None:
        """Put the restored state back into the shared projector state."""


class AstronautProjectorPowerSwitch(AstronautProjectorSwitch):
    """Projector power, sent as the remote's single toggle code."""

    @property
    @override
    def is_on(self) -> bool:
        """Return the assumed power state."""
        return self._projector.power

    @override
    def _restore(self, is_on: bool) -> None:
        self._projector.power = is_on

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Wake the projector, send the power toggle and assume it came on.

        The toggle is sent even when the projector is assumed on already, so
        pressing on again is how a projector out of step is brought back.
        """
        await self._send_commands(
            wake_command(),
            AstronautProjectorCode.POWER.to_command(
                repeats=self._projector.power_on_repeats
            ),
        )
        self._projector.power_on()
        self._projector.async_notify()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Send the power toggle and assume the projector went off."""
        await self._send_command(AstronautProjectorCode.POWER.to_command())
        self._projector.power = False
        self._projector.async_notify()


class AstronautProjectorStarsSwitch(AstronautProjectorSwitch):
    """The laser stars: a short press turns them on, a long press off."""

    @property
    @override
    def is_on(self) -> bool:
        """Return whether the stars are assumed on."""
        return self._projector.power and self._projector.stars

    @override
    def _restore(self, is_on: bool) -> None:
        self._projector.stars = is_on

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the stars on, unless they are assumed on already."""
        self._raise_if_powered_off()
        if self._projector.stars:
            return
        await self._send_command(AstronautProjectorCode.STAR.to_command())
        self._projector.stars = True
        self._projector.async_notify()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the stars off.

        Safe to repeat: from off, the hold turns them on and straight off again.
        """
        self._raise_if_powered_off()
        await self._send_command(
            AstronautProjectorCode.STAR.to_command(long_press=True)
        )
        self._projector.stars = False
        self._projector.async_notify()


class AstronautProjectorNebulaSwitch(AstronautProjectorSwitch):
    """The LED nebula: a short press turns it on at green, a long press off."""

    @property
    @override
    def is_on(self) -> bool:
        """Return whether the nebula is assumed on."""
        return self._projector.power and self._projector.nebula

    @override
    def _restore(self, is_on: bool) -> None:
        self._projector.nebula = is_on

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the nebula on, unless it is assumed on already.

        A short press while the nebula is on steps the colour instead.
        """
        self._raise_if_powered_off()
        if self._projector.nebula:
            return
        await self._send_command(AstronautProjectorCode.NEBULA_COLOR.to_command())
        self._projector.nebula = True
        self._projector.nebula_color = NebulaColor.GREEN
        self._projector.async_notify()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the nebula off.

        Safe to repeat: from off, the hold turns it on and straight off again.
        """
        self._raise_if_powered_off()
        await self._send_command(
            AstronautProjectorCode.NEBULA_COLOR.to_command(long_press=True)
        )
        self._projector.nebula = False
        self._projector.async_notify()
