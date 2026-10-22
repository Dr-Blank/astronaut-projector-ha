"""IR codes for astronaut galaxy star projectors.

Standard NEC frames on address 0x00, one fixed code per button. The projector
tells a long press from a short one by how long the NEC repeat bursts last
after the frame: 7 or more repeats, about 0.7 s, count as a long press.
"""

from enum import IntEnum

from infrared_protocols.commands import Command
from infrared_protocols.commands.nec import NECCommand

# Address 0x00 followed by its inverse, 0xFF.
ADDRESS = 0xFF00

# Comfortably past the 7-repeat threshold, so one lost burst does not turn a
# long press into a short one.
LONG_PRESS_REPEATS = 12

# The most repeats that still read as a short press.
SHORT_PRESS_MAX_REPEATS = 6

# A tap on the remote sends the frame and one repeat. A projector that is off
# can miss a lone frame while it wakes, so power-on sends the repeat as well.
DEFAULT_POWER_ON_REPEATS = 1


class AstronautProjectorCode(IntEnum):
    """IR command codes for the astronaut projector remote."""

    POWER = 0x45
    TIMER = 0x47
    NEBULA_COLOR = 0x44
    NEBULA_BRIGHTNESS_UP = 0x09
    NEBULA_BRIGHTNESS_DOWN = 0x15
    NEBULA_SPEED_UP = 0x43
    NEBULA_SPEED_DOWN = 0x40
    STAR = 0xFF
    STAR_BREATHING_UP = 0x19
    STAR_BREATHING_DOWN = 0x46
    STAR_BRIGHTNESS_UP = 0x0D
    STAR_BRIGHTNESS_DOWN = 0x07

    def to_command(self, *, long_press: bool = False, repeats: int = 0) -> Command:
        """Build the NEC command for a short or long press of this button.

        A short press sends repeats bursts after the frame, which must stay at
        SHORT_PRESS_MAX_REPEATS or fewer to keep it short.
        """
        return NECCommand(
            address=ADDRESS,
            command=self.value,
            repeat_count=LONG_PRESS_REPEATS if long_press else repeats,
        )
