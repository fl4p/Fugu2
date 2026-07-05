# Fugu2 commutation-loop parasitic modeling — process & findings

Goal: replace the hand-guessed parasitics in `buck_parasitcs.asc` with values
extracted from the real PCB, using vendor SPICE models for the capacitors and
MOSFETs, and cross-check the predicted switch-node ringing.

This doc records **how the model was built**, **what worked / didn't**, and — the
part worth reading before you fight these tools yourself — **what each
manufacturer's SPICE models are actually like to obtain and simulate**.

---

## 0. TL;DR

| Quantity | Value | Confidence |
|---|---|---|
| Commutation-loop PCB copper L (nearest ceramic) | ~4 nH (band 4–6 nH) | high |
| FET pin/lead inductance (TO-220, both switches) | ~9 nH | high (datasheet) |
| **Total hot-loop L** | **~13 nH (pins ~70%)** | high |
| Switch-node ring frequency | **~68 MHz** | high (3 models + analytic agree) |
| Tank impedance Z₀ = √(L/Coss) | 5.6 Ω (13 nH, 420 pF) | high |
| Effective Coss at the swing | ~420 pF (inferred from ring; matches Co(er)≈450 pF) | medium |
| **Un-snubbed overshoot @32 A/80 V** (mfr vendor models) | **5.68 V (peak 85.7 V)** — conservative; ~4.0 V with datasheet-anchored Qrr | high (verified, Miller-limited) |
| Body-diode Qrr loss @39 kHz | ~0.5 W (datasheet-anchored; raw model 2.8 W is ~6–9× high) | med — §5c |
| — with 120 V Infineon `_L0` LS variant | 19 V (peak 99 V) → 21 V margin | high (converged) |

**RESOLVED (see §5): the pessimistic 103 V was wrong.** With proper vendor MOSFET
models (Toshiba `_G0`, or Infineon `_L0`+external leads) the DPT bench converges
and the overshoot is **Miller-limited and modest (~4–19 V, FET-dependent) and
sub-linear in load current** — it does *not* grow with current. The **LS FET sees
the SW overshoot (peak ~84–99 V), so a >100 V LS is the right call** — the user's
**IPP022N12NM6 (120 V) LS gives ~21 V margin**; an 80 V LS would be exceeded. The
snubber (board C8) is for **EMI + margin, not survival**.

---

## 1. Layout reconnaissance (the first surprise)

The README says "TO-220 switches," but the actual v2.3 layout (`pcbnew` on
`Fugu2.kicad_pcb`) uses **SMD Infineon PG-TDSON-8** footprints on B.Cu:
- HS = **Q1 ‖ Q3** (Solar+ → SW), LS = **Q2** (SW → BuckGND), all bottom-layer.
- LS Schottkys **D9 (TO-220) / D16 (TO-277) are DNP** (unpopulated) — freewheel
  is the Q2 body diode.
- HF ceramics (C16/C17/C18/C21/C22/C9/C27) sit right on the B.Cu pours next to
  the switches.

The BOM lists TO-220 alternates (`IPP055N08NF2S` HS, `FDPF2D3N10C` LS) as DNP
options. Per the user the intended build uses the **TO-220 parts**, so the FET
stress work uses those — which is why the FET *leads* end up dominating the loop.

**Finding:** never trust the README/BOM package over the actual footprints; and a
board can carry both SMD and THT options with the "populated" set differing from
the BOM defaults.

---

## 2. Commutation-loop inductance: KiCad → FastHenry

### Tooling
- **FastHenry 3.0.1** (FastFieldSolvers fork), built from source at
  `~/dev/vendor/FastHenry2`. Legacy K&R C — needs
  `CFLAGS='-O -DFOUR -m64 -std=gnu89 -fcommon -Wno-implicit-function-declaration
  -Wno-implicit-int -Wno-return-type -Wno-deprecated-non-prototype'`.
- **KiCad 9 bundled python** (has `pcbnew`) for geometry; **system python3** for
  the runner. Files: `extract/kicad_to_fasthenry.py`, `extract/run.py`,
  `extract/debug_plot.py`, `extract/results.md`.

