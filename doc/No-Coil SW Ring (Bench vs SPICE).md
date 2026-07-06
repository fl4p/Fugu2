# No-Coil SW-Node Ring — Bench vs SPICE

Investigation of the half-bridge switch-node (SW) waveform during a **coil-disconnected
bench test**, and the reconciliation of an over-predicting LTspice model against the scope.
The short version: **the real board is benign** (small overshoot, no avalanche); the sim
over-predicted for three separable reasons, the biggest of which was a **test-deck setup
error (missing input decoupling)**, not device physics.

## Bench measurements (Rohde&Schwarz, RT-ZP11 passive probe)

| Config | Vin | SW peak | Overshoot | Rise | Ring | Avalanche? |
|---|---|---|---|---|---|---|
| No coil, no snubber | 60 V | **74 V** (max 74.1, mean 66.6) | ~1.23× | 15.8 ns | ~55–65 MHz, ~4 cyc | **No** |
| Coil + load (Vout 9 V, Iout 2.6 A) | 20 V | **24 V** (max 24.1, mean 22.1) | ~1.2× | 15.3 ns | **~37 MHz** (Coss loop, scales w/ Vin) | **No** |

Key cross-checks from having two operating points:

- **Overshoot ratio is ~1.2× in both** (60 V→74 V and 20 V→24 V). A steep-low-V-Coss
  device would blow up the *20 V* case (ratio grows as Vin drops); it doesn't. → the real
  Coss(V) is **gentle** (StrongIRFET is planar-trench, not superjunction).
- **The ~60 MHz ring is the local Coss commutation ring — present with *and* without the coil.**
  The loaded (coil-connected) ring **scales with bias** exactly as a Coss tank must:
  **37.0 / 53.8 / 58.5 MHz at 20 / 40 / 60 V** (Fab on-scope periods 27 / 18.6 / 17.1 ns),
  matching **f ∝ 1/√Coss(V)** (bench ratios f₂₀/f₆₀ = 0.63, f₄₀/f₆₀ = 0.92 vs predicted 0.64 / 0.89).
  Solving the tank at 60 V (58.5 MHz, ~800 pF) gives **L ≈ 9.3 nH = the same commutation loop as
  no-coil**, and **loaded-60 V (58.5 MHz) ≈ no-coil-60 V (60 MHz)** → the output coil does **not**
  touch the ring. **Correction history (reversed twice, now stable):** an intermediate draft claimed
  the loaded ring was a *voltage-independent ~18–19 MHz coil self-resonance* (a different loop) —
  that was **bad on-scope cursor reads, ~2× too low**, since retracted: `codex-ee-ring`'s pixel reads
  flagged the scaling, and Fab re-measured 20 V = 27 ns = **37 MHz**. The `--coil-cw` winding-cap SRF
  model built for it is reverted. So the original "present with and without the coil" reading stands,
  now backed by the full 1/√Coss scaling. **(My own earlier pixel read of the 20 V shot as ~20 MHz
  was also wrong — the humps are ~27 ns apart, ~37 MHz.)** Peak/no-avalanche is coil-independent
  regardless (loaded peaks reconcile via Coss: ~25 V@20 V / ~54 V@40 V / 74 V@60 V = the no-coil 74 V).
- **No flat clamp plateau** at 80–85 V in either capture → no avalanche.
- Two grounding methods (GND-croc and "no probe clips") agreed at 72–74 V → the peak is
  real, not a probe-attenuation artifact.

Devices: LS `IPP024N08NF2S`, HS `2× IPP055N08NF2S` (StrongIRFET 80 V), Rg = 15 Ω, no gate
discharge diode.

## What the sim first said, and why it was wrong

The first LTspice model (Infineon `_L0` vendor models, no-coil deck) predicted a **105 V
natural / 85 V-clamped** SW overshoot and concluded the OFF LS FET went into **repetitive
avalanche** (the `_L0` body-diode `Dbd` breaks down at BV = 85 V). That conclusion was
**wrong** — falsified by the scope. It failed for three independent reasons, found in order:

### 1. Missing input decoupling (Cin) — the dominant error, a deck-setup bug

The no-coil driver built the deck with **no input capacitor** (`cin_text=None`, `Cbulk=0`).
The trap: "no coil, no load" strips the *output* side, but **Cin is on the input side and
is always physically present** on the board. Without it, the commutation loop can only close
through the 200 nH input feed (`Lfeed`), which fabricates a **spurious ~11 MHz resonance
that replaces the real ~60 MHz Coss ring** and badly inflates the SW peak.

