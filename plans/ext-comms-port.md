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
| Modbus RTU | Isolated RS-485 adapter (small PCB with a pigtail) |
| CAN | Isolated CAN adapter (small PCB with a pigtail) |

The adapters are dumb: an isolated supply, an isolator and a transceiver, with no MCU. There is no ID
pin; Fab decided on 2026-09-28 that wrong-adapter protection is handled in software, and on 2026-09-29
that the hardware adds nothing for it beyond:
- A TX output-enable that hardware holds off through reset and boot.
- Adapters that echo TX back on RX.

## Decisions (Fab, 2026-09-28/29)

| # | Decision |
|---|---|
| Q1 | V+ comes from the 3.3 V rail. |
| Q3 | Place the connector the way Victron does: **next to the power terminals**. No connectors on the upper PCB side. The unit is wall-mounted with the power terminals facing down, so an upward-facing opening would let water in. |
| Q4 | Target BMS/inverter models come later; hardware only for now. |
| Q5 | Isolation: nothing special. Use the industry-standard ratings of off-the-shelf isolated CAN/RS-485 parts. |
| Q6 | mcu-head header grows 2×7 → **2×9** and carries the port signals; D+/D− are not added. **Re-confirm:** since Q15/Q16 the port needs only three signals, so 2×8 would do (see pin count below). The motherboard J4 is unchanged for now. |
| Q7 | Adapters are a small PCB with a pigtail. |
| Q8 | The RS-485 adapter echoes (/RE tied low). See the adapter section. |
| Q9 | GPIO7 tied to +3.3V is a rail voltage monitor. Keep it. **Review finding, open:** see GPIO7 below and Open questions. |
| Q10 | The redesign (Q12) supersedes syncing the July layout to the schematic. |
| Q11 | USB-C also moves next to the power terminals. |
| Q12 | The board gets a slight redesign with more area (additional Cin bulk caps), which makes room for both connectors on the bottom edge. The detailed placement is still open (see Open questions). |
| Q13 | The USB1 pin header is **removed**. The J2 I2C socket stays where it is. |
| Q14 | The product's USB-C is the motherboard one, in the lower board area (Q11). The head's USB-C is a development/service port; its position in the upper area is accepted. |
| Q15 | **No V+ load switch.** V+ is always on, fed from 3.3 V through a Schottky that blocks a peer back-feeding pin 4. **No short protection on pin 4**: a short browns out the 3.3 V rail. (A PTC was considered and rejected: any PTC that holds 0.17 A at 60 °C trips at 0.75 A, above the rail's 0.5 A, so it never trips.) |
| Q16 | **No V+ current sense.** Wrong-adapter handling is purely in software. |

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
| Ground | Logic GND is the battery-terminal negative (J9.2) and is bonded to the USB-C shell. Shunt R26 (0.5 mΩ) sits low-side between BuckGND (solar −, J10.1) and GND. A non-isolated link to anything referenced to a BMS's B− bridges its low-side FET, so the CAN adapter must be isolated. A GX on the same P− bus is fine over a plain VE.Direct cable. |
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
| ISO1042 | TXD→RXD loop delay ≤ 215 ns. TXD high needs ≥ 0.7×VCC1, which is 2.31 V at VCC1 = 3.3 V. Bus side up to 73.4 mA while dominant; recessive only ~1.3 mA (VCC1) + 2.8 mA (VCC2) typ. Dominant timeout ≥ 1.2 ms. |
| THVD1426 | Auto-direction. The driver actively drives a '1' for only 0.4–1.45 µs (0.8 µs typ), then releases the bus. Its own receiver reads an idle terminated bus as high without bias; other receivers on the network may need fail-safe bias. With /RE = 0 the receiver stays on while transmitting (echo). Bus pins −7…+12 V relative to its local ground. |
| SN74LVC1G17 | Input 5.5 V-tolerant at any VCC, Ioff (partial power-down). |
| SN74LVC1G125 | /OE active low; TI recommends a pull-up on /OE. Output tolerates up to 6.5 V abs max only while **disabled or unpowered**; an enabled output is limited to VCC + 0.5 V. |
| LESD5D5.0CT1G (LRC) | Bidirectional TVS, VRWM 5 V, 15 pF typ, IEC 61000-4-2 ±8 kV contact. |
| MSS1P4-M3/89A (Vishay) | Schottky, VF ≈ 0.35 V typ at 0.17 A (Fig. 3); no max specified near 0.2 A. |

**CAN timing:** a bit is 2 µs at 500 kbit/s; with an 80 % sample point the sample is at 1.6 µs. ISO1042
plus the two buffers is about 225 ns, so the parts leave margin. The cable, the remote nodes and the
series resistors still need qualifying.

**V+ at the connector:** 3.3 V × 0.97 − VF(0.35 typ, ~0.42 est. max) ≈ **2.78–2.85 V at 170 mA**. The
adapters' isolated DC-DC must accept that.

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
   - GPIO36, 100 k pull-up (R47) → SN74LVC1G125 (U7) off 3.3 V → 220 Ω (R48) → TVS (D20) → connector.
   - /OE has a 10 k pull-up (R46), so TX is high-impedance through reset and boot.
   - /OE is on **GPIO48** (`EXT_TX_OE_N`). Not GPIO38/39: Espressif drives both low in USB-OTG download
     boot mode (Hardware Design Guidelines, schematic checklist → USB), which would enable TX.
   - 220 Ω bounds contention if a peer drives TX while it is enabled (5 V into a driven-low output:
     ~23 mA, under the ±50 mA absolute-maximum output current, SCES223U §5.1).
4. **V+ (pin 4), from 3.3 V (Q1, Q15):** 3.3 V → Schottky D22 (MSS1P4) → 1 µF (C33) + TVS (D19) → pin 4.
   Always on. No switch, no current limit, no current sense (Q15, Q16).
5. *(dropped: V+ current sense, Q16)*
6. **ESD and return path:** the TVS diodes (LESD5D5.0CT1G) sit at the connector, with a short return to
   GND.
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
only"**. They draw far more than a Victron port's 10 mA allowance, and their isolated DC-DC must run from
**~2.8 V** (V+ after D22, see above).

| | CAN adapter | RS-485 adapter |
|---|---|---|
| Power | Isolated DC-DC, V+ (~2.8–3.3 V) → 5 V bus side | Isolated DC-DC → bus side |
| Signal chain | ISO1042, VCC1 = V+ | 2-channel digital isolator, one channel each way, default output high (e.g. ISO7721, not the F variant) → THVD1426 |
| Logic idle | TXD pull-up to V+ | Pull-up on the isolator input carrying R |
| Echo | Inherent: CAN transceivers echo TXD on RXD | **/RE tied low**, so echo is on |
| Termination and bias | 120 Ω split termination on a DIP switch, **off by default** | 120 Ω termination and fail-safe bias on DIP switches |
| Bus reference | GND2 to the remote bus ground | **GND2 terminal to the remote bus ground** (THVD1426 bus pins must stay within −7…+12 V of it) |
| Bus connector | Screw terminal. RJ45 is deferred until target models are chosen (Q4). | Screw terminal. RJ45 deferred. |
| ESD | Bus-side TVS | Bus-side TVS |
| Isolation rating | Standard part ratings | Standard part ratings |

**RS-485 echo (Q8), yes.** A Victron device never echoes, while both adapters then do. So in VE.Direct
mode, an echo means "adapter plugged in, stop transmitting". The limits:
- Echo alone cannot tell the CAN adapter from the RS-485 adapter.
- Echo only shows up after something has been sent. At 19200 baud, one byte sent into the CAN adapter
  holds TXD low (dominant) for up to ~0.47 ms and disrupts the bus; the ISO1042's ≥ 1.2 ms dominant
  timeout does not stop that. With no V+ sensing (Q16), what happens before the first byte is a
  firmware matter.
- Echo is evidence, not proof: the ISO1042's RXD reports the bus, which another node can hold
  dominant, and a Victron HEX response can byte-match its request. Firmware should correlate echo with
  timing.
- In Modbus mode the firmware discards its own echo. Transmitting on RS-485 is half-duplex anyway, so
  echo costs nothing on the bus.
- There is no jumper; /RE is hardwired low.

## Qualification (bench, before freezing the host PCB)

1. **Prototypes.** Build the adapter prototypes and a host-side prototype of the protected port, wired to
   J5 on a v2.3 bench board (not fry/flat).
2. **CAN timing and signal integrity** on the real path (buffers, 220 Ω, TVS, cable, isolator, bus), at
   500 kbit/s with an independent CAN monitor.
3. **Pin 4 on real Victron gear:**
   - Check whether the VE.Direct cable is straight or crossed on 2↔3.
   - Measure pin-4 voltage and current at GX and USB-cable ends.
   - Check whether their TX level follows Fugu's 3.3 V.
   - Check every source/sink combination, powered and unpowered, including D22's leakage into an
     unpowered Fugu.
4. **3.3 V headroom (Q1).** WiFi TX peak (355 mA) plus the adapter at maximum (~170 mA, CAN dominant)
   already exceeds the LM5163's 0.5 A before the gate-drive boost. Measure the worst case, and check the
   adapter hot-plug inrush and a short on pin 4 (Q15 accepts a brownout; confirm the converter stays
   safe through it).
5. **Reset and boot.** Scope that TX stays high-impedance through power-up, reset, bootloader, OTA
   reboot and USB-OTG download mode.
6. **Echo.** Measure the echo on both adapters.
7. **ESD.** Run IEC 61000-4-2 contact and air discharges at the connector with the device powered.
8. **Isolation.** Confirm there is no DC path from GND to the bus side of either adapter.
9. **Adapter supply at low V+.** Confirm both adapters start and run at 2.7 V V+.

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
