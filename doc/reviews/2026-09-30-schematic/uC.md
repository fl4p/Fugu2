# Fugu2 schematic review: uC block (`uC.kicad_sch`)

Reviewer: independent agent, 2026-09-30. The review was read-only. Scratch files are in `/tmp/fugu_split/review_uC/`.
Vision probe: VISION-PROBE-PASS in this session. I inspected the rendered sheet `Fugu2-uC.png` visually.

## Evidence used

| Source | Revision | Used for |
|---|---|---|
| ESP32-S3 Series Datasheet (espressif.com, fetched rung 1, `%PDF`, 1.10 MB) | v2.2 | Table 2-1 (pin reset states, p.16-17), Table 2-2 (power-up glitches, p.18-19), Table 5-6 (ADC range), Table 5-4 (IOL/IOH), §5.1 |
| ESP32-S3-WROOM-1/1U Datasheet (espressif.com, rung 1, `%PDF`, 1.28 MB) | v1.8 | §4 strapping (Tables 4-1..4-5, p.13-15), Fig 9-1 peripheral schematic + EN RC note (p.41), pin numbering |
| UCC21330-Q1 (local `~/dev/ee/datasheets/ucc21330-q1.pdf`) | SLUSFF3A, Jun 2024 | Pin functions Table 4-1 (INA/INB pull-down, DIS pull-up), RINxD/RDISD 50/90/185 kΩ |
| WS2812B (Worldsemi, adafruit mirror, rung 1) | undated legacy rev | VDD 3.5-5.3 V, VIH 0.7·VDD |
| UEXT spec (Olimex, rung 1) | rev B | pinout 1=3.3V … 3=TXD 4=RXD 5=SCL 6=SDA |
| TLV702 (ti.com, rung 1) | SLVSAG6D | §7.3.1 reverse current through PMOS body diode is unlimited |
| LESD5D5.0CT1G (LCSC-hosted PDF C5246195, rung 1) | — | VRWM 5 V, CJ 15 pF typ, bidirectional |
| SHOUHAN TYPE-C 16P QTGM027 spec (LCSC C2681552, rung 1) | drawing 2016-10-20 | Recommended PCB layout (p.6) |
| ESP Hardware Design Guidelines, ESP32-S3: *Schematic Checklist* and *PCB Layout Design* (docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/, fetched 2026-09-30 at rung 1. The legacy PDF URL now 302s to this HTML; content confirmed by `<title>` and ~79 kB / ~54 kB of body text) | "latest" web edition, © 2023-2026 | power, CHIP_PU RC, USB, ADC, UART, USB-OTG download pad states |
| Netlist `/tmp/fugu_split/repo.net`, ERC `erc_after.rpt`, `Fugu2.kicad_pcb` pad nets, mcu-head netlist (fresh `kicad-cli` export to scratch) | working tree 2026-09-30 | connectivity |

Update 2026-09-30: I have now read the ESP32-S3 Hardware Design Guidelines (HDG) myself; they are cited directly below.

## Pin map (U2 = ESP32-S3-WROOM-1-N4), verified against module pin numbering (WROOM DS Fig 9-1)

