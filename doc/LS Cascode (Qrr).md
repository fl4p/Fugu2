# Low-Side Cascode for Qrr Relief — assessment, 2026-10-11 (rev. 2, 2026-10-12)

Status: **analysis only, nothing measured.** Rev. 2 after an independent Codex review
(`~/codex-reviews/ls-cascode/review.log`, 9 findings, report at line 6955). Rev. 1's
quantitative ledger did not survive that review and has been withdrawn — see §0.

Operating point throughout: 72 V in / 27 V out / 32 A (864 W out, ~880 W in),
fsw 39 kHz, D_LS = 0.625, commutation loop 9.2 nH, SW ring 58.3 MHz / Z₀ 3.37 Ω.

Related: `doc/No-Coil SW Ring (Bench vs SPICE).md`, `doc/EMI Precompliance.md`,
`doc/Mosfets.md:248`, `doc/Power Conversion Efficiency Optimization.md:33`,
`~/dev/pv/ee/dcdc-tools/loss/docs/reverse-recovery.md` (canonical modeling rule, and
the measurement procedure at `:351`).

---

## 0. Retractions

### 0.1 "Topologically impossible" — withdrawn

An earlier session argued the LS cascode was topologically impossible, because the body
diode is intrinsic and in parallel with the channel in the same die, so any series element
blocking the diode also blocks the channel.

**Wrong.** That is an argument against a *series blocking diode*, not against a cascode.
A parallel body diode does not have to be blocked — it has to be kept **below its knee**.
The cascode holds the HV channel on during reverse conduction, so the diode never injects.
The mechanism was already correct in `reverse-recovery.md` §3 and in the memory
`~/dev/pv/ee/.claude/memory/cascode-qrr-mitigation.md`. **This retraction survived review.**

### 0.2 "Voltage clamping is where the loss saving comes from" — withdrawn

Rev. 1 claimed the LV device recovers across ~6 V instead of 72 V, and booked cascode
recovery loss as `Q_LV · 6 V · fsw = 22 mW` against a 217 mW baseline.

**Wrong.** The recovery current also flows through the HS switch and the HV channel:

```
E_HS + E_HV + E_LV = ∫[(Vin−V_SW) + (V_SW−V_X) + V_X]·i_rr dt  ≈  Vin · Qrr
```

Before recovery releases the switch node the HS switch supports most of the voltage and
dissipates most of this energy. Limiting the LV device's own voltage does **not** reduce
the cell's recovery energy scale. TI's note (`ssztc00`, pp. 2–3) distinguishes upper-switch
from diode dissipation explicitly. Both papers attribute their benefit to **suppressing HV
body-diode charge**, not to voltage clamping.

Consequence: with the *same* charge estimates, the silicon cascode **increases** recovery
loss by ~52 mW instead of saving ~195 mW.

### 0.3 "0.68 W → 0.22 W" — over-correction, also withdrawn

Rev. 1 replaced the raw datasheet-scale figure `Qrr·Vin·fsw` = 0.68 W with an
operating-point figure of 0.22 W, obtained by treating `τ = Qrr/I_F` as a transferable
carrier lifetime and scaling linearly to 32 A.

**That normalization is not sound.** Recovered *terminal* charge is not steady stored
diffusion charge: carriers recombine during commutation and the reported integral can
include displacement charge. Current, slope, temperature, diode-conduction duration and
integration convention all matter, and the two datasheet rows differ in **both** I_F and
dI/dt. `reverse-recovery.md:521` prescribes the raw datasheet scale only as a *cross-check*, and
`:290` gives the calibrated LM path at operating I_F, dI/dt and T_J as the model — not
linear current scaling.

Fitting the Lauritzen–Ma implementation already in
`~/dev/pv/pwr-mosfet-lib/dslib/qrr_model.py` to each datasheet row gives, at 32 A / 25 °C /
500 A/µs, roughly **218 nC HV and 260 nC LV** — not 77/96 nC. HV loss scale becomes
~0.61 W. *(One-point extrapolation, endpoint assumption, no Qoss decontamination — an
illustration that the normalization matters, not a replacement measurement.)*

Rev. 1's stated direction of bias was also backwards: slower reverse ramps allow **more**
recombination, not more complete extraction. And if 2.42 ns understated the HV device's
parameter, that would make the HV device look *better*, not worse.