Fix / proof: add a Cin bypass at the leg and the ring jumps into place:

| Cin at leg | SW peak | ring |
|---|---|---|
| **none** (the bug) | 104.9 V | **11 MHz** |
| 100 nF | 62.5 V | **71 MHz** (≈ scope 60 MHz) |

This alone explains the 12-vs-60 MHz "mystery" and most of the peak error. It is **not** a
device-Coss shape error and **not** an extractor bug — the extractor emits a full Cin
network (`--emit-cin-network`); the driver just didn't consume one. The `no_coil` mode in
`dcdc-tools/loss/lib/deck.py` now **warns** when built with no Cin.

### 2. Vendor `_L0` behavioral Miller network — ~+18 V

In the **no-Cin regime** the `_L0` model over-states the overshoot further. A **clean
home-built model** built from dslib scalars + datasheet physics (gm channel +
nonlinear-junction Coss + physical gate-charge caps + body diode, **without** the vendor's
behavioral `Maux/Eaux/Cox` Miller network) gives a natural peak of **86.8 V vs the vendor's
105 V** — so that behavioral stack adds ~+18 V. **But this delta is a no-Cin artifact:** with
proper input decoupling the two models converge (vendor 62.9 V vs homebrew 62.2 V) — once Cin
suppresses the (spurious) large overshoot, the aux network's contribution is negligible. So
the vendor-aux +18 V only mattered on the wrong (no-Cin) deck. The home-built model still
earns its keep independently on transparency and as a vendor-free `--device-model`
candidate. **Rise-time is NOT validated**, though: on the canonical (real-bank) deck the
home-built edge is **~21 ns** and the vendor `_L0` **~7.8 ns** vs the scope's 15.8 ns —
neither reproduces it, and they bracket rather than match. (The two differ because `_L0`
carries the behavioral aux-Miller network and the home-built uses a fixed Cgd; and the
edge detector itself is fragile against deadtime Coss-divider drift. An earlier "16.6 ns"
figure did not reproduce on the accepted deck and is retracted.) The 700 MHz-bandwidth
probe (≈0.5 ns rise limit) captures the real 15.8 ns edge faithfully, so this is a genuine
model gap, not measurement smearing.

### 3. The over-ring is edge-limited, not a "missing ~2.5 Ω Coss loss" (reframed)

An earlier draft said the clean model rings under-damped and attributed the gap to a **~2.5 Ω
device Coss loss** modeled in the Coss branch. The `dcdc-tools` loaded-sw-ring **damping budget**
shows that is **not physical** — the 2.5 Ω is ~10× any real loop resistance:

- Tank characteristic impedance **Z₀ = √(L/C) ≈ 3.4 Ω** (9.2 nH / 800 pF).
- The observed **~4-cycle decay needs only ζ ≈ 0.04 → ~0.27 Ω** effective series R — *not* 2.5 Ω.
- The physical R budget is ~10× below even that: FastHenry copper **17 mΩ** + **frequency-resolved
  MLCC ESR ~6–12 mΩ** (the SRF-floor under-counted 2–12×; now extracted via ngspice AC from the
  vendor cap models in `loss/lib/params.py`) ≈ **~25 mΩ**. Radiation is µΩ; core loss is N/A (coil out).
- **Coss hysteresis is a *superjunction* effect** — small for this 80 V **trench** part (IPP024). So
  the earlier "lossy-Coss / hysteresis" attribution is **retracted**.
