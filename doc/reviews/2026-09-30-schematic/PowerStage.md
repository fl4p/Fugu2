# Fugu2 PowerStage schematic review (independent, read-only)

- **Date:** 2026-09-30. Rev 2 (same day) adds the ST40100C, MSS1P4, HoLR2512D and Littelfuse 0997 datasheets. Changed or added items are marked **[rev 2]**: F4 (F3 part), F12, new F15 and F16, and the lists of categories with no finding and of open items.
- **Scope:** `PowerStage.kicad_sch`, covering J10, F3, the input bulk and HF caps, Q1/Q3 (HS in parallel), Q2 (LS), D9, D16, L1 (J3/J6), C10, Q5/Q6/Q7, F1, J9, R26, the snubbers, C14/R17 and H1–H6.
- **Inputs used:** `/tmp/fugu_split/repo.net` (Eeschema 10.0.5 export), `/tmp/fugu_split/work/erc_after.rpt`, and the rendered `/tmp/fugu_split/work/svg/Fugu2-PowerStage.png`. The rendered sheet was inspected visually after a vision probe passed in the same session. I also read the embedded `lib_symbols` in `PowerStage.kicad_sch`, the `open-pe` footprints (`~/Documents/KiCad/9.0/footprints/open-pe.pretty`), and footprint pad nets in `Fugu2.kicad_pcb`. The PCB was only read, never saved.
- **Ratings basis (README "Specs"):** PV input 12–80 V. Battery 12–60 V, meaning 4s–16s LFP, with 16s at 3.65 V/cell = 58.4 V. Maximum output 32 A, and 40 A for the 12/24 V coil build. Boost mode is supported with the terminals swapped.

## Datasheets actually read

| part | source | what was used |
|---|---|---|
| IPA050N10NM5S (Q1, Q3) | `~/dev/pv/pwr-mosfet-lib/datasheets/infineon/IPA050N10NM5S.pdf`, Rev 2.1 2019-08-28 | p.1: PG-TO220 FullPAK, VDS 100 V. p.3 Tab.2/4: VGS ±20 V, RG 1.2 Ω typ, RthJC 3.9 K/W. p.4 Tab.5: Crss 25 pF. p.9: outline |
| IPP022N12NM6 (Q2) | `…/infineon/IPP022N12NM6.pdf` | VDS 120 V, VGS ±20 V, VGS(th) 2.6/3.1/3.6 V, RG 0.55–1.65 Ω, Ciss 8100 pF, Crss 40 pF typ / 70 pF max @60 V, Qrr 412 nC @1000 A/µs |
| TPH1R306PL (Q5/Q6/Q7) | `…/toshiba/TPH1R306PL.pdf`, Rev 4.0 2019-10-18 | p.2 §4: **VDSS 60 V**, VGSS ±20 V, EAS 455 mJ, IAS 50 A. p.3 §6.1: V(BR)DSX 45 V at VGS = −20 V |
| ST15100S (D16) | `~/dev/pv/ee/datasheets/smc/ST15100S N2219 REV.-.pdf` | p.1: **VRRM 100 V**, IF(AV) 15 A, IR 50 mA max @125 °C at rated VR, CT 650 pF @5 V. p.2: RθJA 70 K/W |
| ST15100C (family proxy for D9) | `…/smc/ST15100C … N1043 REV.B.pdf`, p.1 | TO-220AB: pin 2 and tab = common cathode, pins 1 and 3 = anodes |
| Würth 691256610002 (J9, J10) | `https://www.we-online.com/components/products/datasheet/691256610002.pdf` (rung 1, plain curl, returned real `%PDF`, 340 kB) | Rated current 40 A (UL) / 57 A (VDE). M4 screw. Pin 1.2 mm. **Recommended hole Ø1.6 mm** |
| KEMET C0805C222K2GEC7800 (C8) | Serper search: Mouser/Farnell listings (no PDF) | 200 V, 2.2 nF, **C0G** ("ESD C0G Dielectric") |
| **[rev 2]** SMC/Sangdest ST40100C (D9) | `https://www.smc-diodes.com/propdf/ST40100C%20N0264%20REV.C.pdf`, Data Sheet N0264 Rev C. Saved as `review_PowerStage/st40100c_vendor.pdf` (5 pp, `%PDF-1.4`, 128 kB) | p.1 circuit diagram: **pin 2 and base = common cathode, pins 1 and 3 = anodes**. VRWM 100 V, IF(AV) 20 A/leg. IR 75 mA max/leg @100 V, 125 °C. CT 845 pF/leg @5 V |
| **[rev 2]** Vishay MSS1P3/MSS1P4 (D1) | `https://www.vishay.com/docs/89019/mss1p4.pdf`, Doc 89019 Rev 03-Aug-2020 (rung 1, `%PDF`, 110 kB) | VRRM 40 V, IF(AV) 1 A, IFSM 25 A. VF 0.48/0.55 V @1 A. CJ 50 pF @4 V. Cathode = large pad (bottom view, p.1) |
| **[rev 2]** Milliohm HoLR2512D (R26, LR2512D-3W-0.5mR-1%) | LCSC C500733 page (title confirms "LR2512D-3W-0.5mR-1% … Milliohm") links to datasheet host `https://datasheet.lcsc.com/datasheet/pdf/65211303ba2dc92cf695315d06c498c7.pdf?productCode=C500733`. Spec HoLR2512D Ho-A1, 2020-07-15, 6 pp, `%PDF-1.5` (rung 1) | p.2: 2 W/3 W/3.5 W, **TCR ≤ 25–50 ppm/°C**, −55…+170 °C, full power to 70 °C then linear to 0 at 170 °C. p.3: recommended land for 0.25–0.5 mΩ is a = 4.0, b = 2.57, gap L = 2.11 mm, with the sense trace taken at the inner pad edge |
| **[rev 2]** Littelfuse MINI 58V, 0997xxx.WXN (F3) | `https://www.littelfuse.com/assetdocs/littelfuse-datasheet-997-mini58v?assetguid=f4bf5724-5a40-4a44-8f08-c52ae959a5ef` (rung 2, Chrome UA + Sec-Fetch headers, `%PDF-1.7`, 621 kB, revised 11/18/2025) | p.1: **58 V DC, interrupting 1000 A @58 V DC**, series 2–30 A. p.2: 0997025 cold R 2.36 mΩ, **I²t 625 A²s typ**. p.3: TCC. **Derating for the 25 A part: 21 A @20 °C, 20 A @40 °C, 18 A @60 °C, 17 A @80 °C** |