> **Standing position: keep 0.68 W as a datasheet-condition reference. Operating-point
> recovery loss is UNRESOLVED. Do not quote 0.22 W.**

---

## 1. Topology

From the GaN/Si-SJ paper (`dcdc-tools/docs/lit/FINALVERSION (1).pdf`, Figs. 3–5):

```
          SW ──┬── HV FET  drain  (= the TO-220 TAB)
               │   IPP024N08NF2S, 80 V, 2.4 mΩ @25 °C
               │   gate ── static +10 V w.r.t. GND, local bias cap, CLAMP (see below)
               │   source = PIN 3
               X ──┬── LV FET drain
                   │   30 V, sub-mΩ, SMD
                   │   gate ── existing UCC21330 LS output
                   │   source
                  GND
```

The HV gate is **not switched** — the paper represents it as a fixed voltage source.
Switching is done entirely by the LV device, which becomes the control gate of the
composite. For a **low-side** position this bias is ground-referenced and does **not**
require a new isolated or bootstrapped supply.

**Dead time.** LV off, freewheel current flows GND → X through the LV body diode, pulling
X below ground by one diode drop. V_GS,HV goes to ~+10.7 V, the HV channel is hard on, and
carries 32 A at **0.077 V cold / 0.11–0.12 V hot** — far below the 0.7 V knee either way.
The HV body diode does not conduct, so there is no HV stored charge. **This is the whole
mechanism, and it survived review.**

Current-limit condition from the modeling rule, `I_lim ≈ V_γ / R_ds,on(reverse)`:

| T_j | R_DS(on) | I_lim |
|---|---:|---:|
| 25 °C | 2.40 mΩ | 292 A |
| 100 °C | ≈3.36 mΩ | ≈208 A |
| 125 °C | ≈3.76 mΩ | ≈186 A |

*(Hot multipliers digitized from the HV datasheet Diagram 9 with dsdig — typical-curve
estimates, not guaranteed limits.)* Against 32 A the margin is ≥5× at any temperature.
**Diode avoidance is not in doubt at this operating point.**

### ⚠ What rev. 1 got wrong here

- **The TO-220 tab is DRAIN, not source.** Rev. 1 said to place the LV drain pad against
  "the HV source tab". The LV drain connects to **HV source, pin 3**. The tab is the SW
  node.
- **V_X is not bounded by `10 − V_th`.** V_GS(th) = 2.2/3.0/3.8 V is specified at 139 µA,
  which is not the gate voltage needed to carry 32 A. The transfer curve gives ≈4.3 V at
  32 A / 25 °C *(dsdig estimate, review-required status)*, so ≈5.7 V at X during a
  corresponding source-follower interval; near zero current the threshold figure instead
  suggests ≈7 V. **Neither bounds the transient.** Peak V_X depends on the nonlinear
  capacitance network, gate-bias impedance, interconnect inductance, displacement current
  and clamp behaviour. A loop inductance and a ring frequency are not enough to compute it.
- **The paper's protection was omitted.** Its cascode includes a local bias capacitor
  `C_E`, a **17 V bidirectional Zener clamp**, and a **40 V** GaN device driven at **5 V**.
  Gate-overstress protection is attributed to that clamp, not to `10 − V_th`. Your 12 V
  driver rail is not directly compatible with a +6 V-max LV GaN part.
- **The HV device can traverse saturation** during the transition. Its switching energy
  and SOA need evaluating; this is not in any ledger here.

> **30 V adequacy for the LV device is UNVERIFIED, not disproved.** A clamp network is
> part of the topology, not an optional extra.

### The variant where both diodes conduct

If the HV gate is switched instead, both body diodes conduct in series during dead time
(~2× V_sd) and the relief comes from the LV device recovering first and interrupting the
loop current before the HV charge is swept. That works, but costs roughly double the
dead-time conduction for no added benefit. The static-bias variant is better and is what
the papers implement.

---

## 2. Precedent: Outback FM40 — series placement evidenced, role unresolved

From `https://open.pe/2023/05/04/teardown-outback-mppt-tracer4214-flexmax/` (Fab's own
teardown; page and both datasheets re-fetched 2026-10-11/12, ladder rung 1, HTTP 200).

