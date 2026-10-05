# Fugu2 GateDrive sheet: independent schematic review

Date: 2026-09-30. Reviewer: Claude (subagent). This review was read-only; no project file was modified.

## Scope and inputs

- Sheet: `GateDrive.kicad_sch`, from render `/tmp/fugu_split/work/svg/Fugu2-GateDrive.png`. The image was visually reviewed after a vision probe passed in the same session.
- Netlist: `/tmp/fugu_split/repo.net`, parsed with `/tmp/fugu_split/review_GateDrive/nl.py`. It has 138 components and 83 nets.
- ERC: `/tmp/fugu_split/work/erc_after.rpt`.
- Interface sheets read: PowerStage and PowerSupply renders.
- `Fugu2.kicad_pcb`: I read footprint positions only, as text, without writing anything.
- Design docs: `doc/Gate Drive.md`, `doc/Backflow Switch.md`, `doc/Power Supply.md`, `README.md` (80 V max PV, 12–60 V battery, 32 A, boost with terminals swapped) and `HW Stories/flat.md`.
- Firmware: `~/dev/pv/fugu-mppt-firmware/src/buck.h` (bootstrap refresh and max duty) and `src/mppt.h` (bflow min duty).

### Datasheets read (source, revision)

| Part | Source | Used for |
|---|---|---|
| UCC21330-Q1 (U1) | TI SLUSFF3A, Jan 2024 / rev Jun 2024. Local copy `~/dev/ee/datasheets/ucc21330-q1.pdf` | Pin table (Table 4-1), ROC (§5.3), UVLO/input/DT tables (§5.x p.8), logic tables 7-1..7-3, §7.4, §8.2.2.2 (RBOOT), §8.2.2.7 (caps), orderables |
| IPA050N10NM5S (Q1, Q3) | Infineon v02_01 (infineon.com dgdl) | Qg 51 typ / 68 max nC at 10 V; VGS ±20 V |
| IPP022N12NM6 (Q2) | Infineon v02_00 | Qg 113 / 141 nC at 10 V; Vth 2.6–3.6 V; Ciss 8.1 nF |
| TPH1R306PL (Q5–Q7) | Toshiba datasheet, 2019-10-18. Fetched at rung 4: headless Chrome with a plain UA, navigating the product page and then docget did=30818. curl got a 403 from Akamai. | Qg 91 nC; Ciss 6250 pF; Vth 1.5–2.5 V; VGS ±20 V |
| DSS310 Slkor (D8, D10) | LCSC C41369492 datasheet (Slkor, Rev.1 2017) | 100 V; IR 0.02 mA at 25 °C and 2 mA at 100 °C at rated VR; Cj 300 pF; package SOD-123FL |
| BSS123 (Q4) | Diodes DS30366 Rev 24-2 | 100 V; VGS(th) 0.8–2.0 V; SOT-23 pinout G=1, S=2, D=3 (verified on the page-1 graphic) |
| BZT52C13-TP (DZ2) | MCC BZT52C2V0–C75 Rev.3-6-05282025. Fetched through a browser on the mccsemi product page. | Vz 12.4 / 13 / 14.1 V at 5 mA |
| AP3012 (U5, +12V source) | Diodes AP3012.pdf | VFB 1.17 / 1.25 / 1.33 V; VOUT = 1.25·(1+R1/R2) |
| ESP32-S3 | Espressif datasheet v2.2 | Pin reset states (Table 2-1), power-up glitches (Table 2-2), VOH ≥ 0.8·VDD |

## Findings (most severe first)

### F1 — MAJOR (confirmed from values and datasheet; the rail was not measured): the "+12V" gate-drive rail is set to about 9.3 V, and the bootstrap then falls to or below the UCC21330B UVLO at high duty

- **Evidence.** `+12V` has only one source: U5 AP3012 through D17. Its feedback divider is R37 = 33k (+12V→FB) and R38 = 5.1k 1% (FB→GND). R38 is labelled Rfb2 on PowerSupply.
  - VOUT = 1.25 × (1 + 33/5.1) = **9.34 V typ**, with a range of 8.74–9.94 V over the VFB limits 1.17–1.33 V.
  - These values have been in place since commit `e4972e0` ("onboard 12v supply", 2025-11-10) and still are at HEAD.
  - The sheet's own table next to U5 lists 43k/5.1k → 11.8 V and 33k/4.3k → 10.8 V. So 33k/5.1k matches none of the listed rows.