The project docs I relied on were `doc/HV Fuse.md`, `Fuse.md`, `Backflow Switch.md`, `Capacitors.md`, `LS Rect Diode.md`, `EMI Parasitics Snubbers.md`, `No-Coil SW Ring (Bench vs SPICE).md`, `spice/PARASITIC_MODELING.md` and `README.md`.

### Access ladder record (rev 2, 2026-09-30)

| source | highest rung | result |
|---|---|---|
| ST40100C | **Rung 4** (headless system Chrome, `channel="chrome"`, plain Chrome 125 UA, 35 s wait, then a context request) | **Vendor PDF obtained.** Rungs 1 and 2 (curl, then curl with Sec-Fetch/sec-ch-ua) returned HTTP 403 with a 759–1917-byte JS cookie challenge ("Browser security check in progress…", `_wtsjsk` cookie). The first N0870 URL I tried was a guess and does not exist (404 at rung 4). At rung 3 a third-party mirror (`micro-semiconductor.de/datasheet/8e-ST40100C.pdf`, SMC N0264 Rev C, 2017 WPS re-export) gave the same pinout. The bundled Playwright headless shell was a version mismatch (my tooling), so I routed around it with system Chrome. |
| MSS1P4-M3/89A | Rung 1 | Vendor PDF obtained |
| LR2512D-3W-0.5mR-1% | Rung 1 | LCSC product page, then the LCSC datasheet host; manufacturer spec obtained |
| Littelfuse 0997 MINI 58V | **Rung 2** | Rung 1 returned HTTP 403 (433 B Akamai page). Rung 2 (Sec-Fetch headers) returned the real PDF |

These datasheets are still not read:

- GRM32EC72A106KE05L, HMK212BC7105KG and HMK107C7224KA. They were not requested for this round; I relied on `Capacitors.md`, which records vendor DC-bias reads.
- The electrolytics. The schematic has no MPN for them.

---

## Findings (most severe first)

### F1 — MAJOR, confirmed (ERC): Q5 and Q7 symbol has stacked hidden S pins numbered 2 and 3, so the netlist puts G and D on the source net

- **Refdes:** Q5, Q7. The symbol is `open-pe:HYG025N06LS1C2` and its embedded copy `HYG025N06LS1C2_2`.
- **Evidence:** the pins are S=1, G=2, **S=2 (hidden)**, D=3, **S=3 (hidden)**. Q6 uses the 3-pin `_1` variant and is fine.
- **Netlist:** `Q5.2` appears in both **BflowG** and **BflowS**, and `Q5.3` appears in both **Bat+** and **BflowS**. Q7 has the same problem, and additionally its hidden S pin 2 is unconnected (`unconnected-(Q7-S-Pad2)`).
- **ERC:** `/PowerStage/` has 5 `duplicate_pins` errors and 1 `pin_not_connected` error.
- **Footprint:** `Infineon_PG-TDSON-8_FL` numbers its pads 1 = S, 2 = G, 3 = D (all drain pads).
- **Current PCB state:** the board happens to hold pad 2 = BflowG and pad 3 = Bat+ for Q5, Q6 and Q7. That is correct today, but it is only KiCad's pick between two conflicting net assignments.
- **Risk:** the next "Update PCB from Schematic", or any netlist consumer (SPICE, BOM or parity tools), may resolve pad 2 to BflowS or pad 3 to BflowS. That would short gate-source or drain-source on two of the three backflow FETs, defeating the backflow and over-voltage protection.
- **Fix:** give Q5 and Q7 the same 3-pin symbol as Q6, or fix the library symbol so it has only pins 1/2/3 (or 1–8 with a matching footprint).

### F2 — MAJOR, plausible (arithmetic confirmed; part unspecified): input bulk electrolytics are far over their ripple rating

- **Refdes and net:** C11 and C12 on Solar+/BuckGND. They are the only electrolytics on Solar+ (checked in the netlist).
- **Load current:** `Capacitors.md` gives I_cin,rms = Io·√(D(1−D)) ≈ 14.3–15 A at 72→27 V, 32 A, and says the electrolytics carry more than 90 % of it.
- **Per-cap current:** that is **about 7 A rms per can**.
- **Available ratings:** every 470 µF / 100 V, 16–18 mm candidate in the project's own selection table (`Capacitors.md` §Selection) is rated **1.85–3.7 A @100 kHz, 105 °C**. The frequency and temperature multipliers were not verified (no electrolytic datasheet read). Even so, reaching 7 A would need a multiplier of about 2–3.8×.
- **Loss:** the documented total loss is 3.4 W, about 1.7 W per can, which means significant self-heating and shorter life.
- **Missing data:** C11 and C12 carry `MPN=DNP`, so the chosen series and rating are not recorded anywhere in the design.
- **Related PCB observation:** the PCB contains a **second "C12" footprint with no sheet path and no nets** at (28.9, 91.5). It looks like an orphaned third bulk-cap slot (`HV Fuse.md` mentions "3×470 µF input caps"), and as placed it would contribute nothing.
- **Fix:** record the MPN and connect a third (or fourth) can, or move to higher-ripple parts. Then check against the datasheet multipliers.

### F3 — MAJOR, confirmed (datasheet vs spec vs project doc): backflow FETs are rated 60 V against a battery up to 58.4–60 V

- **Refdes and nets:** Q5, Q6, Q7 (TPH1R306PL). D = Bat+, S = BflowS.
- **Rating:** TPH1R306PL VDSS = 60 V (datasheet p.2).
- **Stress:** with the battery connected and the converter side at 0 V (off, or the LS clamped on in the HS-short scenario from `Backflow Switch.md`), VDS equals Vbat. That is up to 58.4 V for 16s LFP (97 % of VDSS), and the README specifies a battery up to 60 V (100 %).
- **Transients:** turning off battery→converter current in boost mode opens against the cable inductance, and nothing on Bat+/BT+ clamps it (no local cap or TVS on this sheet). This leaves the FETs in avalanche (EAS 455 mJ per device).
- **Project's own requirement:** `doc/Backflow Switch.md` says "with 60V battery voltage, a 80V switch is sufficient", which also contradicts the fitted part.
- **Fix:** use 80 V parts for 16s builds, or de-rate the spec to ≤ 15s / 48 V nominal. Consider a local cap or TVS on Bat+.

