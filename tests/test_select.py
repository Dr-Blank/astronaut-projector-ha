"""Tests for the Astronaut Projector Infrared nebula colour select."""

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
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import ServiceValidationError

from .conftest import MockInfraredEmitterEntity, sent

COLOR = "select.astronaut_projector_nebula_color"
NEBULA = "switch.astronaut_projector_nebula"
POWER = "switch.astronaut_projector_power"

SHORT = (0x44, 0)
LONG = (0x44, 12)


async def _select(hass: HomeAssistant, option: str) -> None:
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: COLOR, ATTR_OPTION: option},
        blocking=True,
    )


async def _switch(hass: HomeAssistant, service: str, entity_id: str) -> None:
    await hass.services.async_call(
        SWITCH_DOMAIN, service, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )


@pytest.fixture
async def powered_on(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
) -> None:
    """Turn the projector on, nebula in auto-cycle, and forget the press."""
    await _switch(hass, SERVICE_TURN_ON, POWER)
    sent(mock_emitter)


@pytest.mark.usefixtures("powered_on")
@pytest.mark.parametrize(
    ("option", "presses"),
    [
        ("auto_cycle", 0),
        ("red_blue_green", 1),
        # Past the end of the cycle, back round to the start.
        ("green", 2),
        ("red_green", 7),
    ],
)
async def test_steps_from_known_color(
    hass: HomeAssistant,
    mock_emitter: MockInfraredEmitterEntity,
    option: str,
    presses: int,
) -> None:
    """Test the colour is reached by stepping forward from auto-cycle."""
    await _select(hass, option)

    assert sent(mock_emitter) == [SHORT] * presses
    assert hass.states.get(COLOR).state == option


@pytest.mark.usefixtures("powered_on")
async def test_turns_nebula_on_at_green(
    hass: HomeAssistant, mock_emitter: MockInfraredEmitterEntity
) -> None:
    """Test a colour picked with the nebula off turns it on and counts from green."""
    await _switch(hass, SERVICE_TURN_OFF, NEBULA)
    sent(mock_emitter)

    await _select(hass, "blue")

    assert sent(mock_emitter) == [SHORT, SHORT]
    assert hass.states.get(NEBULA).state == STATE_ON
    assert hass.states.get(COLOR).state == "blue"


@pytest.mark.usefixtures("mock_emitter")
async def test_unknown_color_restarts_from_green(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_emitter: MockInfraredEmitterEntity,
) -> None:
    """Test an unknown colour is found by switching the nebula off and on."""
    mock_restore_cache(hass, [State(POWER, STATE_ON), State(NEBULA, STATE_ON)])
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await _select(hass, "red")

    assert sent(mock_emitter) == [LONG, SHORT, SHORT, SHORT]
    assert hass.states.get(COLOR).state == "red"


@pytest.mark.usefixtures("init_integration")
async def test_refused_while_powered_off(
    hass: HomeAssistant, mock_emitter: MockInfraredEmitterEntity
) -> None:
    """Test the colour cannot be picked while the projector is off."""
    with pytest.raises(ServiceValidationError) as err:
        await _select(hass, "red")

    assert err.value.translation_key == "powered_off"
    assert sent(mock_emitter) == []
