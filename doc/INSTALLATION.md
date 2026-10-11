# Fugu2 installation

> **DRAFT, revised 2026-10-11 after two independent reviews. Not yet a product document.** The
> items marked **OPEN** are undecided, and several are safety questions. A test lab reads port
> types from the documentation that accompanies the product, so the port declarations below count
> only once the OPEN items are decided and this text ships with the product. Background, in the
> private `pv/ee/dcdc-tools` repository: `emc/DECLARATIONS-fugu2.md` (the declarations Fab
> accepted on 2026-09-07) and `emc/STANDARD-BASIS.md` §8.0a (no conducted DC-port test, decided
> 2026-10-11, with an accepted residual risk on the battery port).

## Intended use

Fugu2 is a solar charge controller for stand-alone (off-grid) battery systems. It charges a
battery from a photovoltaic (PV) array. Power flows from the PV input to the battery output.

- It is for fixed installation, wall-mounted with the power terminals facing down.
- It is intended for residential, commercial and light-industrial environments.
- It is not a grid-connected power converter: it does not feed or draw power from an AC mains
  network itself. It may be part of a system whose battery is also charged by other equipment,
  such as an inverter-charger.
- Boost operation with the terminals swapped (described in `README.md`) is not an intended use
  of the shipped product. OPEN: reconcile the README.

## Ratings

| Quantity | Value | Source |
|---|---|---|
| PV input voltage | 12–80 V | `README.md` |
| PV open-circuit voltage, maximum at the lowest ambient temperature | OPEN | |
| PV short-circuit current, maximum | OPEN | Victron specifies this rating for SmartSolar |
| Battery voltage | 12–60 V (LiFePO4 4S–16S) | `README.md` |
| Output current, maximum | 32 A | `README.md` |
| Terminal wire range and tightening torque, J9 and J10 | OPEN | Würth 691256610002 datasheet |
| Operating temperature range | OPEN | |

**PV fuse.** The PV input needs no fuse for PV operation (Fab, 2026-10-11): a PV array is a
current-limited source, and Victron's SmartSolar has no PV fuse either. F3 (25 A, 58 V) exists
only for boost operation, where the battery sits at the PV terminals (`doc/HV Fuse.md`). Boost is
not an intended use of the shipped product (see Intended use).

## Ports and cabling

Connect each port only as listed, and keep each cable within its maximum length:

| Port | Connector | On-board fuse | Connect to | Do not connect to | Max. cable length |
|---|---|---|---|---|---|
| PV input | J10, 2-pole terminal block (T_HV+, BuckGND) | F3, 25 A, 58 V, in T_HV+: for boost operation only, not a PV protection device | one PV array (a string, or strings in parallel within the Isc rating) on its own cable | any other source; a DC distribution bus; earth (see Grounding) | **29 m** |
| Battery | J9, 2-pole terminal block (BT+, GND) | F1, 40 A, in BT+ (voltage rating OPEN) | the battery's system side, **through a fuse at the battery end**: positive after the battery fuse and the BMS disconnect; negative after the BMS disconnect and any battery shunt. A fused output of a DC distributor is fine | the raw cell terminals of a battery whose BMS or shunt is separate; a load or inverter wired to Fugu2's terminals; another charger's output | **2 m** |
| External comms | J5, JST-PH 4-pin, VE.Direct pinout | none | a VE.Direct cable (OPEN: the Fugu RS-485 and CAN adapters are not built yet) | any other device: pin 4 (+3.3 V) has no short-circuit or back-feed protection | **< 3 m** (OPEN, see below) |
| USB | P2, USB-C on the main board | none | a computer, for configuration and firmware updates. P2 is also a power input (Vusb) | a USB charger used as a supply during operation (OPEN) | **< 3 m** (OPEN, see below) |

The battery port is intended solely for connection to a battery or other local DC power source,
as described in the table.

### Grounding

PV negative (BuckGND) and battery negative (GND) are separate terminals. Inside Fugu2 they are
joined only through the current-sense shunt R26 (0.5 mΩ), and Fugu2 is not isolated.

- Never connect PV negative to battery negative, or to earth, outside Fugu2. Any external link
  bypasses the current measurement used for regulation and protection.