| | |
|---|---|
| Switching FETs | `075N15N`, 150 V, 7.5 mΩ, **2 in parallel** |
| Low-voltage FET | **`HYG007N03LS1C2`**, listed as *"low-side protection?"* |
| Driver | IR25607S, 12 V gate drive, fsw **50 kHz** |
| LS gate | 7.5 Ω, no discharge diode; rise 330 ns / fall 380 ns |
| Power row | 58 V / 4 A in, 26.6 V / 8.4 A out, "97.3 %" |

`HYG007N03LS1C2` (Huayi, LCSC C2904120 — verified faithful by review):
30 V / 220 A; **0.63 mΩ** typ @ 10 V, 40 A; 0.96 mΩ @ 4.5 V; **Qrr 60 nC / trr 50 ns @
I_SD 20 A, 100 A/µs**; V_SD 0.74 typ @ 20 A; Coss 1636 pF **@ 25 V**; Qg 104 nC **@ 10 V**;
**PDFN5×6-8L**. These are test-point values, not operating-point guarantees.

### Correction to rev. 1

Rev. 1 stated the page contains *"no board photo or traced schematic of the cascode."*
**That is false.** The page carries a board photograph and a hand-drawn power-stage
schematic (`image-70`), which places **G007N03 in series below the low-side 075N15N** —
i.e. in the cascode position. Verified visually.

But the same drawing annotates that device **"Bottom side eFuse?"**, and no gate
connections are drawn. So:

> **Series connection is evidenced. The functional role is unresolved.** Rev. 1's test —
> "one board photo settles it" — is also wrong, because placement alone cannot distinguish
> a fixed-bias cascode from a protection switch. **Gate wiring is what settles it.**

The teardown's power row is internally inconsistent (58×4 = 232 W vs 26.6×8.4 ≈ 223 W,
and the written 225/231 W conflicts with 97.3 %). Treat it as recorded numbers, not a
reconciled measurement.

### The 150 V HV part — now verified

`075N15N` is the marking of Infineon **`IPP075N15N3 G`** (DS Rev. 2.06). From page 3,
read off the rendered page after the PDF text layer came out font-garbled:

| | |
|---|---|
| **Qrr** | **478 nC** typ |
| **trr** | **146 ns** typ |
| conditions | V_R 75 V, I_F = I_S = 100 A, **di_F/dt = 100 A/µs** |
| Coss / Qoss | 638 pF @ 75 V / 179 nC |

That is **≈1.98×** the IPP024N08NF2S's raw 242 nC, at a 5× lower dI/dt. It supports "the
150 V part has a larger recovery concern"; it does **not** establish "several times the
loss", especially with two devices in parallel and a different switching speed. Rev. 1's
scaling claim is **partially confirmed, magnitude not established.**

---

## 3. The loss ledger — withdrawn, with what is left standing

Rev. 1's net figures (−315 mW Si / −486 mW GaN, 98.13 % / 98.12 %) **added up correctly
from their own inputs**, but the inputs and the missing terms do not survive. The ledger is
withdrawn. What can be said:

### Solid

| term | value | basis |
|---|---:|---|
| LV series conduction, 25 °C | **403 mW** | `32² × 0.63 mΩ × 0.625`, plain I²R |
| LV series conduction, 100 °C | **≈583 mW** | R tempco, Huayi Fig. 7 (hand-digitized) |
| LV series conduction, 125 °C | **≈644 mW** | as above |

This is the **best-established quantity in the document**, and it is a cost.
*(Strictly it should use `R·D_ch·(I_out² + ΔI_pp²/12)`; the draft assumes negligible ripple.
Excluding the two 185 ns diode intervals from LV channel conduction removes ~9 mW cold.)*

### Unresolved

- **Recovery charge at 32 A** — see §0.3. Somewhere between the τ-scaled 77/96 nC and the
  LM-fitted 218/260 nC, with the ordering between HV and LV **not established either way**.
- **Recovery loss** — `≈ Vin·Qrr` across the cell (§0.2), mostly in the HS switch. Unchanged
  in scale by the cascode. Only a genuine charge reduction helps.
- **GaN dead-time conduction** — rev. 1 copied the silicon column's 405 mW. Unsupported:
  off-state GaN reverse-channel voltage depends on threshold, gate-off bias and current,
  and every extra volt across the reverse path adds **462 mW** at this timing.

