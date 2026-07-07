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

## DC-bias at the 72 V operating point (verified vs vendor curves)

The parts table below lists the **80 V** DC-bias spec, but the Fugu2 rail is **72 V**.
Reading each populated part's vendor DC-bias curve at 72 V (Taiyo Yuden TY-COMPAS CSV/chart,
Murata SimSurfing CSV) gives the fraction of nominal C actually present:

| populated part | nominal | **C(72 V)/C₀** | SRF @ 0 V → @ 72 V bias |
|---|---|---|---|
| Yuden MCASH168SC7224 (C17/C18) | 220 nF 0603 | **0.164×** (→ 36 nF) | 18.5 → ~46 MHz |
| Yuden MMASH21GBC7105 (C9/C16/C27) | 1 µF 0805 | **0.195×** (→ 195 nF) | 7.3 → higher |
| Murata GRM32EC72A106KE05 (C21/C22) | 10 µF 1210 | **0.157×** (→ 1.57 µF) | 1.6 → higher |

- **The 10 µF derates the *hardest* (0.157×), the 1 µF the *least* (0.195×)** — bigger case ≠
  automatically better. Budget effective C accordingly: a "10 µF" contributes only ~1.57 µF.
- **The derate pushes the hot-loop cap's SRF up into the ~50 MHz commutation-ring band**
  (220 nF: 18.5 → ~46 MHz). So at the ring the ceramic self-resonates — minimum impedance,
  ESL-limited (matches the "limited by ESL" row above), which is why it's the effective HF
  decoupler. The C-derate sets *where that minimum lands*, **not** the ring frequency (the ring
  is loop-L × FET-C_oss). Vendor SPICE models (TY/Murata) cross-check **faithful** to these
  curves. Mechanism + which caps carry the ring (depop candidates): `dcdc-tools/loss/docs/ring.md`.

## Which ceramics carry the ring (BOM / depopulation)

The near-cap branches are in parallel, so the commutation-ring current splits
**∝ 1/branch-L** (at tens of MHz, ωL_b ≫ R_b). By the FastHenry branch inductances
(copper geometry):

| cap | branch L | ring share |
|---|---|---|
| C18, C9, C17 | 0.80–0.92 nH | **~62 % total** (the working HF decouplers) |
| C16 | 1.24 nH | ~14 % |
| C21, C22 (10 µF) | 2.0–3.1 nH | ~9 % / ~6 % |
| **C27** (1 µF) | **5.67 nH** | **~3 %** |

**C27 is a depopulation candidate.** Though it is a 1 µF 0805 grouped with the near caps,
it sits far from the loop (branch L ~7× C18's) and does ~no HF decoupling — the SW peak/ring
barely moves without it. Its ripple role is also negligible (a 1 µF ceramic vs the
electrolytics that own the ripple).

Caveat: this is the **1/branch-L copper proxy**. The authoritative physical current-split
(ceramic ESL/ESR in the extractor, `--cin-esl/--cin-esr`) is still pending — the ideal-cap
copper-only split *over-rates* far caps (C27 reads 28 % there), so confirm on the physical run
before pulling it. Mechanism + the extractor's automatic depop flag:
`dcdc-tools/loss/docs/ring.md` §8.

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

$$ C_{in} >= \frac{D \cdot (1-D) \cdot I_O}{ \Delta V_{in} \cdot f_{sw} }$$

[ref: TIDA-010042 400-W GaN-Based MPPT Charge Controller](https://www.ti.com/lit/ug/tiduej8c/tiduej8c.pdf#page=13)

How to select input capacitors for a buck converter https://www.ti.com/lit/pdf/slyt670

TDK has a
good [parametric search](https://product.tdk.com/de/search/capacitor/ceramic/mlcc/list#ref=characteristic&1a_dcbias%5Bt%5D=80&1a_dcbias%5Bl%5D=1&1a_dcbiasc_f%5Bt%5D=0.15&1a_dcbiasc_t%5Bt%5D=1&1a_dcbiasc_t%5Bl%5D=1.00E-06&_l=100&_p=1&_c=2el_dcbias_meas-2el_dcbias_meas&_d=1&_106=1)

[Digikey aluminium elec. caps D=16mm](https://www.digikey.de/short/dhw78pnf)

See parts datasheet for rated ripple current. Manufacturers usually specify it at 100khz, 105°C.
You'll usually find impedance as well, which gives you an idea how much power lost in the capacitor.

Loss is proportional to HF impedance, usually specified in the data sheet at 100 kHz.

## Rubycon

* [Rubycon Catalog](https://www.rubycon.co.jp/wp-content/uploads/catalog/aluminum-catalog.pdf)
* [Rubycon PX Series](https://www.digikey.de/en/htmldatasheets/production/1059592/0/0/1/16px100mefc5x11)

* ZL low imp.
    * ZLH long life
        * ZLJ high ripple
        * ZLQ mini (up to 35V)

## Selection

| mfr, series   | cap  | v   | D  | L    | ripple @100khz | imp@20°C/100khz | px100  | MPN                                                    |
|---------------|------|-----|----|------|----------------|-----------------|--------|--------------------------------------------------------|
| rubycon PX    | 470µ | 100 | 16 | 26   | 1.06           | <60mΩ  ?        |        |                                                        |
| nichicon HE(M | 470µ | 100 | 16 | 36   | 1.9            | 45mΩ            |        |                                                        |
| rubycon ZLH   | 470µ | 100 | 16 | 31.5 | 2.4@100khz     | 33mΩ            |        |                                                        |
| rubycon ZLJ   | 470µ | 100 | 16 | 31.5 | 2.65           | 32mΩ            | $1.5   |                                                        |
| rubycon ZLJ   | 470µ | 100 | 18 | 25   | 2.5            | 36mΩ            | $1.3   |                                                        |
| BERYL RC      | 470µ | 100 | 16 | 26   | 1.98           | 60mΩ            |        | LCSC C365811                                           |
| samyoung NXA  | 470µ | 100 | 16 | 31.5 | 1.85           | 32mΩ            |        | [pdf](https://www.samyoung.co.kr/download/new/NXA.pdf) |
| Chengx KM     |      | 100 | 16 | 25   | 0.918          |                 |        |                                                        |
| Chemi-Con KZN | 560µ | 100 | 18 | 26.5 | 2.75           | 27mΩ            |        |                                                        |
| Chemi-Con KZN | 680µ | 100 | 16 | 35.5 | 3.15           | 20mΩ            | 1.05 € | EKZN101ELL681MLP1S                                     |

