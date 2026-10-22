"""Astronaut Projector Infrared integration for Home Assistant."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .state import AstronautProjectorConfigEntry, ProjectorState

PLATFORMS = [Platform.BUTTON, Platform.NUMBER, Platform.SELECT, Platform.SWITCH]


async def async_setup_entry(
    hass: HomeAssistant, entry: AstronautProjectorConfigEntry
) -> bool:
    """Set up an astronaut projector from a config entry."""
    entry.runtime_data = ProjectorState()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AstronautProjectorConfigEntry
) -> bool:
    """Unload an astronaut projector config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
