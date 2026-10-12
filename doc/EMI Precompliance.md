# EMI pre-compliance bench procedure (near-field)

Gear: near-field H/E probe set, 20 dB preamp, R&S MXO4.
DUT: Fugu2 sync buck, fsw 39 kHz, 72 V in / 27 V out, up to 33 A.
Observed switch-node ring content: **15–60 MHz**.

Read [No-Coil SW Ring (Bench vs SPICE)](<No-Coil SW Ring (Bench vs SPICE).md>)
first — the switch-node ring is already measured and reconciled there, and this
document does **not** re-open it. Tooling: `spice/ring_analysis.py`.

---

## 0. What is already known, and what this session is actually for

The differential-mode side is done. From the No-Coil study, on the bench board
(LS `IPP024N08NF2S`, HS 2× `IPP055N08NF2S`, Rg = 15 Ω):

| | measured |
|---|---|
| loaded ring vs bias | **37.0 / 53.8 / 58.5 MHz** at 20 / 40 / 60 V |
| ring tank C | LS Coss only (HS channel shunts its own Coss), ~780–810 pF at 60 V |
| commutation loop L | **~9.2 nH** = ~4 nH copper + ~1 nH drain tab + ~4 nH source CSI |
| SW peak | 74 V at 60 V in (~1.2×), **no avalanche** |
| rise time | 15.8 ns ≈ **one ring period** — the edge only weakly excites the tank |

**The 37 MHz bench point is not an operating point.** It was taken at Vin = 20 V
with Vout = 9 V — a characterisation point. In service this is a buck into a
**27 V battery**, so Vin ≥ ~28 V is a hard floor and the MPP of a string sized
for 72 V sits at 55–80 V (`README.md` specs; `doc/Thermal tests.md`;
`HW Stories/fbox2.md` MPPT landing at 65 V). Over that range the ring barely
moves:

| Vin | 28 V | 40 V | 55 V | 65 V | 72 V | 80 V |
|---|---|---|---|---|---|---|
| f_ring @ 9.16 nH | 45.8 | 54.2 | 58.5 | 60.0 | 60.8 | 61.1 MHz |

It reaches 37 MHz only at **Vin ≈ 21 V**, below the battery voltage. **The
in-service ring span is ~59–61 MHz** as modelled — but §4 states the bias series
*"cannot resolve L better than ~±15 %"*, and since f ∝ L^−½ that is ∓7 % in
frequency, i.e. a real band of **~55–65 MHz** — which is exactly what the No-Coil
study reports from the scope (*"~55–65 MHz, ~4 cyc"*). **Quote 55–65 MHz as the
measured span**; the 59–61 MHz figure is a two-significant-figure model output
and an earlier version of this section presented it as if measured. The
*relative* conclusion in step 8 (bias shift too small to discriminate) survives,
because ratios are robust where the absolute value is not (~46–61 MHz across the whole legal Vin
range). So the unexplained band is not 15–37 MHz — it is essentially the
**entire 15–55 MHz**, and the ring accounts only for the top sliver.

**And it may not need a resonance at all.** A 15.8 ns edge has a spectral knee
at 1/(π·t_r) = **20 MHz**; below that the trapezoid envelope rolls off at only
−20 dB/dec. There is abundant broadband edge energy across 15–37 MHz with no
resonator there whatsoever. Establish whether the band is *combed and
broadband* (edge) or *peaked* (a resonance) before hunting for a loop.

### The standards basis, and what it makes the limiting case

**Decided 2026-10-10: Fugu2 keeps the ESP32-S3 BLE on board** — the integrated-radio
route, as Victron's SmartSolar MPPTs do. The declaration is therefore **RED only**,
not EMCD. The reasoning, the conditions and the open items live in
`~/dev/pv/ee/dcdc-tools/emc/STANDARD-BASIS.md` §8.6 and are **not** repeated here;
that document is the authority on the legal wrapper and this one must not contradict
it. Three of its findings set the measurement priorities below:

| finding | consequence for this bench session |
|---|---|
| **Radiated limits start at 30 MHz** (`STANDARD-BASIS.md` §8.3) | Everything below 30 MHz is out of *radiated* scope entirely |
| **In this band, radiation is CM current on the PV/battery cables** (`STANDARD-BASIS.md` §8.3) | CM current is the measurand with a limit line behind it — not SW-node voltage |
| **No conducted measurement at either DC port** — Fab's decision of 2026-10-11, `STANDARD-BASIS.md` §8.0a | The sub-30 MHz content has no conducted limit to breach either. **The grounds are not a cable-length rule** — see below |

**This inverts the priority an earlier draft of this document gave.** The
"unexplained 15–55 MHz" is real as a physical observation, but 15–30 MHz of it
has **neither** a radiated nor a conducted limit applying to it. It is
diagnostically interesting and compliance-irrelevant. The **59–61 MHz in-service
ring sits squarely in radiated scope**, and the mechanism that gets it off the
board is CM current on the harness — which is still unmeasured.

**Corrected 2026-10-11 — the grounds for the conducted relief, which an earlier
draft of this section got wrong.** It attributed the relief to a **30 m
cable-length rule**. That is not where it comes from, per `LISN-70ec` on channel
`emc`, verified against `STANDARD-BASIS.md`:

- **EN 55011 ed 6.1 has no length dependence at all.** It tests DC ports only on
  **grid-connected** converters (§8.0). The 30 m gate in §5a is from
  **AMD2:2019 Table 6, which is not harmonised**, so it never governed this.
  Stated dependency: ed 6.1 holds **until a new OJEU citation** supersedes it.
- **Under EN 61000-6-3 Table 3 the 30 m qualifier binds only the "local battery"
  case.** A *"local DC power network"* is tested **at any length**.

So the relief rests on an **interpretation** — that neither a PV string nor a
battery bus is a DC power network — plus two port declarations accepted on
2026-09-07 (`dcdc-tools emc/DECLARATIONS-fugu2.md`): the battery port *"intended
solely for connection to a battery or other local DC power source … maximum
length of cable … 2 m"*, and the **PV port at 29 m**. The interpretation is
**open with a test house** (Q3/Q4 in `emc/TEST-HOUSE-QUESTIONS.md`). Treating it
as a settled length rule would be wrong in both directions: a longer cable does
not break it, and a short one does not secure it.

**The declarations are adopted and in the product repo — checked 2026-10-12.**
`DECLARATIONS-fugu2.md` once called them *"accepted, correct, and homeless"*.
They are not homeless: **`Fugu2 doc/INSTALLATION.md`** (commit `2b7a7e8`, 154
lines) carries both sentences in the Ports-and-cabling table — **PV 29 m,
battery 2 m** — with the connector, fuse, connect-to and do-not-connect-to
columns, the bundling instruction, and the rationale table citing EN 55011
§6.2.1.1 and EN 301 489-1 §8.3.1. No `PLACEHOLDER` remains in it.

This paragraph has now been wrong twice in opposite directions: first *"no
document exists"*, then *"drafted but not adopted"*, pointing at the `dcdc-tools`
draft (`emc/INSTALLATION-INSTRUCTIONS-fugu2.md`, `36abe9c`) while the adopted
product version already sat in this repo's own `doc/` directory.

**What actually blocks shipping it** is the file's own *"OPEN: decisions needed
before this ships"* list — eight items, of which only two touch EMC:

| # | item | EMC? |
|---|---|---|
| 1 | **Battery port C10 — decided 2026-10-11, reopened 2026-10-12 by the coil.** The shipped KDM KS184-125A is ~25.6 µH at 32 A against the 50 µH the sim assumed, roughly doubling ripple; the KZN then fails Table 3 AV by ~3 dB and runs ~33 % over its ripple rating | **yes, live** |
| 7 | Immunity **EN 61000-6-2:2019** decided; its industrial levels not yet checked against the design | **yes** |
| 3 | **F1 is specified only as 40 A.** Standard ATO fuses are rated **32 V**, below a 16S LiFePO4 pack | no — **safety** |
| 2, 4, 5, 6, 8 | PV Voc/Isc limits, fuse selectivity, comms adapters, USB, remaining 62109-1 §5.3 content | no |

Item 3 deserves naming even though it is outside this document's scope: a 32 V
fuse in a ~58 V DC circuit is not a paperwork gap — a DC arc at 58 V may not
self-extinguish in a fuse body rated for 32 V.

**Correction to a claim this section made about the 29 m.** It said the PV figure
sits 1 m under the 30 m gate and so leaves a one-metre fallback margin. That
conflates two standards, per `LISN-70ec`:

- The EN 61000-6-3 *"local battery > 30 m"* branch concerns the **battery** port,
  which is declared **2 m** — nowhere near the gate.
- The **29 m** is set against the 30 m row of **EN 55011 AMD2:2019 Table 6**,
  which is **not harmonised** and therefore not binding. The draft instructions
  note the `L ≥ 30 m` row is inclusive, which is why 29 was chosen over 30.

So there is no one-metre cliff on the harmonised route. The margin the relief
actually rests on is the *interpretation*, not a length.

One caution stands unchanged: under the RED route a generic EMC standard is
Art 16–17 self-assessment evidence, not a presumption of conformity. So "no
limit applies" remains a conditional statement about a reading of the standards,
not a property of the hardware.

### How much margin there is — an independent estimate, 2026-10-11

Relayed from session `ee-1b` and verified against the source before being
recorded here. Two independent radiated estimates now exist in `dcdc-tools`,
both modelling the board **as it will ship** (no filter, EKZN caps, heatsink
bonded via H1):

- `emc/radiated-indep/RESULTS-radiated-indep.md` on branch `rad-indep-20261011`
  (under review), and
- the `rad300` work in `emc/cm-conducted` plus
  `plans/desk/DESIGN-radiated-cm-cable-estimate.md`.

**The central estimate sits at the class B limit** — that file's own words are
*"at the class B limit, not clearly under it"* — **−0.1 / +2.5 / +0.5 / +4.0 dB
at 3 m** across 30–50 / 50–70 / 70–90 / 90–110 MHz, band peak at 106 MHz.

**Both numbers below are pre-fix and moving.** Updated 2026-10-11 direct from
the author (channel `emc`), superseding an earlier relay: the file is being
revised after a Codex review that found the **uncertainty band too narrow**, so
the ~−15…+31 dB band will widen. And the inter-model disagreement is
**≈18 dB at 30 MHz**, per the source: *"E at 3 m, 30 MHz … 58.5 dBµV/m =
+18.5 dB | 30–50 MHz band peak 39.9 dBµV/m QP = −0.1 dB | **≈ 18 dB**"*, closing
with *"**Disagreement: about 18 dB at 30 MHz.**"*

⚠️ **Corrected 2026-10-11.** An earlier version of this paragraph replaced that
with *"~31 dB at 30 MHz frequency-matched (27.2 vs ~58.5 dBµV/m QP)"* on the
strength of a channel relay, and dismissed the 18 dB as *"a different
comparison."* **The value 27.2 appears nowhere in the committed file**, and 18 dB
is the figure the owning document states twice. Overturning a number that is in
the source, in favour of one that is not, was the wrong way round.

The cause is still the **PV-port differential voltage**, 60–62 vs ~86 dBµV,
which the author traces to an **input-bank inductance of 0.7 vs ~11 nH**. That
is why step 6 exists — and see §5's Cin-bank note, because this repo has
measured data bearing on it: a 16× disagreement in bank inductance is hard to
read as one model simply being wrong, when the bank has a **ceramic branch and
an electrolytic branch** whose effective ESLs plausibly differ by that order
(9 MLCCs at ~0.35 nH each, against a bulk branch). If the two models each took a
different branch as "the" bank inductance, the 31 dB is a difference in
modelling scope rather than an error.

**Corroborated twice, independently, 2026-10-11** (channel `emc`) — the
electrolytic branch really is in the 8–11 nH class:

- `ee-cd`'s DM deck gives **~11 nH** for the electrolytic branch, and that is
  with an *optimistic* 5 nH package ESL.
- `ee-86` reports Chemi-Con's **KZN vendor models use L1 = 8 nH** for every can
  ≥ 12.5 mm.

