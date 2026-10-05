# Fugu2 — Sensors sheet review (`Sensors.kicad_sch`)

Reviewer: independent schematic review, 2026-09-30. The project was only read, never modified. Scratch files are in
`/tmp/fugu_split/review_Sensors/`.

## Scope and evidence

- **Inputs:** `/tmp/fugu_split/repo.net` (Eeschema 10.0.5 export), `/tmp/fugu_split/work/erc_after.rpt`, the rendered
  `/tmp/fugu_split/work/svg/Fugu2-Sensors.png` and the `Sensors.kicad_sch` symbol flags (parsed read-only). I also read
  the PowerStage, uC and PowerSupply interface nets from the netlist.
- **Docs and firmware read:** `README.md`, `doc/Current Sense.md`, `doc/ESP32.md`, `doc/Thermal.md`,
  `doc/Protection Circuit.md`, `doc/Power Supply.md`, `doc/HV Fuse.md`. For how the sense values are consumed I read
  firmware `~/dev/pv/fugu-mppt-firmware`:
  - `src/adc/temperature.h`
  - `src/adc/ina226.h`
  - `src/adc/sensor_setup.cpp`
  - `src/mppt.h`
  - `config/*/conf/sensor.conf`
- **Vision gate:** `VISION-PROBE-PASS` in this session, so the rendered sheet was actually viewed.
- **Datasheets (actually read):**
  - **INA226:** TI SBOS547C (rev. Aug 2026). Sources: `https://www.ti.com/lit/ds/symlink/ina226.pdf`, rung 1 (curl),
    `%PDF`, 1.52 MB.
  - **ESP32-S3:** Espressif ESP32-S3 Series Datasheet v2.2. Rung 1, `%PDF`, 1.10 MB.
  - **ESP32-S3-WROOM-1:** datasheet downloaded, used only for the pin mapping.
  - **NCP18XH103F03RB:**
    - The catalog PDF endpoint returned HTML (rung 1).
    - Rung 4 (headless Chrome with a plain-Chrome UA) returned the Murata product page with the spec table.
    - Values used: R25 = 10 kΩ ±1 %, B25/50 = 3380 K ±1 %, B25/80 = 3428 K, B25/85 = 3434 K, B25/100 = 3455 K,
      max voltage 5 V, "Maximum Operating Current (25 °C) 0.1 mA", dissipation constant 1 mW/°C, −40…125 °C.
    - The full PDF (R–T table) was not obtained. The curve below is a β-interpolation from these reference B values.
      That is a model, not the table.
  - **LESD5D5.0CT1G (LRC/Leshan):**
    - onsemi URL: Akamai "Access Denied" (rung 1). This is the wrong vendor anyway: LESD is an LRC part.
    - Found the chipdip.ru mirror PDF via Serper (rung 6), then fetched it with rung 1: `%PDF`, 356 kB. The revision is
      unknown because it is a mirror.
    - Values: VRWM 5 V, VBR ≥ 5.8 V @ 1 mA, IR ≤ 1 µA @ 5 V, VC 6 V @ 1 A / 10 V @ 8 A, CJ 15 pF.
  - **AS333:** Diodes DS45351 Rev. 2-2, rung 1. Only lightly used, because the block is off-board.

### Block topology (from the netlist)

**Shunt and INA226 (U3)**
- R26 = 0.5 mΩ, LR2512D-3W-0.5mR-1%. It sits in the battery return: BuckGND (PV−, J10.1) on one side, GND (battery−,
  J9.2, MCU ground) on the other.
- U3 = INA226AIDGSR:
  - Vin+ comes from BuckGND through R25 (22 Ω).
  - Vin− comes from GND through R27 (22 Ω).
  - C23 = 1 µF differential across the inputs.
  - VBUS = BT+/2 through R28/R29 (47k/47k, 1 %), with C24 = 10 nF.
  - VS = +3.3 V, bypassed by C25 = 100 nF.
  - A0 = A1 = GND.
  - ALERT goes to GPIO41 with R15 = 10k pull-up (uC sheet). SDA/SCL go to GPIO42/GPIO2.