### F4 — MAJOR, plausible (MPN missing): F1 (40 A, ATO) has no voltage-rated part recorded

- **Refdes and nets:** F1 between Bat+ and BT+. The footprint is `Fuse_Blade_ATO_directSolderThin` and `MPN=DNP`.
- **Why a standard fuse fails:** standard ATO fuses are 32 V DC, and `HV Fuse.md` itself says "Standard ATO/ATOF/MINI (32 V DC) are **not usable**". The battery side reaches 60 V.
- **Rating needed:** a 58 V part (ESKA 340.0xx-58V goes up to 40 A per `HV Fuse.md`) only covers ≤ 58 V, so a full 60 V spec needs an 80 V part.
- **Breaking capacity:** these blade fuses break 1 kA. A large 16s LFP pack can source well above that into a board short (LS plus backflow short, or output short). The board fuse therefore cannot be the primary battery protection. Document that a Class-T/MEGA fuse or BMS is required at the battery.
- **Current margin:** 40 A fuse at 32–40 A continuous is 80–100 % of rating in a warm enclosure. Blade fuses need derating for that.
- **F3 (related, minor):** the value text says 25 A 58 V, but `MPN=DNP` loses the chosen Littelfuse 0997025.WXN, and a 32 V MINI would fit the same footprint. The 58 V rating is below the 80 V PV Voc. That is acceptable only while PV Isc < 25 A, because the fuse then never has to open against the PV. Record this assumption.
  - **[rev 2] Now confirmed from the Littelfuse datasheet (p.1):** 58 V DC, 1000 A @58 V DC. The datasheet's rejection feature only stops a 58 V fuse being replaced by a lower-voltage one *in a MINI 58V holder*. The direct-solder footprint gives no such protection.
  - **[rev 2]** F3's current derating is a separate new finding: see F15.

### F5 — MAJOR, plausible (design decision not recorded): no reverse-polarity protection on either terminal

- **PV reversed at J10:** Solar+ goes to about −Voc relative to BuckGND. The LS body diode (BuckGND→SW) and the HS body diodes (SW→Solar+) then short the array at Isc (~12 A). That dissipates roughly 10 W in Q2 and in Q1/Q3 combined, for as long as the array is connected. F3 does not open because Isc < 25 A. C11 and C12 are reverse-biased by about 2 body-diode drops (~1.5 V).
- **Battery reversed at J9:** current flows GND → R26 → Q2 body diode → L1 → Q5/6/7 body diodes → F1. This is a battery dead-short cleared only by F1 (see F4), with reversed voltage on everything powered from BT+/Bat+ until F1 clears.
- **Fix:** either add protection, or record explicitly that it is the installer's responsibility.

### F6 — MAJOR, plausible (arithmetic; resistor part unspecified): snubber resistor R11 is overloaded

- **Refdes and nets:** R11 = 7.5 Ω, 1206 footprint, with the MPN field just "7.5". C8 = 2.2 nF, between SW and BuckGND.
- **Dissipation:** P = C·V²·f = 2.2 nF · 72² · 39 kHz = **0.44 W**, and **0.55 W at 80 V**. Ringing energy adds to this.
- **Rating:** a generic 1206 is 0.25 W (some are 0.5 W). `EMI Parasitics Snubbers.md` itself says "Resistor should handle 2W".
- **Fix:** specify a pulse- and power-rated part (e.g. a 2010/2512 or 1206 anti-surge ≥ 1 W), or split it into parallel resistors.
- **Minor, tuning:** the documented tank is Z0 ≈ 3.4 Ω (9.2 nH / 800 pF, from `No-Coil SW Ring…md`). R11 at 7.5 Ω is about 2.2× Z0, so it under-damps. Optimal R is about Z0 (3.3–3.9 Ω). C8 at 2.75× Cpar is reasonable.
- **Nit:** C8's value text says "X7S", but C0805C222K2GEC7800 is **C0G** (distributor listings). C0G is the better part; fix the text.

