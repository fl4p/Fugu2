# PV input bank — what is actually on it, and a retracted measurement spec

2026-10-12. This file began as a bench spec for an unpowered J10 impedance measurement.
**That spec is retracted (§4)** after an independent Codex review
(`~/codex-reviews/j10/review.log`, 8 findings, report at line 6972). What survives, and
the reason the file is kept, is a set of **corrected facts about the board** that nothing
else in either repo records — including an RC snubber that is already fitted.

For the measurement itself use **`dcdc-tools/emc/BENCH-j10-dm-voltage.md`** (commit
`97be9a2`, on dcdc-tools `main`): the powered J10 DM voltage spectrum, which tests the two
radiated models' own published values (56.7–58.1 vs 80–86 dBµV, ~25 dB apart).

---

## 1. The real PV input bank

Taken from the **PCB netlist** (`Fugu2.kicad_pcb`), which is authoritative — not from the
schematic value fields, which mislead in three separate ways.

**On `Solar+` / `BuckGND` (the actual input bank):**

| part | value | type |
|---|---|---|
| C11, C12, C34 | 1000 µF, 100 V, Chemi-Con `EKZN101ELL102MM40S` | electrolytic, **3000 µF** |
| C21, C22 | 10 µF, 1210 `GRM32EC72A106KE05L` | MLCC, 20 µF |
| C9, C16, C27 | 1 µF, 0805 `HMK212BC7105KGHTE` | MLCC, 3 µF |
| C17, C18 | 220 nF, 0603 `HMK107C7224KAHTE` | MLCC, 0.44 µF |
| | | **MLCC total 23.44 µF** |

**Three parts that look like input capacitors and are not:**

| part | actual net | what it really is |
|---|---|---|
| **C8** (2.2 nF) | `Net-(C8-Pad1)` ↔ `BuckGND` | **snubber capacitor** — see §2 |
| **C10** (1000 µF) | `BflowS` ↔ `BuckGND` | **output** reservoir, behind the inductor |
| **C14** (1 µF) | `BuckGND` ↔ `Net-(C14-Pad2)` | heatsink-coupling node, not across the input |

**And one series element in the measurement path:**

| part | net | consequence |
|---|---|---|
| **F3** | `T_HV+` ↔ `Solar+` | A **fuse sits between J10 and the bank.** Anything injected or measured at J10 sees F3 in series. A 0 V reading at J10 does not prove the bank behind an open F3 is discharged. |

An earlier revision of this file listed C8, C10 and C14 in the input bank and gave
4000 µF / 24.44 µF. Both figures were wrong. **Do not read the schematic `MPN` field as a
population flag** either — C11/C12/C34 carry `MPN = DNP` with the KiCad `dnp` flag clear
and a description reading "hand-assembled"; they **are** fitted.

---

## 2. The snubber footprint across SW is NOT populated

```
SW ── R11 (7.5 Ω) ── C8 (2.2 nF) ── BuckGND      ← footprint only, not fitted
```

> **⚠ Retraction, 2026-10-12.** This section first claimed *"there is already an RC snubber
> on this board"*, read off the PCB netlist plus the schematic `dnp` flag. **Both are the
> wrong source for that question.** Fab: *"I think we never used snubbers."*

**The authority is the as-built attestation**, `~/dev/pv/ee/dcdc-tools/loss/examples/ftall.yaml`:

```yaml
board_as_built:
  attested: 2026-08-11        # Fab, from the board. The schematic is stale.
  snubber:
    fitted: false
    other_snubbers: none fitted (no gate snubbers, no diode snubbers)
```

Its header lists three places the schematic is stale, and this is one of them:

| | schematic says | board is |
|---|---|---|
| HS / LS parts | IPA050N10NM5S / IPP022N12NM6 | IPP050N10NF2S ×2 / IPP039N10N5 ×2 |
| R1 (UCC dead time) | 20 kΩ → 185 ns | **33 kΩ → 297 ns** |
| R11 + C8 snubber | `dnp=no`, i.e. fitted | **NOT populated** |

**What each source is good for:**

- the **PCB netlist** is authoritative for *topology* — nets, pads, footprints — and says
  nothing about population. R11/C8 are wired as a snubber; that is all it establishes.
- the schematic **`dnp` flag** is not authoritative for population either. Here it reads
  *fitted* and is wrong. Nor is the `MPN` field (§1: C11/C12/C34 read `MPN = DNP` and
  **are** fitted). The two fields disagree in opposite directions on the same board.
- only the **as-built YAML / `HW Stories`** answer "is it on the board?"

**Consequences:**

- `doc/EMI Precompliance.md`'s "+ LS RC snubber" rows are **genuine additions, not
  re-tunes.** The lever is not double-counted and the baseline stands.
- **The bench data cannot distinguish the two cases.** A fitted 7.5 Ω / 2.2 nF snubber is a
  7.78 Ω equivalent shunt predicting ring **Q ≈ 3.9** against a measured **3.94**.
  `ftall.yaml` records that this near-degeneracy is exactly what made the wrong version
  persuasive the first time — matching the measurement is not evidence here.