- **The modest first overshoot is the FINITE EDGE, not damping.** The 15.8 ns rise ≈ **one ring
  period** at 60 MHz, so the edge only *weakly excites* the tank. The sim over-rings (undamped ~140 V
  with the correct small Cgd) largely because it does **not reproduce the 15.8 ns edge** (rise-time
  gap → `dcdc-tools` issue #1); a too-fast sim edge over-excites the ring.

**So `Rcoss ~2 Ω` is a peak-calibration knob (~10× physical loop R), not a device Coss-loss term** —
don't cite it as physics. This also resolves the earlier **peak-vs-decay tension**: the peak is
*edge*-controlled, not damping-controlled, so forcing the peak with a series R necessarily over-damped
the decay. With the correct edge, **light damping (~0.27 Ω) matches the decay and the peak falls out**.
A small residual remains (0.27 Ω is still ~10× the ~25 mΩ budget), but it is an order of magnitude
smaller mystery than the retracted 2.5 Ω, and largely moot once the edge is right.

## Refinement: the exact peak is a bracket; the real Cin bank closes it

The *missing-Cin frequency artifact* is settled (missing Cin → 11 MHz; add Cin → the real
~60 MHz-regime ring). The *exact* ring frequency / loop-L split is a separate, still-open
question (see "Frequency" below). The *exact peak* is bracketed, not yet pinned:

- **Lower bound ~62 V** — an *ideal* local input cap (`Cbulk vi 0`, zero ESL) strongly
  decouples and collapses the overshoot to ~62 V (just above the 60 V rail). Vendor `_L0`
  and the home-built model agree here (62.9 V vs 62.2 V), so this bound is model-independent.
- **Upper bound ~105–107 V** — the no-Cin / decoupling-defeated case.
- **Real board 74 V** sits between the two.

An attempt to interpolate by giving a *single* Cin an ESL **failed as a deck/topology bug,
not physics**: a sweep of Cin ESL from 50 pH to 1 nH pinned the peak flat at ~107 V —
i.e. right back at the no-Cin value. The tell (ee-review): 50 pH is 0.02 Ω at 60 MHz and
*cannot* defeat decoupling, and a flat result across a 20× ESL range is not an inductance
effect. What actually happened is the single-branch `cin_text`/`Vs_cin` path was **not
decoupling the commutation node at all** — the loop stayed on the 200 nH `Lfeed`, exactly
as in the no-Cin deck (hence 107 V ≈ 105 V). So that experiment is inconclusive about the
peak; only the two clean brackets above are trustworthy.

Closing the bracket to the measured 74 V needs the **validated `out_cinnet` cin_network**
(9-cap bank, per-cap Lb/ESL/ESR — ceramics ∥ bulk) assembled and wired to the commutation
node by the loss tool's cin-consumer path.

**Acceptance test — peak/avalanche PASS.** With the real assembled 9-cap bank wired to the
commutation node, the canonical no-coil sim at Vin = 60 V gives **peak 72.4 V (vendor `_L0`,
−2 %) / 78.0 V (home-built, +5 %) vs the scope's 74 V**, and **no avalanche** (BV = 85 gives
the same peak as BV = 200, so it never reaches the clamp; Dbd stays off). The scope sits
*between* the two models — a **~5.6 V (~7 %) model spread**, so the peak is *primarily* but
**not exclusively** Cin-limited (it is NOT a clean model "convergence"). The full parallel
bank reproduces the ~74 V overshoot that a single cap could not (it was binary 62 / 107 V).
A separate loss-budget
concern — the Cin trunk (`cin_L_shared/R_shared`) and
the commutation loop (`L_loop`, `r_hs/r_ls`) are **largely the same copper** (7.67 nH ≈
8.21 nH; 6.28 mΩ ≈ 6.85 mΩ), so a deck that places both in series double-counts the loop —
must be fixed in the cin-consumer contract (deck carries only the residual switch-side
copper, `L_loop − cin_L_shared`).

**Caveat on the peak — composition-sensitive, and the mechanism is *not* "ceramics".** A
bank-toggle test shows the **full 9-cap bank gives the lowest peak (77 V)**, while
ceramics-only (91 V) and bulk-only (82 V) are both *higher* — so the decoupling is set by
the **number of parallel branches (lowest effective decoupling ESL)**, not by ceramics
"catching the fast edge" (an earlier framing, now **retracted**). The peak therefore carries
a **±14 V composition sensitivity** tied to the per-cap ESL/ESR/DC-bias-derate defaults in
the assembled `cin_network` — the 77 V ≈ 74 V match is not a clean mechanism proof at that
tolerance. One tell to chase in Slice 2: **bulk-only decoupling *better* than ceramics-only
is physically backwards** at 50–60 MHz (a 0402 ceramic ~0.5 nH/0.19 Ω should beat a bulk can
~5 nH/1.9 Ω ~10× at HF); that the sim shows the reverse points at the ceramic-branch ESL
being set too high (or bulk too low) in the per-cap defaults — the same knob that sets the
±14 V band.

## Frequency — reconciled at ~60 MHz (three measured corrections), hardware Δf pending

