# Bench spec — J10 source inductance, **unpowered**: is it 1.73 nH or 11 nH?

Written 2026-10-12. **Companion to `dcdc-tools/emc/BENCH-j10-dm-voltage.md`** (commit
`97be9a2`, on dcdc-tools `main`), which is the authoritative plan for the **powered**
path. This file covers only the **unpowered** path, which that plan lists in one sentence
as "find the input-bank anti-resonance with a VNA (NanoVNA-class)".

**Two corrections to that sentence, which are the reason this file exists:**

1. **The anti-resonance is not the in-band feature** (§2). It sits at 230–712 kHz. Across
   30–70 MHz the bank is past every resonance and purely inductive, so there is nothing to
   back out of a resonance — you read the inductive asymptote directly.
2. **No VNA is needed.** `*OPT?` reports **K36** (frequency *and impedance* analysis, to
   100 MHz) with **B6** as source, both installed. 30–70 MHz is covered by the instrument
   already on the bench.

> **For the powered DM-voltage measurement, use their file, not this one.** It carries the
> verified J10 pinout (pin 1 `BuckGND`, pin 2 `T_HV+`), the Bumblebee differential-probe
> path, the DC-block fallback and the capture/record procedure. Its predicted values
> supersede any quoted here.

---

## 1. The question, and what rides on it

| source | L at J10 | J10 DM per harmonic | 3 m margin, 30–50 / 50–70 / 70–90 / 90–110 MHz |
|---|---:|---:|---|
| nominal — MLCC branch sets J10 | **1.73 nH** | 56.7–58.1 dBµV | −1.7 / +1.0 / +0.0 / +3.8 dB |
| alternative — 11 nH effective transfer | **11 nH** | 80–86 dBµV | **+21.7 / +22.6 / +15.3 / +8.8 dB** |

The **single widest uncertainty in the radiated estimate**: it changes the answer from
"fix it with a snubber" to "this is a design problem". It also decides whether the PV
terminal cap is worth −9.5 dB or ≤1 dB, and whether the heatsink strap is a lever at all
(nominal case only).

The `radiated-indep` model states MLCCs carry **94 %** of the loop current and that it
**cannot reach 11 nH** over the declared grid — so this is expected to confirm the nominal
case. The 11 nH row is retained only because the other deck's PV DM voltage implies it.

### The board's actual bank (from `PowerStage.kicad_sch`, populated parts only)

| branch | parts | total |
|---|---|---:|
| **Electrolytic** | C10, C11, C12, C34 — Chemi-Con `EKZN101ELL102MM40S`, 1000 µF / 100 V, radial, **hand-assembled** | 4000 µF |
| **MLCC** | C21, C22 `GRM32EC72A106KE05L` 10 µF 1210 | 20 µF |
| | C9, C14, C16, C27 `HMK212BC7105KGHTE` 1 µF 0805 | 4 µF |
| | C17, C18 `HMK107C7224KAHTE` 220 nF 0603 | 0.44 µF |
| | C8 `C0805C222K2GEC7800` 2.2 nF | — |
| | **MLCC nominal total** | **≈24.4 µF** |

⚠ The 1000 µF parts carry `MPN = DNP` in the schematic but their KiCad `dnp` flag is
**not** set and the description reads "hand-assembled" — they **are** fitted, just not
machine-placed. Reading that field literally models the board without its entire
electrolytic branch.

---

## 2. ⚠ Correction: the "anti-resonance" is not the discriminator

The plan as named says *"the J10 DM voltage spectrum, or the **bank anti-resonance**."*
The anti-resonance between the inductive electrolytic branch and the capacitive MLCC
branch sits at:

| L_elco | C_mlcc 10 µF | C_mlcc 24 µF |
|---|---:|---:|
| 5 nH | 712 kHz | 459 kHz |
| 10 nH | 503 kHz | 325 kHz |
| 20 nH | 356 kHz | 230 kHz |

**230–712 kHz — two orders of magnitude below the band in dispute.** And every MLCC in
the bank self-resonates far below 30 MHz:

| part | SRF (incl. mounting L) |
|---|---:|
| GRM32 1210 10 µF | ~1.1 MHz |
| HMK212 0805 1 µF | ~4.1 MHz |
| HMK107 0603 220 nF | ~9.8 MHz |

> **So across 30–70 MHz the bank is past every resonance and is purely inductive.**
> There is no peak to hunt for. The discriminator is the **inductive asymptote**, and it
> is a clean 6.4× in impedance, flat in ratio across the whole band.

One useful consequence: in the inductive region capacitance is irrelevant, so **DC bias
derating does not matter** and the measurement can be made **unpowered**.

---

## 3. Method A (primary) — unpowered impedance at J10

### Why this is possible now

`*OPT?` on the instrument returns **`B6, B2415, K36, …`**:

- **B6** — built-in 2-channel arbitrary waveform generator, **sine to 100 MHz**.
- **K36** — frequency **and impedance** response analysis, **range up to 100 MHz**, source
  = internal generator.