- **Impact on U1 (UCC21330BQDRQ1, 8 V UVLO option).**
  - The recommended minimum VDDx is **9.2 V** (SLUSFF3A §5.3; orderable table p.1 "UCC21330BQDRQ1 … 9.2V").
  - UVLO falling threshold is 7.2 / 7.9 / 8.4 V. Rising threshold is 7.7 / 8.5 / 8.9 V (§5.x UVLO table).
  - VDDA (low side): 9.34 V typ. That is at the recommended minimum, and at the low VFB corner (8.74 V) it is below it.
  - VDDB (bootstrap):
    - Formula: VDDB ≈ V12 − Vf(D10) − ΔV(R19). Per cycle, ΔV(R19) ≈ Q_cycle·R19 / t_LS.
    - Q_cycle ≈ 2 × Qg(IPA050N10NM5S at about 8.5 V, ≈ 45 nC) plus IVDDB/fsw (≈ 2 mA / 39.3 kHz ≈ 50 nC), so about 140 nC.
    - The firmware's minimum LS on-time is 2 µs (`buck.h`, `boot_refresh_ns` = 2000). At that point ΔV ≈ 140 nC × 22 Ω / 2 µs ≈ 1.5 V.
    - Result: VDDB ≈ 9.34 − 0.5 − 1.5 ≈ **7.3 V**. That is below the typical UVLO-off level, so HO drops pulses.
    - Even at moderate duty, VDDB is about 8.8 V, which is below the 9.2 V recommended minimum.
- **Field corroboration.**
  - `HW Stories/flat.md`: "when connecting the gate discharge r 2.2, it fails (boot strap supply UV, failure)".
  - Firmware comment in `buck.h` (about line 1222): measured HS-drive "BURSTS" when the LS refresh is too short, and "LS ≥ 300 counts" was set empirically.
- **Fix.**
  - Change R38 to 3.9k (→ 11.8 V) or 4.3k with R37 = 33k, or use 43k/5.1k from the sheet table. Check AP3012 current capability at the higher output voltage; that belongs to the PowerSupply review.
  - Then also apply F3, which lowers R19.
  - Measure +12V, VDDA-VSSA and VDDB-SW at maximum duty on a built board.

### F2 — MAJOR (confirmed topology and placement): VDDA (low-side channel) has only 100 nF locally; the +12V bulk capacitor is about 53 mm away and returns to a different ground

- **Evidence.**
  - The +12V net has U1.16, C7 (100 nF X7R 25 V 0805, to BuckGND), R19 (bootstrap feed), D17, R37 and C28 (10 µF 16 V, to **GND**).
  - PCB positions: U1 at (38.0, 40.8); C7 at (41.1, 45.5); C28 at (75.7, 77.7) on F.Cu, next to U5.
- **Why it matters.**
  - Q2 (IPP022N12NM6) has Qg of 113 nC typ / 141 nC max at 10 V (Infineon v02_00). The C7 capacitance left under DC bias (≈ 70–80 nF at 9–12 V) would sag by more than 1.5 V on each LO turn-on. The rest has to come from C28 through a long trace plus the BuckGND→R26 shunt→GND return.
  - The bootstrap refill pulses (R19/D10, 0.1–0.5 A) come from the same node.
  - TI (§8.2.2.7.3) uses 10 µF + 220 nF on the non-bootstrap VDD, and says to add more than 10 µF if the supply is far away. Every test condition in the datasheet uses "1-µF + 100-nF from VDDA and VDDB".
- **Impact.** LO droop at LS turn-on, and bootstrap refill starved further (this compounds F1). It also creates a large loop that includes the current shunt.
- **Fix.** Add ≥ 4.7–10 µF, ≥ 25 V X7R, on VDDA–VSSA right at pins 16/14, keeping C7 as the HF capacitor.

### F3 — MINOR (confirmed): R19 = 22 Ω bootstrap resistor is outside TI's recommended 1–20 Ω and dominates VDDB droop at high duty

