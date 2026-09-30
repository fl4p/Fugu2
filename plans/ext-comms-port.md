*this document is an LLM generated placeholder*

# Fugu2 rev: external comms port (VE.Direct-compatible, with CAN and RS-485 adapters)

**Scope: hardware only, meaning the connector, the circuitry on the port and the two adapter boards.**
Firmware and the choice of target BMS/inverter are scoped later. The firmware-side draft is in
`fugu-mppt-firmware/plans/ext-serial-port.md`.

**Status (2026-09-29):** the host-side port is captured in `ExtPort.kicad_sch` on branch `ext-comms-port`
(host changes 1–6 below). The layout is not started; it comes with the redesign (Q12).

## Goal

Replace `J5 "UART (CAN) Conn"` with a single protected 4-pin port in the Victron VE.Direct pinout. The
port carries logic-level TX/RX. The firmware puts either the UART or the TWAI (CAN) controller on the two
signal pins:

| Mode | What's plugged in |
|---|---|
| VE.Direct | Victron GX / VE.Direct-USB cable, plugged in directly |
| Modbus RTU | RS-485 adapter (small PCB with a pigtail) |
| CAN | CAN adapter (small PCB with a pigtail) |

The adapters are dumb: a fault-protected transceiver and little else, with no MCU (Q17). There is no ID
pin; Fab decided on 2026-09-28 that wrong-adapter protection is handled in software, and on 2026-09-29
that the hardware adds nothing for it beyond:
- A TX output-enable that hardware holds off through reset and boot.
- Adapters that echo TX back on RX.

## Decisions (Fab, 2026-09-28/29/30)