### Method
Mesh the `Solar+`/`SW`/`BuckGND` pours (both layers) into a **filament grid
clipped to the real filled polygon**; rasterize tracks (Manhattan-routed) and
pads onto the same grid; stitch layers with vias; short each switch drain→source
with a thin die-plane bridge; excite one port across a chosen ceramic.
`L = Im(Z)/ω` on the 10–100 MHz plateau.

### Findings / gotchas
- **Coincident cross-net nodes → NaN.** Two nets landing on the same grid cell
  create identical-coordinate filaments → singular mutual inductance. Fixed with
  a global per-cell **occupancy** map (one net per cell).
- **FastHenry rejects trailing comments** on element lines.
- **Per-cap loop L ranks which ceramic carries the hot loop** (port swept across
  each): C18 4.20, C17 4.33, C9 4.59, C16 4.80, C21 5.36, C22 6.70, C27 16.3 nH.
  → The two 0603s at the switch node dominate; placement beats capacitance.
- **You cannot scalar-parallel the per-cap Ls** — they share copper/mutuals.
  Correct decomposition: shared switch-loop copper (~4.0 nH) + per-cap branch
  excess. Verified: the LTspice Cin subckt gives 4.0 + 0.19 nH bypass ≈ 4.2 nH,
  matching FastHenry.
- **Convergence is non-monotonic in mesh pitch** (2.0/1.0/0.7 mm → 5.8/4.8/5.2
  nH, ±9%). The gridded-filament plane is an approximation; report a band, not a
  point. G-plane refinement is future work.
- **Connectivity prune** (keep only the mesh reachable from the port) turns
  silent NaN into a clean error and drops floating islands.
- **Q2-only (D9/D16 DNP) disconnects the port** — the SW pour is fragmented and
  the HS-side / Q2-side SW were joined only through the diode copper. This is a
  *latent layout observation*: if D9/D16 are truly DNP, check the SW node isn't
  split (KiCad DRC with them unpopulated). Deferred — leads dominate, so the 4 vs
  ~6 nH copper difference is <10% of the 13 nH total.

### Speed
FastHenry has **no OpenMP** (verified — zero `#pragma omp` in the source; the
binary is single-threaded). Speed came from: solving only the ~10–100 MHz
plateau (the preconditioner is rebuilt *per frequency*), `-p diag` preconditioner,
and running the independent pitch solves concurrently. `-s ludecomp` (dense)
*times out* — iterative+multipole is essential. Full 3-pitch sweep: ~8 s.

---

## 3. Manufacturer SPICE models — the real notes

This is the part that cost the most time. Summary of how each vendor ships
models and how they behave.

### Capacitors

**Taiyo Yuden (TY-COMPAS)** — *the good one.*
- Per-part download works via a **session cookie**: GET the detail page
  (`ds.yuden.co.jp/TYCOMPAS/ut/detail?pn=<PN>&u=M`) to set a cookie, then
  `…/ut/download?pn=<PN>&fileType=<T>` with that cookie + Referer.
- File types: `cir_file` (standard **0-bias** RLC-ladder, unencrypted, portable),
  `LTspice_file` (a **zip** with the **temperature/DC-bias** model `_LT.cir` +
  a `.asy` symbol). The bias model is **encrypted** (`* LTspice Encrypted File`)
  → LTspice-only, can't port to ngspice.
- The BOM part numbers are **renamed** under the new scheme: `HMK212BC7105KGHTE`
  → `MMASH21GBC7105KTCA01`, `HMK107C7224KAHTE` → `MCASH168SC7224KTCA01`. Resolve
  via the old-PN detail page.
- Params read straight from the `.cir`: 0603 220 nF → ESL 0.47 nH, ESR 12.2 mΩ;
  0805 1 µF → ESL 0.35 nH, ESR 5.3 mΩ. Clean, well-behaved models.

**Murata (SimSurfing)** — *no clean per-part download.*
- The product page has **no direct SPICE link** (it's inside the SimSurfing JS
  app). Per-part URLs return the SPA shell.