### Corrected smaller terms

- **Gate drive:** rev. 1's 49 mW was *gross* LV drive power, not the incremental cost of
  replacing a switched HV gate with a static one. At the two parts' specified 10 V Qg
  points the gross difference is `(104 − 89) nC × 10 V × 39 kHz` = **5.85 mW**. (A 10 V Qg
  is not a 12 V Qg; bias-network losses still need accounting.)
- **Baseline dead-time V_sd:** 0.75 V was an assumption. The HV 25 °C curve gives ≈0.81 V
  at 32 A → **≈376 mW**, about 30 mW above rev. 1's 346 mW. Hot operation changes it again.
- Two dead-time intervals per cycle **is** correct for positive-current CCM, though actual
  diode-conduction durations need measuring rather than assuming the full 185 ns.

> **Bottom line: the efficiency penalty is real and roughly 0.4–0.65 W from series
> conduction alone, but the complete "−0.3 to −0.5 W" figure is withdrawn and the sign of
> the recovery term is unresolved.**

---

## 4. Does it reduce the ringing?

Rev. 1 concluded "only a zero-Qrr LV device is an EMC lever." **That conclusion is
unsupported.** What is actually known:

### Rev. 1's current estimates were not bounds

`72 V / 9.2 nH = 7826 A/µs` is a full-bus inductive slope, **not automatically the
commutation slope**. During current transfer, HS gate drive, transconductance and
common-source inductance determine how much voltage actually reaches that inductance. The
~15.8 ns switch-node edge is not a current-slope measurement either.

For an ideal triangular recovery, `I_RRM = √(2·Qrr·(di/dt)/(1+S))` with `S = t_b/t_a`.
Rev. 1's `√(2Q·di/dt)` assumes **S = 0** — the hardest possible snap. Its `di/dt·τ` lower
bound used the discredited τ. **Neither brackets the real snap current.**

### Charge does not determine softness

This is the logical failure in rev. 1's reasoning. On the same one-point model at 32 A and
2000 A/µs, the LV part shows **higher** charge (525 vs 470 nC) but **lower** peak recovery
current (29.3 vs 33.5 A). A lower-voltage, thinner-drift-region diode can recover *softer*
at equal or greater charge — and peak current, not charge, is what the tank converts to
overshoot. So:

> **"The Si part stores more charge, therefore no ring benefit" is a non-sequitur.**
> Silicon may improve ringing through reduced charge **or** a softer waveform. Whether it
> does here is unmeasured.

### The tank is not unchanged

Rev. 1's L/C table assumed 811 pF throughout. The LV device's Coss sits at node X together
with the HV source/gate capacitances and the clamp/bias network — it can be neither ignored
nor added directly across SW. Its 1636 pF is specified at **25 V**, not at the operating
bias. **The cascoded tank has not been established.**

### Zero-Qrr GaN

Removes the diffusion-recovery contribution. Load-commutation and capacitive currents
remain, so it does not zero the ring either.

---

## 5. Packaging

| | L_loop | f_ring | Z₀ |
|---|---:|---:|---:|
| as built | 9.2 nH | 58.3 MHz | 3.37 Ω |
| + PDFN5×6 LV device (~+1 nH, **unverified**) | 10.2 nH | 55.3 MHz | 3.55 Ω |
| + a second TO-220 (~+4.8 nH) | 14.0 nH | 47.2 MHz | 4.15 Ω |

Frequencies and impedances are arithmetically correct **for a fixed 811 pF tank**, which
§4 shows is not the cascoded tank. The +4.8 nH TO-220 figure is a plausible sensitivity
assumption — `to220.md:16` gives a family default of 4.5 nH drain + source — but is not a
measured addition for this part. The +1 nH PDFN figure is unverified. Liu's TO-220 cascode
extraction concerns a different topology.

**Arithmetic correction:** a 23 % Z₀ increase is offset by a current reduction of
`1 − √(9.2/14)` = **18.9 %**, not "more than 23 %" as rev. 1 stated.

The papers' own warning stands:

> "The oscillation induced by the parasitic inductance hindered the reduction of switching
> loss. **Co-packing the discrete components is expected to help fully unlock the
> potential of the cascode device.**" — `FINALVERSION (1).pdf`