The part identification: C11, C12, C34 (input bank) are **`EKZN101ELL102MM40S`**,
confirmed in `PowerStage.kicad_sch` — 18 × 40 mm cans.

⚠️ **Two corrections, 2026-10-11.** (a) **C10 is not that part.**
`RESULTS-batport-20261010.md` §0: *"**C10 IDENTIFIED 2026-10-10 (Fab): Rubycon
100ZLH470MEFC18X25** — 470 µF, 100 V, 18 × 25 mm. The board's '1000uF' value
field was stale."* ESL unpublished, assumed **15 nH**. An earlier version here
said *"C10 is the same part"* — and "verified in `PowerStage.kicad_sch`" leaned on
exactly the field that document records as wrong. The input-bank identification
stands; the output one was invented. (b) **The 8 nH does not belong to this
part.** §1c: *"**EKZN101ELL102MM40S is not among them.** Every KZN can of
12.5 mm and up carries L1 = 8 nH … So 8 nH is a same-series, same-case
**sibling** value, **not this part's own model**."* The relay was accurate about
the rule; "and the part applies" inverted the source's conclusion.

So 0.7 nH cannot be the electrolytic branch, and ~11 nH cannot be the ceramic
one. Two numbers 16× apart, each independently plausible for a *different*
branch, is much better explained by a modelling-scope difference than by either
model being wrong. **Still not measured** — step 5 settles it by backing the
effective branch ESL out of the bank's anti-resonance, and that remains the
cheap decisive test.

Three caveats, all from the source rather than the relay:

1. That document calls itself **"a design-stage margin estimate, not a
   compliance prediction."** Do not quote the margin as a verdict.
2. Its **credibility ceiling is 110 MHz**, because above that the existing
   switch-node capture is within 6 dB of the scope-and-probe floor. The
   110–300 MHz numbers are computed but not quoted; 300 MHz–1 GHz is not
   estimated at all. This is the same instrument limit as §2's bandwidth
   question — **one `*OPT?` query now unblocks two workstreams.**
3. It evaluates **CISPR 11 class B** and records EN 61000-6-3 radiated as
   *"assumed equal to the CISPR class B values above"*, marked
   ***"unverified: not re-read for this note."*** Since EN 61000-6-3 is now the
   declared basis (above), that assumption has become load-bearing. The limits
   do appear to coincide — 40/47 dBµV/m at 3 m breaking at 230 MHz, i.e. the
   30/37 at 10 m used in §2 — but coincidence by inspection is not
   verification, and this is the owning document's own open item.

⚠️ **A "cross-check" that was an artefact — removed 2026-10-11.** An earlier
version of this section claimed the two models' CM currents *"18.1 dBµA at
30 MHz = 8.03 µA"* coincided with §6's independently derived 8 µA
limit-equivalent — *"two unrelated routes to the same microamp."* They are at
**different frequencies**: the source reads *"PV 31.7, BAT 30.5 dBµA **@
30.07 MHz** | PV **18.1**, BAT 16.7 dBµA **@ 40 MHz**."* The limit-equivalent at
40 MHz is **5.95 µA = 15.5 dBµA**, so 8.03 µA is +2.6 dB over it, not equal to
it. The agreement was a frequency mismatch.

The same sentence also called the high model's **+13.6 dB** both the *inter-model*
difference and its *margin over the limit*. Those are different quantities that
coincide only because 18.1 dBµA happens to equal the 30 MHz limit-equivalent in
dBµA — and the inter-model figure at matched frequency is ≈18 dB (above), not
13.6.

### The CM-current target for step 4, and a harder headline

From `dcdc-tools emc/STATUS.md` (banner, read 2026-10-11) — the rad300 deck's
cable CM current, scored with the short-cable antenna formula against
min(CISPR 11 B, EN 300 328 RX) ≈ 40 dBµV/m at 3 m, 1 m cable, Z_cm 150 Ω:

| board | 30–50 MHz | 100–150 MHz |
|---|---:|---:|
| **bench board, no input filter — the board that exists** | **+17.5 dB** | **+13.0 dB** |
| + terminal cap 0.8 µF / 1 nH at the PV connector | −16.1 dB | +11.1 dB |
| + LS RC snubber 1.5 Ω / 4.7 nF | +9.4 dB | +3.7 dB |
| recommended filter, real Würth 220 µF `Cfilt` | −0.3 dB | — |

**The bottom row is not an available fix.** Fab's 2026-10-11 decision is *"no
conducted test at the DC ports; **no filter on the device**"* (`STATUS.md`
banner, commit `90d2ae7`). So the top row — **+17.5 dB over** — is the shipping
configuration, and the filter row describes a device that will not be built.
`STATUS.md`'s own headline is *"THE BENCH BOARD IS OVER, AND RADIATED IS THE
TEST THAT APPLIES."*

That promotes §5 from a list of contingencies to **the only available path**:
terminal capacitance at the PV connector (−16.1 dB in the table), the snubber,
and the heatsink bond. **Open question for whoever owns the decision:** whether
a terminal cap at the PV connector counts as "a filter on the device" and is
therefore also excluded. If it does, the −16.1 dB row goes too and the remaining
levers are the snubber, the bond and the edge rate.

**This is harder than "at the limit."** The board as it exists models **+17.5 dB
over** at 30–50 MHz. The radiated-indep estimate above and this one agree on
direction and disagree on magnitude; neither is bench-calibrated, and that is
the point of step 4.

