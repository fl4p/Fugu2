# Calibrating the ESP32-S3 ADC on the Fugu converters

The Fugu boards read their high-voltage side (up to ~80 V) through a 200k/7.5k divider into
ESP32-S3 ADC1 ch3, converted with ESP-IDF's curve-fitting calibration. Two of them, `fboost` and
`fmetal`, were measured on the same node against an HP3458A-traced reference from 16.5 to 74.5 V.

The ADC has a ±0.2 V S-curve, input-referred, on top of a gain and offset that differ per board.
The S-curve has the same shape on both chips and stays stable over two months. One fixed
correction curve plus a two-point gain/offset calibration per board brings the error from
~100 mV rms to ~40 mV rms, that is, from ~0.25 % to ~0.1 % at 40 V. The correction ships in the
firmware as an opt-in (`esp32adc1_inl`).

The table compares each method's error against the reference:

| Board error vs reference | rms | max |
|---|---|---|
| IDF calibration, best per-board gain/offset (the existing linear model) | 96–102 mV | 212 mV |
| Universal curve from the other board, 2-point cal at 25 V and 65 V | **38–45 mV** | 97–173 mV |
| Board's own degree-5 fit (best case, for comparison) | 33–35 mV | 80–98 mV |

## Setup

- Node: the output of `fboost`, driven up a ladder of duty-cycle rungs from a Korad supply (10 V,
  0.75 A). Plan `ina228-u-4ref-dense`: 0.5 V rungs from 16.5 to 77 V, 30 s per rung.
- Devices under test: `fboost` (`Uo`, sent as BLE advertisements, float16, ~2 Hz) and `fmetal`
  (`Uo`, WiFi line protocol, 10 mV resolution, ~25 Hz). Both are configured as boosts with
  `vout_adc=esp32adc1`, `vout_ch=3`, 200k/7.5k. `fmetal` hangs on the node and is powered by it.
- Reference: `BLE_ESP32_INA228_2`. A rung's value is the median of each device's readings
  over the rung window, so a rare garbage BLE packet cannot shift it.
- Data: four dense runs, 2026-10-09/10 (211 rungs for fboost, 201 for fmetal). Run 1 covered
  16.5–73.4 V. The others were cut short when the reference board dropped off BLE, see
  pwr-metering `doc/friction/20261010-supply-guard-s-3-poll-blind-tolerance-3-s-lets-one-27-s-ina2.md`.
  The August `ina228-U-2+3` runs add fboost against the HP3458A directly (166 rungs).

## Reference check

![INA228_2 against the HP3458A](img/esp32-adc-reference.webp)

Over the same 16–79 V, `INA228_2` sits on a straight line through the HP3458A within
0.57 mV rms (1.6 mV peak) over 259 rungs. That is about 200× smaller than the effect below, so
the rest of this article treats the INA228 as the true value.

## Raw error

![Raw error](img/esp32-adc-raw-error.webp)

With IDF's calibration and the nominal divider, both boards read 2.6–3.5 % high in gain, with an
offset of −0.7 to −1.3 V. Uncalibrated, they are off by −0.5 to +1.2 V across the range. That
part is ordinary gain/offset: resistor tolerance, the ADC's 500 kΩ input load and the chip's eFuse
calibration. A per-board linear calibration removes it, and `sensor.conf` could already express
that through the divider values.

## Residual S-curve

![INL of both boards](img/esp32-adc-inl.webp)

After subtracting each board's own best line, an S-curve remains: +180 mV at 17 V, −150 mV around 30 V,
+130 mV around 50–58 V, −130 mV above 70 V (~100 mV rms, ~215 mV peak). A linear calibration
cannot remove it. It is worth correcting in firmware because it has:

- The same shape on both boards. fboost and fmetal are different chips on different PCBs.
- The same shape two months apart. The grey points are fboost against the HP3458A in August, the
  blue ones fboost against the INA228 in October.
- The same shape across runs:

![Repeatability](img/esp32-adc-repeat.webp)

Runs taken over three hours fall on the same curve. Even the ~35 mV rung-to-rung scatter that
remains after a smooth fit repeats: comparing run 1 and run 5 rung by rung, it correlates at 0.89.
Within a rung the averaging noise is under 2 mV, so the scatter is an operating-point effect,
fixed for a given duty and voltage. It is neither a smooth function of voltage nor the same on the
two boards, so a shared correction cannot remove it. This scatter sets the ~35 mV floor.

## The correction

![Universal correction](img/esp32-adc-correction.webp)

The fit works in the ADC's own coordinates, pin millivolts, so the result does not depend on
the divider:

```
U_true / k  =  g_b · ( a + d(a) )  +  o_b
```

- `a`: the pin voltage reported by IDF.
- `k = 28.07`: the divider, including the ADC's 500 kΩ load.
- `g_b`, `o_b`: the gain and offset of board `b`.
- `d`: the shared correction, built from Legendre polynomials P2..P5 only. P0 and P1 are left out,
  so `d` adds no offset or gain over the fitted range, and every board's gain/offset stays in its
  own `g_b`, `o_b`.

