"""Tests for the Astronaut Projector Infrared switches."""

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache,
)

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ASSUMED_STATE,
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import ServiceValidationError

from .conftest import MockInfraredEmitterEntity, sent

POWER = "switch.astronaut_projector_power"
STARS = "switch.astronaut_projector_stars"
NEBULA = "switch.astronaut_projector_nebula"
COLOR = "select.astronaut_projector_nebula_color"


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
    """Turn the projector on and forget the power press."""
    await _switch(hass, SERVICE_TURN_ON, POWER)
    sent(mock_emitter)


@pytest.mark.usefixtures("init_integration")
async def test_power_on_resets_everything(
    hass: HomeAssistant, mock_emitter: MockInfraredEmitterEntity
) -> None:
    """Test power-on brings stars and nebula on, the nebula in auto-cycle."""
    for entity_id in (POWER, STARS, NEBULA):
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == STATE_OFF
        assert state.attributes[ATTR_ASSUMED_STATE] is True

    await _switch(hass, SERVICE_TURN_ON, POWER)

    assert sent(mock_emitter) == [(0x00, 0), (0x45, 1)]
    for entity_id in (POWER, STARS, NEBULA):
        assert hass.states.get(entity_id).state == STATE_ON
    assert hass.states.get(COLOR).state == "auto_cycle"


@pytest.mark.usefixtures("powered_on")
async def test_power_toggle_always_sent(
    hass: HomeAssistant, mock_emitter: MockInfraredEmitterEntity
) -> None:
    """Test power sends its toggle even when already in the asked state."""
    await _switch(hass, SERVICE_TURN_ON, POWER)
    assert sent(mock_emitter) == [(0x00, 0), (0x45, 1)]

    await _switch(hass, SERVICE_TURN_OFF, POWER)
    assert sent(mock_emitter) == [(0x45, 0)]
    for entity_id in (POWER, STARS, NEBULA):
        assert hass.states.get(entity_id).state == STATE_OFF
    assert hass.states.get(COLOR).state == STATE_UNKNOWN


@pytest.mark.usefixtures("powered_on")
@pytest.mark.parametrize(("entity_id", "code"), [(STARS, 0xFF), (NEBULA, 0x44)])
async def test_long_press_turns_off(
    hass: HomeAssistant,
    mock_emitter: MockInfraredEmitterEntity,
    entity_id: str,
    code: int,
) -> None:
    """Test turning stars or nebula off sends a long press, even when off."""
    await _switch(hass, SERVICE_TURN_OFF, entity_id)
    assert sent(mock_emitter) == [(code, 12)]
    assert hass.states.get(entity_id).state == STATE_OFF

    await _switch(hass, SERVICE_TURN_OFF, entity_id)
    assert sent(mock_emitter) == [(code, 12)]


@pytest.mark.usefixtures("powered_on")
@pytest.mark.parametrize(("entity_id", "code"), [(STARS, 0xFF), (NEBULA, 0x44)])
async def test_short_press_turns_on(
    hass: HomeAssistant,
    mock_emitter: MockInfraredEmitterEntity,
    entity_id: str,
    code: int,
) -> None:
    """Test turning stars or nebula on sends a short press, only when off."""
    await _switch(hass, SERVICE_TURN_ON, entity_id)
    assert sent(mock_emitter) == []

    await _switch(hass, SERVICE_TURN_OFF, entity_id)
    sent(mock_emitter)
    await _switch(hass, SERVICE_TURN_ON, entity_id)
    assert sent(mock_emitter) == [(code, 0)]
    assert hass.states.get(entity_id).state == STATE_ON


@pytest.mark.usefixtures("powered_on")
async def test_nebula_on_starts_at_green(hass: HomeAssistant) -> None:
    """Test the nebula's own button brings it back at green."""
    await _switch(hass, SERVICE_TURN_OFF, NEBULA)
    assert hass.states.get(COLOR).state == STATE_UNKNOWN

    await _switch(hass, SERVICE_TURN_ON, NEBULA)
    assert hass.states.get(COLOR).state == "green"


@pytest.mark.usefixtures("init_integration")
@pytest.mark.parametrize("entity_id", [STARS, NEBULA])
@pytest.mark.parametrize("service", [SERVICE_TURN_ON, SERVICE_TURN_OFF])
async def test_refused_while_powered_off(
    hass: HomeAssistant,
    mock_emitter: MockInfraredEmitterEntity,
    entity_id: str,
    service: str,
) -> None:
    """Test stars and nebula refuse changes the projector would ignore."""
    with pytest.raises(ServiceValidationError) as err:
        await _switch(hass, service, entity_id)

    assert err.value.translation_key == "powered_off"
    assert sent(mock_emitter) == []


@pytest.mark.usefixtures("mock_emitter")
async def test_restore(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test the assumed state survives a restart."""
    mock_restore_cache(
        hass,
        [
            State(POWER, STATE_ON),
            State(STARS, STATE_OFF),
            State(NEBULA, STATE_ON),
            State(COLOR, "red"),
        ],
    )
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(POWER).state == STATE_ON
    assert hass.states.get(STARS).state == STATE_OFF
    assert hass.states.get(NEBULA).state == STATE_ON
    assert hass.states.get(COLOR).state == "red"
