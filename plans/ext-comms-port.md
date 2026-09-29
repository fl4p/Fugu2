*this document is an LLM generated placeholder*

# Fugu2 rev: external comms port (VE.Direct-compatible, with CAN and RS-485 adapters)

**Scope: hardware only, meaning the connector, the circuitry on the port and the two adapter boards.**
Firmware and the choice of target BMS/inverter are scoped later. The firmware-side draft is in
`fugu-mppt-firmware/plans/ext-serial-port.md`.

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
pin; Fab decided on 2026-09-28 that wrong-adapter protection is handled in software. The hardware
supports that with three things:
- A TX output-enable.
- V+ current sensing.
- Adapters that echo TX back on RX.

## Decisions (Fab, 2026-09-29)

| # | Decision |
|---|---|
| Q1 | V+ comes from the 3.3 V rail. |
| Q3 | Place the connector the way Victron does: **next to the power terminals**. No connectors on the upper PCB side. The unit is wall-mounted with the power terminals facing down, so an upward-facing opening would let water in. |
| Q4 | Target BMS/inverter models come later; hardware only for now. |
| Q5 | Isolation: nothing special. Use the industry-standard ratings of off-the-shelf isolated CAN/RS-485 parts. |
| Q6 | mcu-head header grows 2×7 → **2×9** and carries the five port signals; D+/D− are not added. |
| Q7 | Adapters are a small PCB with a pigtail. |
| Q8 | The RS-485 adapter echoes (/RE tied low). See the adapter section. |
| Q9 | GPIO7 tied to +3.3V is a rail voltage monitor. Keep it (note below). |
| Q10 | The redesign (Q12) supersedes syncing the July layout to the schematic. |
| Q11 | USB-C also moves next to the power terminals. |
| Q12 | The board gets a slight redesign with more area (additional Cin bulk caps), which makes room for both connectors on the bottom edge. The detailed placement is still open (see Open questions). |
| Q13 | The USB1 pin header is **removed**. The J2 I2C socket stays where it is. |
| Q14 | The product's USB-C is the motherboard one, in the lower board area (Q11). The head's USB-C is a development/service port; its position in the upper area is accepted. |

## Current state: Fugu2 v2.3

Sources:
- The netlist, exported with kicad-cli on 2026-09-29 from the **working-tree** schematic, which has
  uncommitted edits and was last saved 2026-08-11.
- Footprint positions from `Fugu2.kicad_pcb`, last saved 2026-07-27. **The layout is older than the
  schematic.**

| Item | Finding |
|---|---|
| J5 | 1×4 socket at 2.54 mm: 1 = +3.3V, 2 = GND, 3 = CAN_RX (GPIO37), 4 = CAN_TX (GPIO36). Direct to the ESP32 with no protection. V+ is the unswitched 3.3 V rail. |
| J5 position | (76.0, 109.6) mm. That is the bottom-right corner, **already next to J9** (battery terminal at y = 113.7). The board spans x 28.7–78.7 and y 31–119, and the terminals are on the bottom edge. |
| Free GPIOs | Unconnected: 3, 5, 6, 9, 15–18, 38, 39, 45, 48. Unrouted `SPI*` labels: 10–13. |
| GPIO7 | Tied directly to +3.3V (ADC1_CH6) as a rail monitor. The S3 ADC tops out below 3.3 V even at 12 dB attenuation, so the reading sits at full scale and only moves when the rail sags below the top of the range. It detects a sag, not the rail value. Add a divider if a real reading is wanted. |
| Ground | Logic GND is the battery-terminal negative (J9.2) and is bonded to the USB-C shell. Shunt R26 (0.5 mΩ) sits low-side between BuckGND (solar −, J10.1) and GND. A non-isolated link to anything referenced to a BMS's B− bridges its low-side FET, so the CAN adapter must be isolated. A GX on the same P− bus is fine over a plain VE.Direct cable. |
| 3.3 V | External `psu/buck100` board: LM5163, **0.5 A**. Fed through a diode-OR of Bat+, Solar+ and Vusb. It also supplies WiFi and the AP3012 12 V gate-drive boost. |
| USB-C P2 | At (51, 34.5), on the **top edge**. Moves to the bottom (Q11). USB1 (1×4 USB pin header, top edge) is removed. J2 (I2C socket, mid-board) stays (Q13). |
| Bottom edge space | Courtyards: J10 x 32.2–52.6, J9 x 52.5–72.9, J5 x 74.2–77.8, all to y = 120. The board spans x 28.7–78.7, so the free strips are **3.5 mm on the left (mounting hole H4 at 30.7/105.5) and 5.8 mm on the right**. A JST-PH 4 side-entry is about 10 mm wide and a USB-C receptacle about 9 mm, so **neither fits beside the terminals as the board stands** (Q12). |
| mcu-head | Its 2×7 header (J4 on the motherboard, J2 on the head) has 10 signals, GND on pins 2 and 7, +3.3V on pin 5, and one spare (pin 11). GPIO36/37 are not routed. **USB is not available on the motherboard when the head is used**: D+/D− are not on the header, and the head has its own USB-C (P1) and ESP-PROG header. The motherboard USB-C then only powers the board (Vusb → D7 → PSU diode-OR); it carries no data. |