**PV voltage divider**
- ADC_Vin = Solar+ through R18 (200k) over R20 (7.5k), with C15 = 10 nF, to GPIO4 (ADC1_CH3).
- D6 is DNP (`dnp yes`, `in_bom no`, footprint on board).

**NTC**
- TH1 connects +3.3 V to node NTC. R16 = 10k connects NTC to GND. The node goes to GPIO8 (ADC1_CH7).

**AS333 alternative**
- U6 (AS333) and R39–R42, C26, C29, C32 are `on_board no`, `dnp yes`. They are absent from the netlist and the PCB.

### ERC

- The `/Sensors/` section of `erc_after.rpt` is empty: no errors or warnings.
- The report ignores four check classes globally: single global label, four-way junction, SPICE model, and footprint
  filter.

### Confirmed OK (no finding)

**INA226 shunt range**
- Full scale is 81.92 mV / 0.5 mΩ = 163.8 A (SBOS547C Table 5.5).
- 33 A gives 16.5 mV, which is 20 % of full scale. 1 LSB = 2.5 µV = 5 mA. VOS max ±10 µV = ±20 mA.
- The F1 40 A fuse clears far below the point where the reading saturates. The differential abs max is ±40 V (§5.1).

**INA226 input filter capacitor**
- C23 = 1 µF is within the recommended 0.1–1 µF (§6.4.2).
- The differential corner is 1/(2π·44 Ω·1 µF) = 3.6 kHz, which agrees with the sheet note.

**INA226 common mode**
- Common mode is about 0 V, inside the −0.3…40 V abs max range.
- BuckGND sits −I·0.5 mΩ relative to GND, which is −16.5 mV at 33 A. It would take about 600 A to reach −0.3 V at
  Vin+.

**VBUS in normal operation**
- 60 V battery gives 29.2 V at the pin, inside the 0–36 V range (Table 5.5).
- §8.3 says VBUS/IN tolerate 0–36 V whether the device is powered or not, so the 3.3 V power state does not matter here.

**I2C address and ALERT**
- A0 = A1 = GND gives address 1000000b = 0x40 (Table 6-2). U3 is the only on-board I2C target.
- J2 (DNP I2C connector) is the only other device on the bus, so an off-board 0x40 device must not be attached there.
- ALERT is open drain (IOUT ≤ 10 mA abs max) with a 10k pull-up, which is fine.
- GPIO41/42 are the MTDI/MTMS JTAG pins, so JTAG cannot be used together with ALERT/SDA. This is informational.

**VS decoupling**
- 100 nF on VS matches the typical 0.1 µF (§8.3).

**ADC_Vin divider impedance and leakage**
- The Thevenin source is 7.23 kΩ with a 10 nF reservoir.
- ESP32-S3 IIH/IIL ≤ 50 nA (Table 5-4, p65) gives ≤ 0.36 mV error.
- The ADC1 channel is used, so there is no conflict with WiFi.

**Shunt Kelvin taps (layout, partial)**
- In `Fugu2.kicad_pcb` (read-only), each R26 pad has a 0.2 mm B.Cu track leaving toward the resistor centre, which is
  consistent with Kelvin taps.
- I did not trace the complete path to R25/R27, which sit about 34 mm away at x ≈ 87 mm. That is left to the layout
  review. The schematic uses plain BuckGND/GND nets with no net-tie, so DRC cannot enforce the Kelvin routing.

**Sense sign**
- Vin+ is on the BuckGND side, so charge current reads negative. Firmware compensates with `iout_factor=-1.0` in
  `sensor.conf`. Consistent.

## Findings (most severe first)

### F1 — major, confirmed arithmetic / plausible impact: NTC divider puts the over-temperature region at the top of the ESP32-S3 ADC range