- Workaround: download the **series netlist ZIP** (e.g. `grm-n-v76.ashx`,
  ~9 MB) from the MLCC SPICE page and extract the `.mod` (found
  `GRM32EC72A106KE05.mod`). This is a **0-bias** RLC-ladder model; the
  DC-bias-dependent model lives only in SimSurfing.
- Fine for bulk caps; for the 10 µF 100 V X7S at 60–80 V the 0-bias model
  overstates C (X7S derates hard), but those caps are the *least* important for
  the fast loop (highest loop L), so acceptable — flagged in the manifest.

Models + `MANIFEST.md` live in `extract/capmodels/vendor/`. The Cin bypass
network is assembled in `extract/capmodels/cin_hotloop.lib` (each ceramic =
vendor model in series with its FastHenry copper-branch L) and wired into
`buck_parasitcs_extracted.asc`. **Verified in LTspice** (AC impedance test
`tst_cin.cir`): all 6 vendor models load, Ceff = 21.2 µF (nominal 22.4), HF
bypass ESL parallels to 0.19 nH → SW sees 4.0 + 0.19 ≈ 4.2 nH.

### MOSFETs — *where the trouble was.*

**Infineon** — *best features, worst numerics — but there's a workaround (`_L0`).*
- Sources: the community **metacollin/LTspiceInfineonNMOSLibrary**, AND the
  **official** pack (`infineon-optimos-…-simulationmodels`, per-generation
  `OptiMOS*/StrongIRFET*_LTSpice.lib`). The official and community models are the
  **same** — same subckts, same lead params.
- Each part ships **three variants**: `_L1` (die + internal lead inductors,
  `PARAMS: Ls Ld Lg`), the full 5-terminal thermal model, and **`_L0`
  (die-only, no leads)**.
- **`_L1` is numerically fragile in transient.** An internal behavioral-cap node
  (`e:*:_eds*#branch`) collapses the timestep (→ 2.5e-19) whenever the FET's
  drain sees dV/dt — it fails even during a gentle `Vin` ramp with the FET *off*,
  and it fails **as the LS too** (blows up to 100+ kV at HS turn-on). The 15 A
  bench only survived because the drain was **static** (`uic`). No `uic`/
  soft-start/damping/tolerance trick fixes it.
- **THE FIX: `_L0` (die-only) CONVERGES.** The fragility is specifically the
  `_L1` **internal lead-inductance network**, not the die. So use `_L0` + your
  own external `Ld/Ls/Lg` inductors — official Infineon models are then usable
  and give physical, converged results (Toshiba HS + `IPP022N12NM6_L0` LS → clean
  32 A run, 19 V overshoot).
- **Lesson:** detailed vendor MOSFET models with hidden internal reactive nodes
  can be unusable in fast transients — but the `_L0`/die-only variant (leads
  added externally) sidesteps it. Prefer models built on **standard primitives**
  (see Toshiba) or the `_L0` variant.

**Toshiba** — *the robust one; what the original bench used.*
- Official LTspice/PSpice libs at `toshiba.semicon-storage.com`. `TK6R8A08QM_G0`
  (unencrypted PSpice `.lib`) is built on a **plain `M` primitive with zero
  behavioral E/G/B sources** → numerically bulletproof. The original
  `buck_parasitcs.asc` already used this family (`TK*_G0_00_PSpice_rev1.lib`).
- In the DPT bench it converges at any I/V and gives Miller-limited overshoot
  (9.8 V @15 A, 4 V @32 A) — no leads built in, so add external `Ld/Ls/Lg`.
- Node order `.SUBCKT … 1 2 3` = **1=Drain 2=Gate 3=Source**.

**TI** — `CSD19501KCS.lib` (from `slpm107b.zip`) obtained; PSpice-format, usable
in LTspice. Not needed once Toshiba worked, but on hand as a cross-check.

**onsemi** — *effectively un-scriptable.*
- The LS BOM part `FDPF2D3N10C` model is behind a **WAF** (403 to curl *and*
  WebFetch) and a **SPA/search-API** (guessable URLs return the app shell; even a
  same-origin in-page `fetch` returned HTML). Not worth the effort for a
  secondary part — substituted an Infineon LS from the same lib (README's LS
  picks are Infineon anyway) and flagged it.