This section was **"open / under-determined"** after a 3-agent adversarial review broke an
earlier "solved at 8.2 nH" claim (that was a degenerate `L·C` fit — 60 MHz only appeared when
the physically-present TO-220 leads were zeroed; with the model's own leads restored it rang
37–40 MHz). It is now **reconciled** by anchoring both L and C to *measurements* rather than
model outputs. `f = 1/2π√(LC)` has a one-parameter family of solutions, so the fix is to pin
L and C **independently** — which the following two anchors do.

**Anchor 1 — Coss from the datasheet, not the SPICE models.** A quasi-static C–V charge sweep
(`coss_cv.py`: device off, constant I into drain, `Coss(V) = I / (dV/dt)`) on both models:

| IPP024N08NF2S | Css@40 V | **Css@60 V** | Css@74 V | chord 60→74 V (ring C) |
|---|---|---|---|---|
| vendor `_L0` | 1259 pF | **960 pF** | 835 pF | 893 pF |
| home-built | 1001 pF | **907 pF** | 864 pF | 883 pF |
| **datasheet** | 1000 pF | **~800 pF** | — | ~780 pF |

Both models run **~15–20 % high** on Coss at 60 V vs the datasheet. Corrected to the
datasheet, the ring C (chord over the real 60→74 V swing) is **~780–800 pF** — *not* the
~470 pF once speculated, and *not* the models' ~890 pF. (HS Coss is confirmed **shunted**
during the HS-on ring — its channel mΩ shorts its Coss — so the ring C is LS-side only.)

*Curve-fit close (no scale fudge).* Rather than scaling the whole model down, the home-built
Coss/Cgd were **re-fit to the datasheet Diagram-11 curve** (`coss_fit.py` → behavioral charge
capacitors, with `Qoss=105 nC` / `Qgd=19 nC` as integral constraints). C–V re-verify:
**815 pF@60 V (ds 800), 727@74 V (ds 748)** — within ~3 % of the datasheet across 40–80 V. On
that curve-fit model the ring lands at **60 MHz @ 9.2 nH with no `coss_scale`** — so the
reconciliation is not an artifact of the earlier 0.85 scaling. This also surfaced a genuine
model bug: the old build held **`Cgd = Qgd/40 = 475 pF` constant**, but the real Crss collapses
to ~37 pF by 60 V — so the old model carried ~440 pF of **phantom Cgd** at the ring bias, which
was silently **loading/damping the ring** (see the peak note below). Lesson: a charge-averaged
*constant* Cgd secretly damps a ring and can fake a peak match — use a voltage-dependent Cgd.