| GPIO | Net | Reset state (S3 DS Tbl 2-1) | Power-up glitch (Tbl 2-2) | External bias | Safe? |
|---|---|---|---|---|---|
| 14 | INL → U1.INA | no pull/IE | 60 µs **low** | U1 INA internal pull-down 50-185 kΩ | yes: a low level means LS off |
| 21 | INH → U1.INB | floating | none | U1 INB internal pull-down | yes |
| 47 | SD → U1.DIS | IE only | none | U1 DIS internal **pull-up** 50-185 kΩ, which disables the driver | yes |
| 40 (MTDO) | BflowSD → Q4 gate | IE | none | R23 10 k pull-up. Q4 turns on, BflowG is pulled low, and the backflow FETs are off | yes |
| 35 | LV_PGOOD → Q9 gate | IE | none | R45 10 k pull-down. Q9 is off and the Solar feed Q8 is enabled | yes |
| 48 | EXT_TX_OE_N → U7 /OE | IE | none | R46 10 k pull-up, so TX is Hi-Z | yes |
| 36 / 37 | EXT_TX / EXT_RX | IE | none | R47 100 k pull-up / U8 output | OK on N4 (no PSRAM) |
| 0 | IO0 | WPU | — | R3 10 k pull-up + SW1 to GND | OK |
| 46 | **tied to GND** | WPD | — | hard GND | boot OK (Tbl 4-3: SPI boot with GPIO0=1, download needs GPIO46=0) |
| 45 | NC | WPD | — | — | VDD_SPI = 3.3 V, correct for N4 |
| 3 | NC; the footprint `ESP32-S3-WROOM-1-noPIN15` has **no pad 15** | floating | low | — | OK unless EFUSE_STRAP_JTAG_SEL is burnt |
| 1 | LED (D2 DIN, J4.1) | IE | low | — | OK |
| 2 / 42 | SCL / SDA | IE | low (GPIO2) | R14 / R13 10 k | OK |
| 41 | ALERT | IE | — | R15 10 k | OK |
| 4 | ADC_Vin (ADC1_CH3) | — | low | divider R18 200 k / R20 7.5 k, C15, D6 | OK (ADC1) |
| 8 | NTC (ADC1_CH7) | — | low | R16 / TH1 | OK (ADC1) |
| 7 | **+3.3V directly** | — | 60 µs **low output** | rail | see F1 |
| 19 / 20 | USB D− / D+ | USB_PU | high glitches | P2, D3 / D4 | OK |
| 43 / 44 | TX / RX → TP2 / TP1 only | WPU | — | — | OK |
| 10-13 | SPICS / SPID / SPICLK / SPIQ | IE | low | only J12, which is DNP and off-board | dead labels |

**USB-OTG Download Boot (HDG Schematic Checklist → USB, table "IO Pad Status After Chip Initialization in the USB-OTG Download Boot Mode").** In this mode the ROM drives OEN (MTDO = **GPIO40 = BflowSD**) as an output **HIGH**, VPO (MTCK/GPIO39) LOW and VMO (GPIO38) LOW. It sets RCV (**GPIO21 = INH**), VP (MTMS = SDA) and VM (MTDI = ALERT) as inputs. On this board that is safe:
- BflowSD high is the same state R23 already imposes (Q4 on, backflow FETs off).
- INH stays an input, so U1 INB is held by its internal pull-down.
- GPIO38/39 are unconnected.

The HDG suggests burning EFUSE_DIS_USB_OTG_DOWNLOAD_MODE if that mode is not needed. The design does not depend on it, and no other ROM mode drives a gate-drive pin.

**Conclusion on the half-bridge safe state:** during reset, the ROM download mode and a flash, every gate-drive control pin is high-Z. The UCC21330's own internal resistors then hold INA/INB low and DIS high, so both outputs are disabled. The only power-up glitch on a gate pin is GPIO14's 60 µs low, which is the inactive level. No glitch path turns a FET on (confirmed). Robustness is covered in F6.

## Findings (most severe first)

