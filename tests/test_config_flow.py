"""Tests for the Astronaut Projector Infrared config flow."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import EMITTER_ENTITY_ID
from custom_components.astronaut_projector_infrared.const import (
    CONF_INFRARED_EMITTER_ENTITY_ID,
    DOMAIN,
)


@pytest.mark.usefixtures("mock_emitter")
async def test_user_flow(hass: HomeAssistant) -> None:
    """Test picking a transmitter creates the entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Astronaut Projector"
    assert result["data"] == {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
    assert result["result"].unique_id == EMITTER_ENTITY_ID


@pytest.mark.usefixtures("init_infrared")
async def test_no_emitters(hass: HomeAssistant) -> None:
    """Test the flow aborts when there is no transmitter to pick."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


@pytest.mark.usefixtures("mock_emitter")
async def test_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test a transmitter cannot be set up twice."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