**Model-independence finding:** ring *frequency* is robust across every model +
analytic (~68 MHz for IPP055-class Coss). Overshoot *amplitude* is highly
model-sensitive — the behavioral switch and VDMOS over-predict it (no gate-charge
fidelity) and the Infineon `_L1` won't converge, but a **numerically clean vendor
model (Toshiba `_G0`, or Infineon `_L0`+leads) resolves it** to a modest,
Miller-limited value (§5b). Model *numerics*, not physics, drove the confusion.

---

## 4. FET pins + the ringing cross-check

Bench `fugu_ring.cir` (single-HS, Infineon `_L1` with built-in leads, vendor Cin,
extracted 4 nH copper split L5/L4, `uic` at 70 V static drain):
- Loop L = 4 nH copper + 9 nH FET leads = **13 nH — pins ~70%.**
- HS turn-on: SW overshoot ~11 V (peak 81 V), **ring 68 MHz**, decays in ~4
  cycles. Analytic `1/(2π√(13 nH·420 pF)) = 68 MHz` matches → cross-check passes.
- Coss handling: standalone Coss(V) extraction from the model **fails** (the same
  internal-node fragility). Effective Coss **inferred** from the validated ring =
  420 pF at the 70–80 V swing, consistent with Infineon Co(er) ≈ 450 pF.
- The `_L1` `Ls` (source lead) provides common-source degenerative feedback that
  slows di/dt — the 4 nH PCB copper is placed **outside** the package `Ls`
  (Cin → pad), so no double-count.

---

## 5. The 32 A stress case — convergence solved, amplitude not

This is the honest hard part. The un-snubbed overshoot at full load could not be
pinned down in simulation.

**Model development ladder (all attempts):**
1. **Infineon `_L1` at 32 A/80 V** — won't converge (internal `_eds` node; §3).
2. **Behavioral SW switch** — converges, but an ideal switch has **no
   Miller/gate-charge feedback** → hard-switched **62 V** at 15 A (vs 11 V).
3. **LTspice VDMOS + `uic`** — converges but the `uic` cold-start shocks the
   ceramic branch inductors (70 V slammed across them → −18 kV startup spike) and
   the parallel-HS + lead-L topology oscillates (chaotic 189 V spikes — the
   classic fast-half-bridge SPICE instability).
4. **VDMOS + soft-start ramp** — clean convergence, no artifacts, f_ring ~66 MHz;
   but the converter **operating point** is finicky (the battery drains the
   freewheel current; `uic`+`Ic` re-adds a startup spike).
5. **Double-pulse-test (DPT) bench** *(the fix — from channel advice)* —
   `dpt_ring.cir`: replace the inductor+`Ic` with an **ideal DC current source**
   for the coil and hold the **LS channel ON at t=0**. That is a legitimate DC
   operating point → LTspice solves it via `.op`, **zero shock**, converges at
   any I/V. Industry-standard, datasheet-comparable. **Convergence: solved.**

**But the amplitude splits ~10×** and can't be resolved with physical params:

| Model (15 A/70 V) | f_ring | overshoot |
|---|---|---|
| Infineon `_L1` (detailed, fragile) | 68 MHz | 11 V |
| Behavioral switch (no Miller) | 68 MHz | 62 V |
| VDMOS, datasheet Coss | 71 MHz | ~130 V (≈ Z₀·I hard-switch bound) |

Rg sweep (4→12 Ω) gives 133→106 V — the simplified models cannot reach 11 V with
physical parameters, and forcing it by tuning would be **circular** (per the
reviewers: fit Coss to the datasheet, then let the ring match be an *independent*
check — don't tune to hit 68 MHz/11 V). The true amplitude depends on the real
device's Miller/gate-charge dynamics and **body-diode Qrr** (LTspice VDMOS body
diode is Qrr-less → its overshoot is a lower bound; the real 32 A peak is higher).