| # | Decision |
|---|---|
| Q1 | V+ comes from the 3.3 V rail. |
| Q3 | Place the connector the way Victron does: **next to the power terminals**. No connectors on the upper PCB side. The unit is wall-mounted with the power terminals facing down, so an upward-facing opening would let water in. |
| Q4 | Target BMS/inverter models come later; hardware only for now. |
| Q5 | Isolation: nothing special. Use the industry-standard ratings of off-the-shelf isolated CAN/RS-485 parts. *Superseded by Q17: the adapters are non-isolated.* |
| Q6 | mcu-head header grows 2×7 → **2×9** and carries the port signals; D+/D− are not added. **Re-confirm:** since Q15/Q16 the port needs only three signals, so 2×8 would do (see pin count below). The motherboard J4 is unchanged for now. |
| Q7 | Adapters are a small PCB with a pigtail. |
| Q8 | The RS-485 adapter echoes (/RE tied low). See the adapter section. |
| Q9 | GPIO7 tied to +3.3V is a rail voltage monitor. Keep it. **Review finding, open:** see GPIO7 below and Open questions. |
| Q10 | The redesign (Q12) supersedes syncing the July layout to the schematic. |
| Q11 | USB-C also moves next to the power terminals. |
| Q12 | The board gets a slight redesign with more area (additional Cin bulk caps), which makes room for both connectors on the bottom edge. The detailed placement is still open (see Open questions). |
| Q13 | The USB1 pin header is **removed**. The J2 I2C socket stays where it is. |
| Q14 | The product's USB-C is the motherboard one, in the lower board area (Q11). The head's USB-C is a development/service port; its position in the upper area is accepted. |
| Q15 | **No V+ load switch.** V+ is always on, **directly from the 3.3 V rail** (the back-feed Schottky D22 was removed on 2026-09-30: every ±60 V-class transceiver needs ≥ 3.0 V, and D22 left 2.7–2.95 V). **No short protection and no back-feed block on pin 4**: a short browns out the 3.3 V rail, and a peer driving pin 4 drives the rail. (A PTC was considered and rejected: any PTC that holds 0.17 A at 60 °C trips at 0.75 A, above the rail's 0.5 A, so it never trips.) |
| Q16 | **No V+ current sense.** Wrong-adapter handling is purely in software. |
| Q17 | **Adapters are non-isolated**, with ±70 V-class fault-protected transceivers (2026-09-30). The other device's ground normally sits at the same battery negative as Fugu. **Hard requirement: survive a GND fault on the 60 V battery** (16s LFP, 58.4 V max), where either ground floats to battery voltage relative to the other. |

## Current state: Fugu2 v2.3 (before this branch)

Sources:
- The netlist, exported with kicad-cli on 2026-09-29 from the schematic as committed in `3fb7364` (the
  working-tree edits last saved 2026-08-11).
- Footprint positions from `Fugu2.kicad_pcb`, last saved 2026-07-27. **The layout is older than the
  schematic.**

| Item | Finding |
|---|---|
| J5 | 1×4 socket at 2.54 mm: 1 = +3.3V, 2 = GND, 3 = CAN_RX (GPIO37), 4 = CAN_TX (GPIO36). Direct to the ESP32 with no protection. V+ is the unswitched 3.3 V rail. |
| J5 position | (76.0, 109.6) mm. That is the bottom-right corner, **already next to J9** (battery terminal at y = 113.7). The board spans x 28.7–78.7 and y 31–119, and the terminals are on the bottom edge. |
| Free GPIOs | Unconnected: 3, 5, 6, 9, 15–18, 38, 39, 45, 48. Unrouted `SPI*` labels: 10–13. |
| MCU module | ESP32-S3-WROOM-1-**N4** (motherboard U2) and -1U-N4 (head): quad flash, no PSRAM, so GPIO35–37 are free. Keep that variant; an octal-PSRAM module takes GPIO33–37. |
| GPIO7 | Tied directly to +3.3V (ADC1_CH6) as a rail monitor. The S3 ADC tops out below 3.3 V even at 12 dB attenuation, so the reading sits at full scale and only moves when the rail sags below the top of the range. It detects a sag, not the rail value. **Also:** the S3 datasheet (v2.2, Table 2-2) gives GPIO7 a ~60 µs *low-level output* glitch at power-up, which fights the rail through the pad. A divider or series resistor fixes both. |
| Ground | Logic GND is the battery-terminal negative (J9.2) and is bonded to the USB-C shell. Shunt R26 (0.5 mΩ) sits low-side between BuckGND (solar −, J10.1) and GND. A non-isolated link to anything referenced to a BMS's B− (behind a low-side FET) would bridge that FET; per Q17 the far end normally shares Fugu's battery negative. A GX on the same P− bus is fine over a plain VE.Direct cable. |
| 3.3 V | External `psu/buck100` board: LM5163, **0.5 A**. Fed through a diode-OR of Bat+, Solar+ and Vusb. It also supplies WiFi (module TX peak 355 mA, WROOM datasheet Table 6-4) and the AP3012 12 V gate-drive boost. |
| USB-C P2 | At (51, 34.5), on the **top edge**. Moves to the bottom (Q11). USB1 (1×4 USB pin header, top edge) is removed. J2 (I2C socket, mid-board) stays (Q13). |
| Bottom edge space | Courtyards: J10 x 32.2–52.6, J9 x 52.5–72.9 (both to y ≈ 120.0), J5 x 74.2–77.8 (to y ≈ 119.0). The board spans x 28.7–78.7, so the free strips are **3.5 mm on the left (mounting hole H4 at 30.7/105.5) and 5.8 mm on the right**. A JST-PH 4 side-entry is 9.9 mm wide and the current P2 courtyard is 10.7 mm, so **neither fits beside the terminals as the board stands** (Q12). |
| mcu-head | Its 2×7 header (J4 on the motherboard, J2 on the head) has 10 signals, GND on pins 2 and 7, +3.3V on pin 5, and one spare (pin 11). GPIO36/37 are not routed. **USB is not available on the motherboard when the head is used**: D+/D− are not on the header, and the head has its own USB-C (P1) and ESP-PROG header. The motherboard USB-C then carries no data; Vusb reaches the PSU through D7, but the LM5163 needs ≥ 6 V in (datasheet §5.3), so **USB alone does not run the board**. |

## Verified facts that constrain the design

**VE.Direct** (Protocol 3.34 PDF and FAQ, victronenergy.com):
- The connector is JST PH, 2.0 mm pitch, 4 pins: 1 = GND, 2 = RX, 3 = TX, 4 = Power +.
- The link runs at 19200 8N1.
- Logic level is 3.3 V or 5 V depending on the product, and Victron interfaces adapt.
- The power pin allows at most 10 mA on average, with bursts up to 20 mA for 5 ms.
- On a product (charger, MPPT, BMV) the port is not isolated, and the VE.Direct side of Victron's
  cables is powered from it. GX VE.Direct ports are always isolated.

**Parts** (manufacturer datasheets):

| Part | Constraint |
|---|---|
| SN74LVC1G17 | Input 5.5 V-tolerant at any VCC, Ioff (partial power-down). |
| SN74LVC1G125 | /OE active low; TI recommends a pull-up on /OE. Output tolerates up to 6.5 V abs max only while **disabled or unpowered**; an enabled output is limited to VCC + 0.5 V. |
| LESD5D5.0CT1G (LRC) | Bidirectional TVS, VRWM 5 V, 15 pF typ, IEC 61000-4-2 ±8 kV contact. |

**CAN timing:** a bit is 2 µs at 500 kbit/s; with an 80 % sample point the sample is at 1.6 µs. The
candidate transceivers' loop delays are 140–215 ns (table below), plus about 10 ns for the two buffers,
so the parts leave margin. The cable, the remote nodes and the series resistors still need qualifying.

**V+ at the connector:** the 3.3 V rail itself, ~3.2–3.4 V (3.3 V ± 3 %), minus trace drop.

## Host board changes

Captured in `ExtPort.kicad_sch` (items 1–6). Net names follow the firmware conf keys.

1. **Connector.**
   - Replace J5 with a **JST-PH 4, side entry, facing down** (S4B-PH-K-S), in VE.Direct pinout.
   - Put it on the **bottom edge next to the power terminals**, where J5 already sits. The cable exits
     downward alongside the power wires, the same way Victron MPPTs do it.
   - TX on GPIO36 (`EXT_TX`), RX on GPIO37 (`EXT_RX`).
   - Check the fit against the enclosures (fmetal, fheat) and the terminal-block wire clearance.
2. **RX path:** connector → TVS (D21) → 220 Ω (R49) → SN74LVC1G17 (U8) off 3.3 V, 47 k pull-up (R50) so
   the input idles high → GPIO37.
3. **TX path:**
   - GPIO36, 100 k pull-up (R47) → SN74LVC1G125 (U7) → 220 Ω (R48) → TVS (D20) → connector.
   - U7 runs from +3.3V, the same rail as V+, so TX high equals the adapter transceiver's supply.
     (From 2026-09-29 to -30 U7 ran from V+ after D22, for the ISO1042's VCC1 + 0.5 V limit; with D22
     and the ISO1042 gone, that no longer applies.)
   - /OE has a 10 k pull-up (R46), so TX is high-impedance through reset and boot.
   - /OE is on **GPIO48** (`EXT_TX_OE_N`). Not GPIO38/39: Espressif drives both low in USB-OTG download
     boot mode (Hardware Design Guidelines, schematic checklist → USB), which would enable TX.
   - 220 Ω bounds contention if a peer drives TX while it is enabled: 5 V into a driven-low output is
     ~23 mA (under the ±50 mA absolute-maximum output current, SCES223U §5.1); into a driven-high output
     ~7.7 mA flows back into the 3.3 V rail. A sustained 5 V short dissipates ~114 mW in R48, so R48 needs a
     ≥ 0.125 W rating after derating (1206 if in doubt).
   - Firmware rule: never hold GPIO48 low across a reset or deep sleep (`gpio_hold_en`,
     `gpio_deep_sleep_hold_en`). Drive it high (TX off) before any hold, or R46 cannot disable TX.
4. **V+ (pin 4), from 3.3 V (Q1, Q15):** +3.3V → 1 µF (C33) → pin 4, no series part. No TVS on
   pin 4 (Fab, 2026-09-29): C33 absorbs an IEC 61000-4-2 8 kV discharge (150 pF × 8 kV = 1.2 µC, ~1.2 V
   on 1 µF). **Place C33 at J5 pin 4, next to U7's VCC**, so it is both the port ESD sink and U7's bypass.
   Always on. No switch, no current limit, no current sense (Q15, Q16).
5. *(dropped: V+ current sense, Q16)*
6. **ESD and return path:** the TVS diodes on TX and RX (D20, D21, LESD5D5.0CT1G) sit at the connector,
   with a short return to GND.
7. **USB-C next to the power terminals (Q11).**
   - Move P2, with its ESD diodes (D3/D4) and CC resistors, beside the terminals, facing down.
   - Remove the USB1 pin header (Q13; done on this branch). P2 is then the only branch on D+/D−.
   - D+/D− then run about 70 mm from U2 to the bottom edge, past the power stage. Route them as a 90 Ω
     differential pair on a continuous ground reference, length-matched, with return vias at any layer
     change. Keep them away from the SW node, the gate-drive loop and the shunt, and don't route them
     between split grounds (GND vs BuckGND).
   - Full speed (12 Mbit/s) tolerates the length, but the SW-node coupling needs checking once the
     layout is done.
   - **Open (review):** Espressif recommends reserving 22–33 Ω series-resistor footprints near the chip,
     and a self-powered device needs VBUS detection (divider to a GPIO). Neither is on the schematic.
8. **mcu-head:** carry the port signals across the head connector (see pin count below). Not done on
   this branch (J4 unchanged).

### mcu-head pin count (Q6)

The port needs three MCU signals: TX, RX and TX /OE. GND and 3.3V are already on the header. One pin is
spare (J4.11).

| Variant | Signals | Missing pins | Head connector |
|---|---|---|---|
| As captured (Q15/Q16) | TX, RX, /OE | **2** | 2×7 → **2×8** |
| Bare port | TX, RX | 1 | 2×8 with 1 spare |

Carrying USB data to the motherboard USB-C as well would add D+ and D−, giving 4 missing, 2×9. This is not
done (Q14).

## Adapter boards (small PCB with a pigtail, Q7)

Both adapters have a JST-PH 4 pigtail on the Fugu side (VE.Direct pinout) and are labelled **"Fugu
only"**. They draw more than a Victron port's 10 mA allowance. They are **non-isolated** (Q17), so the
transceiver itself must survive the 60 V ground fault.

Source for everything in this section: survey of 2026-09-30, `~/research/fugu2-comms-transceivers/`
(`NOTES.md` has page citations; `pdf/` has the datasheets). DigiKey DE prices at qty 1.

**Why ±70 V, not ±60 V:** in a ground fault the far end's ground can sit at 58.4 V and its bus signal adds
a few volts, so a bus pin can reach ~63 V against our ground (estimate). A ±60 V part has no margin and a
±65 V part about 1.5 V.

| | CAN adapter | RS-485 adapter |
|---|---|---|
| Transceiver | **TCAN1042HV** (±70 V abs max; VCC 4.5–5.5 V, so it needs a 3.3 → 5 V boost, e.g. TPS61023 ~€1). Its **VIO pin runs from 3.0–5.5 V**: tie VIO to V+ (3.3 V) so RXD is a 3.3 V signal (RXD ≤ VIO + 0.3 V) and stays inside D21's 5 V stand-off. IEC 61000-4-2 on CANH/CANL: ±8 kV contact powered, ±15 kV unpowered (SOIC). IIO 90 µA typ / 300 µA max. (SLLSES7D §7.1 p6, §7.3, §7.4 p8, p9.) HV price and stock not checked. The plain **TCAN1042H** (€1.89) has no VIO: its RXD swings to VCC (up to 5.5 V), above D21's 5 V stand-off; U8 tolerates it but D21 would leak. Alternatives that run directly from 3.0–3.6 V: MAX33053E/54E (±65 V, €7.88) or LTC2875 (±60 V, €5.60). | **THVD2410** (±70 V abs max, 3.0–5.5 V, €3.55), directly from V+ |
| Direction | n/a | None of the ±60 V-class parts has auto-direction, so **DE is driven from TX**: D tied low, DE = inverted TX, bias holds the bus idle (recessive-style), /RE tied low for echo. The DE timing and bias values still need working out. |
| V+ current, worst (typ) | TCAN1042H + boost: ≤ 174 mA dominant (98); ≤ 5.4 mA recessive. MAX33053E direct: ≤ 50 mA dominant. | ≤ 67 mA driving 54 Ω; ≤ 3.5 mA idle, plus ~2.3 mA for the bias |
| Logic idle | TXD pull-up to V+ | TX idle high → DE low |
| Echo | Inherent: CAN transceivers echo TXD on RXD | **/RE tied low**, so echo is on |
| Termination and bias | 120 Ω split termination on a DIP switch, **off by default** | 120 Ω termination and fail-safe bias on DIP switches |
| Ground reference | Comms GND to the far end through a **fault-rated limiter** | same |
| V+ clamp | Some transceivers push fault current back into VCC (LTC2862A: up to 80 mA). The 3.3 V rail is not a guaranteed sink, so fit a clamp (e.g. 5.6 V, 1 W Zener, as LTC suggests) or pick a part that doesn't back-feed. | same |
| Bus connector | Screw terminal. RJ45 is deferred until target models are chosen (Q4). | Screw terminal. RJ45 deferred. |
| ESD | Rely on the transceiver's own IEC 61000-4-2 rating. An external TVS would have to stand off the 58.4 V fault, and a TVS with that stand-off clamps well above the 70 V the transceiver tolerates, so it cannot protect it. Check each candidate's IEC rating (not yet in the survey). | same |

**Comms ground wire.** It is a reference, not a return: both buses are differential, so it carries only
µA–mA in normal operation. In a ground fault it becomes the return path for the whole board, so it must be
current-limited. TI's 100 Ω (SLLA272D §11, SLLA070D §4.5.2) is a ground-loop measure, not a fault limiter:
at 58.4 V it would carry 0.58 A and dissipate 34 W. Something like 10 kΩ (5.8 mA, 0.34 W) or a PTC would
survive the fault continuously (estimate, not bench-tested). AN-960 (Rev. 0, pp. 7–8) gives no value and
recommends galvanic isolation whenever node grounds can't be guaranteed within common mode.

**Isolated fallback** (if the far end sits behind a low-side BMS switch, Q4): LTM2889-3 (CAN, ≥ 3.0 V,
≤ 225 mA, €26.70) or ISOW1412 (RS-485, ≥ 3.0 V, ≤ 158 mA driving, €8). ISOW1044 and ADM3055E need 5 V.

**RS-485 echo (Q8), yes.** A Victron device never echoes, while both adapters then do. So in VE.Direct
mode, an echo means "adapter plugged in, stop transmitting". The limits:
- Echo alone cannot tell the CAN adapter from the RS-485 adapter.
- Echo only shows up after something has been sent. At 19200 baud, one byte sent into the CAN adapter
  holds TXD low (dominant) for up to ~0.47 ms and disrupts the bus; a transceiver's dominant timeout
  (typically ≥ 1 ms) does not stop that. With no V+ sensing (Q16), what happens before the first byte is a
  firmware matter.
- Echo is evidence, not proof: a CAN transceiver's RXD reports the bus, which another node can hold
  dominant, and a Victron HEX response can byte-match its request. Firmware should correlate echo with
  timing.
- In Modbus mode the firmware discards its own echo. Transmitting on RS-485 is half-duplex anyway, so
  echo costs nothing on the bus.
- There is no jumper; /RE is hardwired low.

## Qualification (bench, before freezing the host PCB)

1. **Prototypes.** Build the adapter prototypes and a host-side prototype of the protected port, wired to
   J5 on a v2.3 bench board (not fry/flat).
2. **CAN timing and signal integrity** on the real path (buffers, 220 Ω, TVS, cable, transceiver, bus), at
   500 kbit/s with an independent CAN monitor.
3. **Pin 4 on real Victron gear:**
   - Check whether the VE.Direct cable is straight or crossed on 2↔3.
   - Measure pin-4 voltage and current at GX and USB-cable ends.
   - Check whether their TX level follows Fugu's 3.3 V.
   - Check every source/sink combination, powered and unpowered. With D22 gone, **a peer that drives
     pin 4 drives Fugu's 3.3 V rail**; if any real peer does, fix before freezing the PCB.
4. **3.3 V headroom (Q1).** WiFi TX peak (355 mA) plus the adapter at maximum (up to ~174 mA with the
   TCAN1042H + boost, ~50–67 mA with a 3.3 V part) approaches or exceeds the LM5163's 0.5 A before the
   gate-drive boost. Measure the worst case, and check the
   adapter hot-plug inrush and a short on pin 4 (Q15 accepts a brownout; confirm the converter stays
   safe through it).
5. **Reset and boot.** Scope that TX stays high-impedance through power-up, reset, bootloader, OTA
   reboot, USB-OTG download mode, and deep sleep/wake and watchdog resets after TX was enabled.
6. **Echo.** Measure the echo on both adapters.
7. **ESD.** Run IEC 61000-4-2 contact and air discharges at the connector with the device powered and
   unpowered, both polarities. The TVS clamps at up to 18.6 V (8/20 µs, 9.4 A), above the buffers'
   6.5 V absolute maximum, so the 220 Ω and the ICs' own ESD structures must absorb the residual.
   Add a secondary clamp only if this fails.
8. **60 V ground fault (Q17).** With each adapter connected and communicating, open Fugu's battery-negative
   connection, and separately the far end's, on a 58.4 V battery, in both polarities and powered and
   unpowered. Confirm the transceivers, the comms-GND limiter and the V+ clamp survive, and that nothing
   carries the board's return current.
9. **Adapter supply.** Confirm both adapters start and run at the low end of the 3.3 V rail (3.2 V).

## Order of work

1. **Adapter prototypes and a host-port prototype on J5**, run through qualification items 2–9.
2. **Fugu2 redesign** (more area, extra Cin bulk): lay out `ExtPort.kicad_sch` and host change 7. Both
   connectors go on the bottom edge beside the terminals. Then DRC and a check against the enclosures.
3. **mcu-head rev**: header per Q6 (re-confirm 2×8 vs 2×9).
4. **Adapter PCBs.**

## Open questions

- **Q12 (layout detail):** place the port and USB-C **side by side** on the bottom edge next to the
  terminals, facing down. Fall back to stacking (front/back) only if width is still short. Side by side
  keeps assembly single-sided for these parts and avoids clashes between through-hole shell tabs.
  Whichever layout is chosen:
  - Keep clearance to Solar+ nets. The PSU feed parts Q8, D11, R43 and R44 currently sit at the
    bottom-right.
  - Keep mounting holes clear.
  - Keep the USB D+/D− routing rules in host change 7.
  - Leave room for plugs and cable bend radius beside the power lugs.
- **GPIO7 (Q9 follow-up):** add a series resistor or divider so the power-up output-low glitch cannot
  fight the rail? Keeps the monitor function.
- **Q6:** re-confirm the head header size now that only three signals cross it.
- **USB (host change 7):** add series-resistor footprints and VBUS detection?