- **C8's dielectric question is resolved** should a snubber ever be fitted:
  `C0805C222K2GEC7800` is 200 V **C0G**, per
  `doc/reviews/2026-09-30-schematic/PowerStage.md:18`. The `Value` text saying X7S and the
  description saying *"maybe C0G?"* are both stale. No dc-bias derating applies.
- The only Fugu build where a snubber part appears is the old **Fugu Metal**
  (`HW Stories/Fugu Metal/README.md:41`) — a different power stage (IR2184, TK6R8A08QM),
  not this board.

---

## 3. What survives of the bank analysis

The original premise — that across 30–110 MHz the bank is **past every resonance and
purely inductive** — **holds for the corrected bank**, and it holds *because* C8 turns out
to be a snubber rather than an input capacitor.

Pairwise anti-resonances for the real 20 / 3 / 0.44 µF groups, using
`f = (1/2π)·√((1/C_a + 1/C_b)/(L_a + L_b))` with per-part ESL 2.0 / 1.5 / 1.2 nH:

| branches | anti-resonance |
|---|---:|
| 20 µF / 3 µF | 2.54 MHz |
| 20 µF / 0.44 µF | 6.06 MHz |
| 3 µF / 0.44 µF | 7.75 MHz |

All below 10 MHz. The elco/MLCC anti-resonance sits lower still, 230–712 kHz.

> **Had C8 been an input capacitor it would have changed this.** Treated as a parallel
> branch it puts anti-resonances at **68–78 MHz** — inside the band of interest, and inside
> the 90–110 MHz band's lower skirt. The premise is correct only because the topology is.

Two caveats: identical-value branches contribute no inter-value anti-resonance, and the
bank is not *exactly* asymptotic — apparent L moves ~4 % between 30 and 70 MHz, so any
future "is it flat?" test needs a stated tolerance rather than a yes/no.

---

## 4. RETRACTED — the unpowered impedance method

The earlier §3 of this file specified an unpowered shunt-through sweep at J10 with K36,
a copper-shim short reference, and a 1.73 / 11 nH decision rule. **It is withdrawn.** It
fails on four independent counts:

1. **Wrong observable.** The radiated model defines its J10 equivalent as a **transfer**
   impedance, `V_J10 / I_hot-loop`, with the hot loop and the electrolytic end as distinct
   nodes (`radiated-indep/branch_pv.py` at `97be9a2`). Driving the network *at* J10
   measures the **driving-point** impedance instead. On the model's own values those are
   **0.377 nH vs 4.46 nH** — so a perfect measurement of the nominal case would have landed
   in the "inconclusive" row. The thresholds could not select between the models at all.
   The 1.73 nH figure is also a *maximum* transfer equivalent over the declared grid, not a
   central value.
2. **The instrument option is not installed.** `*OPT?` returns
   `B6, B2415, K36, K510, K520, K530`. **K36 is gain/phase FRA only**; the impedance
   analysis option, which is what provides shunt-through, is **`MXO4-K337`** (order
   `1335.6085.02`, requires B6) and is **absent**. The claim "K36 does impedance analysis,
   so no VNA is needed" came from a distributor listing that conflated the two options.
3. **The board confounds it.** At zero bias the FET Coss is at its *largest*; a screening
   estimate puts the HS/LS series path at ≈2.8–3.6 nF, i.e. **0.6–0.8 Ω at 70 MHz** —
   comparable to the 0.76 Ω being used as the discriminator. Add F3, the inductor winding
   capacitance, D16 and the auxiliary-supply loading. "Non-flat means fixture" was
   unjustified.
4. **The decision rule was not fail-closed.** Leaving the shorting shim installed produces
   a low, flat reading that satisfies "nominal confirmed" — i.e. **making the connection
   worse moves the verdict toward PASS.** There was no known-standard recovery, no
   receiver-floor or phase check, and no explicit `unverified` outcome. A short-reference
   subtraction is also not equivalent to a calibrated measurement: with an illustrative
   50 nH fixture, 1.73 and 11 nH differ by only 18 % of the total.

Nothing here says an unpowered measurement is impossible — a properly calibrated
two-port instrument measuring the **transfer** quantity between defined injection and
observation points could do it. It says this spec did not describe that measurement, and
the hardware to run it is not on the bench.

---

## 5. Open

- ~~Whether the radiated deck's baseline includes R11/C8.~~ **CLOSED 2026-10-12** (§2): no
  snubber is fitted, so the deck's unsnubbed baseline is right and the lever is real.
- ~~C8's dielectric.~~ **CLOSED** (§2): `C0805C222K2GEC7800`, 200 V C0G.
- **Stale schematic fields are a standing hazard, not a closed item** (§2): `dnp` and `MPN`
  disagree in opposite directions on this board. Any claim about what is fitted needs the
  as-built YAML or `HW Stories`, never the `.kicad_sch`.
- Whether the powered plan's read-out can be affected by F3's impedance.
- The powered measurement itself: `dcdc-tools/emc/BENCH-j10-dm-voltage.md`. Note it sweeps
  30–70 MHz, while the worst radiated band is **90–110 MHz**, which neither plan covers.
