"""Tests for the Astronaut Projector Infrared number."""

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache_with_extra_data,
)

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er

from .conftest import MockInfraredEmitterEntity, sent

REPEATS = "number.astronaut_projector_power_on_repeats"
POWER = "switch.astronaut_projector_power"


async def _power_on(hass: HomeAssistant) -> None:
    await hass.services.async_call(
        SWITCH_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: POWER}, blocking=True
    )


@pytest.mark.usefixtures("init_integration")
async def test_power_on_repeats(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_emitter: MockInfraredEmitterEntity,
) -> None:
    """Test the setting changes how many repeats power-on sends."""
    state = hass.states.get(REPEATS)
    assert state is not None
    assert state.state == "1"
    assert state.attributes["min"] == 0
    assert state.attributes["max"] == 6
    assert state.attributes["mode"] == "slider"
    entry = entity_registry.async_get(REPEATS)
    assert entry is not None
    assert entry.entity_category == "config"

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: REPEATS, ATTR_VALUE: 3},
        blocking=True,
    )
    assert hass.states.get(REPEATS).state == "3"
    assert sent(mock_emitter) == []

    await _power_on(hass)
    assert sent(mock_emitter) == [(0x45, 3)]


async def test_restore(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
) -> None:
    """Test the setting survives a restart."""
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(REPEATS, "4"),
                {
                    "native_max_value": 6,
                    "native_min_value": 0,
                    "native_step": 1,
                    "native_unit_of_measurement": None,
                    "native_value": 4,
                },
            )
        ],
    )
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(REPEATS).state == "4"
    await _power_on(hass)
    assert sent(mock_emitter) == [(0x45, 4)]