- **Evidence.** TI SLUSFF3A §8.2.2.2: "The recommended value for RBOOT is between 1 Ω and 20 Ω." With the numbers from F1, R19 costs about 1.5 V at the 2 µs minimum LS time.
- **What R19 does well.** It limits D10 displacement current from SW dv/dt (Cj 300 pF at 4 V) into +12V, and limits the inrush to the 10 µF C19 (about 0.5 A peak).
- **Fix.** Use about 4.7–10 Ω, together with F1 and F2.
- **Firmware coupling.** The 2 µs `boot_refresh_ns` floor and the maximum HS duty (≈ 1 − 2 µs × 39.3 kHz ≈ 0.92) were tuned around the current values. Revisit them after the change.

### F4 — MAJOR (plausible; depends on fault current and firmware latency): the backflow-switch turn-off through Q4/R22 is slow (about 0.3–1.5 ms) with no active gate-source discharge

- **Circuit.** Q4 (BSS123) pulls BflowG to GND through R22 = 47k. DZ2 then conducts forward, clamping Vgs at about −0.7 V.
- **Sink current.** About V(BflowS)/47k: 0.26 mA at a 12 V battery and 1.24 mA at 58.4 V.
- **Charge to remove.** C20 × ~11 V ≈ 110 nC, plus 3 × TPH1R306PL Qg (91 nC typ each at 10 V, Toshiba 2019-10-18) ≈ 270 nC. Total ≈ 380 nC.
- **Turn-off time.** About 0.3 ms at 58 V and about 1.5 ms at 12 V. The gate also crosses the Miller plateau slowly: Vth is only 1.5–2.5 V.
- **Conflict with the design intent.** `doc/Backflow Switch.md` says: "(2) In case of a shorted LS switch the backflow switch on the battery side can prevent a burned fuse". In that fault the battery drives current through Q5–Q7 → L1 → a shorted Q2. A millisecond-scale, plateau-dwelling turn-off would spend that time in linear mode at high current, which is an SOA risk for Q5–Q7, and F1 (40 A) may clear first anyway.
- **Scope.** For normal (non-fault) turn-off the speed is adequate.
- **Fix, if the protective claim is to hold.** Add an active G–S discharge referenced to BflowS: for example a PNP whose emitter is on BflowG and collector on BflowS, driven by Q4's pull-down current. Alternatively, restate the claim in the doc.
- **Standing drain.** With Q4 on and BF off, the battery cannot feed BflowS (body diode points toward the battery). So there is no drain from the battery at night, and R22 dissipation stays at 73 mW or less at 58.4 V (0805).

### F5 — MINOR (confirmed): the input RC filters recommended for INA/INB/DIS are absent; the R31–R33 placeholders are shorted out and excluded from the board

- **Evidence.** R31, R32 and R33 have `on_board no`, `in_bom no` and `dnp yes`. Wires with junctions bridge them: the netlist shows INL→U1.1, INH→U1.2 and SD→U1.5 as direct connections. The sheet note "use resistors to disconn drv & uC" is therefore not implemented.
- **What TI recommends** (Table 4-1, §7.4.1, §8.2.2.1):
  - INA/INB: R = 10–100 Ω, C = 10–100 pF.
  - DIS: R = 0–100 Ω, C = 100–1000 pF (≈ 1 nF) "when connecting DIS pin to a micro controller with distance".
- **Why it matters here.** These nets also go to J4 (the MCU-head option, a pin-header daughterboard), so the traces can be long and lie next to a noisy switch node.
- **Fix.** Populate real footprints: for example 47 Ω + 33 pF on INA/INB, and 47 Ω + 1 nF on DIS.

### F6 — MINOR (confirmed): bootstrap diode D10 and D8 are 100 V, which is the lowest voltage rating on the switch node

- **Evidence.**
  - D10's reverse voltage equals the SW peak (Vin plus overshoot). SW rings at 15–60 MHz (EMI notes).
  - DSS310 is rated 100 V, with IR up to 2 mA at 100 °C at rated voltage (Slkor Rev.1).
  - Q2 is 120 V. The PV maximum is 80 V (README).