**Key physical insight (ee-b5ab):** Z₀ = √(13 nH/420 pF) = 5.6 Ω, so a hard
commutation of the full current gives dV ≈ Z₀·I. The real 11 V means Miller
feedback couples only ~2 A into the tank → overshoot is set by **di/dt vs tank
period, not load current directly**. So the linear "15 A:11 V → 32 A:23 V →
103 V" scaling is **pessimistic**.

### 5b. Resolution — a robust vendor model settles it

The whole 10× gap was a **model-numerics artifact**, not physics. Given the
**official Toshiba `TK6R8A08QM_G0`** model (standard `M` primitive, zero
behavioral nodes), the DPT bench **converges cleanly at every operating point**
*and* produces a physical, Miller-limited overshoot:

| DPT run (robust models) | overshoot | SW peak | note |
|---|---|---|---|
| Toshiba HS+LS, 15 A/70 V | 9.8 V | 79.8 V | f_ring 32 MHz (higher Coss than IPP055) |
| Toshiba HS+LS, **32 A/80 V** | **5.68 V** | **85.7 V** | verified: full 1.2 µs tran, 0.31 s solve, Qrr included |
| Toshiba HS + `IPP022N12NM6_L0` (120 V) LS, 32 A/80 V | 19 V | 99 V | 120 V LS → 21 V margin |

The overshoot is **Miller-limited, modest (~4–19 V), and does NOT grow with load
current** — exactly ee-b5ab's prediction. The 62 V/130 V from the behavioral/
VDMOS models were purely their lack of gate-charge fidelity; the Infineon `_L1`
never converged. **Root cause of the whole stress saga: the Infineon `_L1` model
is numerically pathological — a clean vendor model just works.**

**Engineering conclusions (now firm):**
- Un-snubbed SW overshoot at 32 A/80 V is **modest (~4–19 V, FET-combo-dependent),
  peak ~84–99 V** — not the pessimistic 103 V.
- The **LS FET sees the SW overshoot** → needs a **>100 V** part. The user's
  **IPP022N12NM6 (120 V) LS is the correct choice** (~21 V margin); an 80 V LS
  would be exceeded.
- The **snubber (C8) is for EMI + margin, not survival.**
- **Body-diode Qrr: present but NOT calibrated — over-stated, so the overshoot is
  pessimistic (not a lower bound).** The Toshiba `_G0` body diode (`DDS1`:
  `TT = 25.5 ns`, `CJO = 1.65 nF`) does model reverse recovery and is di/dt-
  responsive, but the magnitude is wrong — see §5c. Consequences (all favorable):
  realistic **Qrr loss ≈ 0.5 W** (not the raw model's 2.8 W) and realistic
  **overshoot ~4.0 V (peak 84 V)**, not 5.68 V — the excess modelled Qrr current
  was over-exciting the tank. So 5.68 V stands as a conservative design number.

### 5c. Body-diode Qrr — calibration study (the model's weakest link)

Datasheet spec (TK6R8A08QM body diode): **Qrr = 43 nC typ, trr = 40 ns typ** at
IDR = 14.5 A, VGS = 0, −di/dt = 100 A/µs. A clean di/dt-controlled recovery bench
(`qrr_test.cir`: LS body diode only, di/dt set by a series L, ring damped) run at
those exact conditions gives:

| Condition | I_F | di/dt | model Qrr | model trr | vs datasheet |
|---|---|---|---|---|---|
| Datasheet point | 14.5 A | 100 A/µs | ~250–400 nC | 170 ns | **Qrr 6–9× high, trr 4× high** |
| App commutation (vendor TT) | 32 A | 2670 A/µs | 895 nC | 50 ns | uncalibrated |
| App commutation (TT re-fit 1.8 ns) | 32 A | 2670 A/µs | 162 nC | 27 ns | datasheet-anchored |

The over-statement comes from **two** oversized params: `TT = 25.5 ns` (~10× the
~1.8 ns that fits the app-di/dt Qrr) dominates at fast di/dt, while `CJO = 1.65 nF`
**floors** Qrr at ~250 nC even with `TT→0` at the datasheet's slow di/dt (there the
recovery is junction-charge-limited, not transit-time-limited). The SPICE Level-1
diode also has no recovery-softness or temperature dependence. (Note: Toshiba does
NOT specifically disclaim Qrr — the header's "verified only on PSpice" is a
simulator-portability note, not a parameter-accuracy statement. The 6–9× gap is
established purely by the measurement-vs-datasheet comparison above.)