The fit is a joint least-squares fit over both boards' rungs. The curve spans −8.3 to +4.8 mV at
the pin. There is no data outside the fitted 570–2658 mV, so the firmware fades the edge value to
zero over 261 mV, and an unmeasured range reads as it did before the correction.

To check that the curve transfers, the test fits it on one board only and applies it to the other. That board
gets only a gain and offset from two rungs, at 25 V and 65 V, as a production calibration would:

![After correction](img/esp32-adc-after.webp)

| Board | Line only (rms / max) | Other board's curve + 2-point cal (rms / max) |
|---|---|---|
| fmetal | 96 / 211 mV | **38 / 97 mV** |
| fboost | 102 / 212 mV | **45 / 173 mV** |

fboost's worst points sit at its lowest rungs, where fmetal's curve has the fewest supporting
points. Fitting the curve on both boards, which is what the firmware ships, removes most of that.

## Integer truncation in the old firmware path

Before this change, the ADC1 driver averaged 32 raw codes with integer division and converted
the result with `adc_cali_raw_to_voltage()`, which only accepts an integer code. Flooring drops
0.37 mV at the pin, or ~10 mV input-referred, and adds a staircase of one code (~21 mV
input-referred). The firmware now builds a 65-knot float table of the IDF conversion at start-up
and interpolates the fractional average. IDF's own integer arithmetic stays in; a simulation puts
its effect at about −1.2 mV, nearly constant, which a board's offset absorbs.

The fit uses readings taken with the old path, shifted by the +0.37 mV the new path adds. The
shift moves the curve by less than 0.05 mV and matters only for the per-board offsets (~14 mV).

## Firmware

Branch `esp32-adc-inl` of fugu-mppt-firmware (commits `582cf8a`, `83d3fa2`). Nothing is
merged or flashed yet.

- `src/adc/adc_esp32_cont.cpp`:
  - `buildMvTable()` and `rawToMv()`: the fractional conversion.
  - `inlDelta()`: the six coefficients, scaled to `x = (mV − 1614) / 1044` so float32 stays exact,
    then a Horner loop of five multiply-adds and the taper.
- `sensor.conf`:
  - `esp32adc1_inl` (default `0`): applies the correction at 12 dB on ESP32-S3, to every ADC1
    channel.
  - `<vin|vout>_gain` / `_offset`: per-board, as `V = gain · V_div + offset`.

Cost: about 0.5 kB of code and 260 B of RAM. The table build runs once (~4k IDF calls) and
is skipped when `resetPeripherals()` re-enters `start()`. Per sample, the new path is cheaper
than the IDF call it replaces.

The correction is opt-in because turning it on shifts a deployed board's reading by up to ±0.23 V.
A boost regulating its output at 54 V, for example, would end up 0.12 V higher. Turn it on only
together with that board's gain and offset.

### Calibrate a board

To calibrate a board:

1. Set `esp32adc1_inl=1` and run the new firmware.
2. Hold the node at two voltages, about 25 V and 65 V, against a trusted reference. Two rungs
   of a plan like `ina228-u-4ref-dense` are enough.
3. Fit `gain` and `offset` from the two points and write `vout_gain` / `vout_offset`.

The following values come from these runs, which used the old firmware path. Use them as a starting
point and re-measure on the new firmware before trusting them.

| Board | `vout_gain` | `vout_offset` |
|---|---|---|
| fboost | 0.973991 | +0.680 V |
| fmetal | 0.967109 | +1.182 V |

## Limits and open questions

- Only two chips, both measured the same way: each board has its own 200k/7.5k divider into ch3.
  With the same channel and the same divider values on both, the data cannot yet tell an ADC
  property apart from a source-impedance effect, or from two chips that happen to match. A third
  board, ideally on another channel or with different divider values, would settle it.
- Range: 16.5–74.5 V, that is, 570–2658 mV at the pin, with a single rung above 73 V. Below and
  above that range, the correction fades out; nothing there was measured.
- Other channels: the correction applies to NTC and to current channels on ADC1 as well.
  For NTC that is a 0.06–0.4 K shift (estimate, unmeasured). For current channels it is untested.
- The ~35 mV floor is repeatable per operating point. Removing it would take a correction
  indexed by operating point instead of voltage.
- fboost's float16 telemetry quantizes at 31 mV between 32 and 64 V. With medians over
  30–60 readings per rung this adds a bias of at most half a step: small next to the floor, but
  not zero.

## Reproduce

```sh
# in pwr-metering (needs its influx access): per-rung data -> CSV
.venv/bin/python esp32-adc-extract.py ~/dev/ee/hw/Fugu2/doc/esp32-adc/data
# in Fugu2: figures, numbers and firmware coefficients, from the CSVs only
python3 doc/esp32-adc/plots.py
```

`plots.py` reads only the CSVs and prints the coefficients that go into `inlDelta()`.