**If built at all, the LV device must be SMD** (PDFN5×6 / PG-TDSON-8, footprint already on
this board for Q5/Q6/Q7), drain pad against the HV **source pin**, not the tab.

The ring does not move below the 30 MHz radiated floor in any variant, so none of this
changes the standards basis in `doc/EMI Precompliance.md`.

---

## 6. Would it help EMC?

**Not reliably, and with a Si LV device the sign is not predictable.** Figures below are
from the `doc/EMI Precompliance.md` **update of 2026-10-12** (independent estimate merged
to `dcdc-tools` main at `050842c`), which supersedes the numbers rev. 1 of this file used.

Central 3 m margins (+ = over), nominal two-branch PV source:

| geometry | 30–50 | 50–70 | 70–90 | 90–110 MHz |
|---|---:|---:|---:|---:|
| **lh04 (central)** | **−1.7** | **+1.0** | **+0.0** | **+3.8** |
| 1.0 m run | −2.1 | −3.0 | +2.7 | **+10.2** |
| isolated AE | +10.3 | +8.1 | +0.8 | +4.1 |
| 11 nH PV-source **alternative** | +21.7 | +22.6 | +15.3 | +8.8 |

Read as **straddling the limit, not a pass**: setup geometry alone swings it ~10 dB, and
the file calls itself *"a design-stage margin estimate, not a compliance verdict."* The
11 nH row is the named alternative, not the baseline — MLCCs carry 94 % of the loop
current and the largest J10 equivalent over the declared grid is 1.73 nH, so the model
cannot reach 11 nH; it is kept only because the rad300 PV DM voltage implies it.

The SW ring at 58.3 MHz lives in the **50–70 MHz** band, which is **+1.0 dB** over in the
central case. The **worst** band is 90–110 MHz at +3.8 dB, and that is the
board–heatsink–toroid structure resonance — nothing the cascode touches.

*(The older rad300 figure of +17.5 dB at 30–50 MHz is now partly explained rather than
merely disputed: PV DM accounts for ~18 dB of the 32 dB gap at 30 MHz. That deck is
credible only to ~10 MHz and its ring sits at 25–33 MHz against the measured 58–61 MHz.)*

### For the cascode: one credit, three debits

- **credit:** possibly lower I_RRM via softer recovery — unquantified (§4).
- **debit:** Z₀ up ~5 % from ~+1 nH — small but near-certain.
- **debit:** a **new resonant node X** (LV Coss against inter-die inductance). The GaN
  paper's own measurement is that exactly this parasitic oscillation limited their gains.
  Adding a resonator to a board whose problem is resonators.
- **debit:** charge may not fall at all (§0.3).

> **The EMC case rests on three stacked unknowns:** that recovery drives the loaded ring
> (unmeasured), that a Si 30 V part recovers more softly (unestablished), and that node X
> does not ring (unassessed). Against a band that is +1.0 dB over.

### The snubber is the lever, and it is quantified

From the same update, 4.7 nF across the LS:

| | 30–50 | 50–70 | 70–90 | 90–110 MHz | worst band after |
|---|---:|---:|---:|---:|---:|
| Rs = Z₀ = 3.4 Ω | −6.9 | −11.7 | −5.2 | −2.7 | **+1.1 dB, still over** |
| **Rs = 1.5 Ω** | **−10.4** | **−17.2** | **−10.1** | **−6.9** | **−3.1 dB, a pass** |

Both survive the 11 nH case. The snubber damps the tank **regardless of what excites it**
— load step, recovery, or both — so unlike the cascode it does not depend on the
measurement that has not been made.

> ### ⚠ Correction: `Rs = Z₀` is the wrong answer to *this* question
>
> An earlier session (this one) contributed the rule **Rs = √(L/C) = Z₀ = 3.37 Ω** to
> channel `emc` as the correct snubber sizing, on impedance-matching grounds from the
> Toshiba app note, and rev. 1 of this file repeated it — asserting a correctly sized
> snubber "should do better" than the deck's 1.5 Ω. **The model says the opposite for
> emissions:** 1.5 Ω beats Z₀ by 3–6 dB in every band and is the difference between +1.1 dB
> and a pass.
>
> And the trade is free: since `P_snub = Cs·Vin²·fsw` is **independent of Rs**, the
> under-damping is not paid for in dissipation. So `Rs = Z₀` is right for the *ringing*
> question and **unexamined — and apparently wrong — for the *emissions* question.**
>
> `EMI Precompliance.md` records this as **parked 2026-10-12, unresolved**: `ee-1b` left
> the channel without answering and the radiated-indep deck now has no live owner.