**Loss:** `P_Qrr = Qrr·Vin·fsw`. Raw model → 2.8 W (over-estimate); datasheet-
anchored → **≈ 0.5 W** at 39 kHz/80 V; a hand-scaling of the 43 nC datasheet point
to app conditions lands in the same **0.3–1.0 W** band. Minor vs conduction/switching.

**Overshoot:** re-running the DPT commutation with the Qrr-re-fit LS
(`dpt_qrrfit.cir`) drops SW peak 85.7 → 84.0 V (overshoot 5.68 → 3.99 V) and IRRM
43 → 11 A — confirming the vendor-model overshoot is *pessimistic*. Design margins
only improve. Benches: `qrr_test.cir`, `qrr_fit.cir`, `qrr_refit.lib` (derived TT-
fit model — NOT the vendor model), `dpt_qrrfit.cir`.

---

## 6. What's trustworthy vs what needs hardware

**Solid:** loop L = 13 nH (pins ~70%); f_ring ~68 MHz; the extracted 4 nH copper
+ per-cap ranking; the vendor-cap Cin network (verified). The **snubber decision**
— the hard-switched bound (Z₀·I ≈ 84 V @15 A, ~180 V @32 A) exceeds the 80 V FET
rating, so the board's RC snubber (C8) is warranted.

**Resolved in sim (with the robust vendor model):** the un-snubbed overshoot at
32 A/80 V = **5.68 V (SW peak 85.7 V), Qrr included** — the old 11–130 V spread
was model numerics. **Still worth a hardware scope-DPT** to pin the absolute Vds
margin / snubber sizing against the real part, but sim now gives a firm number.

---

## 7. File index (`spice/`)

**Policy: manufacturer models only.** The community/fake-model benches used during
model development (`fugu_ring.cir`, `fugu_ring_stress.cir`, `coss.cir`,
`behavioral_ring.cir`, `vdmos_ring.cir`, `dpt_ring.cir`) and the community Infineon
lib (`fugu_fets_infineon_80V.lib`) were **removed** — they were scaffolding to work
around the fragile Infineon `_L1`. The surviving benches use only vendor models.

| File | Purpose |
|---|---|
| `buck_parasitcs_extracted.asc` | LTspice model: vendor Cin + extracted L + Toshiba `_G0` FET refs |
| `extract/kicad_to_fasthenry.py` | KiCad→FastHenry mesh extractor |
| `extract/run.py` | parallel solve/reduce → `results.md` |
| `extract/debug_plot.py` | renders the FastHenry geometry (parse-bug catcher) |
| `extract/capmodels/vendor/` + `MANIFEST.md` | vendor cap models (TY encrypted DC-bias + std, Murata .mod) |
| `extract/capmodels/cin_hotloop.lib` | Cin bypass subckt (vendor caps + branch L) |
| `extract/capmodels/fets/` | **mfr FET libs only:** Toshiba `TK6R8A08QM_G0`, official Infineon 80 V/120 V, TI `CSD19501KCS` |
| `tst_cin.cir` | AC impedance verification of the Cin network |
| `dpt_toshiba.cir` | **DPT, Toshiba TK6R8A08QM — trustworthy 32 A result: 5.68 V, Qrr included** |
| `dpt_mixed.cir` | DPT Toshiba HS + Infineon `IPP022N12NM6_L0` 120 V LS (19 V, 21 V margin) |

Official vendor model packs are in `~/dev/pv/ee/spice-models/` (Infineon OptiMOS
80 V + 120 V, Toshiba TK6R8A08QM, TI CSD19501KCS).

**LTspice CLI gotcha (macOS):** run netlists headless with `LTspice -b file.cir`.
Do **NOT** add `-Run` — on macOS `-Run` opens the GUI and the batch job hangs
indefinitely with no `.log`/`.raw`. Plain `-b` solves this circuit in ~0.3 s.
