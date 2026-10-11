# Fugu2 installation

> **DRAFT, 2026-10-11. Not yet a product document.** The EMC study agreed the content, but the
> items marked **OPEN** are undecided. A test lab reads port types from the documentation that
> accompanies the product, so the port declarations below count only once the OPEN items are
> decided and this text ships with the product. Background:
> `pv/ee/dcdc-tools/emc/DECLARATIONS-fugu2.md` (the declarations Fab accepted on 2026-09-07) and
> `STANDARD-BASIS.md` §8.0a (no conducted DC-port test, decided 2026-10-11).

## Intended use

Fugu2 is a solar charge controller for stand-alone (off-grid) battery systems. It charges a
battery from a photovoltaic (PV) array.

- It is intended for residential, commercial and light-industrial environments.
- It must not be connected to the public mains, directly or through any converter.
- It is not a grid-tie inverter and not part of a grid-connected system.

## Ports and cabling

Connect each port only as listed, and keep each cable within its maximum length:

| Port | Connector | On-board fuse | Connect to | Do not connect to | Max. cable length |
|---|---|---|---|---|---|
| PV input | J10, 2-pole terminal block | F3, 25 A (Solar+) | one PV array (a string, or strings in parallel) on its own cable | any other source; a DC distribution bus | **29 m** |
| Battery | J9, 2-pole terminal block | F1, 40 A (BT+) | **the battery terminals, or the battery's own fuse or disconnect, with a dedicated cable that serves only Fugu2** | a DC distribution busbar; loads; an inverter input; another charger's output | **2 m** |
| External comms | J5, JST-PH 4-pin, VE.Direct pinout | none | a VE.Direct cable, or the Fugu RS-485 or CAN adapter | anything else (the port has no hardware protection against a wrong adapter) | **< 3 m** (OPEN, see below) |
| USB | on the MCU head | none | a computer, for configuration and firmware updates | n/a | **< 3 m** (OPEN, see below) |

The battery port is intended solely for connection to a battery or other local DC power source.

### Wiring rules

- Run the positive and negative conductors of each power port together, twisted or bundled
  tightly, over the whole cable length.
- Fuse the battery cable at the battery end. F1 protects Fugu2, but it sits at the far end of
  the cable from the battery, so it can't protect the cable itself. Rating: OPEN.
- Connect loads and inverters to the battery or its distribution system, never to Fugu2's
  battery terminals.

## Why each statement is there

This section is for the design team. Remove it from the shipped version. Each row names a
statement above, the standard it serves, and what it changes:

| Statement | Standard it serves | Effect |
|---|---|---|
| Off-grid; never connected to the public mains | EN 55011:2016+A1 §6.2.1.1 and §8.2.2.2.1 | Only grid-connected power converters have DC-port limits, so Fugu2 has none under the harmonised edition (`STANDARD-BASIS.md` §8.0). |
| Residential, commercial, light industrial | EN 61000-6-3:2007+A1:2011 | Selects the class B generic emission standard, as Victron's SmartSolar DoCs do. |
| Battery: dedicated cable to the battery, serving only Fugu2 | IEC 61000-6-3 §3.8 NOTE | The NOTE keeps a battery link out of the "DC power network" definition only *"if such a link comprises only power supply for a single piece of equipment"*. A cable that lands on a busbar shared with an inverter doesn't meet that condition. |
| Battery: 2 m | EN 301 489-1 V2.2.3 §8.3.1 (> 3 m); EN 61000-6-3 Table 3 note (> 30 m); CISPR 11 ed 6.2+ (`L < 3 m`) | Removes the "local battery" branch of every route. |
| Battery: "intended solely for connection to a battery or other local DC power source" | CISPR 11 §8.2.2.2.1 battery exemption | Gives a second route if a later CISPR 11 edition is cited. |
| PV: one array on its own cable | IEC 61000-6-3 §3.8 | A dedicated PV string is not a site supply network. |
| PV: 29 m | CISPR 11 ed 6.2+ cable-length table; EVVO lab practice applies the 30 m note to PV ports too | Limits the conducted band to ≥ 2.07 MHz if a later edition applies. The value sits below 30 m on purpose, because the inequality is strict. |
| PV: 29 m (immunity side effect) | EN 301 489-1 §9.4, §9.5 | The PV port **is** tested for fast transients and RF common-mode immunity, because its cable may exceed 3 m. The battery port at 2 m is not. |
| Comms and USB < 3 m | EN 301 489-1 V2.2.3 §9.4 (fast transients) and §9.5 (RF common mode): *"performed on signal ports, wired network ports, control ports, and DC power ports … if the cables may be longer than 3 m"* | The lab skips these immunity tests on ports declared < 3 m and records which ports it skipped. CAN and RS-485 to a local BMS are signal ports, not "wired network ports" (§3.1: CATV, PSTN, LAN …), so §8.7's conducted emission test does not apply to them. |
| Twisted power pairs | none (design choice) | Reduces the loop area that radiates. Radiated emissions still apply on every route, and that's where the margin is tightest. |

## OPEN: decisions needed before this ships

1. **Can installers really give the battery a dedicated cable?** It is a real installation
   constraint, because most off-grid systems land everything on one busbar. If the constraint is
   not acceptable, delete the battery row's "dedicated cable" wording and design the battery port
   to meet EN 61000-6-3 Table 3. In simulation, a Chemi-Con EKZN101ELL102MM40S as C10 passes by
   about 2.4 dB, and the fitted Rubycon ZLH fails by about 4.3 dB
   (`emc/RESULTS-batport-20261010.md`).
2. **External comms cable length.** CAN and RS-485 are bus cables and often run longer than 3 m.
   Allowing a longer cable adds the §9.4 and §9.5 immunity tests on J5. It adds no emission test,
   because these are signal ports, not wired network ports. Decide the maximum length per adapter,
   or state that the adapter's pigtail and bus are a separate product.
3. **USB.** Is the USB port on the MCU head reachable when the unit is installed? If it is for
   factory or service use only, say so; the port may then not need a cable-length declaration.
4. **Battery-end fuse rating** and recommended cable cross-sections for J9 and J10. One option
   to weigh: rate the battery-end fuse above F1's 40 A, so that F1 opens first on a fault inside
   Fugu2, and within the cable's current rating.
5. **Where this text lives.** A lab reads it only if it ships with the product: as a printed
   sheet, in the manual, or on the product page linked from the DoC.

## Assembly requirements (for `doc/Assembly.md`)

These two items are build rules, not installer instructions. They are recorded here until
`doc/Assembly.md` carries them.

The H1 mounting screw is the only path from the heatsink to BuckGND. It must be a metal M3
screw, with no insulating washer. A nylon screw or shoulder washer moves the conducted
common-mode result from the bonded column to the floating one (`emc/DECLARATIONS-fugu2.md`,
Declaration C).

The off-board coil connects to J3 (SW) and J6 (L_out) with solder wires. If the coil sits outside
the enclosure, those leads become a port carrying the switch node. Keep the coil inside the
enclosure, with the leads as short as practical.