Cost, `P = Cs·Vin²·fsw`, independent of Rs:

| Cs | vs tank | P_snub |
|---|---:|---:|
| 1.0 nF | 1.2× | 202 mW |
| 2.2 nF | 2.7× | 445 mW |
| **4.7 nF** (the modelled value) | 5.8× | **950 mW** |

So the pass above costs ~0.95 W — more than the cascode, but for a modelled pass rather
than a hypothesis. Whether a smaller Cs holds the margin is **not modelled** and is worth
asking of whoever picks up that deck.

### Ranking for EMC

1. **LS RC snubber.** Quantified, mechanism-agnostic, two parts, no respin, takes the
   worst band to a pass at 1.5 Ω / 4.7 nF. Open: whether less than 4.7 nF suffices.
2. **The free bench step first** — the **J10 DM voltage spectrum / bank anti-resonance**.
   It discriminates the nominal case from the 11 nH alternative, which is the single widest
   uncertainty in the whole estimate, and it needs only the scope and a probe already on
   the bench. **Not gated on any purchase.**
3. **Heatsink strap** — −14.6 dB at 90–110 MHz, the worst band. But **nominal only**: it
   drops to −0.9 dB under the 11 nH case, which is another reason to do step 2 first.
   *(Rev. 1 and a verbal summary placed this lever at 30–50 MHz. Wrong band.)*
4. **Edge rate** via R_g,on — reduces load-step *and* recovery contributions for a resistor,
   trading against overlap loss. Lever 7 in `reverse-recovery.md`.
5. **Cascode** — not on the list on its own merits.

## 7. Verdict

| | |
|---|---|
| Mechanism valid? | **Yes.** HV body-diode suppression, ≥5× I_lim margin hot. |
| Recovery loss reduced? | **No, not by itself.** Energy is `Vin·Qrr` across the cell; only a charge reduction helps, and the Si part may not deliver one. |
| Efficiency? | **Costs 0.4–0.65 W** in series conduction alone. Recovery term unresolved. |
| Ring / EMC with Si LV? | **Unknown, sign unpredictable.** One unquantified credit against three debits. |
| Ring / EMC with GaN LV? | Removes the diffusion term. Still needs a real device, drive scheme and clamp; not costed. |
| Outback precedent? | **Series placement evidenced, functional role unresolved.** |
| 30 V LV adequacy? | **Unverified.** Clamp network required. |
| **Recommended now** | **Do not respin.** Run the free J10 DM / bank anti-resonance check, then the snubber. Measure (§8) before considering a cascode. |

The one thing a Si cascode uniquely buys is **decoupling**: today a single device sets
R_DS(on), the 80 V margin *and* the recovery behaviour. A cascode makes recovery the
property of a cheap swappable 30 V SMD part. That is real, but it only pays off if the
intent is to later fit something genuinely better in that socket — a soft-recovery part
chosen on trr, or a zero-Qrr LV GaN. As a one-shot swap to generic silicon it is ~0.6 W
spent to find out whether a different diode is softer.

---

## 8. The measurement that decides it

Rev. 1's §7 proposed a temperature sweep plus a load sweep with a binary decision rule.
**Withdrawn — it was a false-negative trap:**

- Temperature moves R_DS(on), Coss, damping, V_sd and the thermal/mechanical configuration
  as well as Qrr. Flat ring-vs-temperature **does not exclude** recovery (opposing changes
  cancel); rising amplitude does not uniquely identify it.
- Both mechanisms scale with load: `Q ∝ I` and `di/dt ∝ I` give
  `I_RRM ∝ √(Q·di/dt) ∝ I`. **Linear load dependence is not exclusive to load-step
  excitation.**
- Increasing dead time can read flat simply because stored charge has already saturated;
  extrapolating that plateau toward zero conduction time recovers nothing. It is also not
  unqualifiedly "safe" — diode loss and recovery stress rise.