- **Where:** TH1, R16, net NTC to GPIO8.
- **Circuit:** NTC on the high side, 10k to GND, so V = 3.3·10k/(10k + R_NTC). Firmware uses ATTEN 12 dB
  (`temperature.h:92`) and `temp_max` = 90 °C by default (`mppt.h:51`, shutdown at `mppt.h:556`).
- **Limit:** ESP32-S3 DS v2.2 Table 5-6 (p66) gives the ATTEN3 effective range as 0–2900 mV with total error ±50 mV.

| T (°C) | R_NTC (model) | V_NTC | dV/dT |
|---:|---:|---:|---:|
| 25 | 10.0 k | 1.650 V | 31 mV/K |
| 60 | 3.02 k | 2.53 V | 18 mV/K |
| 80 | 1.67 k | 2.83 V | 11 mV/K |
| 87 | 1.38 k | 2.90 V | 9.6 mV/K |
| 90 | 1.27 k | 2.93 V | 8.9 mV/K |
| 100 | 0.97 k | 3.01 V | 6.7 mV/K |

**Consequences**
- **The shutdown threshold is off the ADC's specified range.** The 90 °C threshold and everything above about 87 °C lie
  outside the effective range.
- **Accuracy near 90 °C is poor.** The ±50 mV error alone is about ±5.6 K there.
- **The measurement is not ratiometric.** The ADC uses an internal reference, while the divider is fed from +3.3 V and
  firmware assumes a fixed VCC. A 1 % rail error adds about 29 mV, roughly 3 K.
- **The sheet note makes it worse.** The note "ADC max: 2.45V" is the classic-ESP32 figure. If anyone uses it, the NTC
  saturates at about 56 °C.
- **Firmware does not catch saturation.** It returns NaN only for raw codes ≥ 4080. The shutdown and start checks are
  `>` comparisons, which are false for NaN, so a saturated or NaN reading does not trip OTP. The MCU die temperature is
  the only backstop. This is firmware behaviour, noted as the path that makes this schematic choice matter.

**Fix**
- Swap the positions: TH1 to GND, a 10k pull-up to +3.3 V. Then 90 °C gives 0.37 V, so a low-attenuation range can be
  used (±5–10 mV error, well under 1 K).
- Alternatively, reduce R16 to about 1.5–2.2 kΩ so that 90–110 °C sits mid-range.
- Either way, update the firmware `Rp` and the topology in `volt2Temp`.

### F2 — major, confirmed arithmetic / plausible impact: ADC_Vin has no headroom above the rated 80 V PV input, and the tolerance is unspecified

- **Where:** R18, R20, C15, net ADC_Vin to GPIO4.
- **Ratio:** 7.5/207.5 = 0.03614.
  - Full scale at the 2.9 V ATTEN3 limit (DS Table 5-6) is 80.2 V.
  - Using the sheet's own "2.45 V" figure, full scale is 67.8 V.
- **Rated input:** README gives PV 12–80 V, and Protection Circuit.md says 0–80 V. The sheet note says the channel is
  needed "for OV/UV detection".
- **Consequences:**
  - An OV threshold at or above the rated maximum cannot be measured reliably.
  - R18/R20 carry no tolerance and no MPN: the value and MPN fields are just "200k" / "7.5k". With 5 % parts the
    saturation point can fall below 80 V.
  - The ±50 mV ADC error is ±1.4 V at the input.

**Fault path**
- ADC_Vin exceeds VDD + 0.3 V (VIH max, Table 5-4) at Solar+ ≥ 99.6 V. Power Supply.md mentions 100 V solar.
- The ESP32-S3 datasheet gives no injection-current rating. The only clamp is the pin's internal ESD diode, fed through
  200 kΩ: about 0.48 mA at 100 V.
- +3.3 V comes from the off-board PSU, fed from Solar+ (Q8) or Bat+ (D12). Normally the rail is up whenever PV is up.
- During PSU start-up or a PSU fault with PV present, the injection back-feeds the unpowered 3.3 V rail. The rail's
  consumption is not a guaranteed sink.

