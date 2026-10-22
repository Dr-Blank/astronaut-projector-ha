"""Button platform for the Astronaut Projector Infrared integration."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import AstronautProjectorCode
from .entity import AstronautProjectorEntity
from .state import AstronautProjectorConfigEntry

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class AstronautProjectorButtonEntityDescription(ButtonEntityDescription):
    """Describes an astronaut projector button."""

    code: AstronautProjectorCode
    long_press: bool = False


BUTTONS: tuple[AstronautProjectorButtonEntityDescription, ...] = (
    AstronautProjectorButtonEntityDescription(
        key="timer",
        translation_key="timer",
        code=AstronautProjectorCode.TIMER,
    ),
    AstronautProjectorButtonEntityDescription(
        key="cancel_timer",
        translation_key="cancel_timer",
        code=AstronautProjectorCode.TIMER,
        long_press=True,
    ),
    *(
        AstronautProjectorButtonEntityDescription(
            key=code.name.lower(),
            translation_key=code.name.lower(),
            code=code,
        )
        for code in (
            AstronautProjectorCode.NEBULA_BRIGHTNESS_UP,
            AstronautProjectorCode.NEBULA_BRIGHTNESS_DOWN,
            AstronautProjectorCode.NEBULA_SPEED_UP,
            AstronautProjectorCode.NEBULA_SPEED_DOWN,
            AstronautProjectorCode.STAR_BREATHING_UP,
            AstronautProjectorCode.STAR_BREATHING_DOWN,
            AstronautProjectorCode.STAR_BRIGHTNESS_UP,
            AstronautProjectorCode.STAR_BRIGHTNESS_DOWN,
        )
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AstronautProjectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up astronaut projector buttons from a config entry."""
    async_add_entities(
        AstronautProjectorButton(entry, description) for description in BUTTONS
    )


class AstronautProjectorButton(AstronautProjectorEntity, ButtonEntity):
    """A remote button with no state to track."""

    entity_description: AstronautProjectorButtonEntityDescription

    def __init__(
        self,
        entry: AstronautProjectorConfigEntry,
        description: AstronautProjectorButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(entry, description.key)
        self.entity_description = description

    @override
    async def async_press(self) -> None:
        """Send the button's code."""
        await self._send_command(
            self.entity_description.code.to_command(
                long_press=self.entity_description.long_press
            )
        )