- **The 70 ns shoot-through margin was never established.** `HW Stories/fwhite.md:74`'s
  115 ns gate fall was measured with an **IPP024 substituted into the HS position**, not
  the IPA050 pair actually fitted. A historical gate fall time subtracted from a programmed
  dead time does not establish channel non-overlap, and LS gate voltage alone cannot
  confirm body-diode conduction.

### Replacement spec

Matched loaded / double-pulse measurements, per the canonical procedure at
`reverse-recovery.md:351`. Measure, at matched conditions:

1. **LS branch current** — the primary signal.
2. **Both gate voltages**, to establish actual channel non-overlap and the real
   diode-conduction interval (not the programmed 185 ns).
3. **Commutation slope** `di/dt`, measured rather than assumed from `Vin/L_loop`.
4. **SW node voltage**, ≥500 MHz probe, ground spring, no ground lead.

Report **charge, peak current and recovery softness separately**, and distinguish the
reverse-lobe charge from Qoss and from ringing. A single "does Qrr matter" yes/no cannot
be extracted from ring amplitude alone.

### Instrument — rev. 1's recommendation was wrong

Rev. 1 named the Tek CT-2 and Pearson 6585. **Both are disqualified by the guide rev. 1
cited**, `~/dev/pv/ee/dcdc-tools/docs/hf-current-measurement.md`:

- **CT-2** (`:164`, `:296`): 50 A·µs rating, against a total HS conduction pulse of
  `32 A × 0.375/39 kHz` ≈ **308 A·µs**. Also 36 A rated, below load plus recovery spike.
- **Pearson 6585** (`:305`): 50.8 mm bore needs ~120 mm of threaded wire ≈ **100 nH**,
  roughly 30× the 9.2 nH loop under investigation.
- Bandwidth alone does not establish charge accuracy: the guide's one-pole smearing model
  gives ~**25.5 nC** of error at 32 A / 200 MHz.

**Use a coaxial current shunt.** The guide already names the choice (`:431–440`):
**UFCS-R005** (`:193`, `:431`) — 5 mΩ, 4.30 mV/A, >900 MHz, 140 pH, 129 mV at 30 A, 1.1 W at 14.9 A rms, 300 A /
100 µs pulse rating, "the leading charge choice", conditional on its §3.3 perturbation
check. UFCS-R001 (0.957 mV/A, 120 pH, 50 A) if perturbation or current headroom dominates.

**"One purchase unblocks both workstreams" is false.** The EMC clamp needs a whole-harness
aperture and ≥250 MHz (`doc/EMI Precompliance.md` §6), which explicitly disqualifies the
CT-2 for that job and names a different part. These are two separate purchases.

### Decision rule

No binary rule. The measurement must resolve **actual charge, recovery shape, node-X stress
and EMC response**. Only then is a cascode — and only a GaN-LV one — worth costing against
the snubber and the heatsink bond.

---

## 9. Open items

- Operating-point recovery charge and loss at 32 A: **unresolved** (§0.3). Needs the
  calibrated model path in `reverse-recovery.md`, or measurement.
- Whether recovery drives the loaded ring at all: **unmeasured**. The no-coil TT = 0 result
  (`doc/No-Coil SW Ring (Bench vs SPICE).md:288`) cannot exclude it — there was no
  freewheel current.
- Outback cascode **gate wiring** — the one thing that would settle the precedent.
- 30 V LV adequacy under transient V_X; clamp network design (§1).
- HV device SOA / saturation-traversal energy during the transition — not in any ledger.
- The cascoded tank capacitance at node X (§4).
- Measured inductance adders for PDFN5×6 and TO-220 in *this* layout (§5).
- Whether any 80 V-class co-packaged cascode, or a zero-Qrr LV GaN in a PDFN5×6-class
  package at this current, exists — not searched.
- UFCS-R005 unpurchased; blocks §8. **Separate from the EMC clamp purchase** — rev. 1's
  "one purchase unblocks both" was wrong.
- **Snubber `Rs` is unresolved for emissions** (§6): `Rs = Z₀` is justified for ringing,
  the radiated model prefers 1.5 Ω by 3–6 dB, and `P_snub` does not depend on Rs. The
  radiated-indep deck has **no live owner** as of 2026-10-12.
- Whether a snubber smaller than 4.7 nF still takes the worst band to a pass — not
  modelled, and it is the difference between ~0.95 W and ~0.45 W.