### F1. GPIO7 is hard-wired to +3.3V as a "monitor 3.3V". The monitor is ineffective and the pin fights the rail at every power-up. **Major / confirmed**
- Net: `+3.3V` includes `U2.7 (GPIO7/ADC1_CH6)`. The ERC reports it on this sheet as `pin_to_pin` Bidirectional↔Power output (#FLG03).
- S3 DS Table 2-2 lists GPIO7 with a "Low-level glitch 60 µs". The footnote defines that as "pin at low-level output status". Table 5-4 gives IOL ≈ 28 mA at the default drive strength. The pad therefore sinks the rail through its output driver for about 60 µs on every power-up.
- S3 DS Table 5-6 limits ATTEN3 (12 dB) to an effective range of 0-2900 mV. The reading saturates at 3.3 V and only moves when the rail is below 2.9 V. That is already below the 3.0 V recommended VDD minimum (Tbl 5-1), which the internal brown-out detector covers anyway. The function is redundant.
- A firmware mistake (`gpio_set_direction(7, OUTPUT)` low) shorts the rail directly.
- Fix: feed GPIO7 through a divider, e.g. 2 × 100 k with an optional 100 nF. That gives about 1.65 V, inside the ATTEN2/ATTEN3 range, a real rail measurement and no contention. This matches the open item in `plans/ext-comms-port.md` (Q9 follow-up), which the design already knows about.

### F2. No bulk capacitor at the module's 3V3 pin: 100 nF only. **Major / confirmed against WROOM DS and HDG (severity depends on layout)**
- HDG Schematic Checklist → Power Supply: VDD3P3 "may [see] a sudden increase in the current draw, causing power rail collapse. Therefore, it is **highly recommended to add a 10 μF capacitor** to the power rail". It also suggests "an ESD protection diode and at least 10 μF capacitor at the main power entrance" and a supply of ≥ 500 mA. HDG PCB Layout → Power: "Add a 10 µF capacitor before the power trace enters the chip". This is chip-level guidance; the module-level figure is WROOM DS Fig 9-1, which shows 22 µF + 0.1 µF.
- The power entrance is J7 (PSU board). DZ1 SM2T3V3A is the ESD diode on +3.3V, but the nearest 10 µF-class part is the PSU board's 22 µF, behind a connector about 26 mm away. The LM5163 is rated 0.5 A, exactly the HDG minimum, and also supplies the AP3012 boost.
- The WROOM DS Fig 9-1 peripheral schematic has C1 = 22 µF + C3 = 0.1 µF on 3V3. On this sheet only C4 (100 nF) is on U2.2.
- The nearest other +3.3V capacitors are C30 1 µF (AP3012 input, PowerSupply), C33 1 µF (ExtPort), and the 22 µF on the external `psu/buck100` board behind J7. In the current (pre-redesign) PCB, J7 is about 26 mm from U2 and C30 about 45 mm.
- The supply is an LM5163 COT buck rated 0.5 A. It also feeds the AP3012 boost, and Wi-Fi TX peaks reach 355 mA (per plan, WROOM Tbl 6-4). Brown-out resets during TX bursts are the classic symptom.
- Fix: add 10-22 µF X5R/X7R (≥ 6.3 V, derated) next to U2 pin 2.

### F3. mcu-head via J4: two 3.3 V sources are paralleled with no ORing, and the head's LDO back-feeds the whole motherboard rail. **Major / confirmed topology, plausible consequence**
- On the head, `+3.3V` is driven by the head's TLV70233 (U2) from Vusb (head netlist) and reaches motherboard `+3.3V` through J4.5, where the LM5163 via J7 also drives it.
  - **Head USB plugged, motherboard unpowered:** a 300 mA LDO supplies the entire motherboard 3.3 V domain. That includes the AP3012 12 V gate-drive boost (U5 SHDN tied to 3.3 V), so the 12 V gate rail comes up. It also feeds the INA226, UCC21330 VCCI, the WS2812, and the ext-port V+ (J5.4). The likely result is current limit or a brown-out loop, with the gate-drive supply live from a USB cable.
  - **Head USB unplugged, board powered:** TLV702 §7.3.1 says OUT > IN conducts through the PMOS body diode, "not limited". The motherboard therefore back-drives the head's Vusb net and the VBUS pins of its USB-C receptacle, to about 2.7 V.
- Fix: ORing on one side, e.g. a Schottky or ideal diode on the head LDO output or its input, or a jumper. Alternatively, document that the head LDO is DNP when the head is used on Fugu2.
- The same J4 contract also lacks LV_PGOOD (GPIO35), EXT_TX / EXT_RX / EXT_TX_OE_N (GPIO36/37/48) and the GPIO7 monitor. With a head fitted, the ext port stays disabled (R46 keeps /OE high: safe), and the PSU LV switch cannot be commanded. This is known and tracked in the plan (Q6, 2×7 → 2×8/2×9).

### F4. P2 footprint does not match the QTGM027 recommended land pattern (shell tabs). **Major / confirmed on the drawing, impact unverified**
- The footprint is `open-pe:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`. It has four **plated through-hole oval slots** (0.6 × 1.7 / 0.6 × 1.4 mm drill) at x = ±4.32 mm, y = −3.105 / +1.075.
- The SHOUHAN QTGM027 "Recommended P.C.B. Layout" (spec p.6) shows four **SMD rectangular shell pads, 2.02 × 1.50 mm**. Their inner edges are 4.32 mm from the centreline (centres at about ±5.33 mm) and their centres are 4.00 mm apart in y.
- The signal row (0.5 mm pitch, 0.30/0.60 × 1.15 mm, ±3.2 outer) and the Ø0.65 locating holes at ±2.89 (5.78 span) do match. A6/A7 are duplicated for flip orientation (checked in the PCB: both A6 and both A7 pads carry USB_D+ / USB_D−).
- Consequence: the SMD shell feet land mostly outboard of the slot pads. That weakens mechanical retention and shell-to-GND bonding, and paste/reflow will not form the intended joints.
- Fix: either change the BOM part to a USB4105-compatible (THT-tab) connector, or use a land pattern for QTGM027. Check the as-built board: the schematic note "see esp-rust-board for footprint" suggests the land came from another part.

### F5. No way to reset the ESP32 on the motherboard without cycling the battery. **Minor / confirmed**
- The `EN` net contains only R2, C3 and U2.3. The J1 ESP-PROG header is `on_board no`, there is no reset button, and there is no EN test pad. SW1 only pulls IO0.
- 3.3 V comes from a diode-OR of Bat+/Solar+/Vusb, and USB alone cannot run the LM5163 (plan: ≥ 6 V). To recover from a boot loop, which `doc/ESP32.md` names as the reason for the BOOT button, you must hold BOOT while disconnecting the battery and the PV.
- Fix: add an EN test pad or a second tactile switch from EN to GND. The existing C3 already debounces it.

### F6. Gate-driver safe state relies only on the UCC21330's weak internal resistors (50-185 kΩ). **Minor / plausible**
- The INL, INH and SD nets have no external resistors (netlist). The nets also run to J4 (head header) and the TP pads. With U2 high-Z during reset or flashing, or with the head unplugged, their only bias is ≥ 50 kΩ, next to a 39 kHz hard-switched half-bridge.
- UCC21330 Table 4-1 recommends RC filters on INx (10-100 Ω, 10-100 pF) and DIS (0-100 Ω, 100-1000 pF) when driven from an MCU. That belongs to the GateDrive review.
- Suggestion: add external 10 k pull-downs on INL/INH and a 10 k pull-up on SD, so the off state does not depend on internal resistors with a 3.7:1 spread.
- `doc/ESP32.md`'s own rule ("GPIO ≥ 21 for outputs") is broken by INL on GPIO14. As shown in the table above this is harmless, because the glitch is low and INA is active-high. Record that reasoning so a later pin swap to an active-low input does not reintroduce the risk.

### F7. USB device-side contract gaps. **Minor / confirmed (already listed as open in the plan)**
- HDG Schematic Checklist → USB: "It is recommended to **reserve series resistors (initial value can be 22/33 Ω) and capacitors to ground** on the traces (initially can be unpopulated), and **place them close to the chip**." HDG PCB Layout → USB says the same: reserve R/C near the chip, use a continuous ground reference, add GND return vias at transitions and surround the pair with ground copper. The schematic has neither the R nor the C footprints. Add 2 × 22 Ω + 2 × DNP C at U2.13/U2.14.
- The HDG USB section does not mention ESD. D3/D4 on D+/D− therefore follow general practice and the DevKitC reference; they should sit at P2 once P2 moves (plan item 7). The HDG ESD guidance covers only the power entrance and the antenna.
- HDG: "upon power-up, the USB_D+ signal will fluctuate between high and low states … if you need a stable initial state, adding an external pull-up resistor is recommended." This matters only if a host is attached at power-up. No action is needed for a service port.
- There is no 22-33 Ω series resistor footprint on D+/D−. There is no VBUS detection: this is a self-powered device, and the S3's USB_PU D+ pull-up is enabled by default (Tbl 2-1 note 4), so D+ is driven while VBUS is absent.
- There is no TVS or bulk capacitance on Vusb. Vusb goes only to D7 (SS310, 100 V VRRM) into the PSU diode-OR.
- **Interface note for the PowerSupply reviewer.** D7's cathode node (Net-(D13-K)) is clamped by SMAJ85A D13, whose standoff is 85 V. Its clamping voltage in a surge is therefore likely to exceed D7's 100 V VRRM with USB plugged in. I did not verify the SMAJ85A clamping figure against its datasheet.
- USB-alone does not power the ESP (LM5163 ≥ 6 V), so flashing over P2 needs battery or PV connected. Document it as the port contract.
- D3/D4 are LESD5D5.0CT1G (15 pF typ, bidirectional, 5 V VRWM). That is fine for Full Speed and is the part the Espressif DevKitC uses.

### F8. WS2812B D2 powered from +3.3V. **Minor / confirmed vs datasheet**
- The Worldsemi WS2812B datasheet specifies VDD +3.5 to +5.3 V, so 3.3 V is outside the recommended range. The blue die in particular runs dim or off-colour, and the part is characterised only at 4.5-5.5 V. Data levels are fine at 3.3 V (VIH = 0.7·VDD = 2.31 V).
- There is no local 100 nF on D2 VDD.
- Fix: use a 3.3 V-rated addressable LED (e.g. SK6812-mini-E / WS2812C-2020 class; check the exact VDD range), or accept this and document it as indicator-only.

### F9. ADC_Vin full scale is at the spec limit (interface to Sensors). **Minor / confirmed arithmetic**
- The divider is R18 200 k / R20 7.5 k, a ratio of 27.67. With ATTEN3's 2900 mV effective range (Tbl 5-6), full scale is **80.2 V**, which equals the README's 80 V max solar input. There is no headroom for Voc at cold temperature or for overshoot, and overvoltage reads as a clamped 80 V.
- D6 (VRWM 5 V) does not clamp below the ESP's 3.6 V limit. The 200 k resistor limits injection to about 0.5 mA at 100 V, which is acceptable.

### F11. ADC inputs lack the HDG-recommended 0.1 µF pin capacitor. **Minor / confirmed**
- HDG Schematic Checklist → ADC: "Please add a 0.1 μF filter capacitor between ESP pins and ground when using the ADC function to improve accuracy. ADC1 is recommended for use." It also restates the ATTEN3 effective range of 0-2900 mV with ±50 mV error, and ATTEN2 as 0-1600 mV with ±10 mV.
- **ADC_Vin (GPIO4):** C15 is 10 nF, 100 V, 10× below the recommendation. The source impedance is R18 ∥ R20 ≈ 7.2 kΩ, so a 0.1 µF cap gives τ ≈ 0.72 ms, which suits an MPPT voltage loop.
- **NTC (GPIO8):** no capacitor at all. R16 ∥ TH1 is about 5 kΩ at 25 °C, and the net runs to J4.13 (header). Add 0.1 µF at the pin.
- **GPIO7:** see F1. If it becomes a divider, add 0.1 µF there too.
- Accuracy note: ATTEN3 is ±50 mV. Scaling to ≤ 1.6 V and using ATTEN2 (±10 mV) is the better accuracy choice where the range allows.

### F12. Proposed ADC_I (op-amp current-sense output) on GPIO5 / J4 pin 11: suitable, with conditions. **Assessment requested by coordinator**
GPIO5 is a good choice:
- It is ADC1_CH4 (S3 DS / HDG ADC table), so it is usable with Wi-Fi on. The HDG says "ADC1 is recommended".
- It is unconnected today on both the motherboard and the head.
- It is not a strapping pin and is not used by any ROM download mode (HDG USB-OTG pad table).
- Its reset state is high-Z, with no IE and no pull (S3 DS Tbl 2-1).
- The alternatives on ADC1 are GPIO6 and GPIO9, which are also free. GPIO9 (FSPIHD) is a worse choice.
- J4 pin 11 is the only spare pin, and it is spare on both boards (`unconnected-(J4-Pin_11)` / `unconnected-(J2-Pin_11)`). The head's U1 GPIO5 is also free, so mapping J4.11 to GPIO5 on both boards keeps the firmware identical.

Conditions for driving it from a low-impedance op-amp output:
1. **Power-up glitch.** S3 DS Table 2-2 gives GPIO5 a 60 µs *low-level output* glitch (IOL ≈ 28 mA, Tbl 5-4). A directly connected op-amp output would fight the pad driver, the same mechanism as F1. Put a **series resistor between the op-amp and the pin** (≈ 1 kΩ). That limits the glitch current to about 3 mA.
2. **Overvoltage.** The pin's VIH max is VDD + 0.3 V (Tbl 5-4). If the op-amp runs from a rail above 3.3 V (5 V/12 V) or can rail during a fault, the same series R limits clamp-diode injection. At 12 V and 1 kΩ that is about 8 mA, so it needs ≥ 10 kΩ or a 3.3 V op-amp rail. The better option is to power the op-amp from 3.3 V, or add a clamp.
3. **Filter / load.** Add the HDG 0.1 µF at the pin, on the pin side of the series R. The R then also serves as the op-amp's isolation resistor against the capacitive load. Check the op-amp's datasheet for capacitive-load stability. With 1 kΩ and 0.1 µF, f−3dB ≈ 1.6 kHz. That is fine for an averaged inductor/battery current at 39 kHz switching, but too slow for any cycle-by-cycle or fast OCP function. If ADC_I is meant for protection, use a separate comparator path, and choose R/C for the needed bandwidth.
4. **Range.** Scale the op-amp output to ≤ 1.6 V (ATTEN2, ±10 mV) or at most ≤ 2.9 V (ATTEN3, ±50 mV). If the current is bidirectional, bias the op-amp output to mid-range.
5. **Header adjacency.** On J4, pin 11 sits between ADC_Vin (9) and NTC (13) in the odd rows, which is good. The even rows opposite it carry INH (10), SD (12) and INL (14), whose PWM edges are about 4-5 mm away. GND is pin 7 in the same column. Place the 0.1 µF at the ESP pin, i.e. on the head board as well when the head is used, not only at the motherboard header.
6. **Contracts.** Update `doc/Connectors.md` and the mcu-head schematic (the J2.11 net, plus its own R/C) together. Update the ext-comms-port plan's free-GPIO list (GPIO5 is no longer free) and the head header-size decision (Q6).

### F10. Label, ERC and capture hygiene. **Nit / confirmed**
- HDG Schematic Checklist → UART: "It is recommended to connect a **499 Ω series resistor to the U0TXD line** to suppress harmonics." GPIO43 → TP2 is direct. That is harmless for a test pad, but add the resistor if a UART0 cable is ever connected routinely.
- ERC reports three `unconnected_wire_endpoint` items, all in uC.kicad_sch:
  - (134.62, 64.77)→(134.62, 66.04): a 1.27 mm stub into the U2 body below pin 2.
  - (224.79, 69.215)→69.85: a 0.635 mm stub at the P2 shield.
  - (79.375, 174.625): a junction and stub at the J12 RXD pin.
  - All three are cosmetic, since U2.2 and P2.S1 are connected in the netlist.
- GPIO46 is tied straight to GND (ERC pin_to_pin). Firmware must never drive it. A 1-10 k resistor to GND would make it fault-tolerant; nit.
- SPICS / SPID / SPICLK / SPIQ labels reach only J12 (DNP, `on_board no`), so GPIO10-13 are named but dead nets. The UEXT pinout on J12 does match the Olimex spec (3 TXD ← TX, 4 RXD ← RX, 5 SCL, 6 SDA).
- `TP3` uses a *global label* "GND" instead of a power symbol. It works, but it is a second GND naming path.
- `LV_PGOOD` is an MCU *output* that turns Q9 on and cuts the Solar feed to the PSU. A "PGOOD" name suggests an input; consider `PSU_SRC_LV` or similar.
- The sheet text "todo pull up cap?" at IO0 is stale.
- R34 (0 Ω shield-to-GND, DNP, `on_board no`) is redundant: P2.S1 is already wired to GND.
- P2 uses the `USB_C_Plug_USB2.0` symbol, which has a pin named "VCONN" at B5, on a receptacle. It is electrically correct (B5 = CC2 with 5.1 k R35), but misleading. ERC also reports `lib_symbol_mismatch`.
- J4 is `in_bom no`. U2 and the head are mutually exclusive by assembly, and no variant or DNP field captures that.
- J2 (I2C socket, DNP): its pinout (1 3V3, 2 GND, 3 SDA, 4 SCL, 2.0 mm) is non-standard, and it has no ESD or series R. That is acceptable only while it stays internal.

## Checks that passed
- EN RC: R2 10 k / C3 1 µF matches the WROOM DS p.41 recommendation (10 k / 1 µF).
- CHIP_PU/EN: HDG Schematic Checklist → Chip Power-up and Reset recommends "R = 10 kΩ and C = 1 μF" and says CHIP_PU "must not be left floating". R2/C3 comply. The HDG also advises keeping the CHIP_PU trace short and, for slow or abnormal supplies, reserving a supervisor at about 3.0 V; the design has no supervisor. The LM5163 soft-start plus the diode-OR input is a plausible slow or glitchy supply, so leaving a footprint is cheap insurance (optional).
- Strapping: GPIO0 has a 10 k pull-up and a BOOT switch. GPIO46 = 0 gives valid SPI boot and allows download. GPIO45 is floating (WPD), giving VDD_SPI = 3.3 V, correct for N4. GPIO3 is unbound.
- N4 (quad flash, no PSRAM): GPIO35/36/37 are free. GPIO47/48 run in the 3.3 V VDD_SPI domain, which is not the 1.8 V of N16R16V.
- Analog inputs are all on ADC1 (GPIO4, 7, 8), so there is no Wi-Fi conflict with ADC2.
- I2C: a single 10 k pull-up set to 3.3 V (R13/R14), with the INA226 VS at 3.3 V. The head adds no second pull-ups. ALERT has R15 10 k, and the INA226 Alert output is open-drain. 10 k supports 100 kHz comfortably. At 400 kHz, bus capacitance above about 35 pF (e.g. a cable on J2) would violate the 300 ns rise time.
- USB-C: CC1 (A5) and CC2 (B5) each have 5.1 k 1 % to GND (sink). Both D+/D− pad pairs in the footprint are wired.
- J4 ↔ head J2: the pin-for-pin net mapping is identical (1 LED, 2 GND, 3 SCL, 4 SDA, 5 3V3, 6 ALERT, 7 GND, 8 BflowSD, 9 ADC_Vin, 10 INH, 11 NC, 12 SD, 13 NTC, 14 INL). Every net lands on the same GPIO on both boards. Pad grids agree within about 0.4 mm (J4 F.Cu vs head J2 B.Cu mirrored variant). I did not verify physical mating.
- ESD diodes D3/D4 are on the connector side of D+/D−. The current PCB places them near the MCU rather than at P2. P2 is being relocated (plan item 7), and D3/D4 must move with it.

## Unverified / not done
- The HDG was read in its web "latest" edition. The page gives no version number, so I recorded the retrieval date 2026-09-30.
- The SMAJ85A clamping voltage and the LM5163 minimum VIN are taken from the plan's statements; I did not read those datasheets.
- For F4, I did not compare against the as-built board or the esp-rust-board source.
- The layout is pre-redesign, so no placement or routing conclusions are drawn beyond the F2 distance.
- The WS2812B datasheet used is an older Worldsemi revision (adafruit mirror). Newer revisions (e.g. WS2812B-V5) may specify a different VDD range. Check the exact part ordered.
