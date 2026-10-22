"""Common entity for the Astronaut Projector Infrared integration."""

import asyncio

from infrared_protocols.commands import Command

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_INFRARED_EMITTER_ENTITY_ID, DOMAIN
from .state import AstronautProjectorConfigEntry

# Pause between presses sent in a row, so the projector reads each frame as a
# press of its own rather than part of one hold.
PRESS_GAP = 0.5


class AstronautProjectorEntity(InfraredEmitterConsumerEntity):
    """Astronaut projector base entity."""

    _attr_has_entity_name = True

    def __init__(self, entry: AstronautProjectorConfigEntry, key: str) -> None:
        """Initialize the entity."""
        self._projector = entry.runtime_data
        self._infrared_emitter_entity_id = entry.data[CONF_INFRARED_EMITTER_ENTITY_ID]
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Astronaut Projector",
            model="Astronaut galaxy star projector",
        )

    async def _send_commands(self, *commands: Command) -> None:
        """Send presses one after another."""
        for index, command in enumerate(commands):
            if index:
                await asyncio.sleep(PRESS_GAP)
            await self._send_command(command)

    def _raise_if_powered_off(self) -> None:
        """Refuse a change the projector ignores while it is off."""
        if not self._projector.power:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="powered_off"
            )
