"""Tests for the Astronaut Projector Infrared buttons."""

import pytest

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .conftest import MockInfraredEmitterEntity, sent


@pytest.mark.usefixtures("init_integration")
@pytest.mark.parametrize(
    ("entity_id", "expected"),
    [
        ("button.astronaut_projector_timer", (0x47, 0)),
        ("button.astronaut_projector_cancel_timer", (0x47, 12)),
        ("button.astronaut_projector_nebula_brightness_up", (0x09, 0)),
        ("button.astronaut_projector_nebula_brightness_down", (0x15, 0)),
        ("button.astronaut_projector_nebula_speed_up", (0x43, 0)),
        ("button.astronaut_projector_nebula_speed_down", (0x40, 0)),
        ("button.astronaut_projector_star_breathing_up", (0x19, 0)),
        ("button.astronaut_projector_star_breathing_down", (0x46, 0)),
        ("button.astronaut_projector_star_brightness_up", (0x0D, 0)),
        ("button.astronaut_projector_star_brightness_down", (0x07, 0)),
    ],
)
async def test_press(
    hass: HomeAssistant,
    mock_emitter: MockInfraredEmitterEntity,
    entity_id: str,
    expected: tuple[int, int],
) -> None:
    """Test each button sends its code, the cancel button as a long press."""
    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )

    assert mock_emitter.send_command_calls[0].address == 0xFF00
    assert sent(mock_emitter) == [expected]
