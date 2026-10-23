"""Select platform for the Astronaut Projector Infrared integration."""

from typing import override

from infrared_protocols.commands import Command

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .codes import AstronautProjectorCode
from .entity import AstronautProjectorEntity
from .state import (
    NEBULA_COLORS,
    AstronautProjectorConfigEntry,
    NebulaColor,
    PowerOnMethod,
)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AstronautProjectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the astronaut projector selects."""
    async_add_entities(
        [
            AstronautProjectorNebulaColorSelect(entry, "nebula_color"),
            AstronautProjectorPowerOnMethodSelect(entry, "power_on_method"),
        ]
    )


class AstronautProjectorNebulaColorSelect(
    AstronautProjectorEntity, SelectEntity, RestoreEntity
):
    """Nebula colour, reached by stepping through the colour cycle."""

    _attr_assumed_state = True
    _attr_options = [color.value for color in NEBULA_COLORS]

    def __init__(self, entry: AstronautProjectorConfigEntry, key: str) -> None:
        """Initialize the select."""
        super().__init__(entry, key)
        self._attr_translation_key = key

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the last colour and follow changes made by sibling entities."""
        await super().async_added_to_hass()
        if (
            last_state := await self.async_get_last_state()
        ) is not None and last_state.state in self._attr_options:
            self._projector.nebula_color = NebulaColor(last_state.state)
            self._projector.async_notify()
        self.async_on_remove(
            self._projector.async_add_listener(self.async_write_ha_state)
        )

    @property
    @override
    def current_option(self) -> str | None:
        """Return the assumed colour while the nebula is on."""
        if not (self._projector.power and self._projector.nebula):
            return None
        return self._projector.nebula_color

    @override
    async def async_select_option(self, option: str) -> None:
        """Step the colour button until the nebula shows the chosen colour.

        Turning the nebula on with its own button always starts at green, so
        when the current colour is unknown the nebula is switched off and on
        again to count from there.
        """
        self._raise_if_powered_off()
        target = NEBULA_COLORS.index(NebulaColor(option))
        code = AstronautProjectorCode.NEBULA_COLOR
        commands: list[Command] = []
        if self._projector.nebula and self._projector.nebula_color is not None:
            presses = target - NEBULA_COLORS.index(self._projector.nebula_color)
        else:
            if self._projector.nebula:
                commands.append(code.to_command(long_press=True))
            commands.append(code.to_command())
            presses = target
        commands.extend(code.to_command() for _ in range(presses % len(NEBULA_COLORS)))
        await self._send_commands(*commands)
        self._projector.nebula = True
        self._projector.nebula_color = NebulaColor(option)
        self._projector.async_notify()


class AstronautProjectorPowerOnMethodSelect(
    AstronautProjectorEntity, SelectEntity, RestoreEntity
):
    """How power-on is sent, picked by whichever the unit takes reliably."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False
    _attr_options = [method.value for method in PowerOnMethod]

    def __init__(self, entry: AstronautProjectorConfigEntry, key: str) -> None:
        """Initialize the select."""
        super().__init__(entry, key)
        self._attr_translation_key = key

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the last setting."""
        await super().async_added_to_hass()
        if (
            last_state := await self.async_get_last_state()
        ) is not None and last_state.state in self._attr_options:
            self._projector.power_on_method = PowerOnMethod(last_state.state)

    @property
    @override
    def current_option(self) -> str:
        """Return the power-on method."""
        return self._projector.power_on_method

    @override
    async def async_select_option(self, option: str) -> None:
        """Set the power-on method."""
        self._projector.power_on_method = PowerOnMethod(option)
        self.async_write_ha_state()