### F7 — MINOR, plausible: D16 (ST15100S, 100 V) on SW has little voltage margin at 80 V input, and its fitted status is ambiguous

- **Ambiguous status:** D16 has dnp = no and in_bom = yes, but `MPN=DNP`. It is placed on the PCB (SW/BuckGND pads). It is drawn at the far bottom-right of the sheet, away from the bridge, and nothing says whether it is intended.
- **Voltage margin:** the bench measured SW overshoot at 1.23× (74 V at 60 V in), and the sim gives +11 V at 70 V. At the 80 V spec that extrapolates to about **91–98 V** reverse voltage against VRRM 100 V.
- **Leakage and heating:** IR is up to 50 mA @125 °C at rated VR, and RθJA is 70 K/W, so there is a thermal-runaway risk.
- **Switching loss:** CT 650 pF also adds switch-node capacitance, which increases HS turn-on loss.
- **Fix:** decide fitted or not and set the DNP flag and MPN accordingly. If it is fitted, use a 150 V part for 80 V PV builds.

### F8 — MINOR, plausible: LS gate has no fast turn-off path

- **Circuit:** Q2 is driven through R10 = 4.7 Ω in both directions. The HS got a diode turn-off path (D1 with R5/R7); the LS did not.
- **Rough estimate:** Crss is 40 pF typ / 70 pF max @60 V, and larger at low VDS. During HS turn-on at about 4 V/ns, the Miller current is about 0.16–0.3 A. Through 4.7 Ω + RG 1.1 Ω + driver sink, that produces about 1–2 V on the gate.
- **Threshold:** VGS(th) minimum is 2.6 V at 25 °C and drops when hot.
- **Result:** this is not proven to be a problem, but the margin is thin.
- **Fix:** verify with a scope probe on LS_GATE during HS turn-on, or add a turn-off diode or smaller turn-off resistor, mirroring the HS.

### F9 — MINOR, plausible (datasheet vs footprint): J9/J10 footprint drill is smaller than Würth's recommended hole

- **Refdes:** J9, J10 (691256610002).
- **Datasheet:** recommended hole **Ø1.6 mm** for a 1.2 mm pin (p.1).
- **Footprint:** `TerminalBlock_WR-TBL_2566_1x02_P10.16mm` uses **drill 1.3 mm** with a 2.5 mm pad. After plating, the finished hole may be too tight for the pin.
- **Caveat:** if previous boards assembled fine, this is only a nit.
- **Current rating:** 40 A UL is adequate for 32 A. For the 40 A (12/24 V) build it is at 100 % of UL.

### F10 — MINOR, plausible: J9 and J10 have opposite pin-1 polarity

- **Pins:** J10 pin 1 = BuckGND (PV−) and pin 2 = T_HV+. J9 pin 1 = BT+ and pin 2 = GND.
- **Risk:** these are identical connectors with opposite pin-1 meaning, which becomes a miswiring risk if the silkscreen and orientation are not unambiguous. This matters especially in boost mode, where the user swaps the roles of the terminals.
- **Action:** verify the silkscreen.

### F11 — MINOR, plausible: only electrolytic output capacitance

- **Circuit:** the LV side has only C10 (470 µF, `MPN=DNP`) on BflowS. There is no MLCC on BflowS or Bat+.
- **Ripple:** ΔI_L ≈ 8.6 A pp (`Capacitors.md`) gives about 2.5 A rms. That is at or above the rating of the listed 470 µF cans, and the battery cable shares only part of it.
- **Boost mode:** the LV side becomes the input side.
- **Fix:** add 1–2 × 1 µF/100 V X7S at the output for HF, and record C10's MPN and ripple rating.

### F12 — NIT, confirmed: D9 embedded symbol has A/K pin names swapped