- **Margin.** The project's own rule in `doc/Gate Drive.md` is "high voltage (≥ 1.5x of DC-Link)", which means ≥ 120 V. The README section "Higher input voltages" lists FETs and caps but not D8/D10.
- **Other effects.** Hot leakage adds up to about 2 mA of VDDB discharge and about 0.1 W in D10 when HO is on.
- **Fix.** Use a ≥ 150 V fast diode or a low-Cj Schottky (the doc table lists SS315 at 150 V), and add D8/D10 to the "Higher input voltages" list.

### F7 — MINOR (confirmed): C19 bootstrap capacitor is "10uF, 16V" with no dielectric specified

- **Evidence.** C19 is a 0805 part.
  - Normally VDDB-VSSB ≈ 9–12 V.
  - With SW undershoot (LS body diode plus ringing) the capacitor can overcharge by several volts. R19 limits this.
  - The effective capacitance of a 16 V 0805 10 µF at 11 V bias is probably only 30–40 % of nominal. That is still plenty for charge, but the voltage margin is thin.
  - TI's example uses 50 V capacitors (§8.2.2.7). Its note that a large CBOOT slows the first charge also applies with R19.
- **Fix.** Use a 25 V X7R part (for example 4.7 µF 25 V X7R 0805/1206) and specify the dielectric in the MPN field.

### F8 — MINOR (BOM hazard, confirmed): MPN/manufacturer fields are wrong or ambiguous

- U1's `MPN` field = "DNP". The part is populated; the Digikey field says UCC21330BQDRQ1. A BOM tool keyed on MPN would drop or flag the driver. Q1, Q2 and Q3 on PowerStage do the same.
- D8's MPN is "DSS310" with Manufacturer "Diodes Inc.", but DSS310 is a Slkor part (LCSC C41369492). D10 correctly says Slkor.
- DZ2: Value "BZT52C13-TP", MPN "BZT52C16 or BZT52C13-TP", LCSC "BZT52C16". A 16 V Zener is still under TPH1R306PL's VGS ±20 V, but the design intent (13 V) is ambiguous.
- D8/D10 use the footprint `Diode_SMD:D_SOD-123`, but DSS310 is SOD-123FL: body 3.55–3.75 × 1.75–1.95 mm, flat leads 0.8–1.1 mm wide. Check the land pattern against the SOD-123F / SOD-123FL pattern. This is plausible, not verified: I did not compare pad geometry.

### F9 — MINOR (plausible, firmware coupling): the backflow gate is charged only while HO is high and bleeds through R24 1M when switching stops

- **When the gate charges.** D8/R21 feed BflowG from VDDB. VDDB exceeds BflowS only while SW is high: when SW is low, VDDB ≈ 9–11 V, which is below BflowS.
- **Steady-state Vgs.** Vgs ≈ Vh·5D/(1+5D), clamped at 13 V by DZ2, where Vh ≈ Vin − Vout + V12 − 0.4. This is adequate across the stated operating range in buck mode: for example about 11 V at 30 V → 27 V.
- **But:**
  - The switch cannot be turned on without HS switching. This is relevant to boost mode and to HS-off / diode-emulation states.
  - The firmware comment in `mppt.h` ("TODO lift this, bflow switch will be powered from bootstrap cap and not gate drive signal") describes the current hardware. It does not remove the HS-on-time dependency.
  - When switching stops, the gate decays with τ ≈ 1 MΩ × (10 nF + about 27 nF effective) ≈ 37 ms, crossing Vth after roughly 70 ms unless firmware asserts BflowSD.
- **Fix.** None required in hardware. Make sure firmware asserts BflowSD on every stop or fault path, and correct the TODO comment.

### F10 — NIT: ERC items on this sheet

- `power_pin_not_driven`: U1 pin 9 (VSSB) on SW. There is no PWR_FLAG on SW after the sheet split. Add a PWR_FLAG to SW (the prior flat schematic did not show this error).
- `same_local_global_label`: the global `SW` (GateDrive) collides with the local label `SW` in PowerSupply (U5/L2/D17 node, net `/PowerSupply/SW`). KiCad keeps them separate and the connectivity is correct, but rename the local label (for example `SW_12V`) to avoid confusion.
- Off-grid endpoints on the test points (TPINL1, TPINH1, TPSD1, TPHO1, TPLO1, PWRGND1, bfg1, bfs1). All of them are connected in the netlist.
- `lib_symbol_mismatch` on Q4 BSS123. The pinout is correct: SOT-23 G1/S2/D3 per the Diodes DS30366 graphic.

