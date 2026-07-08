# Two roles: ripple (electrolytic) vs. spikes (ceramic)

The input cap bank does two physically separate jobs, split across the two cap types:

|              | Electrolytic (bulk)             | Ceramic (hot-loop MLCC)                |
|--------------|---------------------------------|----------------------------------------|
| absorbs      | 39 kHz sawtooth ripple          | MHz commutation spikes (Qrr/Qoss)      |
| limited by   | ESR → **loss**                  | ESL → **loop area / Vds overshoot**    |
| purpose      | ripple current, bulk energy     | EMI, switch-node overshoot, rail hold-up |
| size for     | RMS ripple + ESR rating         | low ESL, small loop, hold-up during spike |

**The electrolytics own the loss; the ceramics own the HF behaviour.** Ceramics are
*not* an efficiency part — they cut HF noise/EMI and Vds overshoot, not power loss.



## Loss split (Fugu2 @ 72→27 V, 30 A, D = 0.375, 39 kHz)

Ripple (→ electrolytics). At 39 kHz the electrolytics are low-Z (~17 mΩ) and the
ceramics high-Z (~194 mΩ), so >90 % of the ripple flows through the electrolytics:

$$ I_{cin,rms} = I_O\sqrt{D(1-D)} \approx 14.3\,\text{A} $$
$$ P_{ripple} \approx I_{cin,rms}^2 \cdot ESR_{elec} \approx 14.3^2 \cdot 16.5\,\text{m}\Omega \approx 3.4\,\text{W} $$

This is essentially the *whole* Cin loss.