- **Evidence:** the embedded `Device:D_Dual_CommonCathode_AKA_Parallel` has pin 1 = "K", 2 = "A", 3 = "K". The KiCad 10 library has 1 = A, 2 = K, 3 = A. The graphic is still common-cathode on pin 2.
- **Connection is correct:** pin 2 goes to SW and pins 1/3 go to BuckGND. This matches the SMC TO-220AB "C" pinout (ST15100C p.1: pin 2 and tab = common cathode).
  - **[rev 2] Now confirmed on the ST40100C datasheet itself** (N0264 Rev C, p.1 circuit diagram): "Base common Cathode" is pin 2, and pins 1 and 3 are anodes.
- **[rev 2] Voltage margin if D9 is ever fitted:** it has the same 100 V VRWM margin concern as D16 (F7). IR is 75 mA max per leg @100 V, 125 °C, which is higher than D16's.
- **Problem:** only the pin names and netlist pinfunction are wrong. Refresh the symbol from the library.
- **Mechanical note:** D9's tab is the cathode, which is SW, so it needs an insulator on the heatsink. It is currently DNP.

### F13 — NIT: DNP and MPN field hygiene

- **Sentinel conflict:** `MPN=DNP` is used on fitted, in-BOM parts: Q1, Q2, Q3, C10, C11, C12, F1, F3, J9, J10 and D16. It apparently means "hand-assembled, not fab-sourced", but it conflicts with the KiCad `dnp` flag and leaves the load-bearing ratings unrecorded (F2, F4, F11). Use a separate field (e.g. `Assembly=hand`) and put the real MPNs in.
- **Values in the MPN field:** R4–R10 carry "4.7, 1%" / "10k" in `MPN`, which are values, not part numbers.
- **C5 package mismatch:** C5 (DNP) has a 1206 footprint while its Digikey field is an 0805 part (C0805C222K2GEC7800).
- **Q10:** a crossed-out alternate LS with on_board = no. It still carries a local `LS_GATE` label plus SW/BuckGND labels, which is clutter.
- **H6:** on_board = no.

### F14 — NIT: readability and label hygiene

- The hot-loop MLCCs (C16, C9, C27, C18, C17) and the snubber are drawn in separate blocks joined only by `Solar+`/`BuckGND`/`SW` labels, far from Q1/Q3/Q2. The critical commutation loop cannot be read off the schematic.
- `Bat+` (FET drain, pre-fuse) versus `BT+` (terminal) are easy to confuse.
- The R26 Kelvin sense is expressed only as the hierarchical labels Vin+ and Vin− sitting on BuckGND and GND. ERC reports this as `multiple_net_names` ×2. Nothing in the schematic enforces a Kelvin tap, so a net-tie or 4-terminal shunt symbol would make it explicit. I did not check the PCB Kelvin routing.
- Polarity is worth confirming with the Sensors sheet: charging current flows GND→BuckGND through R26, so Vin+ (BuckGND) reads negative while charging.

### F15 — [rev 2, NEW] MINOR, confirmed (datasheet vs documented current): F3 at 25 A is over its derated capacity in boost mode

- **Datasheet:** the Littelfuse MINI 58V derating table (p.3) allows the 0997025 **20 A at 40 °C, 18 A at 60 °C and 17 A at 80 °C** ambient. That is with the ISO 8820-3 fixture and 2.5 mm² cable. Soldered to a PCB next to the heatsink it is probably worse, but I have not verified that.
- **Documented current:** `HV Fuse.md` says boost at ~900 W draws about 15 A @60 V and **about 25 A @36 V** through F3, with the battery on the HV terminal.
- **Result:** any boost operation with an HV-side battery below about 45 V at full power exceeds the derated rating inside a warm enclosure. That means nuisance opening or fuse aging. Buck mode (about 12 A from PV) is fine.
- **Fix:** use a 30 A part (0997030, 1.85 mΩ, 1100 A²s; 22 A @60 °C), or limit boost current in firmware below about 45 V.

### F16 — [rev 2, NEW] MINOR, confirmed (datasheet vs footprint): R26 land pattern differs from the shunt maker's recommended land

