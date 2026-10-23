"""Tests for the Astronaut Projector Infrared power-on method select."""

from infrared_protocols.commands.nec import NECCommand
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache,
)

from homeassistant.components.select import (
    ATTR_OPTION,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er

from .conftest import MockInfraredEmitterEntity, sent

METHOD = "select.astronaut_projector_power_on_method"
POWER = "switch.astronaut_projector_power"

PRESS = NECCommand(address=0xFF00, command=0x45, repeat_count=1).get_raw_timings()


async def _switch(hass: HomeAssistant, service: str) -> None:
    await hass.services.async_call(
        SWITCH_DOMAIN, service, {ATTR_ENTITY_ID: POWER}, blocking=True
    )


async def _select(hass: HomeAssistant, option: str) -> None:
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: METHOD, ATTR_OPTION: option},
        blocking=True,
    )


@pytest.mark.usefixtures("init_integration")
async def test_single_by_default(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_emitter: MockInfraredEmitterEntity,
) -> None:
    """Test power-on sends one press until the method is changed."""
    state = hass.states.get(METHOD)
    assert state is not None
    assert state.state == "single"
    assert state.attributes["options"] == ["single", "double"]
    entry = entity_registry.async_get(METHOD)
    assert entry is not None
    assert entry.entity_category == "config"

    await _switch(hass, SERVICE_TURN_ON)
    assert sent(mock_emitter) == [(0x45, 1)]


@pytest.mark.usefixtures("init_integration")
async def test_double_press(
    hass: HomeAssistant, mock_emitter: MockInfraredEmitterEntity
) -> None:
    """Test a double press sends the press twice, 200 ms apart, in one go."""
    await _select(hass, "double")
    assert hass.states.get(METHOD).state == "double"
    assert mock_emitter.send_command_calls == []

    await _switch(hass, SERVICE_TURN_ON)
    assert len(mock_emitter.send_command_calls) == 1
    command = mock_emitter.send_command_calls.pop()
    assert command.modulation == 38000
    assert command.get_raw_timings() == [*PRESS, -200_000, *PRESS]

    await _switch(hass, SERVICE_TURN_OFF)
    assert sent(mock_emitter) == [(0x45, 0)]


async def test_restore(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
) -> None:
    """Test the method survives a restart."""
    mock_restore_cache(hass, [State(METHOD, "double")])
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(METHOD).state == "double"
    await _switch(hass, SERVICE_TURN_ON)
    assert mock_emitter.send_command_calls.pop().get_raw_timings() == [
        *PRESS,
        -200_000,
        *PRESS,
    ]
