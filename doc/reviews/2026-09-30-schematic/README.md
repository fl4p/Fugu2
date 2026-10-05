# Schematic review 2026-09-30 — per-block

One independent reviewer per hierarchical sheet, run right after the power stage was moved
off the root sheet into `PowerStage.kicad_sch`. Reviews are read-only snapshots of the
schematic at that point (before the INA226 → AS333 change); files in this folder are the full
reports with datasheet sources and access-ladder notes.

Verified by the coordinator against netlist/PCB: Q5/Q7 duplicate pins, D18 pad mapping,
+12V divider arithmetic.

## Critical / major, cross-block

| # | block | finding | status |
|---|---|---|---|
| 1 | PowerSupply | **D18 (BZX84C62) mapped K=1/A=2 on SOT-23; real pinout 1=A, 2=NC, 3=K** → 62 V gate clamp of Q8 is absent on the PCB (pad 3 no net) | verified |
| 2 | PowerSupply / GateDrive | **"+12V" is 9.34 V** (R37 33k / R38 5.1k, AP3012 Vfb 1.25 V); UCC21330B wants ≥ 9.2 V, bootstrap VDDB sags into UVLO → matches `HW Stories/flat.md` "boot strap supply UV". Fix: R37 = 43k (11.8 V) or R38 = 4.3k | verified (arith.), rail not measured |
| 3 | PowerStage | **Q5/Q7 symbol has hidden S pins numbered 2/3** → netlist puts G and D on BflowS (5 ERC errors). Use Q6's 3-pin symbol | verified |
| 4 | PowerStage | C11/C12 input electrolytics ~7 A rms each vs 1.85–3.7 A ratings; no MPN | |
| 5 | PowerStage | Q5–Q7 are 60 V on a ≤ 60 V battery; no Bat+ clamp (doc says 80 V needed) | |
| 6 | PowerStage | F1 40 A blade fuse has no voltage rating recorded (32 V standard types unusable) | |
| 7 | PowerStage | No reverse-polarity protection on PV or battery, undocumented | |
| 8 | PowerStage | Snubber R11 dissipates 0.44–0.55 W in a 1206; 7.5 Ω ≈ 2.2× ring impedance | |
| 9 | PowerSupply | Q8 has no gate–source clamp (Vgs → 40 V on aux short) | |
| 10 | PowerSupply | Aux rail from Bat+ via D12/F2 has no usable clamp (SMAJ85A Vc up to 137 V > 100 V parts); F2 is 60 V | |
| 11 | PowerSupply | J7 pinout reversed vs `psu/buck100` module, unkeyed 1×3 header → HV on +3.3V if flipped | |
| 12 | GateDrive | VDDA has only 100 nF locally; bulk 10 µF ≈ 53 mm away | |
| 13 | GateDrive | Backflow switch turn-off through 47k takes 0.3–1.5 ms | plausible |
| 14 | Sensors | NTC divider reads 2.93 V at the 90 °C trip, above the 2.9 V ADC range → NaN → OT shutdown never trips | |
| 15 | Sensors | PV divider full scale 80.2 V = rated input, no OV headroom | |
| 16 | uC | GPIO7 tied directly to +3.3V (60 µs low glitch at boot, 28 mA) | verified in netlist |
| 17 | uC | No bulk cap at ESP32 module (guide: ≥ 10 µF) | |
| 18 | uC | MCU-head LDO paralleled with board 3V3 via J4.5, no ORing | |
| 19 | uC | P2 USB-C footprint shell pads don't match QTGM027 | |
| 20 | ExtPort | LESD5D5.0 (5.6–7.8 V) cannot hold U7/U8 pins ≤ 6.5 V under sustained overvoltage | |

Minor findings and nits: see the per-block files.