That covers 30–70 MHz with margin, on the instrument already on the bench. **No VNA, no
NanoVNA, no live board.** *(Confirm the installed K36 variant's top frequency in the FRA
setup dialog before trusting the span — the 100 MHz figure is the published option spec.)*

### Setup

- **Board unpowered and fully discharged.** Verify 0 V across the bank before connecting.
- **Shunt-through (2-port) topology**, not series-through: the DUT is well under 1 Ω in
  this band, which is exactly where shunt-through is the right method.
- Connect **at J10's own pads**, with the shortest achievable loop. Everything you add
  here is measured as part of the DUT.
- Sweep **100 kHz – 100 MHz**, log, with enough points below 1 MHz to catch the
  anti-resonance for the record (it is not the discriminator but it characterises the
  elco branch and is worth capturing once).
- **Fit a common-mode choke** on the source cable, or expect the ground-loop error that
  dominates sub-ohm shunt-through measurements.

### The fixture is the hard part — take a short reference

You are measuring ~1.7 nH with a fixture that is itself several nH. Do **not** report an
absolute inductance from a raw sweep. Instead:

1. Sweep with a **copper shim shorting the same two pads** → `Z_short(f)`.
2. Sweep the board → `Z_dut(f)`.
3. The answer is in the **difference**, and in whether `Z_dut` sits near `Z_short` or
   several times above it.

This is why the measurement works despite a crude fixture: **the question is not "what is
L exactly" but "is it 1.73 or 11"**, and those differ by 9.3 nH.

### Read-out: |Z| = 2πfL

| f | 1.73 nH | 11 nH | ratio |
|---:|---:|---:|---:|
| 10 MHz | 0.109 Ω | 0.691 Ω | 6.4× |
| 30 MHz | **0.326 Ω** | **2.073 Ω** | 6.4× |
| 50 MHz | 0.543 Ω | 3.456 Ω | 6.4× |
| 70 MHz | **0.761 Ω** | **4.838 Ω** | 6.4× |
| 100 MHz | 1.087 Ω | 6.912 Ω | 6.4× |

Equivalently, extract `L = |Z| / (2πf)` across 30–70 MHz and check it is **flat** — if it
is not flat, you are looking at fixture resonance, not the bank.

### Decision rule

| observed L (fixture-corrected, flat over 30–70 MHz) | conclusion |
|---|---|
| **≤ ~3 nH** | Nominal case confirmed. The 11 nH row is retired. Snubber is the lever; terminal cap is worth ~1 dB and can be dropped. |
| **≥ ~8 nH** | The 11 nH alternative is real. The board is +9…+23 dB over and this becomes a design problem, not a snubber problem. Re-open the input-bank layout. |
| **3–8 nH, or not flat** | Inconclusive. Fixture-limited — improve the connection and repeat before concluding anything. **Do not split the difference.** |

The middle row exists deliberately: an unevaluable measurement must not read as a pass.

---

## 4. The powered confirmation — use the other plan

Do not duplicate it here. `dcdc-tools/emc/BENCH-j10-dm-voltage.md` is the authoritative
powered-path plan: J10 DM voltage, 30–70 MHz, Bumblebee differential probe (CMRR >40 dB
measured; **check its bandwidth reaches 70 MHz** before relying on it), with a DC-block +
20 dB attenuator fallback, and its own read-out table (≈55–62 dBµV nominal, ≈78–88 dBµV
for 11 nH, anything else = neither model).

Method A here is safer, needs no live board and no probe-bandwidth check, so **do it
first**; their powered measurement then confirms it against the quantity the models
actually argue about.

## 5. What it settles

- Which radiated margin set is the live one (straddling vs +9…+23 dB).
- Whether the PV terminal cap is worth buying an answer to — the open "does a terminal cap
  count as a filter on the device?" question is **nominally worth only −1.0 dB**, so
  confirming the nominal case likely retires that question entirely.
- Whether the heatsink strap is a −14.6 dB lever or a −0.9 dB one.
- Whether the snubber alone reaches a pass, which is the difference between a two-part fix
  and a respin.

---

## 6. Open / caveats

- **Confirm K36's installed top frequency** in the FRA dialog. The 100 MHz figure is the
  published option spec, not an instrument reading.
- The 1.73 nH figure is the **largest J10 equivalent over the declared grid** in the
  `radiated-indep` model, not a typical value — so a measured result modestly above it is
  not automatically the 11 nH case.
- Electrolytic ESL here is a guess (5–20 nH assumed for the sub-MHz table). The
  hand-assembled radial lead length is unmeasured and could be well above datasheet ESL.
  It does not affect the 30–70 MHz discriminator, which is MLCC-branch dominated.
- MLCC SRFs above assume ~1.2–2 nH of combined part and mounting inductance; they are
  order-of-magnitude anchors for "where does inductive behaviour start", not measurements.
- Results belong in `radiated-indep/RESULTS-radiated-indep.md` §10 item 1, per the companion
  plan's record section.
- Both radiated decks currently have **no live owner** (`EMI Precompliance.md`,
  2026-10-12), so whoever runs this should expect to interpret it themselves.