**Temperature does *not* help here.** Aluminium-electrolytic ESR is strongly
temperature-dependent only on the **cold** side (below 20 °C, where the electrolyte
stiffens). *Above* 20 °C the impedance/ESR is nearly flat — per Rubycon's own curve
(technical note Fig. 14, `Zt/Z(20°C)`) the impedance ratio is ~1.0 at 20 °C, ~0.95 at
60–70 °C, ~0.90 at 105 °C, and the ZLH tan δ curve (Fig. 15) is flat from 20 °C to
105 °C. So hot ESR is only ~4–5 % below the 20 °C spec → **no meaningful hot
derating** (an earlier estimate of "~2 W hot" was wrong; it's ~3.2–3.4 W hot too).
Second-order, 39 kHz is *below* the 100 kHz spec point, so real ESR at 39 kHz is if
anything slightly *higher* than the datasheet 33 mΩ. Net: the 20 °C / 100 kHz value
is a good, slightly-conservative estimate; the tool's ~3.4 W is essentially correct.

Spikes (→ ceramics). Per HS turn-on the ceramics deliver Qrr + Qoss ≈ 860 nC in
~18 ns (≈48 A peak), but that is only **0.73 A rms**. The spike is a **tens-of-MHz**
event, so it sees the ceramic's **ring-band ESR ~26 mΩ**, *not* the ~3–5 mΩ 50 kHz /
SRF-floor value (reading a MHz phenomenon off the low-frequency ESR is the same
wrong-band trap as reading electrolytic ESR at the wrong point). That gives
0.73² · 26 mΩ ≈ **14 mW** — still **negligible** (~250× below the ripple; the spike RMS
is ~20× smaller). The electrolytics **can't** supply these spikes (their ~11 nH ESL is
near-open at MHz) — that is why the ceramics sit in the hot loop. (Ring-band ESR and the
DC-bias'd SRF: `dcdc-tools/loss/docs/ring.md`.)

> The Qrr/Qoss *energy* (~0.6 + 1.0 W) **is** a real loss, but it is dissipated in the
> **FET channels** (counted as P_rr / P_coss in the loss budget), not the caps.

## How to reduce P_cin (and what doesn't)

`P_cin = I_cin,rms² · ESR`, and for a buck the input-cap ripple current is set by the
**chopped DC load current**, not by the inductor ripple:

$$ I_{cin,rms}^2 = \underbrace{I_O^2\,D(1-D)}_{\text{chopped DC — fixed}} + \underbrace{\tfrac{D\,\Delta I_L^2}{12}}_{\text{inductor ripple — tiny}} $$

For Fugu2 (32 A, D = 0.375, L ≈ 50 µH → ΔI_L ≈ 8.6 A pp): term 1 ≈ **240 A²**,
term 2 ≈ **2.3 A²** (< 1 %). So the loss is almost entirely the chopped DC term.

| lever | effect on P_cin | why |
|---|---|---|
| **more electrolytics ∥ / lower-ESR parts** | ✅ **P_cin ∝ 1/N** | same ripple current splits over N caps → ESR/N; also cooler → longer life |
| raise f_sw | ❌ ~none | `I_cin,rms = Io·√(D(1−D))` is **independent of f_sw**; only shrinks ripple *voltage*, and raises FET + core loss |
| raise L | ❌ ~none (~25 mW) | only shrinks term 2; doubling L saves <1 % of I_cin,rms². And on Fugu2 → more turns → **higher DCR** (the dominant loss) |

The classic trap: higher L / higher f_sw reduce the **inductor's triangular ripple**,
which lands in the **output** cap (`I_cout,rms = ΔI_L/√12`), *not* the input cap. The
input cap bursts because the HS FET is fully on/off — a duty-cycle effect L and f_sw
can't change. **The only real Cin lever is ESR: more electrolytics in parallel.**
On this magnetics-limited board that's also cheap vs. touching the coil.

Refs: full loss budget `Fugu2/spice/loss_budget.py`; hot-loop L & overshoot
`Fugu2/spice/PARASITIC_MODELING.md`; ceramic vendor SPICE models (TY/Murata DC-bias)
`Fugu2/spice/extract/capmodels/`.

---

# Ceramic

MLCC have can have poor DC bias performance, resulting capacity drop of around 80% at 80V (100V rated voltage).

https://docs.google.com/spreadsheets/d/1vxxJvD4m8UsKfiyYFJieKQtYqnGDK7agQkgYiSCFPeM/edit?usp=sharing

* X7S (and C0G ?) has lower DC-bias capacitance drop
    * good for snubbers, input caps

**Verified 72 V effective-C** (populated parts, read off the vendor DC-bias curves at the
72 V rail): 220 nF **0.164×**, 1 µF **0.195×**, 10 µF **0.157×**. The **10 µF derates the
*hardest*** (a "10 µF" contributes only ~**1.57 µF** at the rail), the 1 µF the least — bigger
case ≠ automatically better, so budget effective C accordingly.

> Per-part ESR(f) / ESL / DC-bias curve values, the cross-check that the TY/Murata SPICE models
> are datasheet-faithful, the SRF-into-ring-band effect, and **how the loss tool resolves caps
> by value-bucket (not MPN)** are in the tool repo: `dcdc-tools/loss/docs/capacitors.md`
> (mechanism: `dcdc-tools/loss/docs/ring.md`).

## Which ceramics carry the ring (BOM / depopulation)

A **first-cut** ranking splits the commutation-ring current **∝ 1/branch-L** (at tens of MHz,
ωL_b ≫ R_b), from the FastHenry branch inductances (copper geometry):

| cap | branch L | 1/branch-L share |
|---|---|---|
| C18, C9, C17 | 0.80–0.92 nH | **~62 % total** |
| C16 | 1.24 nH | ~14 % |
| C21, C22 (10 µF) | 2.0–3.1 nH | ~9 % / ~6 % |
| **C27** (1 µF) | **5.67 nH** | **~3 %** |

**But `∝ 1/branch-L` is the trunk/scalar approximation — it drops the mutual coupling between
branches, and for a decoupled far cap that is badly wrong.** The authoritative physical port
matrix (ceramic ESL/ESR + all off-diagonals, `--cin-esl/--cin-esr`) has now been run
(`dcdc-tools/loss/cin_physical_split.py`), and it splits into two regimes:

- **f_sw ripple band (100 kHz–1 MHz) — the ESR *heat*.** Capacitance-dominated: the two
  **10 µF C21/C22 carry ~83 % of the current, ~91 % of the MLCC ESR loss**; **C27 ~3 %**. Here
  the 1/branch-L proxy is *wrong the other way* (it says C27 ~3 % for the right reason but ranks
  the small-L near caps top, when the big-C caps actually own the ripple).
- **HF ring (>SRF, ~55 MHz) — inductive.** Mutual coupling matters: the full matrix gives
  **C27 ≈ 26 % of the ring current / 22 % of the ring ESR-loss**, *not* ~3 %. C27 is far/
  decoupled, so it escapes the near-bank's circulating cancellation and carries a clean large
  slice.

**C27 is still a depopulation candidate — but on the *ripple* argument, not the ring one.**
It does ~no f_sw ripple work (~3 % of the ESR heat; a 1 µF ceramic against the electrolytics
that own the ripple), so pulling it costs little filtering. What is **not** true is the earlier
"~3 % at the ring": C27 actually carries ~26 % of the ring *current*. Removing it barely moves
the *aggregate* SW ring/peak (Z_eff is common-mode — the parallel caps back-fill), but do not
justify the pull with the 1/branch-L ring figure. Mechanism + the extractor's automatic depop
flag + the three-band reconstruction: `dcdc-tools/loss/docs/ring.md` §8.

|                                                        |       |      |     |      | 80V dc-bias | R@1kHz | R@50Khz | px              |                                                                                                   |
|--------------------------------------------------------|-------|------|-----|------|-------------|--------|---------|-----------------|---------------------------------------------------------------------------------------------------|
| murata GRM31cr60e227                                   |       |      |     |      |             |        |         |                 |                                                                                                   |
| murata GRM32EC72A106KE05L                              | 10uF  | 100V | X7S | 1210 | 1.4uF       |        | 5mΩ     | 100: 0,47750 €  | [link](https://www.murata.com/en-global/products/productdetail?partno=GRM32EC72A106KE05%23)       |
| tdk C5750X7S2A106K230KB                                | 10uF  | 100V | X7S |      | 2.22uF      | 162mΩ  | 6.3mΩ   |                 | [link](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A106K230KB) |
| tdk CKG57NX7R2A106M500JH                               | 10uF  | 100V | X7R |      | 3.6uF       | 104mΩ  | 5.3mΩ   |                 | 5mm MEGACAP!  expensive                                                                           |
| tdk C3216X6S2A106K160AC                                | 10uF  | 100V | X6S |      | 0.8uF       |        | 4mΩ     |                 |                                                                                                   |
| yuden HMK107C7224KAHTE / MCASH168SC7224 (C17/C18)      | 220nF | 100V | X7S | 0603 | -86% (31nF) |        | 96m     |                 | [link](https://ds.yuden.co.jp/TYCOMPAS/or/detail?pn=MCASH168SC7224KTCA01&u=M)                     |
| yuden HMK212BC7105KGHTE (smps)                         | 1uF   | 100V | X7S | 0805 | -83%        | 762Ω   | 20m     | 100 : 0,14650 € | [link](https://ds.yuden.co.jp/TYCOMPAS/ut/detail?pn=MMASH21GBC7105KTCA01&u=M)                     |
| murata GRJ21BC72A105ME11L                              | 1uF   | 100V |     |      | 0.165uF     | 1.5k   | 40m     | 100 : 0,10120 € |                                                                                                   |
| yuden HMR212CC7105KG-T (bypass)                        | 1uF   | 100V | X7S | 0805 | -82%        | 724    | 20m     | 100 : 0,12090 € |                                                                                                   |
| yuden HMK316AC7225KL-TE (smps)                         | 2.2   | 100V |     |      |             |        | 10m     | 100 : 0,16320   |                                                                                                   |
| TY MSASH32MSB5475MPCA01 (smps)  <br/> HMK325BJ475MM-PE | 4.7uF | 100V |     |      |             | 130mΩ  | 6mΩ     | 100 : 0,17120 € |                                                                                                   |

# Electrolytic


|   |   |   |   |   |   |
|---|---|---|---|---|---|
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |


$$ C_{in} >= \frac{D \cdot (1-D) \cdot I_O}{ \Delta V_{in} \cdot f_{sw} }$$

[ref: TIDA-010042 400-W GaN-Based MPPT Charge Controller](https://www.ti.com/lit/ug/tiduej8c/tiduej8c.pdf#page=13)

How to select input capacitors for a buck converter https://www.ti.com/lit/pdf/slyt670

TDK has a
good [parametric search](https://product.tdk.com/de/search/capacitor/ceramic/mlcc/list#ref=characteristic&1a_dcbias%5Bt%5D=80&1a_dcbias%5Bl%5D=1&1a_dcbiasc_f%5Bt%5D=0.15&1a_dcbiasc_t%5Bt%5D=1&1a_dcbiasc_t%5Bl%5D=1.00E-06&_l=100&_p=1&_c=2el_dcbias_meas-2el_dcbias_meas&_d=1&_106=1)

[Digikey aluminium elec. caps D=16mm](https://www.digikey.de/short/dhw78pnf)

See parts datasheet for rated ripple current. Manufacturers usually specify it at 100khz, 105°C.
You'll usually find impedance as well, which gives you an idea how much power lost in the capacitor.

Loss is proportional to HF impedance, usually specified in the data sheet at 100 kHz.

## Film bulk option

Film caps are plausible as an electrolytic replacement only if we accept more input
ripple, higher switching frequency, or a large off-board/edge-of-board capacitor bank.
They do not remove the buck input-cap RMS-current requirement:

$$ I_{cin,rms} \approx I_O\sqrt{D(1-D)} \approx 15\,\text{A} $$

At the current Fugu2 operating point (72→27 V, 32 A, D≈0.375, 39 kHz), the capacitance
needed for a target input ripple is:

| fsw | 0.2 Vpp, roughly present electrolytic-class ripple | 0.5 Vpp | 1.0 Vpp |
|---:|---:|---:|---:|
| 39 kHz | ~960 µF | ~385 µF | ~190 µF |
| 120 kHz | ~313 µF | ~125 µF | ~63 µF |
| 250 kHz | ~150 µF | ~60 µF | ~30 µF |

So a practical film experiment is not "one film cap" at 39 kHz; it is around
**200 µF** for a 1 Vpp target. At 120 kHz the same 1 Vpp target drops to about
**63 µF**, and at 250 kHz it drops to about **30 µF**. Keep the ceramic hot-loop bank
either way: film bulk replaces the slow switching-ripple/energy role, not the
tens-of-MHz commutation-spike role.

Approximate bank sizes and cost using the cheap shortlisted 20 µF KEMET C4AQCBW5200A3FJ
and 15 µF Eaton EFDKS55K156D132LH. Prices below assume the ~200-piece DigiKey break:
KEMET 20 µF at **$3.61** each (116+ tier) and Eaton 15 µF at **$2.61** each
(140+ tier).

| fsw | target ripple | 20 µF MPN | with 20 µF film | 20 µF price | 15 µF MPN | with 15 µF film | 15 µF price |
|---:|---:|---|---:|---:|---|---:|---:|
| 39 kHz | 0.2 Vpp | C4AQCBW5200A3FJ | 48 pcs = 960 µF | ~$173 | EFDKS55K156D132LH | 64 pcs = 960 µF | ~$167 |
| 39 kHz | 0.5 Vpp | C4AQCBW5200A3FJ | 20 pcs = 400 µF | ~$72 | EFDKS55K156D132LH | 26 pcs = 390 µF | ~$68 |
| 39 kHz | 1.0 Vpp | C4AQCBW5200A3FJ | 10 pcs = 200 µF | ~$36 | EFDKS55K156D132LH | 13 pcs = 195 µF | ~$34 |
| 120 kHz | 0.2 Vpp | C4AQCBW5200A3FJ | 16 pcs = 320 µF | ~$58 | EFDKS55K156D132LH | 21 pcs = 315 µF | ~$55 |
| 120 kHz | 0.5 Vpp | C4AQCBW5200A3FJ | 7 pcs = 140 µF | ~$25 | EFDKS55K156D132LH | 9 pcs = 135 µF | ~$23 |
| 120 kHz | 1.0 Vpp | C4AQCBW5200A3FJ | 4 pcs = 80 µF | ~$14 | EFDKS55K156D132LH | 5 pcs = 75 µF | ~$13 |
| 250 kHz | 0.2 Vpp | C4AQCBW5200A3FJ | 8 pcs = 160 µF | ~$29 | EFDKS55K156D132LH | 10 pcs = 150 µF | ~$26 |
| 250 kHz | 0.5 Vpp | C4AQCBW5200A3FJ | 3 pcs = 60 µF | ~$11 | EFDKS55K156D132LH | 4 pcs = 60 µF | ~$10 |
| 250 kHz | 1.0 Vpp | C4AQCBW5200A3FJ | 2 pcs = 40 µF | ~$7 | EFDKS55K156D132LH | 2 pcs = 30 µF | ~$5 |

The capacitance math improves quickly with frequency, but the system trade changes:
120 kHz and 250 kHz move the input-ripple fundamental closer to / into the conducted
EMI band, and FET/Qrr/Coss/core losses must be re-budgeted rather than scaled only
from the capacitor table.

Current DigiKey shortlist (2026-07-08, USD; bank-cost examples use the shown
quantity break where available; verify stock/price before ordering):

| part | value | voltage | dielectric / role | ESR | size | price basis | 1 Vpp bank |
|---|---:|---:|---|---:|---|---:|---:|
| [Eaton EFDKS55K156D132LH](https://www.digikey.com/en/products/filter/film-capacitors/15-%C2%B5f/62) | 15 µF | 550 V | PP, DC filtering | - | 32 x 22 x 37.8 mm | ~$2.61 @140+ | 13 pcs = 195 µF, ~$34 |
| [Eaton EFDKS70K156D132LH](https://www.digikey.com/en/products/filter/film-capacitors/15-%C2%B5f/62) | 15 µF | 700 V | PP, DC filtering | - | 32 x 22 x 37.8 mm | ~$2.59 @140+ | 13 pcs = 195 µF, ~$34 |
| [KEMET C4AQCBW5200A3FJ](https://www.digikey.com/en/products/filter/film-capacitors/20-%C2%B5f/62) | 20 µF | 650 V | PP, AEC-Q200 DC link | 5.3 mΩ | 42 x 20 x 40.2 mm | ~$3.61 @116+ | 10 pcs = 200 µF, ~$36 |
| [TDK B32776Z0206K000](https://www.digikey.com/en/products/filter/film-capacitors/20-%C2%B5f/62) | 20 µF | 1000 V | PP, DC link | 6 mΩ | 42 x 30 x 45 mm | ~$6.76 | 10 pcs = 200 µF, ~$68 |
| [WIMA DCP4L052007GD4KSSD](https://www.digikey.com/en/products/filter/film-capacitors/20-%C2%B5f/62) | 20 µF | 800 V | PP, AEC-Q200 DC link | 6.2 mΩ | 41.5 x 20 x 39.5 mm | ~$9.62 | 10 pcs = 200 µF, ~$96 |
| [KEMET C4ATDBW5200A30J](https://www.digikey.com/en/products/filter/film-capacitors/20-%C2%B5f/62) | 20 µF | 250 V | PP, DC link / switching | 4.2 mΩ | 42.5 x 28 x 37 mm | ~$13.43 | 10 pcs = 200 µF, ~$134 |

Current LCSC shortlist (2026-07-08, USD; live stock/prices, verify before ordering):

| part | LCSC | value | voltage | package | stock | price basis | 1 Vpp bank | notes |
|---|---|---:|---:|---|---:|---:|---:|---|
| [XIAMEN FARATRONIC C3D1U206JF0BC00](https://www.lcsc.com/product-detail/C783659.html) | C783659 | 20 µF | 600 V | TH, P=37.5 mm | 284 | ~$2.07 @126+ | 10 pcs = 200 µF, ~$21 | best confirmed 20 µF LCSC fit |
| [KYET C3D206K2H2702P](https://www.lcsc.com/product-detail/C51939908.html) | C51939908 | 20 µF | 500 V | TH, P=27.5 mm | 65 | ~$1.30 @30+ | 10 pcs = 200 µF, ~$13 | cheap, but low stock and 85 °C |
| [HONGFA HCDB/1U1505KB420](https://www.lcsc.com/product-detail/C5128961.html) | C5128961 | 15 µF | 600 V | DIP-4, P=27.5 mm | 176 | ~$1.34 @100+ | 13 pcs = 195 µF, ~$17 | good price, stock below 200 |
| [KYET KP106J2E2701](https://www.lcsc.com/product-detail/C5116053.html) | C5116053 | 10 µF | 250 V | TH, P=27.5 mm | 2128 | ~$0.41 @100+ | 20 pcs = 200 µF, ~$8 | very cheap, twice the placements |
| [KYET MPBH106K2H2701](https://www.lcsc.com/product-detail/C18214247.html) | C18214247 | 10 µF | 500 V | TH, P=27.5 mm | 2726 | ~$0.53 @30+ | 20 pcs = 200 µF, ~$11 | better voltage margin than the 250 V part |

Using the LCSC Faratronic 20 µF part at the 126+ price, the same 20 µF bank table
becomes approximately: 39 kHz = **$99 / $41 / $21** for 0.2 / 0.5 / 1.0 Vpp,
120 kHz = **$33 / $14 / $8**, and 250 kHz = **$17 / $6 / $4**.

First prototype picks: **10x LCSC C783659**, **10x KEMET C4AQCBW5200A3FJ**, or
**13x Eaton EFDKS55K156D132LH**. The LCSC 10 µF KYET options are cheaper, but they
double placement count and need a datasheet check for ripple-current/thermal limits.
Avoid the 100 V film parts for this role unless the input is truly clamped well
below 100 V; many of the attractive 100 V listings are polyester and leave little
transient margin for a solar input.

## Rubycon

* [Rubycon Catalog](https://www.rubycon.co.jp/wp-content/uploads/catalog/aluminum-catalog.pdf)
* [Rubycon PX Series](https://www.digikey.de/en/htmldatasheets/production/1059592/0/0/1/16px100mefc5x11)

* ZL low imp.
    * ZLH long life
        * ZLJ high ripple
        * ZLQ mini (up to 35V)

## Selection

Round 100 V electrolytic picks for the input bulk positions, using **35 mΩ max** as
the practical impedance filter. Board footprints cover 7.5 mm lead pitch with 16 mm
and 18 mm cans; check enclosure height before using the 40 mm parts. Prices are live
distributor checks from 2026-07-08. The preferred basis is the DigiKey 200-piece
break; where DigiKey did not expose that break in public indexed data, the nearest
visible break is shown.

| mfr, series | cap | v | D | L | ripple @100 kHz | imp @20°C/100 kHz | price basis | px/Z | MPN / supplier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Rubycon ZLH | 470 µF | 100 | 16 | 31.5 | 2.40 A | **33 mΩ** | ~$1.17 @200, $233.22/200 | ~$0.035/mΩ | [100ZLH470MEFCGC16X31.5](https://www.digikey.com/en/products/detail/rubycon/100ZLH470MEFCGC16X31-5/3568260) |
| Rubycon ZLJ | 470 µF | 100 | 16 | 31.5 | 2.64 A | **32 mΩ** | ~$1.37 @200, $273.03/200 | ~$0.043/mΩ | [100ZLJ470M16X31.5](https://www.digikey.com/en/products/detail/rubycon/100ZLJ470M16X31-5/3133973) |
| Chemi-Con KZN | 680 µF | 100 | 16 | 40 | higher than KZE | **<30 mΩ class** | ~$2.11 @50 | >~$0.070/mΩ | [EKZN101ELL681ML40S](https://www.digikey.com/en/products/detail/chemi-con/EKZN101ELL681ML40S/4843960) |
| Chemi-Con KZE | 470 µF | 100 | 16 | 31.5 | 1.85 A | **32 mΩ** | ~$2.27 @50, 200 not exposed | ~$0.071/mΩ @50 | [EKZE101ELL471MLN3S](https://www.digikey.com/en/products/detail/chemi-con/EKZE101ELL471MLN3S/4001432) |
| Rubycon ZLJ | 680 µF | 100 | 16 | 40 | 3.15 A | **20 mΩ** | ~$1.73 @200, $345.83/200 | ~$0.086/mΩ | [100ZLJ680M16X40](https://www.digikey.com/en/products/detail/rubycon/100ZLJ680M16X40/3133975) |
| Rubycon ZLJ | 680 µF | 100 | 18 | 35.5 | 3.15 A | **20 mΩ** | ~$2.48 @200, $496.32/200 | ~$0.124/mΩ | [100ZLJ680M18X35.5](https://www.digikey.com/en/products/detail/rubycon/100ZLJ680M18X35-5/3564783) |
| Chemi-Con KYB | 470 µF | 100 | 16 | 31.5 | 2.40 A | **22 mΩ** | ~$3.51 @1, limited stock | ~$0.160/mΩ | [EKYB101ELL471MLN3S](https://www.digikey.com/en/products/detail/chemi-con/EKYB101ELL471MLN3S/4843834) |
| Chemi-Con KZE | 680 µF | 100 | 16 | 40 | 2.20 A | **27 mΩ** | DigiKey page, 200 not exposed | - | [EKZE101ELL681ML40S](https://www.digikey.com/en/products/detail/chemi-con/EKZE101ELL681ML40S/4001435) |
| Chemi-Con KZE | 680 µF | 100 | 18 | 35.5 | 2.20 A | **27 mΩ** | DigiKey page, 200 not exposed | - | [EKZE101ELL681MMP1S](https://www.digikey.com/en/products/detail/chemi-con/EKZE101ELL681MMP1S/756261) |
| Chemi-Con KZE | 560 µF | 100 | 16 | 35.5 | 2.00 A | **29 mΩ** | DigiKey page, 200 not exposed | - | [EKZE101ELL561MLP1S](https://www.digikey.com/en/products/detail/chemi-con/EKZE101ELL561MLP1S/756260) |
| Rubycon ZLJ | 820 µF | 100 | 16 | 40 | 3.71 A | **18 mΩ** | check stock/height | - | 100ZLJ820M16X40 |
| Rubycon ZLJ | 820 µF | 100 | 18 | 35.5 | 3.71 A | **18 mΩ** | check stock/height | - | 100ZLJ820M18X35.5 |

Older / unresolved references:

| mfr, series | cap | v | D | L | ripple @100 kHz | imp @20°C/100 kHz | price basis | MPN |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Rubycon PX | 470 µF | 100 | 16 | 26 | 1.06 A | <60 mΩ? | - | - |
| Nichicon HE(M) | 470 µF | 100 | 16 | 36 | 1.9 A | 45 mΩ | - | - |
| BERYL RC | 470 µF | 100 | 16 | 26 | 1.98 A | 60 mΩ | - | LCSC C365811 |
| Samyoung NXA | 470 µF | 100 | 16 | 31.5 | 1.85 A | 32 mΩ | - | [pdf](https://www.samyoung.co.kr/download/new/NXA.pdf) |
| Nichicon UHE | 680 µF | 100 | 18 | 35.5 | 1.89 A | 40 mΩ | ~$1.00 @100 LCSC | UHE2A681MHD / LCSC C340710 |