> ### Update 2026-10-12 — the independent estimate landed, and it is *not* +17.5 dB
>
> Merged to `dcdc-tools` main at **`050842c`**, after a Codex review and a fix
> round. Verified against the committed file, not the relay. Central 3 m margins
> (+ = over), nominal two-branch PV source:
>
> | geometry | 30–50 | 50–70 | 70–90 | 90–110 MHz |
> |---|---:|---:|---:|---:|
> | **lh04 (central)** | **−1.7** | **+1.0** | **+0.0** | **+3.8** |
> | fanned harness | −4.8 | +0.2 | +1.1 | +6.1 |
> | 1.0 m run | −2.1 | −3.0 | +2.7 | **+10.2** |
> | isolated AE | +10.3 | +8.1 | +0.8 | +4.1 |
> | 11 nH PV-source **alternative** | +21.7 | +22.6 | +15.3 | +8.8 |
>
> **Read this as "straddling the limit", not as a pass.** The central case is
> within a few dB either way, **setup geometry alone swings it ~10 dB**, the joint
> bounds over the declared ranges are tens of dB wide, and the file states
> *"This is a design-stage margin estimate, not a compliance verdict."* Credible
> to 110 MHz — a real extension over rad300, which §0 records as credible only to
> ~10 MHz.
>
> **The gap to +17.5 dB is now partly explained, not merely noted.** Imposing the
> rad300 PV DM voltage reproduces its PV cable current (31.7 dBµA); PV DM accounts
> for **~18 dB of the 32 dB gap** at 30 MHz, the remainder being closed-form
> antenna vs MoM. So the two decks no longer merely "disagree on magnitude."
>
> **The two-branch bank hypothesis is confirmed and the 11 nH case is now the
> named alternative, not the baseline.** MLCCs carry **94 %** of the loop current;
> the largest J10 equivalent over the declared grid is **1.73 nH**, and the model
> cannot reach 11 nH. It is kept explicitly because the other session's PV DM
> voltage implies it, and under it the board is **+9 to +23 dB over**.
>
> **This changes two lever rows above.**
>
> - **The terminal cap is worth −1.0 dB, not −16.1 dB** — in the nominal case. It
>   is worth **−9.5 dB only under the 11 nH alternative.** The §0 "open question"
>   about whether it counts as a filter on the device is therefore **much cheaper
>   than it looked**: nominally it buys almost nothing, and it is insurance against
>   a hypothesis this model rejects.
> - **The snubber is the lever that works, and `Rs = 1.5 Ω` beats `Rs = Z₀`.**
>   Rs = Z₀ = 3.4 Ω / 4.7 nF gives −6.9/−11.7/−5.2/−2.7 dB and leaves the worst
>   band still **+1.1 dB over**; Rs = 1.5 Ω / 4.7 nF gives −10.4/−17.2/−10.1/−6.9
>   and takes the worst band to **−3.1 dB, a pass.** Both survive the 11 nH case.
>   **Resolved 2026-10-12 — §0 caveat 4.** The two values answer different
>   questions: Z₀ minimises the *ring*; Rs < Z₀ is simply a harder broadband
>   shunt above the branch corner, 20·log₁₀(3.368/1.5) = **7.0 dB** harder, which
>   brackets the observed 3–6 dB. Average dissipation really is Rs-independent
>   (**0.95 W** at 4.7 nF / 72 V), but **peak current is not**: **53.3 A against
>   23.8 A** at an 80 V step, and the model does not represent that pulse as a
>   radiating loop. **Z₀ stays the design value; 1.5 Ω is a bench experiment.**
>   (`ee-1b` left the channel without answering, so this was settled here rather
>   than by the model's owner.)
> - The heatsink strap is −14.6 dB at 90–110 MHz **nominal only** — it disappears
>   entirely under the 11 nH case (−0.9 dB).
>
> **It also adds a bench step that needs no clamp.** The file names the settling
> measurement as **the J10 DM voltage spectrum, or the bank anti-resonance** — a
> voltage measurement with the scope and a probe already on the bench. That
> discriminates nominal from 11 nH, which is the single widest uncertainty in the
> whole estimate, and it is not gated on the €749 purchase.

Three caveats, all from the source:

1. **Not bench-calibrated, by its own statement** — the deck's ring sits at
   25–33 MHz against flu's measured 38 MHz, so *"the changes between cases are
   usable and the absolute margins are not, until plan step 3 (clamp probe)."*
   That clamp probe is §6's purchase, and it gates **three** workstreams: this
   deck's absolute margins, the radiated-indep 110–300 MHz range, and step 4.
   The scope is believed not to be part of that blockage — the MXO44 is reported as 1.5 GHz (§2, a relay) —
   so the clamp is the single remaining purchase on the critical path.
2. **This deck is credible only to ~10 MHz** — `RESULTS-radiated-indep.md` §9
   tabulates *"credible to | **~10 MHz** (their §4.5) | 110 MHz (§3)"*, and notes
   *"their deck rings at ~31 MHz with Q ≈ 2 … their 30 MHz harmonic sits on their
   ring; mine sits on the edge slope below the real ring."* A 30–50 MHz margin
   from a deck credible to 10 MHz, whose ring is 25–33 MHz against a measured
   38–60 MHz, is the sharpest caveat on the +17.5 dB and an earlier version of
   this list omitted it.
3. The rows are cumulative-looking but the terminal-cap and snubber rows do not
   compose monotonically (−16.1 then +9.4 at 30–50 MHz), so **do not read them
   as a stack** without checking the source file.
4. **The snubber row uses Rs = 1.5 Ω**, against the impedance-matched
   Z₀ = √(9.2 nH / 811 pF) = **3.368 Ω** (§5). **Where 1.5 Ω came from is
   unknown** — an earlier version of this note guessed it was the same
   √(L/(C_tank+Cs)) error §5 corrects, but that formula gives **1.29 Ω**, not
   1.5, and would round to E24 1.3 rather than 1.5. The guess was wrong.

   ### Resolved 2026-10-12: Rs = Z₀ and Rs = 1.5 Ω answer different questions

   The independent radiated model finds **Rs = 1.5 Ω beats Rs = Z₀ by 3–6 dB**
   (−10.4/−17.2/−10.1/−6.9 against −6.9/−11.7/−5.2/−2.7 dB) and takes the worst
   band to **−3.1 dB, a pass**, where Z₀ leaves **+1.1 dB over**. That is not a
   contradiction of the Z₀ rule. It is a different objective:

   - **Rs = Z₀ minimises the *ring*.** It is the matched-damping choice for the
     9.2 nH / 811 pF resonance, and that is what §5 adopted it for.
   - **Rs < Z₀ attenuates more *broadband*.** Above the branch corner
     1/(2π·Rs·Cs) the snubber presents essentially **Rs** shunting the node —
     with Cs = 4.7 nF that corner is **10.1 MHz at Z₀ and 22.6 MHz at 1.5 Ω**, so
     across the whole 30–110 MHz scored band both are resistive and the smaller
     resistor is simply the harder shunt. 20·log₁₀(3.368/1.5) = **7.0 dB** of
     extra shunting, which brackets the 3–6 dB the model reports.

   **It is not free, and the free-lunch argument I put on the channel was
   incomplete.** `P_snub = Cs·Vin²·fsw` *is* independent of Rs — **0.95 W at
   4.7 nF / 72 V, 1.17 W at 80 V** — because the capacitor's energy is dissipated
   whatever the resistor. But **peak current is not**: at an 80 V step the snubber
   draws **ΔV/Rs = 23.8 A at Z₀ against 53.3 A at 1.5 Ω**. That current flows in a
   real loop and is added to the FET's turn-on current. So the trade is:

   | | Rs = Z₀ = 3.37 Ω | Rs = 1.5 Ω |
   |---|---:|---:|
   | ring damping | matched | over-damped |
   | HF shunt above corner | 3.37 Ω | **1.5 Ω** (7.0 dB harder) |
   | branch corner, Cs = 4.7 nF | 10.1 MHz | 22.6 MHz |
   | average dissipation @72 V | 0.95 W | 0.95 W |
   | **peak current, 80 V step** | 23.8 A | **53.3 A** |
   | τ = Rs·Cs | 15.8 ns | 7.0 ns |

   **The caveat that decides it is not in the model.** A lumped radiated model
   represents the snubber as a damping element; it does not represent the
   snubber's own 53 A pulse as a radiating loop, nor the added turn-on loss. So
   the reported 3–6 dB is an **upper bound** on what Rs = 1.5 Ω delivers in
   copper, and the margin it buys is real only if the snubber sits **inside the
   commutation loop with negligible added area**.

   **Recommendation:** keep **Rs = Z₀ = 3.37 Ω** as the design value — it is the
   defensible one and it is what §5 and the re-run both use. Treat **1.5 Ω as a
   bench experiment**, not a design change: fit it only if the measured 30–110 MHz
   level needs the extra few dB, and when fitting it check the resistor's pulse
   rating against 53 A, the FET turn-on loss, and the snubber's physical loop
   area. **Open:** the 2.25×-under-matched row in the rad300 table still has no
   stated provenance, and that deck's owner (session `host-7701`, `0774c03e`) is
   not on channel `emc`.

**Use for step 4:** the limit-equivalent CM current is ~8 µA at 30 MHz and
~4 µA at 60 MHz (§6) — that is **0 dB of margin**, not the target. The two models
predict **~8 µA** (radiated-indep, at 40 MHz) and **~60 µA** (+17.5 dB, rad300).
So a reading near 8 µA **falsifies** the +17.5 dB and supports the
radiated-indep central estimate; a reading near 60 µA does the reverse. An
earlier version of this paragraph said a reading "at or above" 8 µA would
*corroborate* the +17.5 dB, which is backwards.

### What the session is for

Not re-measuring the ring. Its unique value is the part no measurement in this
repo has touched yet, in the order the standards basis implies:

1. **Common-mode current on the harness, 30 MHz up.** Every measurement so far
   is differential-mode switch-node voltage. This is the quantity radiated
   compliance is actually set by, and it is unmeasured. **Do this first.**
2. **Whether the known ~60 MHz ring actually couples out** at a level that
   matters, or stays local to the hot loop. This is the same question as (1)
   viewed from the source end, and the ring is the one in-scope resonance known
   to exist.
3. **What is radiating in 15–30 MHz** — broadband edge energy, an unidentified
   resonance, or shortwave ambient. Worth knowing, and cheap once the rig is set
   up, but **no limit currently applies to this band**, so it does not gate
   anything. Resolve it only after 1–2.

---

## 1. What this rig can and cannot decide

A near-field probe into a scope FFT is a **source-location and A/B-delta
instrument**. It cannot produce a dBµV/m number comparable to any limit line —
the probe factor, the near-to-far-field transform and the quasi-peak detector
are all missing. Absolute numbers are arbitrary units that must stay consistent
across a session.

The limit lines this would eventually be compared against are **EN 61000-6-3**
(radiated, from 30 MHz) as Art 16–17 self-assessment evidence, and
**EN 301 489-1/-17** under the RED — not CISPR 32 or FCC Part 15, which an
earlier draft of this section named. See `STANDARD-BASIS.md` §8.6 and §0 above.

Below 30 MHz this content surfaces as *conducted* emissions on the harness,
above 30 MHz as *radiated* — and only the radiated side currently has a limit
applying to it (§0). At these frequencies both are almost certainly common-mode
current on the cables, not direct board radiation, which is why step 4 measures
that current directly.

---

## 2. MXO4 setup

- [ ] Channel input **DC 50 Ω**. The MXO4 offers only `DC 50 Ω`, `DC 1 MΩ` and
      `AC 1 MΩ` — there is **no AC 50 Ω**, and selecting 1 MΩ to get AC coupling
      de-terminates the preamp and voids the calibration. If the preamp's output
      is not already AC-coupled, use an inline DC block.
- [ ] Set external attenuation **−20 dB** in the channel/probe settings so the
      readout refers to the probe output, not the preamp output. Do this
      *before* any data you intend to keep.
- [ ] **Check the preamp for compression in the time domain first.** A 20 dB
      preamp parked over a 72 V switch node clips on the edge and manufactures
      harmonics that do not exist. Back the probe off until the peak is well
      under the preamp's P1dB, then keep that distance fixed for the session.
- [ ] **Approach from far away — and it is the PREAMP that dies, not the scope.**
      ⚠️ Corrected 2026-10-11. The TBWA2/20 dB spec is **max input +10 dBm =
      0.707 Vrms / 1.00 Vpk** (an absolute maximum, *not* a saturation point),
      with output compression at **+20 dBm = 2.24 Vrms**. So the scope cannot be
      driven to its 5 Vrms limit *through this preamp* — the exposed part is the
      **preamp input**, which is destroyed at **1 Vpk at the probe output**. An
      earlier version of this line quoted the scope's 5 Vrms as the threshold,
      which understates the exposure of the part that actually fails by a factor
      of ~5. **Put any attenuator ahead of the preamp input**, and watch 1 Vpk at
      the loop, not 5 Vrms at the scope.
- [ ] Three spectrum setups. The first two mirror the CISPR bands; the third
      exists because the EN 61000-6-3 class B radiated limit **steps up at
      230 MHz**, so 230 MHz has to be reached to know which side of the step
      the content sits on:
      - 150 kHz – 30 MHz, **RBW 9 kHz** — diagnostic only (§0)
      - 30 – 110 MHz, **RBW 120 kHz** (110 to catch FM ambient)
      - 30 – 250 MHz, **RBW 120 kHz** — the span that covers the binding
        region. The scope reaches it with room to spare (1.5 GHz, see below);
        extend to 1 GHz when the probe allows
- [ ] Window **Flattop** for amplitude accuracy; **Hann** to resolve individual
      39 kHz comb lines below 30 MHz.
- [ ] Traces: **Max-hold** primary + a second trace on **average**.
- [ ] Vertical: smallest V/div that does not clip.

### Bandwidth requirements

Two independent arguments set the same floor:

- **The limit line.** Radiated scope is 30 MHz – 1 GHz, and the EN 61000-6-3
  class B limit **relaxes at 230 MHz**. The critical region is therefore
  30–230 MHz, and 230 MHz is a *must-reach*, not a nice-to-have.
- **The ring.** The in-service ring is 59–61 MHz (§0). Distinguishing a
  resonance from an edge comb needs its 3rd harmonic, ~180 MHz.

**So: 250 MHz minimum for every element in the chain, 1 GHz if buying.**

| element | bandwidth | verdict |
|---|---|---|
| **PEM CWT UM/06** Rogowski (already owned, used for the 2026-09-07 CM datum) | **~2 Hz – 30 MHz** | **Unusable here.** 30 MHz is the *bottom edge* of the radiated band; essentially no response at the 60 MHz ring |
| PEM CWTMini50HF | 50 MHz | Still short of the ring |
| any clip-around Rogowski | ~50 MHz ceiling | Ruled out as a family |
| **TekBox TBWA2/20 dB** preamp (owned) | 2 MHz – ≥2 GHz, 20.2 dB @100 MHz, 20.0 @500 MHz, 19.8 @1 GHz | **Not the constraint.** Flat across the whole band |
| **R&S MXO44** | **1.5 GHz** (MXO4-B2415, **instrument-read** — see below) | **Not a constraint.** Covers 30 MHz – 1 GHz entire |

Probe bandwidths are from `~/dev/pv/ee/dcdc-tools/docs/hf-current-measurement.md`
§3.1 and the preamp from §4 of the same document; that file is the canonical
source for current-sensor selection and this table must not drift from it. Note
its §4 already retired the clip-around Rogowski family at the same ~50 MHz
ceiling for the charge work — a different measurement, the same disqualification.

**Scope bandwidth: 1.5 GHz — INSTRUMENT-READ 2026-10-12.** On the MXO 4 the bandwidth is
a licence option (**MXO4-B243 / -B245 / -B2410 / -B2415**) that the base order number
`1335.5050K04` in `bench/probe-setups/*.json` does not reveal, and it was
recorded nowhere in either repo. It is now read off the instrument, and the
relayed answer was right:

```
*IDN?  Rohde&Schwarz,MXO44,1335.5050k04/201239,2.10.2.0
*OPT?  B6,B2415,K36,K510,K520,K530
```

> **B2415 confirmed — 1.5 GHz.** The relay (`ee-1b` on channel `emc`,
> 2026-10-11) is corroborated, and this no longer rests on a second-hand answer.

> ### B6 EXISTS — the signal-generator blocker is closed
>
> **`B6` is the built-in function/arbitrary generator**, open as a question since
> **2026-08-23**. Consequences, in order of value:
>
> - **§7B's ratiometric Z_T self-calibration is now possible.** It needs a source
>   driving the matched line; the scope can be its own. No external generator and
>   no **TBCP2-CAL fixture (≈€548)** — §9C's "skip it" now rests on a capability
>   that is confirmed rather than assumed.
> - **`K36` is also present** — the MXO4 frequency-response-analysis option, which
>   `scope-backends/scope_backends/fra.py` is already written against. With B6 as
>   the stimulus this is a built-in gain/phase sweep.
> - **That may replace the VNA in the J10 bench plan.** `BENCH-j10-dm-voltage.md`
>   lists "find the input-bank anti-resonance with a VNA (NanoVNA-class)" as the
>   unpowered alternative. K36 + B6 is an FRA on the instrument already on the
>   bench — worth trying before reaching for another box. Caveat: FRA sweeps are
>   usually specified over a far lower span than 30–70 MHz, so **check K36's upper
>   frequency** before relying on it.
>
> `K510/K520/K530` are serial-decode options, not relevant here.

Consequences: the 230 MHz limit step is comfortably reachable, the whole
30 MHz – 1 GHz radiated range is in reach, and the scope **no longer gates** the
clamp-probe purchase, the 110–300 MHz switch-node capture, or step 4. The
**probe** bandwidth is now the sole constraint in the chain — §6's ≥250 MHz
requirement stands on its own, and 1 GHz is worth paying for since the scope can
use it.

**Sensitivity is not the problem** — worth the arithmetic, because it decides
whether this rig can say anything quantitative at all. At 60 MHz the ~4 µA
criterion (§6) across a clamp with Z_T = 15 dBΩ (5.6 Ω) gives
4.2 µA × 5.6 Ω ≈ **24 µV**, and after the 20 dB preamp ≈ **240 µV** — tens of dB
above a scope-FFT noise floor in 120 kHz bins. What stands between this bench
and a defensible margin is a **calibrated Z_T**, not sensitivity. That is a much
cheaper problem than it first looked.

### Gating

The ring is present for ~100 ns out of a 25.6 µs period (**~0.4 % duty**).
Un-gated, the FFT averages it down ~45 dB, which is the *correct* CISPR-like
view. For diagnosis use a **gated FFT triggered on the switch edge** to read a
ring's frequency and Q cleanly. Keep gated and un-gated numbers clearly
labelled and never compare across them.

---

## 3. Procedure

1. [ ] **Ambient baseline.** Probe in its fixture, DUT off. Record both bands.
       Expect shortwave broadcast in 15–30 MHz (strong, drifting) and FM at
       88–108 MHz. Anything that also appears here is not yours. This matters
       more than usual: the unexplained band overlaps the shortwave broadcast
       band, so **rule out ambient before theorising about a mechanism.**
       The decisive test is already configured: DUT emissions are a **39 kHz
       comb**, broadcast is not. The 150 kHz–30 MHz / 9 kHz RBW / Hann setup
       resolves 39 kHz lines, so one acquisition settles it — and unlike a
       baseline subtraction it does not depend on ambient staying put.
2. [ ] **DUT off but fully wired.** Separates ambient pickup on the harness
       from converter emission.
3. [ ] **Fix the probe mechanically** and write down position, orientation and
       height. Repeatability dominates; hand-held A/B at 40 MHz is worthless.
4. [ ] **Common-mode current on the harness — do this first.** This is the
       measurand radiated compliance is set by (§0), and the one quantity with
       no prior data anywhere in this repo. Work **30 MHz and up**; that is
       where the radiated limits begin.

       **Clamp complete pairs, never a single conductor.** Take three readings:
       the **PV pair**, the **battery pair**, and the **whole bundle**. A clamp
       around a complete pair already rejects the differential current (equal
       and opposite, so it cancels) — *the pair reading is the common-mode
       measurement*, and the per-bundle split is what the radiated models want.

       > **Do not clamp one conductor on a live converter.** An earlier version
       > of this step said to, for a bundle-vs-individuals comparison. That is
       > both unnecessary — a pair clamp is already CM-selective — and a real
       > hazard here: Fugu2 runs to **33 A**, and the sourced clamps carry a
       > **3 A RF rating with no DC saturation spec** (`ee-1b`, 2026-10-11, from
       > the TBCP2-750 manual). A single conductor presents the full DC load
       > current to the core, which saturates it: the reading becomes nonsense
       > *without looking wrong*, and the part may not survive. A complete pair
       > puts net DC ≈ 0 through the aperture, which is why the pair is also the
       > electrically safe choice.

       If a DM magnitude is genuinely wanted for comparison, get it from the
       SW-node voltage work already in the No-Coil study, not by threading a
       power conductor through an RF clamp.
5. [ ] **Locate the in-scope source, 30–110 MHz.** Only content above 30 MHz has
       a radiated limit. The known ~59–61 MHz ring sits in it, and the
       independent radiated estimate (§0) puts its band peak at **106 MHz**, so
       do not stop at the ring. H-loop over each candidate in turn, three
       orientations, comparing the level in the peak:
       - the **LS FET tab → heatsink → H1 screw bond**, at **30–70 MHz**. The
         LS drain tab *is* the switch node, and in the horizontal
         bottom-heatsink mount it presents a large area to the heatsink; the
         displacement current returns through the H1 screw. Predicted by
         `dcdc-tools` `emc/radiated-indep/RESULTS-radiated-indep.md` as the
         dominant 30–70 MHz mechanism. Probe the tab, the heatsink face and the
         screw path separately; an E-probe on the heatsink distinguishes it from
         a loop-local source.
       - a **board–heatsink–toroid structure resonance near 100–106 MHz**, the
         band peak of that same estimate, described there as
         damping-limited. Expect it to move when the heatsink bond or the coil
         position changes — which is also the test that identifies it.
       - the **Cin bank** — electrolytic ESL against the HF ceramics. The
         No-Coil study found the bank composition dominates the SW peak
         (9-cap bank 77 V vs ceramics-only 91 V vs bulk-only 82 V) and flagged
         **bulk-only beating ceramics-only as physically backwards** at
         50–60 MHz, pointing at a wrong per-cap ESL default. Seeing a resonance
         does not by itself indict that default — instead **measure the bank's
         anti-resonance frequency and back out the effective branch ESL**, then
         compare it to the per-cap value. That closes the ±14 V composition
         sensitivity the No-Coil study flagged. Best single lead in this
         session, and it lands in the band that counts.
       - the **gate / bootstrap loop**.
       - **current-sense routing**, connector and harness entry.
6. [ ] **PV-port (J10) differential voltage spectrum, 30–70 MHz, at load.**
       Requested by the radiated-estimate work as the measurement that would
       settle the **≈18 dB disagreement** between its two models at 30 MHz
       (§0), which differ here by 60–62 vs ~86 dBµV. Note this is a **model input, not a
       compliance measurement** — §0 explains why the DC port currently carries
       no conducted limit. Use the DC-blocked 50 Ω path from §2 and mind the
       72 V common-mode offset at the connector.
7. [ ] **H1 screw-bond impedance.** VNA across the bond if you have the
       fixture; otherwise near-field over the FETs and the heatsink, comparing
       the bond as fitted against a deliberately degraded one (loosened screw)
       and an improved one (added strap). Worth **+18/−14 dB at 70–110 MHz** in
       the radiated estimate — the largest single term in its table, and the
       reason the heatsink bond is now a lever in §5.
8. [ ] **Sweep operating points** with max-hold: full load, light load,
       CCM/DCM boundary, across the MPPT range. Note that **the bias-shift test
       does not work over the MPPT range** — across 55–80 V the ring moves
       59→61 MHz, ~3 %, inside trace width and probe repeatability, so a null
       result would be misread as "different loop". To use bias as a
       discriminator you need a **bench supply down to ~35–40 V** (ring 52→54
       MHz), not the MPPT range.
9. [ ] **Diagnostic only — characterise 15–30 MHz.** No radiated limit reaches
       this band, and no conducted measurement is made at either DC port (§0),
       so **nothing here gates compliance**. Do it last, and only
       because the rig is already set up. Decide from the trace shape whether it
       is *broadband* (edge energy — expect a smooth −20 dB/dec envelope above
       the 20 MHz knee) or *peaked* (a resonance). If peaked, the coil is the
       obvious suspect, but check the arithmetic first: `HW Stories/flu.md` gives
       **L0 = 83 µH**, so a plausible 5–20 pF winding capacitance puts the
       fundamental SRF at **3.9–7.8 MHz** (an earlier draft said 2–8 MHz; 2 MHz
       would need 76 pF), not in this band; you would need 0.76 pF
       to reach 20 MHz. It only lands here if the core permeability has rolled
       off hard by then. Note also that the No-Coil study **retracted** an
       "~18–19 MHz coil self-resonance" as a bad cursor read — a different
       claim, but the same number in the same band. A 10-minute VNA or ring-down
       sweep of the bare coil settles it without any converter bench time.
       Should the test house reject the "not a DC power network" reading (§0),
       this step is promoted to a compliance item.

---

## 4. Ring analysis tooling

`spice/ring_analysis.py` carries the digitized Coss(V) curves (from
`pwr-mosfet-lib`, datasheet-anchored and Qoss-validated) and the chord-over-
actual-swing effective capacitance the No-Coil study calls for.

> ✅ **RESOLVED 2026-10-12. The capacitance model was open; it is now closed,
> and the answer is that it barely matters.** This block previously warned that
> every frequency and Z₀ in the document inherited an unresolved model. That
> warning was correct to raise and **overstated the magnitude by about 2.6×**.
>
> **What was wrong.** `c_eff_pf` offered a charge chord, with two defects: the
> integrator used to check it was broken — it returned **282 pF where the exact
> answer for a constant 800 pF capacitor is 800 pF** — so neither the chord nor
> the small-signal model had ever been validated against anything; and two call
> sites disagreed about the excursion (`dfreq` passed the upper half `[Vin, Vpk]`,
> `bias`/`solve`/`snub` passed a symmetric swing).
>
> **The fix.** `c_eff_exact_pf` implements the **exact anharmonic period
> integral**. For a lossless L with nonlinear C(v) released at the upper turning
> point, energy conservation gives
>
> `T = 2·√(L/2) · ∫ C(v) dv / √(E − U(v))`, with `U(v) = ∫ (v′−V_eq) C(v′) dv′`
>
> and `C_eff` from `T = 2π√(L·C_eff)` — in which **L cancels**, so the result is a
> pure property of `C(v)` and the swing. The integrand is inverse-square-root
> singular at *both* turning points; writing `E − U = (v_max−v)(v−v_min)·h(v)` and
> using **Gauss–Chebyshev** quadrature absorbs both exactly and evaluates only at
> interior nodes. The lower turning point is **solved for**, not assumed, so the
> steeper Coss below the plateau is included — defect 2 closed as well.
>
> **Validated on the case the old code failed:** `ring_analysis.py selftest`
> returns **800.00 pF (0.000 %)** for a constant 800 pF capacitor at ±5, ±10 and
> ±30 V swing.
>
> **Magnitude, re-measured across all three models** (`--cmodel exact|chord|small-signal`):
>
> | quantity | exact | chord | small-signal |
> |---|---:|---:|---:|
> | `bias` best single L | **9.18 nH** | 9.16 nH | 9.16 nH |
> | `bias` spread | 13.6 % | 13.3 % | 14.5 % |
> | `predict` f_ring, LS tank @72 V | 59.9 MHz | 59.9 MHz | 60.0 MHz |
> | `predict` Z₀ | 3.47 Ω | 3.46 Ω | 3.47 Ω |
>
> **L moves by 0.2 % and Z₀ by 0.3 % across the whole model choice.** The
> 9.2 nH anchor still lands at 1.00×. Vin→f_ring is worst at low bias and still
> small: the spread is **1.25 MHz (3.0 %) at 28 V**, falling to 0.05 MHz (0.1 %)
> at 72 V — and at 28 V the exact answer is **42.0 MHz, which agrees with
> small-signal, not with the chord (40.7)**.
>
> **Correction to the previous version of this block:** it claimed the switch to
> small-signal moved the 28 V point by **3.7 MHz (8 %)**. That does not
> reproduce; the real figure is **1.25 MHz (3.0 %)**, and the earlier number was
> produced while the broken integrator was still in the path. The in-service span
> stays **55–65 MHz**.
>
> **So:** the §0 Vin→f_ring table, Z₀ = 3.37 Ω, the `bias` table, the snubber
> table and discriminator 3 are **robust to this choice** and no longer carry a
> ±8 % model caveat. The remaining uncertainty in them is the datasheet Coss
> curves themselves and the swing assumption, not the effective-capacitance
> definition.

```sh
python3 spice/ring_analysis.py bias      # fit ONE L to the measured f(Vin) series
python3 spice/ring_analysis.py dfreq     # plan the external-cap delta-f test
python3 spice/ring_analysis.py --vin 60 --swing 14 dfreq --f1 58.5e6 --f2 46e6 --c-add 470
python3 spice/ring_analysis.py snub      # L, C_tank -> RC snubber
```

**`bias` result — weaker than it first looks.** A single loop inductance of
**9.16 nH** fits the three measured bias points with a **13.3 % spread in the
per-point L**:

| Vin | V_pk | chord C | L implied | f @ 9.16 nH | err |
|---|---|---|---|---|---|
| 20 V | 24.1 V | 2200 pF | 8.41 nH | 35.4 MHz | −4.2 % |
| 40 V | ~54 V | 909 pF | 9.63 nH | 55.2 MHz | +2.5 % |
| 60 V | 74 V | 783 pF | 9.45 nH | 59.4 MHz | +1.5 % |

**Quote the spread, not the frequency residual.** Because f ∝ L^(−1/2), the
±4 % residual column is *algebraically* the 13.3 % L spread halved by the
square root — it is guaranteed by construction and carries no information the
spread does not. What the spread actually says is that the datasheet curve
predicts C(20)/C(60) = 2.82 while the measurements demand (58.5/37.0)² = 2.50:
**the curve shape and the data disagree by ~13 % in C-ratio.** A ±1–2 ns cursor
error on the 20 V point's 27 ns period is ±8–15 % in L on its own, so the whole
spread sits inside the uncertainty of the one point that was already re-measured
after a 2× retraction. **The bias series cannot resolve L better than ~±15 %**,
so "1.00× the 9.2 nH anchor" is spurious precision.

**And it does not do what I first claimed.** The discrimination against 13.2 nH
does survive — 13.2 nH predicts 49.5 MHz at 60 V against 58.5 MHz measured, a
gap no plausible Coss error closes. But that comes from the **absolute** Coss
anchor at the single 60 V point, which the No-Coil study already had. The bias
series by construction tests only C *ratios*, so it is not what favours the
~4 nH copper. What the series *does* add is a **FET-identity discriminator**:
re-fitting the same three points under each build gives a spread of **13.3 %
(`measured`), 17.5 % (`fitted`), 30.3 % (`schematic`)** — re-run from the script
2026-10-11, superseding a stale "13.3 / 26.6 / 35.2 %" quoted in an earlier
version here and in §8. At 17.5 % the `fitted` build is much closer to
`measured` than the stale figure implied, so **this discriminator is weaker than
it was claimed to be**; §8's other two are the load-bearing ones. See §8.

**`dfreq` — the real closure (open item #1).** Solder a known C0G across the
switch node and re-measure; both unknowns fall out with no datasheet Coss at
all. Planner output at 60 V:

| C_add | f1 | f2 | shift |
|---|---|---|---|
| 470 pF | 58.3 MHz | 46.4 MHz | −20 % |
| 1000 pF | 58.3 MHz | 39.0 MHz | −33 % |

Aim for 20–45 %. **Do two values, 470 pF *and* 1 nF.** That over-determines the
system and lets you solve for the mounting ESL instead of merely bounding it —
which matters, because the two error terms pull opposite ways: going from
470 pF to 1 nF halves the Coss-nonlinearity error (≈5 %→2.5 %) but *increases*
the ESL error by ~50 %. Neither value is simply "cleaner".

Three cautions:

- **The dominant error is the mounting loop, not the package.** A 0402's own
  ESL is ~0.3–0.5 nH; the tab-to-source mounting loop is 1–3 nH however small
  the chip. That inflates the extracted L by ~0.4–1.3 nH, so treat it as an
  upper bound. Shortest possible path, and C0G — X7R loses most of its value at
  60 V DC bias.
- **The overshoot will grow.** The No-Coil study's own explanation for the
  benign 1.2× peak is that the 15.8 ns rise ≈ one ring period, so the edge only
  weakly excites the tank. Adding 470 pF lengthens the period 26 %, 1 nF by
  48 %, while the edge stays put — by that same mechanism the tank gets excited
  *more*. On an 80 V-rated LS this is a real avalanche risk. **Start at 60 V,
  not 72 V, and watch the peak before and after each cap.**
- **The "same C" assumption holds, but not exactly.** The chord is flat against
  swing (−5 % from ±2 V to +30 V), so the bias is ≤5 % in L at 470 pF and
  ≤2.5 % at 1 nF, and its direction is known: a larger overshoot makes the
  extracted L read **low**.

---

## 5. Levers

Retitled 2026-10-11: this was *"Levers, if something needs fixing."* With an
independent estimate putting the shipping configuration **at** the class B limit
(§0), the burden has flipped — the question is no longer whether there is a
problem but whether there is margin. Treat these as candidate fixes to be
costed, not contingencies.

- **The heatsink bond — the largest single term.** `RESULTS-radiated-indep.md`
  §"mechanism" puts a low-inductance bond (a strap, or several screws) at
  **−6 to −14 dB** at 70–110 MHz, against **+7 to +18 dB** for a long or
  anodised screw path and **+17 dB** for a floating heatsink. That is a wider
  swing than any circuit lever below, and it is mechanical: strap, screw count,
  and whether the mating faces are anodised. Measure it before changing it
  (step 7) — the sign of the current bond is unknown, so this is as easily
  already-good as it is broken.
- **Slow the edge.** The 15.8 ns rise is already ≈ one ring period, which is
  *why* the real board's overshoot is modest. Rg is the cheapest EMI knob here
  and its cost is quantified in `spice/loss_budget.py`. Check this before
  reaching for a snubber.
- **Snubber** — `ring_analysis.py snub`. At 9.2 nH / 811 pF (Z₀ = 3.4 Ω,
  matching the No-Coil doc):

  | Cs | Rs | damped f | P_snub @72 V |
  |---|---|---|---|
  | 820 pF | 3.3 Ω | 42 MHz | 0.16 W |
  | 1.5 nF | 3.3 Ω | 35 MHz | 0.31 W |
  | 3.3 nF | 3.3 Ω | 26 MHz | **0.67 W** (0.82 W at 80 V) |

  **Rs = √(L/C_tank) = Z₀ = 3.4 Ω, independent of Cs** — the impedance-matching
  rule from the Toshiba app note already cited in [EMI Parasitics
  Snubbers](<EMI Parasitics Snubbers.md>). Solving the actual L–C‖(Rs+Cs) cubic
  puts this within a few percent of the damping optimum for Cs ≥ 2·C_tank. An
  earlier version of this document used √(L/(C_tank+Cs)), which is ~2× too low
  and delivers about half the damping — do not use those values.

  A snubber also moves the loaded tank's frequency **down**. ⚠️ **Do not count
  that as a second benefit — retracted 2026-10-11.** An earlier version claimed
  pushing the ring to 27 MHz moves it *"below the 30 MHz radiated floor"* and
  that *"the damping and the frequency shift both help."* Two reasons that does
  not follow. (a) The "damped f" column is the **undamped** frequency of the
  loaded tank, 1/(2π√(L(C_tank+Cs))); at Rs = Z₀ the circuit is near critically
  damped, so there is **no narrow line there at all** — the response is a broad
  skirt, and lowering Q *widens* it, so content above 30 MHz is reduced rather
  than removed. (b) The 30–60 MHz content here is substantially **edge-driven**,
  not ring-driven (§0: the 20 MHz knee, −20 dB/dec above), and a snubber barely
  moves the edge. **Count the damping as the benefit; treat the frequency shift
  as unproven.** A lower ring frequency is also not automatically a lower
  *radiated* field if it lands on a harness resonance — confirm with the current
  probe (§6).
  C0G only; check the
  resistor's *pulse* rating (72 V / 3.3 Ω ≈ 22 A per edge, 24 A at 80 V), not
  just average power — that note calls for 2 W.
- **Package, not copper.** ~4 nH of the ~9 nH loop is TO-220 source
  common-source inductance — a *measured package floor*, irreducible by lead
  trimming or mount. Only an SMD half-bridge removes it.
- Re-measure at the **same fixed probe position** and quote the delta in dB.

---

## 6. Closing the quantitative gap

Rule of thumb for a 1 m cable against class B: roughly **8 µA of common-mode
current at 30 MHz, ~4 µA at 60 MHz**, from E = 1.26×10⁻⁶·I·f·L/d. The figure
survives the change of standards basis in §0: FCC class B (40 dBµV/m at 3 m)
gives 3.97 µA at 60 MHz and EN 61000-6-3 class B (30 dBµV/m at 10 m) gives
4.18 µA — the two limit lines are near-equivalent here, so the target does not
move. A near-field loop cannot read µA — no calibrated transfer impedance. If
the number has to be defensible:

- a **clamp-on RF current probe** with a published Z_T — the clean answer, though
  see the free path below before ordering. It reads the quantity that binds
  (step 4), in the band that binds, and converts the near-field work into a
  defensible margin. **Accuracy needed is only ±3…6 dB**: the job is to
  discriminate 18.1 vs 31.7 dBµA and to compare against ~8 µA / ~4 µA, and this
  rig cannot produce a limit-comparable number regardless (§1). Three
  requirements, in order:
  - **≥250 MHz bandwidth** (§2). This rules out the **whole Rogowski family**,
    including the CWT UM/06 already on the bench at 30 MHz. The sensor class is
    an EMC clamp or a wideband current transformer, *not* a Rogowski.
  - **A bore that passes the whole harness bundle.** Step 4 clamps the bundle,
    which disqualifies most single-wire CTs — the Tek CT-2 makes 200 MHz but its
    aperture takes one conductor.
  - **A published transfer-impedance curve**, which is what turns volts into
    amps — and a *high* one, because Z_T sets the sensitivity directly.

  **Sourced 2026-10-11** (`dcdc-tools emc/SOURCING-rf-current-probe-20261011.md`,
  commit `a44fc4b`) — vendor-checked, not yet ordered:

  | part | Z_T (30/60 MHz) | band | DC / RF | price, stock |
  |---|---|---|---|---|
  | **TBCP2-30M1000** snap-on — **recommended** | **22.1 / 23.6 dBΩ** | −3 dB 30–900 MHz; char. 10 kHz–1 GHz | **>50 A DC, 10 A RF, 50 A pulse** | **€749 excl., eleshop `InStock`** |
  | TBCP2-750 snap-on | 20.0 / 20.1 dBΩ | −3 dB 1.5–850 MHz | DC **not specified**, 3 A RF | €769 eleshop `InStock`; €729 calplus *Bestellware* |
  | TBCP4-750 solid core | 20.1 / 20.2 dBΩ | as above | DC not specified, 3 A RF | ≈€579 eleshop / €635 Batronix, in stock |
  | TBCP2-CAL calibration fixture | — | — | — | €548 net, Batronix, in stock |

  At 22.1 dBΩ = 12.7 Ω the 8 µA limit-equivalent gives **101 µV** at the scope,
  ~40 dB over the MXO44 floor **with no preamp** (the source assumes −2.2 dBµV in
  120 kHz RBW at 2 mV/div). Sensitivity is a solved problem.

  Two corrections to earlier versions of this list: the **Pearson 6585** is
  **−6 dBΩ** = 0.5 Ω, so 8 µA yields 4 µV — **26 dB worse** than the recommended
  part and the real reason to avoid it, not price. And **Fischer F-33-1 is
  discontinued** (new; used units exist). An earlier draft also named a
  "TBCP2-250" that does not exist.

  ⚠️ **Choice reverted 2026-10-11 — and the reasoning that moved it was wrong.**
  An earlier version of this section argued the **TBCP2-750** dominated, on the
  grounds that the 30M1000's 25 MHz low corner *"cannot see the 780 kHz CM
  excursion (~+10 dB over EN 61000-6-3 Table 3 AV), the only conducted excursion
  anyone has quantified."* **That excursion does not exist.**
  `dcdc-tools emc/RESULTS-batport-20261010.md` §1c gives that line as
  **−10.3 dB at 0.780 MHz — a 10.3 dB PASS**, and §1b states in its own words:
  ***"CM is never the binding quantity: the battery-port emission is differential
  ripple."*** So the figure was sign-flipped *and* the wrong mode. With the
  premise gone, the **30M1000 wins on every axis that matters**: 2–3.5 dB more
  Z_T across 30–60 MHz, a specified **>50 A DC / 10 A RF / 50 A pulse** rating
  where the 750 specifies no DC at all, in stock, and cheaper than the 750 at the
  same vendor. The sourcing file's own pick was right and this document should not
  have talked itself out of it.

  **It is in stock.** An earlier version said *"nothing shows real stock — all are
  order-in … the clamp is weeks away whichever vendor is used,"* and used that to
  argue for deferring the purchase. `emc/SOURCING-rf-current-probe-20261011.md`
  records **eleshop `InStock` at €749** (schema.org flag on the page), which that
  draft missed by pricing only calplus and Welectron. The self-calibration below
  is still worth doing — but because it is free and immediate, not because the
  part is unobtainable.

  **Caliper the bundle OD before ordering** — the 32 mm bore is an assumption.
- an **artificial mains network** for the 150 kHz – 30 MHz conducted side — **lower
  priority, but not dismissable.** No conducted measurement is required at
  either DC port (§0), so a LISN buys no compliance number. Two things keep it
  on the list:
  - The relief rests on the **"not a DC power network" interpretation**, which
    is open with a test house (§0). If that reading is rejected, a LISN becomes
    mandatory rather than useful.
  - The modelled battery-port worst case is **+3.88 dB at 0.156 MHz,
    differential, on BT+** with an assumed 15 nH C10 ESL — and it **passes by
    2.8–3.1 dB** at Chemi-Con's 8 nH vendor value
    (`RESULTS-batport-20261010.md` §1a/§1c). So there is something to confirm
    down there, but it is a near-pass rather than an exceedance, and it is
    **differential, not common mode**.

  ⚠️ **Retracted 2026-10-11.** An earlier version of this bullet claimed the
  battery lines modelled *"~+10 dB over EN 61000-6-3 Table 3 AV at 780 kHz,
  common mode."* Both halves are wrong: that figure is **−10.3 dB, a pass**, and
  the mode is differential — *"CM is never the binding quantity: the battery-port
  emission is differential ripple"* (§1b, verbatim). It had also become the sole
  argument for the TBCP2-750 over the 30M1000 (above), so it propagated into a
  purchase recommendation before being checked.

  **If one is ever bought, the network must match the route.** EN 61000-6-3
  Table 3 — the route chosen in §0 — specifies a **50 Ω / 50 µH V-AMN**
  (Tekbox TBL5032-1 per line, TBL50100-1B for the battery side). The 150 Ω
  **DC-AN** (TBLDC32-2) is the **CISPR 11 / EN 55011** network and would be the
  wrong instrument here; an earlier version of this line named it. And TBLC08 is
  an 8 A **AC** LISN, wrong on both counts. Correction from `LISN-70ec` on
  channel `emc`, 2026-10-11.

  Whether that justifies the purchase is a judgement call, not a technical one:
  the radiated path can be closed with the current probe alone.

The current probe alone turns this from "relative" into "here is the margin" on
the binding path, for a fraction of a chamber slot.

### Calibrating a probe you already own — the free path

**You may not need to buy a probe to answer the question in front of you.** What
step 4 needs is a *known* transfer impedance, not a purchased one. Z_T can be
measured on this bench, ratiometrically:

Use a **matched line**, with the scope's own 50 Ω input as the load — see §7B for
the wiring and the one mistake that silently zeroes it:

> **Z_T(f) = V2(f) / I(f) = 50 Ω · V2(f) / V1(f)**,  with `I = V_Ch1 / 50 Ω`

Source amplitude, drift and distortion appear in both numerator and denominator
and **cancel** — nothing about the generator needs to be calibrated, which is the
whole point. What must be trusted is the 50 Ω termination and the MXO44's
channel-to-channel match, neither of which is a concern here.

**Superseded:** an earlier version of this section used a lumped series resistor
`R_s` with Ch1 across it, carried over from `PROCEDURE-clamp-ac-gain.md`. That is
right at **39 kHz** and wrong here — at 30–250 MHz the resistor's own leads and
the unterminated line introduce exactly the frequency-dependent error the
procedure's Kelvin-sense warning is about. The matched line removes the resistor
from the problem entirely.

**The source is the blocker, and it is not new.**
`~/dev/pv/ee/plans/BENCH-clamp-ac-gain.md` is *"BUILT, NOT RUN — blocked on
equipment"* for the 39 kHz version of this same ratiometric method, and has been
since **2026-08-23**. Its stated first action still stands: power the MXO and
check for the **-B6** arbitrary-generator option. A single `*OPT?` answers that
*and* confirms the MXO4-B2415 bandwidth (§2) — **done 2026-10-12, see §2**.

If -B6 is absent, an **Si5351 breakout (~€8)** driven over I²C from the `rpi.local`
that already hosts the bench closes it: a programmable square-wave clock to
~200 MHz. **Prefer a stepped single tone over a harmonic comb** — a comb's 1/n
amplitude rolloff and harmonic ambiguity buy nothing when the source is
programmable.

*Withdrawn:* an earlier version of this section proposed using the HaasoscopePro's
**FPGA** as the source. That is wrong — the FPGA runs the acquisition gateware,
so using it as a generator means replacing the firmware that
`scope_backends.haas` depends on. The Pro is a *measuring* instrument here
(2 channels, 3.2 GS/s, 2 GHz nominal, scriptable over TCP 32001 at `rpi.local`,
contract-compatible with the MXO backend). Two cautions from
`dcdc-tools/bench/HAASOSCOPE-BACKEND-BRIEF.md`: `downsamplefactor > 1` decimates
and **aliases a 55 MHz ring**, and `ATT` doubles as an **800 MHz antialias
filter**.

**Reuse the execution constraints already learned** in
`dcdc-tools/verifications/flu-coil/PROCEDURE-clamp-ac-gain.md` — they transfer
verbatim and were paid for once already:

- **Kelvin-sense across the resistor body only.** Sensing across the loop puts
  its inductance in the denominator, where |Z| rises with frequency and the probe
  appears to sag — *"an error with the sign and shape of the measurand."*
- **Both channels across the shunt** at least once, to turn channel asymmetry
  from a declaration into a measurement.
- **Low-inductance resistor, ~0.5–2 Ω. No wirewound.**
- Calibrate the **range and geometry the real run will use**; a bound does not
  transfer between them.

**The catch, and why a clamp is still worth buying eventually.** An H-loop reads
dΦ/dt, so its Z_T depends strongly on geometry and orientation. The calibration
only transfers if the measurement repeats the calibration geometry exactly —
**calibrate around a single wire, then clamp a 20 mm bundle, and it does not
transfer.** A clip-around clamp is far less sensitive to this. *Geometry
insensitivity, not accuracy, is the real argument for the purchase* — the
accuracy needed here is only ±3…6 dB (above).

Sequence this way: calibrate the existing loop, run step 4, and see whether the
CM current sits near 8 µA at 30 MHz or ~13 dB above it. That resolves the
+17.5 dB and discriminates the two models. Buy the clamp once there is a known
problem to size, not a modelled one.


---

## 7. Wiring

### 7A. Current clamp → scope, for step 4

```
   harness pair (PV+ & PV−, or BAT+ & BAT−)   — never a single conductor (step 4)
        ║  clamp snapped around BOTH conductors
        ╚══[ TBCP2-30M1000 ]── N(f)
                            │  N(m)→BNC 50 Ω coax, run perpendicular to the
                            │  harness and away from the board
                     MXO44 Ch1: DC 50 Ω
```

- **No choke in this chain.** The clamp is a current transformer — no galvanic
  path to the DUT, so the §7D common-mode problem does not arise, and a choke
  would only add an uncharacterised term to the Z_T the dBµA conversion uses
  (§9B).
- **`DC 50 Ω`.** The clamp's 22 dBΩ is specified into 50 Ω; terminating in 1 MΩ
  invalidates the Z_T you are about to apply. The output is transformer-coupled,
  so there is no DC to block.
- **The clamp output is N female** (Tekbox spec table, all TBCP2 models). The
  MXO44 inputs are BNC, so an **N(m)→BNC(m) 50 Ω cable** is needed and is not a
  thing that turns up in a drawer. Sourced: Tekbox RG223/U 75 cm, €18.97,
  `ELE002492` — see §9A item 2. Order it with the clamp.
- **No preamp, and no attenuator either.** 8 µA gives 80–101 µV, ~40 dB over the
  scope floor in narrow RBW. The TBWA2 would add a 20 dB calibration term and a
  compression risk for nothing — and its own **1 Vpk input limit** is the thing
  that dies first. An earlier draft of this bullet said to "start with a 10–20 dB
  inline attenuator", which contradicts the 0 dB entry below; it is **struck**
  (§9C). Nothing in this measurement can overload a 50 Ω input.
- **External attenuation 0 dB; record raw dBµV.** The manual's conversion is a
  straight subtraction:

> **dBµA = dBµV (scope) − dBΩ (clamp, at that frequency)**

which is why the 780 kHz point needs ~13.6 dBΩ and not the 20 dBΩ plateau (§6).

### 7B. The Z_T calibration jig

```
source ──coax── [centre conductor through the clamp jaw] ──coax── MXO44 Ch1 (DC 50 Ω)
                 shield routed OUTSIDE the jaw                     ↑ this IS the 50 Ω load
                           ║
                    [ clamp ] ── Ch2
```

`I = V_Ch1 / 50 Ω`, so `Z_T(f) = 50 · V_Ch2/V_Ch1`. No resistor to characterise
and no standing waves.

> **The shield must run outside the jaw.** If the clamp encircles the centre
> conductor *and* its shield return, the two currents cancel and the reading is
> ~zero — which looks like a dead probe rather than a wiring error. Eliminating
> that is the entire job of Tekbox's TBCP2 calibration fixture (§6).

### 7C. Two checks before believing any number

1. **Open-jaw null.** Unclip from the bundle, leave the coax routed exactly as
   it was, re-acquire. What remains is pickup on the cable and clamp body. If it
   is not well below the reading, the measurement *is* the pickup.
   `BENCH-flu-coil.md` latches `unverifiable` on this, which is the right
   instinct.
2. **Sum check.** PV pair + battery pair should be comparable to the
   whole-bundle reading. A bundle reading far *below* both means the two CM
   currents partly cancel — worth knowing before attributing anything to one
   cable.

### 7D. PMK UFCS coaxial shunt → scope

Not part of the EMI procedure, but the same interface question.
`dcdc-tools/docs/hf-current-measurement.md` §3.3 is the reference.

```
UFCS (SMA female) ──[ SMA(M)–SMA(M) 50 Ω coax, RG316/RG405, 0.5–1 m ]──
                              └─[ SMA(F) → BNC(M) adapter ]── MXO44, DC 50 Ω
```

- **Mount with `SHLD` toward BuckGND.** Ground-referenced, so **no galvanic
  isolation** is needed. That doc states isolation *is* required *"when `SHLD` is
  on a hot node"* — and if `SHLD` ever lands on the switch node, the coax shield
  shorts SW to scope ground.
- **Mind the genders.** The UFCS output is SMA **female**; the cable must be
  male at that end, and the adapter is SMA(F)→BNC(M).
- **The common-mode choke IS required — and specifically *for* the
  ground-referenced mount.** ⚠️ **Corrected 2026-10-11.** An earlier version of
  this section said a ground-side mount made the choke unnecessary. That is the
  exact error `hf-current-measurement.md` §6.3 already made and retracted, in
  bold: *"**A common-mode choke IS wanted, and specifically FOR the
  ground-referenced case.**"* The UFCS manual (Rev 02A p. 13) is explicit —
  *"when performing a ground-referenced measurement it is highly recommended to
  place a common mode choke … between the UFCS and the oscilloscope."* The reason
  the intuition fails: *"the sense point being at circuit ground does not make
  circuit ground quiet against scope earth"* — a switching board's ground moves
  against earth through parasitic capacitance, and that CM current returns along
  the coax shield into a signal that is only tens of mV.

  **Galvanic isolation and the CM choke are different requirements.** The
  ground-side mount removes the first and *keeps* the second. §3.3 of that file
  says **"budget the choke in by default … the case where it is most tempting to
  assume it is unnecessary."**

  So a choke is a real line item, and the realistic single-channel cost is
  **shunt + choke ≈ €830–975**, not €385 + €10. **Sourced 2026-10-11 (§9B): buy
  the Tekbox `TBCMC-1` at €445, not PMK's `UFCS-CHOKE` kit at €590** — same
  order as the clamp, >60 dB CMRR to 1 MHz where the 780 kHz CM actually sits,
  and the only one of the two that publishes a **CM saturation current (500 mA
  typ) but publishes no time-domain spec. **Decided 2026-10-11: the PMK
  `UFCS-CHOKE` at €590**, because ns-scale current edges are in scope and the
  Tekbox part's 10 % reflection then lands an echo inside the feature of interest
  (§9B). Not for bandwidth — the PMK assembly's 1 dB bandwidth is 750 MHz against
  Tekbox's <0.6 dB at 1 GHz.

  **Snap-on ferrites are not a substitute at the frequency that matters.** The
  measured CM current on this board is **67.5 mA at 0.78 MHz**
  (`RESULTS-cm-bench-first.md:60`, *"strongest harmonic 67.5 mA at 0.7799 MHz,
  n = 20; peak instantaneous 6.05 A"*) — an earlier version of this section
  misattributed it to 16.38 MHz, which is a different quantity. A clip-on ferrite
  has useful impedance at 16 MHz and essentially **none at 780 kHz**, so "€10 of
  ferrite covers most of it" was wrong at the real frequency.
- **`D010031` (50 Ω BNC feedthrough, €48) is not needed, for the source's
  reason:** it is for 1 MΩ-input scopes, and the MXO44 has a native 50 Ω input.
  An earlier draft replaced that correct reason with a weaker one — that the
  shunt cannot produce a dangerous level. The signal-level arithmetic is right
  (`UFCS-R001` at its 1250 A pulse rating gives **1.196 V**, inside 5 Vrms) but
  it answers the wrong question: the case for a sacrificial terminator would be
  a *fault*, not the designed signal — an open shunt or a mis-mounted `SHLD` puts
  the full 80 V rail on the input. See 7E for why 1 MΩ does not buy protection
  against that at HF either.

### 7E. MXO44 input coupling — the real numbers

From the MXO 4 spec sheet (`farnell.com/datasheets/4026299.pdf`, fetched
2026-10-11). The 1 MΩ path is **not** limited to 200 MHz on this unit; that is
the base model:

| config | 50 Ω | 1 MΩ |
|---|---|---|
| base MXO 4 | — | ≥ 200 MHz |
| -B245 | 500 MHz | ≥ 500 MHz |
| **-B2415** (**confirmed by `*OPT?` 2026-10-12**) | **≥ 1.5 GHz** | **≥ 700 MHz** |

Max input, **quoted in full** — the derating clause is the whole story:

> at 1 MΩ: **300 V (RMS), 400 V (Vp), derates at 20 dB/decade to 5 V (RMS)
> above 250 kHz**
>
> at 50 Ω: **30 V (Vp), 5 V (RMS)**

⚠️ **Corrected 2026-10-11. There is no HF protection margin.** An earlier version
of this section quoted "400 Vp / 300 Vrms at 1 MΩ" without the derating and
concluded that 1 MΩ plus an external 50 Ω feedthrough was a *"legitimate
sacrificial-protection strategy."* It is not, in this band. Follow the derating:
300 Vrms at 250 kHz → 30 Vrms at 2.5 MHz → the **5 Vrms floor from ~15 MHz up**,
i.e. **identical to the 50 Ω input across the whole 30–250 MHz range this
document measures.** The 60× margin exists only for DC and sub-250 kHz faults.

Taking the uncorrected table at face value would invite parking a 1 MΩ channel on
a live 80 V node at HF in the belief that it is protected. It is not, and a
feedthrough does not help: 80 V into 50 Ω is **128 W**, so the terminator fails
first — which is the actual mechanism, and it is a dissipation limit rather than
a voltage one.

---

## 8. Which FETs are on the board under test — **settled 2026-10-10**

**Answer: the `measured` row.** The board is `HW Stories/fetlib.md` "testboard1" —
HS 2× `IPP055N08NF2S`, LS 1× `IPP024N08NF2S`, no external LS diode — in **TO-220**
packages. The reasoning is in doc/"No-Coil SW Ring (Bench vs SPICE).md" §"Which
physical board"; the three sources below turned out to describe *different boards*
rather than contradicting each other on one.

Three sources appeared to disagree:

| source | HS | LS |
|---|---|---|
| No-Coil bench study (the board actually scoped) | 2× IPP055N08NF2S (80 V) | 1× IPP024N08NF2S (80 V) |
| `pwr-mosfet-lib/dslib/coss_curves.py`, "confirmed by Fab 2026-08-11" | 2× IPP050N10NF2S (100 V) | 2× IPP039N10N5 (100 V), Q2 + the D9 footprint |
| `Fugu2.kicad_sch` Value fields (2026-09-06) | 2× IPA050N10NM5S (100 V) | 1× IPP022N12NM6 (120 V), Q2 populated, Q10 DNP |

The second row is **`ftall`** (`HW Stories/ftall.md:6-7`), not the scoped board —
which is why it never reconciled. The third is the schematic's intent, which the
physical builds have diverged from.

A **fourth** source appeared to disagree with all of them on *package*:
`spice/PARASITIC_MODELING.md` §1 reported the v2.3 layout carrying **SMD
PG-TDSON-8** footprints on B.Cu. **That claim is false and is now retracted in
place.** The half-bridge is TO-220 in both the working copy and `HEAD` of
`Fugu2.kicad_pcb` (Q1/Q3 HS, Q2 LS, `TO-220-3_Horizontal_BottomHeatsink`); the
three PG-TDSON-8 footprints are Q5/Q6/Q7, the **backflow** switches. So the
**~4 nH TO-220 source-CSI package floor stands**, and §5's "only an SMD
half-bridge removes it" remains a live lever. The D9-DNP body-diode freewheel in
that section was right, and matches `fetlib.md`'s "no external diode".

Three discriminators, all consistent with the `measured` identity, in increasing
strength:

1. **Ring frequency.** At 9.2 nH and 72 V the turn-on ring is **~60 / ~46 /
   ~39 MHz** for the three rows — well separated. But this is semi-circular:
   the 9.2 nH was itself fitted assuming the `measured` FETs.
2. **Bias-fit spread** (§4). Re-fitting the three bench points under each build
   gives **13.3 % / 17.5 % / 30.3 %** (re-run 2026-10-11; an earlier draft quoted
   13.3 / 26.6 / 35.2) — not circular, since it tests only the curve *shape*
   against the measured frequency ratios. But at 17.5 % `fitted` is close enough
   to `measured` that **this is the weakest of the three**, not the strongest.
3. **Consistency with the physical loop decomposition.** Forcing 58.5 MHz at
   60 V under each identity gives L = 9.45 / 5.45 / 3.71 nH, against a physical
   floor (copper + tab + CSI) of ~9.0 / 7.0 / 9.0 nH. The `fitted` and
   `schematic` identities are **inconsistent with the bench data plus the
   floor**; `measured` is not.

`ring_analysis.py --build {measured,fitted,schematic}` covers all three.

---

## 9. What to order — sourced 2026-10-11

Everything below was read off the live vendor pages today. **Prices exclude VAT.**
On hand already: the **PMK UFCS coaxial shunt** — nothing else in the signal path.

> ⚠️ **"In stock" on eleshop is not in the static HTML.** The page's schema marker
> says `InStock` on *every* product; the real availability line is injected by
> JavaScript. The earlier claim that the TBCP2-30M1000 was in stock came from
> reading the marker. Rendered, its page says **"Expected lead time of 15 days."**
> Every line below was read from the rendered page.

### 9A. The basket — one order, eleshop.de

| # | Part | Code | € excl | Avail. | For |
|---|---|---|---:|---|---|
| 1 | Tekbox **TBCP2-30M1000** RF current probe | ELE009432 | 749.00 | 15 days | §3 step 4, the 30–230 MHz CM measurement |
| 2 | Tekbox **N(m)–BNC(m) RG223 75 cm** | ELE002492 | 18.97 | 15 days | clamp→scope |
| 3 | Tekbox **BNC–BNC RG223 125 cm** ×2 | ELE009877 | 36.00 | **in stock** | general lab / §7B jig |
| 4 | Tekbox **BNC(m)–SMA(m) RG223 35 cm** | ELE009881 | **11.50** | **in stock** | UFCS→scope, stopgap (see below) |
| | **eleshop.de subtotal** | | **815.47** | | |
| 5 | **PMK `UFCS-CHOKE`** | UFCS-CHOKE | 590.00 | *Lieferzeit auf Anfrage* | §7D, the ns-edge choke — **chosen 2026-10-11** |
| | **Total** | | **1405.47** | | €1672.51 incl. 19 % |

**Item 5, two German vendors, same price, neither stocking it:**
`calplus.de/pmk-ufcs-choke` **€590** excl. VAT, *"Bestellware, Lieferzeit auf
Anfrage"* · `datatec.eu/pmk-ufcs-choke` **€590** excl. VAT / €702.10 incl.,
*"Lieferzeit auf Anfrage"*, orderable, free shipping above €50. PMK America holds
**1 in US stock at $696** — a German manufacturer in Bad Soden, so the US route
only adds import handling. **Ask for the lead time before ordering the clamp**, so
the two arrive together; PMK is `sales@pmk.de`, +49 6196 999 5000, and that mail
is needed anyway for the recommended-footprint files before a shunt is laid in.

**Item 4 is a stopgap, not part of the final path.** The PMK kit ships with 1 m and
0.5 m SMA(M)–SMA(M) coax and the SMA(F)→BNC(M) adaptor, so once it lands the UFCS
needs no cable from this order. But it is on an open lead time and the €11.50
cable is in stock tomorrow — it buys a first look at the shunt now. Read that look
as **provisional**: it is the unchoked ground-referenced measurement §7D says not
to trust, and its one legitimate use is to show whether common-mode noise is
limiting at all.

**Dropped from the first version of this basket** (the Tekbox-choke route, €1294.27):
`TBCMC-1` €445, the N(m)–SMA(m) jumper €14.83, and the second N(m)–BNC(m) €18.97.
The PMK route costs **€111.20 more**.

Free shipping to DE above €200 excl. VAT. One shipment, gated by the 15-day items.

### 9B. The three decisions inside that list

**No SMA→BNC adapter is needed.** Item 5 is a one-piece **BNC-male to SMA-male**
RG223/U cable, 6 GHz, 50 ± 2 Ω — the UFCS output is SMA **female**, so the gender
is right and the adapter disappears. €11.50, in stock, ships next day. It also
answers *"which i dont have yet"* for the cheapest possible amount: **this one
line gets the shunt onto the scope.** Treat an unchoked ground-referenced reading
as provisional (§7D), but it will tell you whether CM is limiting before €445
goes out.

**The choke is for the UFCS path only — the clamp does not need one.** A current
clamp is a current transformer: there is no galvanic path from the harness to
scope ground, so the mechanism the choke fixes (board ground moving against scope
earth, the CM current returning down the coax shield into the signal) does not
exist. Worse, inserting a choke ahead of the clamp would add an uncharacterised
term to the **22 dBΩ** that the whole dBµA conversion rests on. The clamp's
residual problem is pickup on its own coax and body, which is what §7C's open-jaw
null measures and what routing fixes; if that null fails, the cheap first move is a
**clip-on ferrite on the clamp coax**, not a €445 inline part.

**The choke choice, re-decided on the ns-rise-time question (2026-10-11).**
Both manuals were read today — PMK `M-UFCS-CHOKE` Rev 01A (Jan 2026) and Tekbox
`TBCMC-1` V1.0 (Feb 2025):

| | PMK `UFCS-CHOKE` | Tekbox `TBCMC-1` |
|---|---|---|
| price | €590 (calplus.de), $696 (PMK America) | **€445** (eleshop) |
| availability | *"Bestellware, Lieferzeit auf Anfrage"* | 15 days, same order as the clamp |
| connectors | SMA; BNC(M) adaptor included | N female both ends (+€33.80 of cable) |
| **3 dB BW** | **>4.5 GHz** assembly / >6 GHz choke alone | not specified |
| **1 dB BW** | **750 MHz** assembly / 4.5 GHz choke alone | **>1 GHz** (0.6 dB at 1 GHz, typ.) |
| **return loss** | **<−40 dB**, 100 kHz–200 MHz | **>20 dB** to 1 GHz |
| **delay** | **10.6 ns** assembly / 3.1 ns choke alone | not specified |
| CM inductance | 1.5 mH @100 kHz | — |
| CM rejection | — | >60 dB to 1 MHz, >30 dB to 100 MHz |
| CM saturation | not published | 500 mA typ |
| contents | choke + 1 m and 0.5 m SMA coax + SMA(F)→BNC(M) | choke only |
| size / mass | 12.65×11.6×6.3 cm, 560 g incl. cables | 70×60×140 mm, 350 g |

> ⚠️ **The "4.5 GHz" headline is the 3 dB figure, and it is for the choke alone.**
> The number that governs amplitude fidelity is the **1 dB bandwidth of the
> assembly you actually use: 750 MHz.** The included coax, not the choke,
> dominates it. Tekbox's **<0.6 dB at 1 GHz** is therefore *flatter* than the PMK
> assembly — the opposite of what the headline bandwidths suggest, and the
> opposite of what §9B said in its first version.

**Neither choke is the bandwidth limit — the shunt is.** `UFCS-R001` is
**>600 MHz**, so t_r,sys ≈ 0.35/600 MHz ≈ **580 ps**. Measuring a 1 ns edge,
√(1² + 0.58²) = **1.16 ns, a 16 % over-read from the shunt alone**, before either
choke contributes. Picking `UFCS-R005` (>900 MHz) or `-R011` (>1 GHz) changes the
answer more than the choke choice does.

**The one real discriminator is return loss, and it is a time-domain problem.**
PMK <−40 dB is a **~1 %** reflection; Tekbox >20 dB is **~10 %**. That matters
here because a shunt is a *low-impedance* source: ~1 mΩ looking back into a 50 Ω
line is effectively a short, so energy reflected at the choke runs back to the
shunt, inverts, and returns as an echo at **twice the one-way delay** — ~21 ns for
the PMK assembly, comparably ~19 ns for the Tekbox plus two 75 cm RG223 jumpers.
**A 10 % echo 19–21 ns after the edge lands inside the 15–18 ns period of the
55–65 MHz ring this document is trying to measure.** At 1 % it is negligible.
PMK's figure is specified only to 200 MHz; Tekbox's to 1 GHz. Neither is
characterised everywhere.

**Decision — PMK `UFCS-CHOKE`, €590 (Fab, 2026-10-11).** The deciding fact is
that ns-scale current edges are in scope, not just this board's 15.8 ns switching
edge. Once that is the deliverable the Tekbox part's **10 % reflection** is the
binding defect: with a ~1 mΩ shunt as the source the far end is effectively a
short, so a mismatch at the choke returns as an inverted echo at twice the
one-way delay — **~19–21 ns, inside the 15–18 ns period of the 55–65 MHz ring**,
and inside the window where a Qrr feature lives. PMK's **<−40 dB (~1 %)** makes
that artifact disappear, and PMK is the only one of the two that specifies a
time-domain quantity at all (**delay 10.6 ns** for the assembly, 3.1 ns for the
choke alone).

Buying it on the correct grounds matters, because two plausible reasons are wrong:

- **Not for bandwidth.** The PMK assembly's 1 dB bandwidth is **750 MHz**; the
  Tekbox is **<0.6 dB at 1 GHz**, i.e. *flatter*. The "4.5 GHz" is a 3 dB figure
  for the choke without its cables.
- **Not because it sets the rise-time limit.** `UFCS-R001` at >600 MHz contributes
  ~**580 ps**, so a 1 ns edge reads 1.16 ns — a **16 % over-read from the shunt
  alone**, with either choke fitted. If ns edges are the point, **the shunt
  resistance choice (`-R005` >900 MHz, `-R011` >1 GHz) is the bigger lever** and
  is still open; `hf-current-measurement.md` frames it as a
  signal-versus-perturbation trade on resistance, and it now has a bandwidth term
  too.

What is given up: the published **CM saturation current** (Tekbox 500 mA typ
against the measured 67.5 mA; PMK publishes none, only 1.5 mH at 100 kHz), a
second vendor on an open lead time instead of one order, and €111.20.

**The Tekbox manual is a VNA-accessory manual.** `TBCMC-1` V1.0 documents one
application: measuring a 0.47 Ω resistor by the shunt method on a TBVNA-6000 at
−5 dBm. All five plots are frequency-domain; there is no group delay, no step
response, no delay figure, and no mention of an oscilloscope. PMK's is written for
exactly the job in §7D. That asymmetry in characterisation is itself part of what
the extra €145 buys.

**Nobody in the EU has the clamp on a shelf.** Checked today: eleshop.eu/.de
€749 / 15 days · rekirsch.at €882, *"derzeit nicht auf Lager"*, ~1 week ·
batterfly €939, 4 weeks · ledxess €946.99 incl. VAT, *"Momentan nicht verfügbar"* ·
Welectron 3–4 weeks (listed for the -500). **eleshop is both the cheapest and the
fastest credible**, and rekirsch's one-week quote costs €133 more for a part they
also do not hold. Note the configurable eleshop listing prices the same probe at
€649 + €119 = **€768** — order from the dedicated product page, not the selector.

### 9C. Not needed

- **TBCP2-CAL fixture (≈€548).** §7B does the same job ratiometrically with the
  scope's own 50 Ω input as the load. Skip it.
- **An attenuator.** This resolves the contradiction flagged in §7A: 8 µA through
  22 dBΩ is ~101 µV, ~40 dB over the scope floor, and the clamp's 10 A RF rating
  is 150× the measured CM current. Nothing here can overload a 50 Ω input, so
  **external attenuation stays 0 dB and the raw dBµV is the reading.** The
  "start with a 10–20 dB attenuator" line was defensive boilerplate; it is struck.
- **PMK `D010031`** (§7D) and any 50 Ω feedthrough — the MXO44 input is natively
  50 Ω.
- **A LISN / V-AMN.** Moot while the no-conducted-test decision stands, and if it
  ever falls, EN 61000-6-3 Table 3 needs a 50 Ω/50 µH V-AMN, not the 150 Ω DC-AN.

### 9D. Corrections this sourcing pass forced

- **`TBCP2-250` is a real part.** An earlier note flagged it as a model number I
  had invented and never datasheet-checked. Tekbox lists it: 13 dBΩ, characterised
  1 kHz–400 MHz, −3 dB 300 kHz–300 MHz, 3 A RF, N female. The flag was wrong.
- **The 3 A RF / no-DC-spec caveat does not apply to the recommended clamp**
  (reviewer F18). That rating belongs to the TBCP2-250/-750. The **TBCP2-30M1000
  is specified >50 A DC (to 400 Hz), 10 A RF, 50 A pulse, 0.007 As** — read from
  the Tekbox spec table today. §3 step 4's **pair-only** rule stands on its own
  physics (a single conductor of a 33 A converter carries the full DC), but it
  must no longer be justified by a saturation rating this probe does not have.
- **eleshop's own description of the TBCP2-30M1000 says "typical transfer
  impedance of 0 dBΩ".** That is a copy-paste from the TBCP2-1M800 entry.
  Tekbox's spec table says **22 dBΩ ± 2 dBΩ from 25 MHz–1 GHz**. Use the
  manufacturer figure; do not let the shop page into the link budget.

### 9E. TBCP2-30M1000 vs TBCP2-750 — both manuals, both Z_T tables

Primary sources read 2026-10-12: `TBCP2_30M1000_Manual.pdf` **V1.0, 22.8.2025,
"preliminary"**; `TBCP2_750_Manual.pdf` **V1.4, 12.7.2025** (V1.0 Dec 2020, with a
*"data update after mechanical modification"* in V1.2). Both probes are physically
identical outside the core: 32 mm aperture, 73 mm OD, 20 mm high, 320 g, **N
female**, 125 °C core.

| | TBCP2-750 | TBCP2-30M1000 |
|---|---|---|
| price, eleshop | €769 | **€749** |
| characterised | 1 kHz – 1 GHz | 10 kHz – 1 GHz |
| −3 dB | **1.5 MHz – 850 MHz** | 30 MHz – 900 MHz |
| Z_T, flat region | 20 dBΩ typ. | **22 dBΩ ± 2**, 25 MHz – 1 GHz |
| **max primary, DC–400 Hz** | **not specified** | **>50 A**, graph to 150 A |
| max primary, RF | **3 A** | **10 A** |
| max pulse / ∫i·dt | not specified | **50 A / 0.007 As** |
| manual maturity | V1.4, 5 revisions | V1.0, preliminary |

**Z_T head-to-head, from the two typical-data tables (dBΩ):**

| f | −750 | 30M1000 | Δ |
|---|---:|---:|---:|
| 0.5 MHz | 10.13 | −4.70 | **−14.83** |
| 0.75 | 13.33 | −1.14 | −14.47 |
| 1 | 15.36 | 1.45 | −13.91 |
| 2.5 | 18.52 | 9.60 | −8.92 |
| 5 | 19.13 | 14.36 | −4.77 |
| 10 | 19.56 | 18.05 | −1.51 |
| **~15.4** | — | — | **crossover** |
| 25 | 19.94 | 21.65 | +1.71 |
| 50 | 20.06 | 23.32 | +3.26 |
| 100 | 20.09 | 24.16 | +4.07 |
| 150 | 20.13 | 24.33 | +4.20 |
| **200** | 20.11 | 24.35 | **+4.24** |
| 300 | 20.30 | 24.24 | +3.94 |
| 500 | 20.31 | 23.67 | +3.36 |
| 1000 | 7.30 | 20.21 | +12.91 |

**They swap places at ~15.4 MHz** (log-interpolated between the 10 and 25 MHz
rows). Below it the −750 is up to **~15 dB more sensitive**; above 25 MHz the
30M1000 leads by **1.7–4.2 dB**, and the lead is widest exactly across
**30–230 MHz**, the band EN 61000-6-3 actually scores. For the §0 target of 8 µA:
**117 µV at 50 MHz and 132 µV at 200 MHz** with the 30M1000, against 81 µV at
both with the −750.

**Why the 30M1000 is the right part here, in order of weight:**

1. **DC current handling, on a 33 A converter.** The −750 specifies **3 A RF and
   no DC figure at all**; the 30M1000 gives **>50 A DC with a saturation graph to
   150 A**, 10 A RF, 50 A pulse. §3 step 4's pair-only rule puts net DC near zero,
   but "near" is doing work: an asymmetric harness leaves residual DC in the core,
   and only the 30M1000 lets you bound the resulting Z_T error. With the −750 a
   single-conductor measurement is simply unavailable.
2. **2–4.2 dB more Z_T across the whole binding band**, and it is **€20 cheaper**.
3. **It survives the top end** — 20.21 dBΩ at 1 GHz where the −750 has collapsed
   to 7.30.

**What the −750 genuinely buys, and why it does not decide it.** Its one real
advantage is **13.33 dBΩ at 750 kHz against −1.14 dBΩ**, ~14.5 dB more sensitivity
at the 780 kHz line. That line is **−10.3 dB, a pass, and differential**
(`RESULTS-batport-20261010.md` §1b–c) — which is precisely the premise whose
collapse reversed the §6 recommendation. Buying 14.5 dB of sensitivity at a
frequency that already passes, and paying 4 dB across the band that does not, is
the wrong trade.

**The one argument for the −750 that is not about this board.** The conducted
relief is an *interpretation* (§0, `STANDARD-BASIS.md` §8.0a), not a limit.
If it is ever challenged, 150 kHz – 30 MHz comes back, and there the 30M1000 is
useless: ~**−15 dBΩ at 150 kHz** puts 8 µA at ~1.4 µV, under the scope floor. The
−750 is ~15 dB better there and still marginal. **Neither part covers that case** —
the one that does is the **TBCP2-30K400** (3 dBΩ flat **30 kHz–400 MHz**,
characterised from 10 Hz, 25 A DC, €679), at the cost of ~19 dB less Z_T than the
30M1000, i.e. ~11 µV for 8 µA instead of 117 µV. That is still ~20 dB over the
floor. **Not a recommendation — a named fallback** if the conducted question
reopens, so the decision is on the record rather than rediscovered later.

**Both manuals carry a warning that touches §9C.** §6/§7, identical in both:
in differential-mode or single-conductor use, *"EUTs with high inrush currents may
cause a voltage transient that might damage the receiver or analyzer frontend …
protect your equipment using attenuators, limiters, or disconnect the RF-input
while powering ON/OFF the EUT."* §9C's "external attenuation 0 dB" stands for the
steady-state CM measurement it was derived for, but **disconnect the scope input
while powering the board up and down**, or accept the vendor's attenuator advice
for that moment. That is a procedure item, not a purchase.