## Verified facts that constrain the design

**VE.Direct** (Protocol 3.34 PDF and FAQ, victronenergy.com):
- The connector is JST PH, 2.0 mm pitch, 4 pins: 1 = GND, 2 = RX, 3 = TX, 4 = Power +.
- The link runs at 19200 8N1.
- Logic level is 3.3 V or 5 V depending on the product, and Victron interfaces adapt.
- The power pin allows at most 10 mA on average, with bursts up to 20 mA for 5 ms.
- The port on the product itself is not isolated. The isolated side of Victron's cables is powered from
  the port.

**Parts** (TI datasheets):

| Part | Constraint |
|---|---|
| ISO1042 | TXD→RXD loop delay ≤ 215 ns. TXD high needs ≥ 0.7×VCC1, which is 2.31 V at VCC1 = 3.3 V. Bus side up to 73.4 mA while dominant. |
| THVD1426 | Auto-direction. The driver actively drives a '1' for only 4–14 µs, so **fail-safe bias is required**. With /RE = 0 the receiver stays on while transmitting (echo). |
| TPS2553 | Reverse-voltage shutdown at 95–190 mV, after 3–7 ms. |
| SN74LVC1G17 | 5.5 V-tolerant input, partial-power-down protection. |

**CAN timing:** a bit is 2 µs at 500 kbit/s. The ISO1042 alone leaves margin, but the full path still
needs qualifying.

## Host board changes

1. **Connector.**
   - Replace J5 with a **JST-PH 4, side entry, facing down**, in VE.Direct pinout.
   - Put it on the **bottom edge next to the power terminals**, where J5 already sits. The cable exits
     downward alongside the power wires, the same way Victron MPPTs do it.
   - Keep TX on GPIO36 and RX on GPIO37.
   - Check the fit against the enclosures (fmetal, fheat) and the terminal-block wire clearance.
2. **RX path:** connector → series R (100–220 Ω) → low-capacitance TVS → SN74LVC1G17 powered from 3.3 V
   → GPIO37.
3. **TX path:**
   - GPIO36 → 74LVC1G125 (off 3.3 V, with I_off) → series R → TVS → connector.
   - Pull /OE to "disabled", so TX stays high-impedance through reset and boot.
   - /OE goes on a free GPIO (38, 39 or 48).
4. **V+ (pin 4), from 3.3 V (Q1).**
   - Use a current-limited load switch with reverse blocking. The enable pin is pulled to off, and the
     enable goes on a free GPIO.
   - Set the limit for an isolated adapter: about 170 mA with the CAN bus dominant.
   - Qualify the switch against a peer that also drives pin 4.
5. **V+ current sense** into an ADC1 channel (GPIO 5, 6 or 9; ADC2 conflicts with WiFi). It lets
   software tell an isolated adapter (tens of mA) from a Victron cable (≤10 mA).
6. **ESD and return path:** place the TVS diodes at the connector, with a short return to GND.
7. **USB-C next to the power terminals (Q11).**
   - Move P2, with its ESD diodes (D3/D4) and CC resistors, beside the terminals, facing down.
   - Remove the USB1 pin header (Q13). P2 is then the only branch on D+/D−.
   - D+/D− then run about 70 mm from U2 to the bottom edge, past the power stage. Route them as a 90 Ω
     differential pair on a continuous ground reference. Keep them away from the SW node, the gate-drive
     loop and the shunt, and don't route them between split grounds (GND vs BuckGND).
   - Full speed (12 Mbit/s) tolerates the length, but the SW-node coupling needs checking once the
     layout is done.
8. **mcu-head:** carry the port signals across the head connector (see pin count below).

### mcu-head pin count (Q6)

The port needs five MCU signals: TX, RX, TX /OE, V+ EN and V+ sense. GND and 3.3V are already on the
header. One pin is spare (J4.11).