**D6**
- D6 does not help. It is DNP, and even if fitted, the LESD5D5.0 has VBR ≥ 5.8 V @ 1 mA and VRWM 5 V (LRC DS), so it
  does not clamp below the 3.6 V limit. The sheet note already says this.

**Fix**
- Rescale to about 100–110 V full scale, e.g. R20 = 5.6 kΩ gives 106 V at 2.9 V. Specify 1 % (or 0.5 %) parts with
  real MPNs.
- If over-voltage beyond about 100 V is credible, add a low-leakage Schottky to +3.3 V (BAT54-class) and verify the
  rail can sink the current.
- Correct the "ADC max" note to 2.9 V (ATTEN3, ESP32-S3).

### F3 — major if charge voltage relies on it, plausible: battery voltage (VBUS) accuracy depends on a typical-only 830 kΩ input impedance

- **Where:** R28, R29, C24, U3 pin 8, BT+.
- **Loading:** INA226 VBUS input impedance is "830 kΩ" with a typical value only and no min/max (Table 5.5). In parallel
  with R29 = 47k it pulls the ratio from 0.5000 to 0.4862 (−2.75 %).
- **Firmware:** it compensates with the same typical constant (`ina226.h:506`, used by `adcVDiv` in
  `sensor_setup.cpp:151`). No per-unit calibration path was found (`calibrationConstraints = {}`).
- **Error budget:**
  - The unspecified spread and temperature coefficient of that impedance enter the battery-voltage reading directly.
  - The two 1 % resistors add up to about ±1 % ratio error.
  - Bus offset adds ±7.5 mV max, which is ±15 mV at BT+.
  - For 16S LFP, 1 % of 58.4 V = 0.58 V = 36 mV/cell. An uncompensated 2.75 % error would be 100 mV/cell (60 V at a
    58.4 V setpoint).
- **Fix:** lower the divider impedance so the pin load is under about 0.2 %. For example, 10k/10k gives about 0.6 %, but
  that raises the drain (see F5) to 2.9 mA. Alternatively, use 0.1 % resistors and add a per-unit calibration step.
  At minimum, document that CV accuracy depends on calibration.

### F4 — minor, plausible: VBUS pin reaches its 40 V abs max during the documented HS-short fault

- **Scenario:** Protection Circuit.md describes a shorted HS MOSFET plus the BMS cutting the battery, which lifts BT+ to
  PV voltage (≤ 80 V, or 100 V per Power Supply.md).
- **Pin voltage:**
  - At 80 V the pin sees 38.9 V, which is 1.1 V under the 40 V abs max (§5.1). With 1 % resistors and the unspecified
    830 kΩ, that margin is roughly zero.
  - The limit is reached at BT+ = 82.3 V.
  - At 100 V the pin sees 48.6 V.
- **Current:** R28 limits pin current to ≤ 1.3 mA, under the 5 mA IIN abs max, so survival is plausible but outside
  ratings.
