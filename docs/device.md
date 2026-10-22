# Astronaut galaxy star projector

The generic "astronaut galaxy star projector" sold on Amazon and elsewhere: an astronaut figure on a base that throws a green laser star field and an LED "nebula" wash onto the ceiling, controlled by a 12-button infrared remote. It carries no brand on the unit, the box or the remote.

This page replaces the paper manual. Each behaviour is tagged with where it comes from:

- **[tested]** checked on a real unit, from its remote or from an infrared transmitter
- **[manual]** taken from the printed manual only

Where the two disagree, the tested behaviour wins and the difference is noted. The manual is wrong in several places.

## Hardware

| Item | Value | Source |
| --- | --- | --- |
| Power | 5 V ⎓ 1 A through a DC jack on the base; must stay plugged in (no battery) | [manual] |
| Stars | 532 nm green laser, Class I, < 1 mW | [manual] |
| Nebula | RGB LED | [tested] |
| Size | 155 × 113 × 233 mm | [manual] |
| Working temperature | 10–40 °C | [manual] |
| Remote range | < 5 m | [manual] |
| Materials | ABS / PC / PVC / TPE | [manual] |

Physical notes [manual]:

- Do not look straight into the laser.
- The head and body join with magnets; turn the head to aim the projection. Pulling them apart can break the wires inside.
- The feet must sit fully in the base.
- The laser is temperature-sensitive. Below 10 °C the stars may not show for the first few minutes after power-on. When it is hot, the stars dim after long use; switch off for 15 minutes or more to cool down and get full brightness back.

## Controls on the unit [manual]

Three keys on the back of the base, plus a timer LED.

| Key | Short press | Long press |
| --- | --- | --- |
| Power | toggle power; stars and nebula (auto-cycle) both come on at power-on | — |
| Nebula | next nebula colour | nebula off; short press turns it back on |
| Star | next star breathing rate | stars off; short press turns them back on |

The timer LED shows whether a timer is running (see [Timer](#timer)). The timer can only be set from the remote.

## Remote

Layout, top to bottom:

```text
 [POWER]         [TIMER]
           [B+]
   [S-]  [NEBULA]  [S+]          <- nebula group
           [B-]
   [S-]            [S+]          <- star breathing rate
          [STAR]
   [B-]            [B+]          <- star brightness
```

### Codes [tested]

Standard NEC on address `0x00`, one fixed code per button, no toggle bits.

| Button | Remote print | Code | Short press | Long press |
| --- | --- | --- | --- | --- |
| Power | ⏻ | `0x45` | toggle power | same as short |
| Timer | clock | `0x47` | next timer step | cancel timer |
| Nebula brightness up | B+ (ring) | `0x09` | nebula brighter | — |
| Nebula brightness down | B- (ring) | `0x15` | nebula dimmer | — |
| Nebula speed down | S- (ring) | `0x40` | nebula changes more slowly | — |
| Nebula speed up | S+ (ring) | `0x43` | nebula changes faster | — |
| Nebula colour | NEBULA | `0x44` | nebula on, or next colour | nebula off |
| Star breathing down | S- | `0x46` | one breathing gear towards steady | — |
| Star breathing up | S+ | `0x19` | one breathing gear away from steady | — |
| Star | STAR | `0xFF` | stars on | stars off |
| Star brightness down | B- | `0x07` | stars dimmer | — |
| Star brightness up | B+ | `0x0D` | stars brighter | — |

All codes except `0xFF` are the same as on the generic 21-key "Car MP3" remote. Other cheap devices that listen on address `0x00` in the same room may react to them too.

### Long press [tested]

There is no separate long-press code. Holding a button sends the frame once, then standard NEC repeat bursts: the first about 32 ms after the frame, then one every 108 ms or so. The projector counts how long the repeats last.

| Repeats after the frame | Result |
| --- | --- |
| 6 or fewer | short press |
| 7 or more (about 0.7 s) | long press |

The integration sends 12 repeats (about 1.2 s) for a margin.

### Power

- Short press toggles power [tested]. A long press does nothing extra [tested].
- A tap on the remote sends the frame and one repeat: 46 of 48 captured taps, the other two came in quick succession with no repeat received [tested]. A lone frame with no repeat turns the unit off but did not turn it on in Home Assistant, so the integration sends one repeat on power-on by default.
- While the unit is off, every other code is ignored. Only power turns it on [tested].
- Power-on always comes up in the same state, with no memory of how it was switched off [tested]:
  - stars on
  - nebula on, in **auto-cycle** (colour 7 below). The manual calls this "mixed colour".
- Brightness, speed and breathing rate probably reset to the manual's defaults too, but that has not been checked one by one.

### Nebula colour

- At power-on the nebula starts in **auto-cycle** (7) [tested].
- From nebula off: a short press turns the nebula back on at **green** (1), every time [tested]. So the starting colour depends on how the nebula came on: power-on gives auto-cycle, the nebula button gives green.
- From nebula on: each short press steps to the next colour [tested]. From auto-cycle (7), one press goes to 8. After 8 it goes back to 1 [tested].

  | # | Colour |
  | --- | --- |
  | 1 | green |
  | 2 | blue |
  | 3 | red |
  | 4 | blue + green |
  | 5 | red + blue |
  | 6 | red + green |
  | 7 | auto-cycle through all colours |
  | 8 | red + blue + green |

- A long press turns the nebula off [tested]. The first frame of the hold acts as a short press before the hold registers:
  - nebula off: the frame turns it on at green, then the hold turns it off again
  - nebula on: the frame steps the colour, then the hold turns it off

### Nebula brightness

- 5 levels: low, low-mid, mid, high-mid, high [tested]. Default is mid [manual].
- Each press moves one level and stops at low or high; it does not wrap [tested].

### Nebula change speed

- 5 gears, 0–4. Gear 0 = static colour, gear 4 = fastest change [tested]. Default is gear 2 [manual].
- S+ stops at gear 4: after 15 presses of S+, exactly 4 presses of S- reach static [tested].
- The manual says S+ goes up only "until the third level". That is wrong.

### Stars

- Short press with the stars off: stars on [tested].
- Long press with the stars on: stars off [tested].

### Star breathing rate

- 5 gears, 0–4 [tested]. Gear 0 = stars steady (no breathing). From the top gear, exactly 4 presses of S- reach steady [tested].
- At the top gear the breathing is the **slowest** [tested]. So S+ moves away from steady towards slower breathing, the opposite of the manual's "S+ increases the frequency".
- The manual says 4 gears (0–3) with default gear 2. The gear count is wrong.

### Star brightness

- 3 levels: low, mid, high [tested]. Default is high [manual].
- Each press moves one level and stops at low or high; it does not wrap [tested].
- Only applies to steady stars (breathing gear 0). Breathing stars ignore the brightness level [tested].

### Timer

| Press | LED [tested] | Duration [manual] |
| --- | --- | --- |
| 1st | red | 45 or 90 min |
| 2nd | blue | 45 or 90 min |
| 3rd and later | keeps alternating red ↔ blue | |
| long press | off (timer cancelled) | |

The manual says the first press is **blue, 45 min** and the second **red, 90 min**. The tested unit shows red first, so the manual's colour order is wrong, and which colour means 45 and which 90 min has not been measured. When the timer runs out the unit switches off [manual].

## Not yet checked

- A short press of STAR while the stars are already on: breathing step, or nothing?
- Which timer colour is 45 min and which is 90.
- Whether the S- buttons stop at gear 0 or wrap round.
- Breathing speeds at gears 1–3, and the breathing gear after power-on.
- Whether brightness, speed and breathing rate reset at power-on.