| Variant | Signals | Missing pins | Head connector |
|---|---|---|---|
| Full | TX, RX, /OE, V+ EN, V+ sense | **4** | 2×7 → **2×9** (exactly +4) |
| V+ always on (no EN) | TX, RX, /OE, V+ sense | 3 | 2×9 with 1 spare |
| Bare port (no software-guard support) | TX, RX | 1 | 2×8 |

Carrying USB data to the motherboard USB-C as well would add D+ and D−, giving **6 missing, 2×10**. This is not done (Q14).

The full variant is recommended. The guard needs /OE and V+ sense, and V+ EN lets the port be powered off
until a mode is configured.

## Adapter boards (small PCB with a pigtail, Q7)

Both adapters have a JST-PH 4 pigtail on the Fugu side (VE.Direct pinout) and are labelled **"Fugu
only"**. They draw far more than a Victron port's 10 mA allowance.

| | CAN adapter | RS-485 adapter |
|---|---|---|
| Power | Isolated DC-DC 3.3 V → 5 V bus side | Isolated DC-DC → bus side |
| Signal chain | ISO1042, VCC1 = 3.3 V | 2-channel digital isolator (default output high) → THVD1426 |
| Logic idle | TXD pull-up to 3.3 V | Pull-up on the isolator input carrying R |
| Echo | Inherent: CAN transceivers echo TXD on RXD | **/RE tied low**, so echo is on |
| Termination and bias | 120 Ω split termination on a DIP switch, **off by default** | 120 Ω termination and fail-safe bias on DIP switches |
| Bus reference | GND2 to the remote bus ground | — |
| Bus connector | Screw terminal. RJ45 is deferred until target models are chosen (Q4). | Screw terminal. RJ45 deferred. |
| ESD | Bus-side TVS | Bus-side TVS |
| Isolation rating | Standard part ratings | Standard part ratings |

**RS-485 echo (Q8), yes.** A Victron device never echoes, while both adapters then do. So in VE.Direct
mode, any echo means "adapter plugged in, stop transmitting". The limits:
- Echo alone cannot tell the CAN adapter from the RS-485 adapter. The V+ current signature can, if the
  two adapters draw distinguishably different currents; design the adapters so they do.
- In Modbus mode the firmware discards its own echo. Transmitting on RS-485 is half-duplex anyway, so
  echo costs nothing on the bus.
- There is no jumper; /RE is hardwired low.
- Echo only shows up after something has been sent, so it is the second check, not the first. At
  19200 baud, one byte sent into the CAN adapter holds TXD low (dominant) for up to about 0.5 ms and
  disrupts the bus. So the **V+ current check runs before /OE is first enabled** after power-up, a
  mode change, or a V+ current change that suggests a replug. Echo then confirms after the fact.

## Qualification (bench, before freezing the host PCB)

1. **Prototypes.** Build the adapter prototypes and a host-side prototype of the protected port, wired to
   J5 on a v2.3 bench board (not fry/flat).
2. **CAN timing and signal integrity** on the real path (buffers, protection, cable, isolator, bus), at
   500 kbit/s with an independent CAN monitor.
3. **Pin 4 on real Victron gear:**
   - Check whether the VE.Direct cable is straight or crossed on 2↔3.
   - Measure pin-4 voltage and current at GX and USB-cable ends.
   - Check whether their TX level follows Fugu's 3.3 V.
   - Check every source/sink combination, powered and unpowered.
4. **3.3 V headroom (Q1).** Measure the worst-case LM5163 load with WiFi TX, full-duty gate drive and the
   adapter at maximum draw (CAN bus dominant). Check for brownout on a hot-plug short at the port.
5. **Reset and boot.** Scope that TX stays high-impedance and V+ stays off through power-up, reset,
   bootloader and OTA reboot.
6. **Echo and V+ signature.** Measure the echo on both adapters, and the V+ current of each adapter and
   of Victron cables, to confirm the bands separate.
7. **ESD.** Run IEC 61000-4-2 contact and air discharges at the connector with the device powered.
8. **Isolation.** Confirm there is no DC path from GND to the bus side of either adapter.

## Order of work

1. **Adapter prototypes and a host-port prototype on J5**, run through qualification items 2–8.
2. **Fugu2 redesign** (more area, extra Cin bulk): host changes 1–8. In the layout, both connectors go on
   the bottom edge beside the terminals. Then DRC and a check against the enclosures.
3. **mcu-head rev**: 2×9 header.
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