"""Number platform for the Astronaut Projector Infrared integration."""

from typing import override

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import SHORT_PRESS_MAX_REPEATS
from .entity import AstronautProjectorEntity
from .state import AstronautProjectorConfigEntry

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AstronautProjectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the astronaut projector power-on repeats setting."""
    async_add_entities(
        [AstronautProjectorPowerOnRepeatsNumber(entry, "power_on_repeats")]
    )


class AstronautProjectorPowerOnRepeatsNumber(AstronautProjectorEntity, RestoreNumber):
    """How many NEC repeat bursts follow the power frame when turning on."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = SHORT_PRESS_MAX_REPEATS
    _attr_native_step = 1

    def __init__(self, entry: AstronautProjectorConfigEntry, key: str) -> None:
        """Initialize the number."""
        super().__init__(entry, key)
        self._attr_translation_key = key

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the last setting."""
        await super().async_added_to_hass()
        if (
            last_data := await self.async_get_last_number_data()
        ) is not None and last_data.native_value is not None:
            self._projector.power_on_repeats = int(last_data.native_value)

    @property
    @override
    def native_value(self) -> float:
        """Return the number of repeats power-on sends."""
        return self._projector.power_on_repeats

    @override
    async def async_set_native_value(self, value: float) -> None:
        """Set the number of repeats power-on sends."""
        self._projector.power_on_repeats = int(value)
        self.async_write_ha_state()