- **Datasheet:** HoLR2512D p.3 recommends, for 0.25–0.5 mΩ, pads a = 4.0 mm wide, b = 2.57 mm long, with gap L = 2.11 mm. The drawing takes the Kelvin sense traces from the **inner pad edges**.
- **Footprint:** `open-pe:R_2512_6332Metric_Pad2.72x3.40mm_HandSolder` has pads 2.72 × 3.40 mm at ±2.14 mm, which gives a **gap of 1.56 mm** and pads 0.6 mm narrower.
- **Why it matters:** at 0.5 mΩ, the solder and copper within the terminations are a noticeable fraction of R. A different land and tap point shifts the effective resistance, and if the taps are not at the inner edges it adds copper TCR (~3900 ppm/K) on top of the alloy's ≤ 25–50 ppm/K.
- **What is unaffected:** power is fine, at 0.54 W @33 A and 0.80 W @40 A against a 3 W rating (full power to 70 °C; 2.1 W still available at 100 °C).
- **Fix:** match the recommended land and tap the sense traces at the inner edges, or calibrate the gain in firmware and accept the extra TCR. PCB Kelvin routing is still unverified.

## Categories checked with no finding

- **[rev 2] D1 (MSS1P4) gate-discharge diode.** VRRM 40 V covers the ≤ ~15 V reverse bias between HO and gate. IFSM is 25 A, and the peak discharge current of both gates is about 4–5 A for tens of ns. The PCB pad mapping is correct: pad 1 (2 × 1.1 mm, the large pad) is on HO, which is the cathode, and the datasheet p.1 bottom view shows the large pad as cathode. Pad 2 (0.8 × 0.8 mm) is on Net-(D1-A).
- **[rev 2] F3 I²t versus input-cap inrush.** This is the case of plugging a battery onto the HV terminal in boost mode.
  - The inputs: C ≈ 940 µF bulk, V = 58.4 V, and minimum loop R ≈ 19 mΩ. That R is 2 × 33 mΩ ESR in parallel plus 2.36 mΩ fuse, and ignores cable and battery resistance.
  - The inrush I²t is C·V²/(2R) ≈ **84 A²s**, or 13 % of the 0997025's typical 625 A²s.
  - A single connect event will not blow or noticeably fatigue the fuse. The 625 A²s figure is "typical" and derived from breaking tests (datasheet p.2 note), so this is an estimate.
- **[rev 2] R26 power and TCR.** Power is covered in F16. TCR is ≤ 25–50 ppm/°C (datasheet p.2).

- **HS VDS.** Q1/Q3 are 100 V against 80 V PV, a 20 % margin that the README acknowledges.
- **LS VDS.** Q2 is 120 V, against about 98 V peak extrapolated.
- **Gate VGS limits.** All FETs are ±20 V.
- **HS paralleling.** Q1 and Q3 each have their own charge resistor (R4, R6) and discharge resistor (R7, R5). The shared D1 ties the gates through R5+R7 = 4.4 Ω, which is acceptable. R9 (10 k) holds both gates off through that link. R8 holds the LS gate off.
- **Backflow orientation.** The body diode conducts converter→battery and blocks battery→converter, as intended. Gate drive is from HO via GateDrive (not reviewed here), with DZ2 clamping BflowG to BflowS. That keeps VGS from going strongly negative, so the V(BR)DSX = 45 V mode is avoided.
- **MLCC DC bias.** Already documented in `Capacitors.md` using vendor curves.
- **Shunt dissipation.** R26 at 0.5 mΩ, 40 A is 0.8 W against the 3 W part named in the MPN string. [rev 2] Now confirmed against the HoLR2512D datasheet (3 W to 70 °C). The land pattern issue is F16.
- **Q1/Q3 package.** Q1 and Q3 are FullPAK (isolated) on a TO-220 horizontal footprint. The outline (p.9) has the same 2.54 mm lead pitch. The screw-hole offset is about 12.6 mm from the body bottom, which is close to TO-220.

## Unverified / left open

- The electrolytic ripple ratings and multipliers. There is no MPN in the schematic.
- [rev 2] Resolved: the ST40100C, MSS1P4, LR2512D (HoLR2512D) and 0997 MINI58V datasheets are now read (see the access ladder record).
- PCB Kelvin routing of Vin+ and Vin−.
- Whether previously built boards used a 1.3 mm drill for J9/J10 without problems.
- D16's intended population.