- **Measurement ceiling:** 36 V at the pin, which corresponds to 74 V at BT+.
- **Fix:** a 1:3 divider (with F3's impedance fix) or a clamp on VBUS.

### F5 — minor, confirmed: permanent battery drain through R28/R29

- BT+ is the battery-side terminal (J9.1, F1 load side). The 94 kΩ divider draws 0.62 mA at 58.4 V continuously, even
  with the converter and MCU off. That is about 5.4 Ah/year.
- This conflicts with F3's lower-impedance fix. A switched divider (P-FET) resolves both.

### F6 — minor, plausible: shunt current includes the auxiliary supply return, and an external PV−/Bat− bond bypasses the shunt

- The auxiliary supply takes power from Solar+ (Q8/R43 on the PowerSupply sheet) and returns it to GND (battery−).
  Its return current therefore flows GND → R26 → BuckGND (PV−) and adds to the measured battery current.
- The offset is of order 10 mA, comparable to the INA226's ±20 mA VOS bound.
- Wiring that ties PV− and Bat− outside the board puts that connection in parallel with R26, so the reading becomes
  wrong. This is not documented as an interface contract (README/Connectors).
- **Fix:** document "PV− and Bat− must not be bonded externally", or accept and calibrate the offset.

### F7 — minor, plausible: no filter capacitor on the NTC node

- The NTC node has a source impedance of about 5 kΩ and no capacitor. TH1 sits about 8 mm from Q2 on B.Cu, next to the
  switch node.
- ESP32-S3 ADC accuracy (Table 5-6) is characterised with an external 100 nF capacitor on the pin.
- **Fix:** add 100 nF from NTC to GND at the MCU pin.

### F8 — minor/nit, confirmed: NTC current above Murata's "maximum operating current"

- Divider current is 165 µA at 25 °C and 290 µA at 90 °C. Murata lists 0.1 mA max at 25 °C.
- Self-heating is 0.27 mW × 1 mW/°C⁻¹, about 0.27 K at 25 °C and 0.11 K at 90 °C, which is negligible for OTP.
- The rating is still exceeded. The F1 fix (NTC to GND with a 10k pull-up) does not change the current. A 22–33 kΩ
  pull-up would, at the cost of range.

### F9 — nit, confirmed: sheet annotation arithmetic is off by 10×

- **Note:** "f_c=1/(2π·R20·C15)=221 Hz, t_r=1.6 ms".
- **Actual:**
  - With R20 alone, 1/(2π·7.5k·10n) = 2.12 kHz.
  - The correct Thevenin value (7.23 kΩ) gives f_c = 2.20 kHz and t_r = 159 µs.
- **Also stale:** "ADC max: 2.45V" (see F2).

### F10 — nit, confirmed: INA226 filter resistors are 22 Ω, above TI's "typically 10 Ω or less"

- TI's guidance is in SBOS547C §6.4.2 / Fig. 6-3.
- With current silicon the input bias is about 0.05 nA (Fig. 5-12; rev. B history "Decreased input bias current typical
  value"). The resulting error is nV-level, and 22 Ω only increases dV/dt protection.
- Keep 22 Ω for the README's "low R_filt" water-robustness goal. Note that the error was not evaluated for older die
  revisions: the earlier datasheet's bias value is unverified here, because the rev. A URL redirected to rev. C.

### F11 — nit: inactive AS333 block and D6 bookkeeping

- **AS333 block:** U6/R39–R42/C26/C29/C32 are `on_board no` + `dnp yes` but `in_bom yes`. Check that BOM exports mark
  them DNP.
- **If the block is revived:**
  - The TODO is valid: U6 V− is on BuckGND while the ADC reads against GND, which puts a shunt-drop-sized error on the
    output reference.
  - The AS333 input common-mode range is (V−) − 0.1 V … (V+) + 0.1 V, with VOS ≤ 22 µV at 5 V (DS45351 Table,
    Electrical Characteristics). That VOS is ±44 mA referred to the input.
- **D6:** DNP, but its footprint is still on the board (`in_bom no`). Either remove it or replace it with a Schottky to
  +3.3 V (see F2).

## Unverified / left open

- **NTC temperatures:** full Murata R–T table not obtained (the catalog PDF endpoint returned HTML). The NTC voltages
  above use β interpolation between Murata's published B25/50, B25/80, B25/85 and B25/100. They are good to about ±1 K,
  which does not change F1.
- **ESP32-S3 pin injection:** there is no injection-current rating in the ESP32-S3 datasheet v2.2, so the pin's
  tolerance of 0.1–0.5 mA injection is unverified.
- **INA226 VBUS impedance spread:** its min/max and temperature coefficient are unpublished.
- **Firmware ESP32 ADC impedance:** firmware assumes 500 kΩ ("?" comment, `adc_esp32_cont.h:206`). That makes the
  computed Vin about 1.45 % high if the real DC load is only leakage. This is outside the schematic scope, but it
  interacts with F2.
- **Kelvin routing:** routing from the R26 pads to R25/R27, and the placement of C15/C23/C24 near their pins, need
  layout review.
- **LESD5D5.0 datasheet:** it came from a third-party mirror (chipdip), so its revision is unknown.