**Anchor 2 — the source lead is a *measured* package floor, not a tunable stub.** Aikawa et
al., *"Measurement of the Common Source Inductance of Typical Switching Device Packages"*
(IFEEC 2017, DOI 10.1109/IFEEC.2017.7992207) measured TO-220 **common-source inductance**
(pad-to-die) directly: **3.9–5.7 nH**, *decreasing* with current rating because higher-current
dies carry more parallel source bond wires (FDP120N10, 74 A, 3 bonds → **3.9 nH**). ~⅓ of the
CSI is the bond wire, ~⅔ the fixed leadframe+lead. Our LS `IPP024N08NF2S` is a very-high-current
80 V StrongIRFET → the **low end, ~4 nH** (matches this repo's own
[EMI Parasitics Snubbers](<EMI Parasitics Snubbers.md>) note, *"TO-220: 4 nH common source
inductance"*). This is a **package floor** — irreducible by lead trimming or mount. The earlier
"leads over-estimated, real 2.5 mm leads → higher f" hypothesis is **falsified** by this
measurement: the ~4 nH is internal bond-wire + leadframe, not exposed lead.

**Mount note (horizontal bottom-heatsink, our footprint `TO-220-3_Horizontal_*`).** The SPICE
model's `Lg/Ld/Ls` are *internal* package parasitics — mount-independent; the model doesn't
"assume" vertical vs horizontal. What the mount changes lives on the **board side**: horizontal
mount solders the drain tab flat to the SW-node copper pour (drain lead ≈ **1 nH**, part of the
plane — not a ~2.5 nH vertical stub) and runs the bent leads close to the return plane
(image-plane lowers loop L). So horizontal mount *helps* the drain/external term, but cannot
touch the ~4 nH source-CSI floor.

**The reconciliation (transient, datasheet-curve-fit Coss, no scale fudge):**

| ring-loop L composition | Ltot | ring |
|---|---|---|
| **4 nH board copper + ~1 nH drain + ~4 nH source CSI** | **9.2 nH** | **60 MHz** ✓ |
| 4 nH board + ~6.5 nH leads | 10.7 nH | 55 MHz (low edge) |
| 8.2 nH `out_cinnet` + ~5 nH leads | 13.2 nH | 50 MHz |
| 8.2 nH `out_cinnet` + ~6.5 nH leads | 14.7 nH | 48 MHz |

*(Both the scaled and the curve-fit model give this same frequency column; the peak is a
separate damping story — see below.)*

With the datasheet ~800 pF, the scope's 55–65 MHz demands a **total ring-loop L ≈ 7.5–10.5 nH**,
which decomposes physically as **~4 nH board copper + ~1 nH drain tab + ~4 nH source CSI ≈
9.2 nH → 60 MHz**, peak unchanged. The frequency gap was **three compounding errors, none of
them "lead length"**: (1) **board-copper L too high** — the 8.2 nH `out_cinnet` `L_loop` is
~2× the **4.2 nH golden** PCB-copper figure from the bespoke DPT solver, and is flagged from a
*non-authoritative* board revision; it is the single biggest contributor to the 45 MHz
under-prediction; (2) **Coss ~15–20 % high** in both models vs the datasheet 800 pF; (3) the
earlier "leads zeroed → 60 MHz" was a degenerate fit that happened to compensate (1).

**Still to confirm (turns "reconciled" into "measured"):**
1. **Hardware external-cap Δf test** — drop a known C0G (~470 pF) on SW and re-scope; the
   frequency shift pins L and C non-circularly on the real board. This is the clean check that
   the ~9.2 nH / ~800 pF split above is the real one and not another compensating pair.
2. **Board-copper re-extraction** on the *authoritative* `Fugu2.kicad_pcb` — expect the ring
   loop copper near the ~4 nH golden, not 8.2 nH. If the re-extraction confirms ~4 nH, the
   reconciliation closes without needing the Δf test; if it lands near 8.2 nH, the Δf test
   arbitrates.

**Peak is an EDGE story, not a ring-C or a damping story (phantom-Cgd + reframe).** With the
*correct* voltage-dependent Cgd (small at the 60–74 V ring bias), the curve-fit model rings
*undamped* to ~140 V at 9.2 nH — the old ~78 V was landing near the scope's 74 V only because
the phantom 475 pF constant Cgd was supplying ~2.5 Ω-equivalent damping. A `Rcoss` series R in
the Coss branch pulls it back (Rcoss 0 → 140 V, 1.5 Ω → 92 V, **2.5 Ω → 78 V**, 4 Ω → 70 V, all
~56–60 MHz) — **but ~2.5 Ω is a calibration knob, ~10× any physical loop R, not a real loss term**
(see §3). The physical reason the *real* board's first overshoot is modest is the **finite 15.8 ns
edge (≈ one ring period)**, which only weakly excites the tank; the sim over-rings mostly because
it doesn't reproduce that edge (rise-time gap, `dcdc-tools` issue #1), not because it's missing
2.5 Ω. This **dissolves** the earlier peak-vs-decay tension: the peak is *edge*-controlled and the
~4-cycle decay needs only ~0.27 Ω, so there's no single-R contradiction once the edge is right —
Rcoss was standing in for the missing edge. The peak also carries the Cin-bank decoupling
composition sensitivity (below), independent of the ring L/C.

**What survives regardless (the safety verdict).** The benign / no-avalanche conclusion is
**independent of the ring-L/C identity** — the peak lives on the lower-Q Cin-bank decoupling
loop, and no lead/Coss/damping treatment in this study pushes the real board into avalanche.
The frequency reconciliation does **not** reopen (nor was it needed for) that conclusion.

## What was falsified along the way (don't re-litigate)

- **Qrr / reverse recovery** — TT = 0 changed the peak by 0.0 V (no freewheel current to
  forward-bias the body diodes in the no-coil case).
- **L_loop magnitude** — peak flat across L_loop 4→20 nH. This was itself a missing-Cin
  artifact: with `Lfeed` = 200 nH dominating, the total loop was ~204–220 nH, so sweeping
  board L 4→20 nH was only ±4% → of course flat. The earlier reading of this as an
  "L-independent nonlinear-Coss energy limit / parametric pumping / no-safe-Vin" is
  **retracted** along with the avalanche. On the corrected Cin-present deck, L_loop is
  load-bearing again for the ring frequency — now **reconciled** at a total ring loop of
  ~9.2 nH (~4 nH board copper + ~1 nH drain + ~4 nH measured source CSI) against a datasheet
  ~800 pF Coss → ~60 MHz (see "Frequency" above); the 8.2 nH `out_cinnet` figure is the
  outlier to re-check, and the hardware Δf test is the final confirmation.
- **Coss magnitude** — scaling it *down* raised the peak; model Coss ≈ datasheet anyway.
- **Skin effect as the damper** — real skin-corrected copper is 17 mΩ (+ freq-resolved MLCC
  ESR ~6–12 mΩ ≈ 25 mΩ total), nowhere near the ~2.5 Ω once assumed — and the ~4-cycle decay
  needs only ~0.27 Ω anyway; the over-ring is edge-limited, not under-damped (see §3).
- **Timestep** — the 105 V and 11 MHz were converged (12.8 ns → 0.1 ns), i.e. a *real*
  feature of the (wrong) deck, which is exactly why convergence ≠ correctness.

## Lessons

- **Robustness ≠ accuracy.** The wrong result was timestep-converged and insensitive to
  L_loop, Coss magnitude, gate-L, and Qrr — a fully self-consistent model of the wrong
  circuit. Only the hardware settled it. Validate the dominant physics against an
  independent measurement *before* the sweep matrix.
- **A no-coil / no-load test still needs the input Cin.** It's the easiest decoupling to
  forget and it fabricates a low-frequency resonance that masquerades as the real ring.
- **Distributed HF ring damping is a device/Coss loss, not loop copper** — put it in the
  right circuit element or it double-counts.
- **Get the scope shot early**, and take two grounding methods / two operating points — the
  20 V loaded point is what proved the Coss(V) is gentle.
- **A frequency match can be a degenerate L·C fit.** "60 MHz reproduced at 8.2 nH" looked
  like a pin but only held because physically-present device leads were zeroed; restoring
  them gave 37–40 MHz. `f = 1/2π√(LC)` has a one-parameter family of (L,C) solutions — you
  cannot claim a loop-L from a frequency match alone. Separate L and C **non-circularly**
  (external-cap Δf on the bench, or a lead-inclusive geometric extraction) before pinning.
- **A large-swing resonant ring uses the charge-effective Coss over the *actual* swing**, not
  the small-signal value at one bias — and for a high-bias ring, not the 0→V charge-effective
  either (that over-weights the low-V high-C region). Use the chord over the real swing.
- **Check the probe bandwidth before trusting (or doubting) a fast feature.** The 700 MHz
  probe (~0.5 ns rise) confirmed the 15.8 ns edge and 60 MHz ring are real, not band-limited.

## Verdict

At 60 V no-coil the real board rings to ~74 V with a well-damped **~60 MHz local-Coss ring**;
in normal loaded operation it rings to ~24 V (20 V) with the **same Coss commutation ring, scaling
with bias** (~37 / 54 / 58.5 MHz at 20 / 40 / 60 V — the coil doesn't touch it). It **does not
avalanche** in either case. The sim's avalanche prediction was an
artifact of (1) a missing input capacitor, (2) the vendor model's behavioral Miller network,
and (3) a too-fast simulated edge over-exciting the ring (the ~2.5 Ω "Coss-loss damping" was a
peak-calibration knob, not physics — see §3) — none of them a real board hazard.

---

*Tooling: `dcdc-tools/loss` `no_coil` deck mode (`DeckOpts.no_coil`, with the missing-Cin
guard), `plot_sw_ids.py`, and the home-built dslib model. Validated Fugu2 parasitics:
`out_cinnet/parasitics.json` (L_loop 8.21 nH, r_hs 2.43 / r_ls 4.42 mΩ, full cin_branches).
Copper R(f) skin-corrected ~17 mΩ (nwinc=3). See also
[Half Bridge Simulation (SPICE)](<Half Brdige Simulation (SPICE).md>),
[EMI Parasitics Snubbers](<EMI Parasitics Snubbers.md>), [SW Phases](<SW Phases.md>).*
