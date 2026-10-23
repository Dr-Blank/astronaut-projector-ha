# Astronaut Projector Infrared for Home Assistant

Control the generic "astronaut galaxy star projector" from Home Assistant through an infrared transmitter. This is the unbranded astronaut figure that projects green laser stars and a coloured LED nebula, sold with a 12-button remote.

Infrared only goes one way, so Home Assistant cannot read what the projector is doing. It keeps track of what it last sent instead, and every entity shows that as an assumed state. The projector always powers on in the same state, which lets that assumption start from a known point.

For everything the projector and its remote do, including where the printed manual is wrong, see [docs/device.md](docs/device.md).

## Supported devices

Astronaut projectors whose remote looks like this:

```text
 [POWER]         [TIMER]
           [B+]
   [S-]  [NEBULA]  [S+]
           [B-]
   [S-]            [S+]
          [STAR]
   [B-]            [B+]
```

Projectors with a different remote, for example one with laser buttons, use other codes and will not respond.

## Requirements

- Home Assistant 2026.10.0 or newer.
- An infrared transmitter set up in Home Assistant as an infrared entity, for example an ESPHome device with an IR LED and the infrared proxy, in line of sight of the projector.

## Entities

| Entity | Type | What it does |
| --- | --- | --- |
| Power | switch | Sends the remote's power button. The projector has a single toggle code, so on and off send the same thing. |
| Stars | switch | On: short press of STAR. Off: long press. |
| Nebula | switch | On: short press of NEBULA, which always starts at green. Off: long press. |
| Nebula color | select | Steps the NEBULA button until the nebula shows the chosen colour. |
| Timer | button | Steps the sleep timer (LED red, then blue, alternating). |
| Cancel timer | button | Long press of TIMER. |
| Nebula brightness up / down | button | 5 levels, stops at the ends. |
| Nebula speed up / down | button | Static, then 4 speeds, stops at the ends. |
| Star breathing up / down | button | Down goes towards steady stars, up towards slower breathing. |
| Star brightness up / down | button | 3 levels, steady stars only. |
| Power-on repeats | number (configuration) | NEC repeat bursts sent after the power frame when turning on, 0 to 6, default 1, like a tap on the remote. |
| Power-on method | select (configuration) | **Single press** (default) or **Double press**: power sent twice, 200 ms apart. See [Troubleshooting](#troubleshooting). |

Turning power on resets the assumed state to how the projector always comes up: stars on, nebula on in auto-cycle. While the projector is assumed off, the stars, nebula and colour refuse changes, because the projector ignores every button except power when off.

## Installation

### HACS (recommended)

This is a custom repository, so HACS has to be told about it once. After that it updates like any other HACS integration.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dr-Blank&repository=astronaut-projector-ha&category=integration)

Click the badge above, then **Download**. It fills the repository in for you.

If the badge does not work, add it by hand:

1. **HACS > ⋮ (top right) > Custom repositories**.
2. Repository `https://github.com/Dr-Blank/astronaut-projector-ha`, type **Integration**, then **Add**.
3. Search HACS for **Astronaut Projector Infrared** and **Download** it.

Either way, **restart Home Assistant** afterwards — custom integrations are only loaded at startup.

### Manual

Copy `custom_components/astronaut_projector_infrared` into your Home Assistant `config/custom_components/` directory and restart Home Assistant.

### Setup

**Settings > Devices & services > Add integration > Astronaut Projector Infrared**, then pick the infrared transmitter that can see the projector.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=astronaut_projector_infrared)

## Removal

Delete the integration from **Settings > Devices & services**, then remove it in HACS.

## Known limitations

- Brightness, speed and breathing are buttons, not levels: the projector only has step buttons, and Home Assistant cannot see which level it is on.
- The timer's colours are not mapped to 45 and 90 minutes yet.
- The codes are shared with many cheap remotes (the generic "Car MP3" remote), so other inexpensive devices in the same room may react too.

## Troubleshooting

**The entities show the wrong state.** Someone used the remote or the buttons on the base, or a command did not reach the projector. To bring Home Assistant back in step:

- **Power**: turn it on or off again from Home Assistant. Power always sends its toggle, even when it already shows the state you picked.
- **Stars or nebula**: turn it off, then on. Turning off is safe to repeat; turning on is skipped while Home Assistant believes it is already on, because a short press would change the colour or breathing instead.
- **Nebula colour**: turn the nebula off and on (it restarts at green), then pick the colour.

**Power turns the projector off but not on.** Some units fall into a deeper sleep a few seconds after switching off and spend the first press waking up. Set **Power-on method** to **Double press** on the device page: the first press wakes the projector and the second turns it on. Do not use it on a unit that turns on reliably with a single press, because it takes both presses and turns on then straight off again. Raising **Power-on repeats** did not help in testing.

**Nothing reacts.** Check the transmitter is in line of sight and within a few metres, and that the projector is on: when it is off, it ignores everything except power.