### F11 — NIT: test points and annotation

- There is no test point on VDDB (bootstrap, `Net-(D10-K)`) or on +12V/VDDA. Given F1 and the history in flat.md, a VDDB-to-SW test pad would make UV diagnosis trivial.
- The DT annotation table leaves the 33k row empty. The formula gives 297 ns.

## Items checked and found OK

- **U1 pinout vs SLUSFF3A Table 4-1.** INA1=INL, INB2=INH, VCCI 3 and 8 = +3.3V, GND4=GND, DIS5=SD, DT6=R1 (20k to GND), NC 7/12/13 unconnected, VSSB9=SW, OUTB10=HO, VDDB11=bootstrap, VSSA14=BuckGND, OUTA15=LO, VDDA16=+12V. Package: SOIC-16 D (3.9 mm). UCC21330BQDRQ1 is Active/Production.
- **Channel assignment.** Channel A is the low side and channel B the bootstrapped high side. This is the reverse of TI Fig 8-1 but electrically fine, because both channels are identical.
- **Ground domains.** The primary side is on GND (MCU/battery side of shunt R26). Channel A is on BuckGND, so the isolated channel absorbs the shunt and ground-bounce difference. VDDA is supplied from a GND-referenced rail. The DC offset is about I·R26, only a few tens of µV, which is negligible. About 10–20 mA of gate-drive supply current returns through R26 and appears as a small current-sense offset.
- **Fail-safe at MCU reset.**
  - DIS has an internal pull-up (50/90/185 kΩ) and is disabled when floating. INA/INB have internal pull-downs of 90 kΩ typ (§5.x, Table 7-3).
  - The ESP32-S3 pins used are GPIO14 (INL), GPIO21 (INH) and GPIO47/SPICLK_P (SD). They have no internal pull at reset (datasheet v2.2 Table 2-1). GPIO14 has only a *low*-level 60 µs power-up glitch (Table 2-2). So both outputs stay low through reset.
  - On WROOM-1-N4, GPIO47 is in the 3.3 V domain.
  - Firmware drives SD high first (`buck.h`).
  - VCCI UVLO (falling 2.35–2.65 V) forces outputs low on a 3.3 V brown-out.
- **Logic levels.** The input VIH max is 2.3 V and VIL min 0.8 V. ESP32-S3 VOH ≥ 0.8·VDD = 2.64 V and VOL ≤ 0.33 V. OK.
- **Dead time.** R1 = 20k gives 185 ns typ (167–203). RDT is inside the 1.7–100 kΩ range, there is no capacitor on DT, and both-high inputs give both outputs low (interlock). It acts as a hardware minimum on top of the firmware dead time.
- **Q4/BflowSD default.** R23 10k to 3.3 V makes the backflow switch default to OFF when the MCU is in reset. BSS123 VGS(th) max is 2.0 V, fine at 3.3 V for a ≤ 1.3 mA sink. Vds stays ≤ Vbat + 13 V ≈ 71 V against the 100 V rating, consistent with the sheet note.
- **D8 reverse voltage.** At most about Vout + 13 − 9 ≈ 62 V, OK. R21 dissipation is 41 mW or less.
- **DZ2.** 12.4–14.1 V at 5 mA (MCC) is below TPH1R306PL VGS ±20 V.
- **CMTI** of at least 125 V/ns is far above this converter's SW dv/dt.

## Unverified / not done

- The actual +12V rail voltage on a built board (F1). Please measure it: this is the single most informative check.
- The SOD-123 vs SOD-123FL land-pattern comparison for D8/D10.
- The fault-case numbers for F4: L1 inductance and saturation, F1 I²t, and firmware detection latency. They are estimates only.
- PowerSupply-side AP3012 load capability at a raised output voltage. That is out of scope; I computed the gate-drive load as roughly 20 mA at 12 V.
- The ESP32-S3 GPIO40 (MTDO) power-up behaviour. It is covered by the external R23 pull-up in any case.
