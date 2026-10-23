"""Fixtures for the Astronaut Projector Infrared tests."""

from collections.abc import Generator
from typing import override
from unittest.mock import patch

from infrared_protocols.commands import Command
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.components.infrared import DATA_COMPONENT, InfraredEmitterEntity
from homeassistant.components.infrared.const import DOMAIN as INFRARED_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.astronaut_projector_infrared.const import (
    CONF_INFRARED_EMITTER_ENTITY_ID,
    DOMAIN,
)
from custom_components.astronaut_projector_infrared.number import (
    AstronautProjectorPowerOnRepeatsNumber,
)
from custom_components.astronaut_projector_infrared.select import (
    AstronautProjectorPowerOnMethodSelect,
)

EMITTER_ENTITY_ID = "infrared.test_ir_emitter"


class MockInfraredEmitterEntity(InfraredEmitterEntity):
    """Infrared emitter that records what it was asked to send."""

    _attr_has_entity_name = True
    _attr_name = "Test IR emitter"
    _attr_unique_id = "test_ir_emitter"

    def __init__(self) -> None:
        """Initialize the emitter."""
        self.send_command_calls: list[Command] = []

    @override
    async def async_send_command(self, command: Command) -> None:
        """Record the command."""
        self.send_command_calls.append(command)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load the integration from custom_components."""


@pytest.fixture(autouse=True)
def no_press_gap() -> Generator[None]:
    """Send presses in a row without waiting between them."""
    with patch("custom_components.astronaut_projector_infrared.entity.PRESS_GAP", 0):
        yield


@pytest.fixture
def enable_power_on_settings() -> Generator[None]:
    """Enable the power-on settings, which are disabled by default."""
    with (
        patch.object(
            AstronautProjectorPowerOnRepeatsNumber,
            "_attr_entity_registry_enabled_default",
            True,
        ),
        patch.object(
            AstronautProjectorPowerOnMethodSelect,
            "_attr_entity_registry_enabled_default",
            True,
        ),
    ):
        yield


@pytest.fixture
async def init_infrared(hass: HomeAssistant) -> None:
    """Set up the infrared integration."""
    assert await async_setup_component(hass, INFRARED_DOMAIN, {})
    await hass.async_block_till_done()


@pytest.fixture
async def mock_emitter(
    hass: HomeAssistant, init_infrared: None
) -> MockInfraredEmitterEntity:
    """Add an infrared emitter entity."""
    entity = MockInfraredEmitterEntity()
    await hass.data[DATA_COMPONENT].async_add_entities([entity])
    assert entity.entity_id == EMITTER_ENTITY_ID
    return entity


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry for the projector."""
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="01JTEST0000000000000000000",
        title="Astronaut Projector",
        data={CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID},
        unique_id=EMITTER_ENTITY_ID,
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
) -> MockConfigEntry:
    """Set up the integration."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry


def sent(emitter: MockInfraredEmitterEntity) -> list[tuple[int, int]]:
    """Return each sent command as (code, repeat count), then forget them."""
    calls = [
        (command.command, command.repeat_count)
        for command in emitter.send_command_calls
    ]
    emitter.send_command_calls.clear()
    return calls