- Earth the system at one point only, at the battery negative.
- Do not earth either PV conductor.
- J5 and P2 are referenced to battery negative and are not isolated. A computer or device whose
  ground is earthed elsewhere creates a second earth connection. OPEN: decide whether to require
  an isolated USB link or an unearthed laptop.
- Heatsink and enclosure potential: OPEN (see Assembly requirements).

### Wiring rules

- Run the positive and negative conductors of each power port together, bundled tightly over the
  whole cable length, and twisted where practical.
- Connect the battery before the PV array, and disconnect the PV array before the battery.
  OPEN: confirm that this order suits Fugu2's input circuit.
- Fuse the battery cable at the battery end with a fuse rated for the battery's DC voltage and
  prospective short-circuit current (for example Class T or MEGA), sized to the cable. F1
  protects Fugu2, but it sits at the far end of the cable from the battery, so it can't protect
  the cable itself.
- Check polarity before connecting. A reversed battery is cleared only by F1.
- Connect loads and inverters to the battery or its distribution system, never to Fugu2's
  battery terminals.

## Why each statement is there

This section is for the design team. Remove it from the shipped version. Each row names a
statement above, the standard it serves, and what it changes:

| Statement | Standard it serves | Effect |
|---|---|---|
| Not a grid-connected power converter | EN 55011:2016+A1 §6.2.1.1 and §8.2.2.2.1 (read from Fab's DRM copy; quoted in `STANDARD-BASIS.md` §8.0) | Only grid-connected power converters have DC-port limits, so Fugu2 has none under the harmonised edition. |
| Fixed installation | EN 301 489-1 V2.2.3 §8.3.1 ("radio equipment and ancillary equipment for fixed use") | Places the DC-port clause's applicability question on the cable and network conditions below. |
| Residential, commercial, light industrial | EN 61000-6-3:2007+A1:2011 | Selects the class B generic emission standard, as Victron's SmartSolar DoCs do. Immunity is a separate choice. **Decided (Fab, 2026-10-11): EN 61000-6-2:2019 (industrial immunity)**, the pairing in Victron's 2025 DoC. |
| Battery port designed to pass, not argued out of the test | EN 61000-6-3 Table 3 (DC power port, class B); IEC 61000-6-3:2006 §3.8 NOTE (§3.1.8 in the 2011 edition) | **Decided 2026-10-11 (Fab): C10 is the Chemi-Con EKZN101ELL102MM40S**, the part the PCB already specifies. In simulation it passes the Table 3 AV limit by about 2.4 dB at the rated operating point (`emc/RESULTS-batport-20261010.md`; ESL borrowed from same-size KZN models). A lab may still classify the battery bus as a DC power network, because the battery also feeds the inverter and loads (the NOTE excludes a battery link only *"if such a link comprises only power supply for a single piece of equipment"*). If it does, the port is tested and is designed to pass, so the manual needs no dedicated-cable rule. |
| Battery: 2 m | EN 301 489-1 V2.2.3 §8.3.1 (> 3 m); EN 61000-6-3 Table 3 note (cable exceeding 30 m); CISPR 11 Table 6 (`L < 3 m`) | Removes the "local battery" length branch of each route. It does not affect the DC-power-network branch. |
| Battery: "intended solely for connection to a battery or other local DC power source" | CISPR 11 §8.2.2.2.1 battery exemption | Gives a second route if a later CISPR 11 edition is cited. It must stay true in every document, including the README (see Intended use). |
| PV: one array on its own cable | IEC 61000-6-3 §3.8 | A dedicated PV string is plausibly not a site supply network. This is an interpretation; no clause names PV strings. |
| PV: 29 m | CISPR 11 Table 6 (`3 m ≤ L < 30 m`); EVVO report BL-SZ19B0347-401 skips DC-port emissions for cables shorter than 30 m | Limits the conducted band to ≥ 2.07 MHz (60/29) if CISPR 11 ed 6.2 or later applies. Exactly 30 m would restore the full band. |
| PV: 29 m (immunity side effect) | EN 301 489-1 §9.4, §9.5 | The PV port **is** tested for fast transients and RF common-mode immunity, because its cable may exceed 3 m. The battery port at 2 m is not. |
| Comms and USB < 3 m | EN 301 489-1 V2.2.3 §9.4 (fast transients) and §9.5 (RF common mode): *"performed on signal ports, wired network ports, control ports, and DC power ports … if the cables may be longer than 3 m"* | The lab skips these immunity tests on ports declared < 3 m and records which ports it skipped. ESD (§9.3) still applies to the exposed connectors. |
| J5 classification | EN 301 489-1 V2.2.3 §3.1 ("wired network port" interconnects widely dispersed systems) | A short link to a local BMS is a signal port. A CAN or RS-485 bus that interconnects dispersed systems may be a wired network port, which brings §8.7's conducted emission test with no 3 m exemption. The classification depends on the declared topology, not on the protocol. |
| Bundled power pairs | none (design choice) | Reduces the loop area that radiates. Radiated emissions still apply on every route, and that's where the margin is tightest. |

## OPEN: decisions needed before this ships

1. **Battery port: decided 2026-10-11, hardware.** C10 is the Chemi-Con EKZN101ELL102MM40S
   (simulated −2.4 dB against Table 3 AV; the bench board's Rubycon ZLH fails by about 4.3 dB).
   Still open: confirm that the 40 mm can fits the enclosure, and measure the margin on the bench
   once the part is fitted. The simulated margin uses an ESL borrowed from same-size KZN models.
2. **PV limits.** Maximum array Voc (at the lowest ambient temperature) and Isc. No PV fuse is
   required (decided 2026-10-11).
3. **F1 voltage rating.** F1 is specified only as 40 A. Standard ATO fuses are rated 32 V,
   below a 16S LiFePO4 battery. Specify a part rated for the maximum battery voltage.
4. **Battery-end fuse coordination.** A larger rating alone doesn't make F1 open first. If
   selectivity is wanted, verify it from both fuses' characteristics and the prospective fault
   current.
5. **External comms.** Which adapters ship, the topology and cable length each supports, and whether a remote device must share Fugu2's
   battery negative.
6. **USB.** Whether P2 stays installer-accessible, the earthing condition for the host, and
   whether the MCU head's USB-C ships at all (`plans/ext-comms-port.md` Q14 calls it a
   development and service port).
7. **Immunity standard.** Decided 2026-10-11: EN 61000-6-2:2019. Its industrial test levels are
   not yet checked against Fugu2's design.
8. **Remaining ratings and safety content.** The empty rows of the ratings table,
   disconnection instructions, and the other installation content that IEC/EN 62109-1 §5.3
   requires.
9. **Lab test specification.** A separate controlled document for the lab: operating modes
   (for example 72 V in, 27 V out, 32 A, BLE active), ancillary equipment, functional monitoring
   and thermal limits (EN 301 489-1 Annex C).
10. **Delivery.** IEC 62109-1 §5.3.1.2 generally requires the safety instructions on paper with
    the product. A product-page link alone does not meet that.

## Assembly requirements (for `doc/Assembly.md`)

These items are build rules, not installer instructions. They are recorded here until
`doc/Assembly.md` carries them.

**Heatsink path: OPEN, do not act on it yet.** The heatsink reaches BuckGND only through the H1
mounting screw. On the PCB at HEAD, H1 lands on `Net-(C14-Pad2)`, and C14 (1 µF, 100 V, X7S) in
parallel with R17 (200 kΩ) connects that net to BuckGND. The EMC study's "as built" board has a
0 Ω bridge at C14 instead. Its conducted results (`emc/RESULTS-av-rescore-20260930.md`):
as built, −6.62 dB vs the AV limit, common-mode limited at 16.38 MHz; with a nylon screw (no
path), −7.36 dB. A nylon screw is therefore not worse for conducted emissions. The study's
build constraints say no heatsink rule should be acted on until the screw path is extracted or
measured. Record which C14 fitting ships, and whether the heatsink contact face is bare metal.

**Off-board coil.** The coil connects to J3 (switch node, net `SW`) and J6 (coil output, net
`BflowS`) with solder wires. If the coil sat outside the enclosure, those leads would be a port
carrying the switch node. Keep the coil inside the enclosure, with the leads as short as
practical.
