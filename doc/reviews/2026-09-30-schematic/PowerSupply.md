# Fugu2 PowerSupply sheet — independent schematic review

Date: 2026-09-30. Scope: `PowerSupply.kicad_sch` (Q8/Q9/D18 source-follower pre-regulator, D7/D11/D12 diode-OR,
F2, D13, C13, J7 3.3 V module socket, J8 (excluded), U5 AP3012 boost to "+12V", DZ1). Interfaces read in
PowerStage, GateDrive, uC, and in `psu/buck100` (the J7 module). Project was not modified.
All scratch files are in `/tmp/fugu_split/review_PowerSupply/`.

Inputs: `/tmp/fugu_split/repo.net` (parsed with an s-expr parser, script `review_PowerSupply/nl.py`),
`/tmp/fugu_split/work/erc_after.rpt`, the rendered sheet PNG, `Fugu2.kicad_pcb` (read-only text parse of
pad nets), the `psu/buck100.kicad_sch` module (netlist and SVG exported from a scratch copy), and the docs.
Vision probe: `VISION-PROBE-PASS` in this session, so the renders were actually looked at.

Ratings used (from `README.md` § Specs): PV 12–80 V, battery 12–60 V (16s LiFePO4 at 58.4 V).
`doc/Power Supply.md` also says to expect PV voltage (80 V or more) on the battery terminal after a
charger/BMS fault.

## Datasheets read (source, revision, and where each value came from)

| Part | Source (highest rung needed) | Values used |
|---|---|---|
| GT800N10D3 (Q8) | local `~/dev/pv/pwr-mosfet-lib/datasheets/goford/GT800N10D3.pdf` (A2029.06-V1.1) | VDS 100 V, **VGS ±20 V**, Vth 1.0–2.5 V, RthJA 53 K/W (p1); SOA Fig 8 (p5); pinout 1-3 S, 4 G, 5-8 D (p1) |
| SP010N90NJ (Q8 alt) | local siliup PDF | VDS 100 V, VGS ±20 V, Vth 1.0–2.5 V |
| BZX84C62LT1G (D18) | onsemi BZX84C2V4LT1/D **Rev 23, Aug 2021**. Rungs 1–3 were blocked by Akamai; rung 4 (headless Chrome, plain UA) worked | **Pinout: 1 = Anode, 2 = NC, 3 = Cathode** (p2 table header); Vz 58/62/66 V @ 5 mA, 57.4–66 V @ 1 mA |
| AP3012 (U5) | diodes.com DS44577 Rev 2-2 (rung 1) | **VFB 1.17/1.25/1.33 V** (EC table), VOUT = 1.25·(1+R1/R2), fsw 1.1–1.9 MHz, switch current limit 500 mA, VIN 2.6–16 V, typical app 10 µH + 1 µF (p1) |
| UCC21330-Q1 (load of +12V) | TI SLUSFF3A (rung 1) | B-grade (8 V UVLO): **recommended VDD min 9.2 V**; UVLO rising 7.7/8.5/**8.9 V**, falling 7.2/7.9/8.4 V (§5.3, §5.5) |
| LM5163 (J7 module U2) | TI SNVSBB3A Apr 2024 (rung 1) | VIN abs max 100 V; **recommended VIN 6–100 V**; VREF 1.181/1.2/1.218 V |
| SMD1206B010TF/60 (F2) | YAGEO SMD1206 spec V.5, 2024-11-05, yageogroup.com (rung 1; the Farnell copy is an older revision without the /60 variant) | Ihold 0.10 A @23 °C (**0.07 A @60 °C**), Itrip 0.25 A, **Vmax 60 V**, Imax 100 A, Rmin 1.6 Ω, R1max 15 Ω. The manufacturer is YAGEO, not EATON as the symbol field says |
| SMAJ85A (D13) | Littelfuse SMAJ, revised 12/02/25. Rung 1 was Akamai-blocked; rung 4 worked | VR 85 V, VBR 94.4–104 V, **VC 137 V @ 2.9 A** |
| DSS310 Slkor (D7/D11/D12) | LCSC-hosted Slkor datasheet, Rev.1 2017 (found through rung 4 LCSC product page, PDF via rung 1) | 100 V, 3 A, **SOD-123FL**, IR 0.02 mA @25 °C / **2 mA @100 °C** at VR |
| BSS123-7-F (Q9) | Diodes DS30366 Rev 24-2 | 100 V, ±20 V, Vth 0.8–2.0 V |
| MSS1P4 (D17) | Vishay doc 89019 (rung 1, correct URL) | VRRM 40 V, 1 A |
| SM2T3V3A (DZ1) | ST DocID11738 Rev 3 (Aug 2015). Rung 4: direct navigation in headless Chrome saved the download | VRM 3.3 V, **IRM 500 µA max**, VBR min 3.6 V, VCL 6.5 V @ 25 A, STmite (DO-216AA) |
| MLZ2012M100WT000 (L2) | TDK product page (rung 4, headless) | **Rated current (L change) 150 mA (50 % down)**, 350 mA (ΔT 20 °C), DCR 470/611 mΩ |

Not fetched or read: HMK325C7475KN (C13), and the passives whose "MPN" field only holds a value (C28, C30,
C31, R37, R43, R44, R45). No finding depends on them.

## Findings (most severe first)

### F1 — CRITICAL, confirmed: the D18 62 V gate clamp is not connected on the board (symbol-to-footprint pin map is wrong)
- Schematic D18 is a 2-pin Zener with pin 1 = K and pin 2 = A. It uses footprint `Package_TO_SOT_SMD:SOT-23-3`. Netlist: `D18.1/K → Net-(D18-K)` (Q8 gate), `D18.2/A → GND`.
- BZX84C62LT1G pinout (onsemi Rev 23): **1 = Anode, 2 = NC, 3 = Cathode**.
- PCB (`Fugu2.kicad_pcb`): pad 1 = Net-(D18-K), pad 2 = GND, **pad 3 has no net**.
- As built, the anode sits on the gate, the NC pin sits on GND, and the cathode floats, so there is no clamp at all. R43 and R44 form a gate-to-source divider, so the source follower gives about V_PV − 2·V_GS(load). The aux rail then follows PV (about 75 V at 80 V PV) instead of being limited to about 56–63 V. Every PV transient up to Q8's 100 V passes onto Net-(D13-K), which reaches LM5163 VIN (100 V abs max), C13 (100 V), and F2 (60 V Vmax). The "power rail selection / suppresses voltage transients" function described on the sheet is missing.
- Fix: use a Zener symbol with pins K = 3 and A = 1 (or a SOD-123/SOD-323 Zener), then update the PCB and run DRC with `--schematic-parity`. Check every other 2-pin-symbol-on-SOT-23 part the same way.

### F2 — CRITICAL, confirmed arithmetic: the "+12V" gate-drive rail is actually 9.3 V, right at the UCC21330B UVLO and bootstrap limits
- U5 feedback: R37 (Rfb1) = 33 k, R38 = 5.1 k 1 %. VOUT = 1.25 × (1 + 33/5.1) = **9.34 V nominal**. With VFB 1.17–1.33 V and 1 % resistors the range is **8.59–10.11 V**.
- The sheet's own table says 33 k/4.3 k gives 10.8 V and 43 k/5.1 k gives 11.8 V. The fitted pair (33 k/5.1 k) is not in that table.
- Load: U1 UCC21330**B**QDRQ1 VDDA sits directly on +12V (VSSA = BuckGND, which is 0.5 mΩ from GND). VDDB is bootstrapped through D10 (SS310) and R19 (22 Ω) from +12V. Datasheet (SLUSFF3A): **recommended VDDx ≥ 9.2 V**, UVLO rising **max 8.9 V**, falling max 8.4 V.
  - VDDA nominal is 9.34 V, 0.14 V above the minimum. At the low tolerance corner (8.6 V) it is below the recommended minimum and below the worst-case UVLO rising threshold.
  - VDDB ≈ 9.34 − V_F(D10) − I·R19 − V_DS(LS). That is about 8.8 V nominal, which is below the 9.2 V recommended minimum and within the UVLO window. So the HS driver can refuse to turn on, or drop out on ripple.
- This matches the bench history in `HW Stories/flat.md`: "when connecting the gate discharge r 2.2, it fails (boot strap supply UV, failure)".
- Fix: R37 = 43 k (11.8 V nominal, 10.8–12.8 V worst case), then recheck L2 (F6). If the plan was really about 9–10 V, a 5 V-UVLO driver variant would be needed, but the net name and the notes say 12 V.

### F3 — MAJOR, confirmed topology (a fault case): Q8 has no gate–source clamp, so VGS can far exceed ±20 V
- R44 (200 k) is the only G–S element. When the source sits near 0 V while the drain is high, V_G = V_D·R44/(R43+R44) = V_D/2, which is 40 V at 80 V PV, capped only by D18 (about 62 V, and D18 does nothing today, see F1). GT800N10D3 is rated **VGS ±20 V**.
  - This happens when the aux rail is shorted: cracked C13 1210 MLCC, D13 failing short (the usual TVS failure mode), a J7 module fault, or reverse insertion of the module. After gate rupture Q8 usually fails D–S short, which puts full PV on the aux rail.
  - It also happens on a hard collapse of Solar+ (input short, F3 blowing). C31 (10 nF) holds the gate near 60 V while the body diode pulls the source down with Solar+. The decay constant is C31·(R43‖R44) ≈ 1 ms, so the event has to be faster than that. A normal PV disconnect with the converter drawing down 940 µF takes ms, so VGS lag stays around 12 V there, which is acceptable.
- Normal start-up is fine: the source follows the gate and the inrush is about 0.2 A for about 1.5 ms, well inside SOA Fig 8.
- Fix: add a 12–15 V Zener from G to S (cathode on gate). This is the standard source-follower clamp, as in the LibreSolar reference cited in the docs. Optionally add a small series resistor in the source.

### F4 — MAJOR, confirmed ratings: the aux rail has no clamp that protects its 100 V parts when fed from Bat+, and F2's 60 V rating is exceeded
- Bat+ → D12 → F2 → aux rail is unregulated. The project's own requirement (`doc/Power Supply.md`, `Protection Circuit.md`) is to survive PV voltage (80 V or more) on the battery terminal, plus inductive transients when a BMS opens during charge.
- The only clamp is D13 SMAJ85A: VBR min 94.4 V, **VC 137 V @ 2.9 A**. That is above LM5163 VIN abs max (100 V), C13 (100 V), DSS310 VRRM (100 V) and GT800N10D3 VDS (100 V). It cannot protect the rail it sits on.
- D13 is also ambiguous. The MPN field says `DNP`, but the dnp attribute is `no` and it is in the BOM/on the board.
- **F2 SMD1206B010TF/60: Vmax 60 V.** A tripped PTC has to hold off the full source voltage: up to about 63 V from Q8 once F1 is fixed (Vz up to 66 V minus VGS), about 75 V from Q8 today, and 58.4 V to 80 V (fault) from Bat+. Interrupting a fault above 60 V is outside the PTC rating.
- Fix options:
  - (a) Feed Bat+ into Q8's drain as well (diode-OR ahead of the source follower), so both sources are limited to ≤ 62 V. This gives up the "use LV for efficiency" path; Q9 can still turn Q8 off, but then the LV path would need its own limiter.
  - (b) Keep the topology, use a ≥ 80 V-rated PTC or fuse, and add a series resistor so that a TVS with VBR above 80 V actually clamps below 100 V at the limited current.

### F5 — MAJOR, plausible (the module is a separate project): the J7 module's pin order is reversed relative to J7, and the socket is unkeyed; as drawn, the module outputs 5.2 V
- Board J7 (`Conn_01x03_Socket`): 1 = aux HV (Net-(D13-K)), 2 = GND, 3 = +3.3V. Module `psu/buck100` J1: **1 = +3.3V, 2 = GND, 3 = VIN**. Whether they mate correctly depends on how the module is mounted. A 1×3 2.54 mm header is symmetric, so a 180° insertion is always possible, and that puts 56–80 V on the +3.3V rail (ESP32, INA226, UCC21330 VCCI, DZ1).
- Module feedback: Rfb1 = 33 k, Rfb2 = 10 k, and R3 (33 k, parallel to Rfb1) is marked **DNP**. VOUT = 1.2 × (1 + 33/10) = **5.16 V**. With R3 fitted it is 1.2 × (1 + 16.5/10) = 3.18 V. `psu/README.md` gives 390 k/220 k for 3.33 V. If a module is built as drawn, DZ1 (SM2T3V3A) conducts against the LM5163 current limit and the ESP32 (3.6 V abs max) is overdriven.
- Fix: key or polarize the connection (for example a 1×4 with one position blanked, or an asymmetric pitch/footprint), mark pin 1 on both silkscreens, and fix the module BOM for the 3.3 V variant. The sheet text "open-pe/buck80-XL7005A" is stale; README and plans say `psu/buck100` (LM5163).

### F6 — MAJOR, plausible: L2 (MLZ2012M100WT000) current rating is far below AP3012's 500 mA switch limit
- TDK: 150 mA rated current is where inductance is already 50 % down.
- At 9.3–11.8 V output, about 10–15 mA of gate-drive load and 1.5 MHz, the steady-state peak is about 0.14–0.25 A. Start-up into C28 plus the bootstrap/VDDA caps (about 10 µF) runs at the 500 mA cycle-by-cycle limit. L2 then collapses, the ripple and switch peak rise, and the output sags. That would aggravate F2.
- The AP3012 reference design uses a CDTH3D14-class 10 µH power inductor. Fix: use an Isat ≥ 0.6 A 10 µH part (for example a 3×3 mm shielded power inductor).

### F7 — MAJOR, plausible: F2 hold current is marginal for 4s (12 V) batteries in a warm enclosure
- Estimated 3.3 V load: ESP32-S3 about 120 mA average and 355 mA TX peak (per the docs/plan), AP3012 input about 50 mA, logic about 10 mA. That is about 0.6 W average and about 1.4 W peak, which is about 60 mA average and about 140 mA peak at 11.5 V after LM5163 (η ≈ 0.85).
- F2 Ihold is 100 mA at 23 °C but **70 mA at 60 °C**. Once tripped, R1max is 15 Ω.
- At 48 V batteries the current is about 4× lower, so there is no issue. Size the PTC for the 12 V corner (and see F4 for voltage), or use a fuse.

### F8 — MINOR/MAJOR, confirmed: USB (Vusb) cannot power the 3.3 V module within spec, and D7 leakage lets Vusb float up to the aux voltage
- Vusb 5 V − V_F(D7) ≈ 4.6 V into LM5163, whose **recommended VIN minimum is 6 V**. USB-only bring-up or flashing is therefore outside spec. README already has "usb-c: select 12V instead of 5V".
- Vusb has no load other than D7 and the P2 VBUS pins. DSS310 IR at VR is up to 20 µA at 25 °C and 2 mA at 100 °C. With no cable attached, the VBUS pins charge toward the 56–80 V aux rail. A sink should not present voltage on VBUS; only a small amount of energy is involved.
- Fix: a 100 k bleeder on Vusb, and PD/12 V negotiation (or a boost) if USB power is meant to work.

### F9 — MINOR, confirmed: schematic and PCB have diverged
- D17: schematic footprint `Diode_SMD:D_MicroSMP_AK` (MSS1P4), but the PCB still has `D_SOD-323` (the old 1N5819WS). ERC also reports "Footprint 'D_MicroSMP_AK' not found in library 'Diode_SMD'".
- L2: footprint `L_0805_2012Metric_Pad1.15x1.40mm_HandSolder` not found in `Inductor_SMD` (ERC).
- DZ1: library `PCM_Diode_SMD_AKL` / `PCM_Diode_TVS_AKL` is not configured (ERC).
- D7/D11/D12: the DSS310 is SOD-123FL, but the footprint is `D_SOD-123`. It usually fits; check against the land pattern.
- Q8 symbol is `HYG025N06LS1C2` (a 60 V part name) and does not match the library (lib_symbol_mismatch).
- Run Update PCB from Schematic and DRC with `--schematic-parity` after F1.

### F10 — NIT
- Stale or wrong annotations:
  - F2 Manufacturer field says "EATON"; it is YAGEO.
  - "F2: 375mA seems to small (for 47uF cap load)".
  - The "open-pe/buck80-XL7005A" label.
  - "maybe add inductor", "TODO add inductor, fuse PTC?", "TODO: use SMA DO214?".
  - The R37 value is not visible on the sheet (only "Rfb1").
- MPN fields that hold values instead of MPNs: C28, C30, C31, R37, R43, R44, R45.
- `+12V` net name misleads (see F2).
- `LV_PGOOD` reads like a status input, but it is an MCU output (GPIO35) that turns Q8 off.
- ERC attribution: the report's `/PowerSupply/` section is empty. This sheet's off-grid and footprint-link warnings are listed under the root `Sheet /` (the coordinates match this sheet), so filtering the report by sheet hides them. The two uC `pin_to_pin` warnings name this sheet's #FLG01 (GND) and #FLG03 (+3.3V) only because ESP32 GPIO46 is on GND and GPIO7 is on +3.3V. That belongs to the uC review.

## Checks that passed or have no finding
- **Power-state matrix**
  - PV only: Q8 supplies, about 56–63 V once F1 is fixed. The low end is about V_PV − 2·V_GS − V_F, so about 7 V at 12 V PV, which is above LM5163's 6 V minimum.
  - Battery only: D12. Both present: highest wins, and firmware LV_PGOOD → Q9 turns Q8 off. At reset GPIO35 floats and R45 pulls it down, so Q8 is on. That is fail-safe, and a brown-out loop self-recovers.
- **Q8 dissipation**, PV 80 V with Q8 supplying: (80 − 60) V × about 16–27 mA ≈ 0.3–0.55 W, ΔT ≈ 30 K at RthJA 53 K/W (vendor board). The inrush of about 0.2 A for 1.5 ms at up to 80 V is inside SOA Fig 8. Q9 BSS123 sees ≤ 62 V (≤ 40 V today); rated 100 V.
- **Reverse polarity**: Bat+ reversal is blocked by D12. PV reversal is clamped near −1.5 V by the power-stage body diodes, so Q8 sees a small VGS; the power-stage dissipation is out of scope.
- **Diode reverse voltages** (D7/D11/D12 ≤ 80 V vs 100 V), R43/R44 0805 at ≤ 80 V, and C31 100 V are all within rating.
- **AP3012 pinout** matches the datasheet (SW 1, GND 2, FB 3, SHDN 4 tied to VIN, VIN 5). C30 1 µF and a 10 µF output cap cover the datasheet's 1 µF/1 µF. MSS1P4 40 V is adequate for ≤ 12.8 V. OVP is 29 V.
- **Sequencing**: +12V follows 3.3 V (SHDN = VIN). U1 holds its outputs low until the VDDx UVLO releases. VCCI UVLO is 2.7 V.
- **DZ1**: 500 µA leakage at 3.3 V is fine. It only clamps ESD/surge (6.5 V @ 25 A), not a sustained overvoltage.
- **Q8 footprint**: gate is pad 2 at the pin-4 position and source pads are at pins 1–3, which matches the DFN3x3 pinout (partially checked from pad coordinates).

## Not verified
- DZ1 STmite polarity on the `D_Powermite_KA` footprint. DS4459 only says "band indicates cathode" and does not name which terminal is the tab. A reversed DZ1 would short +3.3V, so existing boards probably show it is right, but no datasheet confirms it.
- C13 HMK325C7475KN (4.7 µF 100 V X7S) DC-bias capacitance: datasheet not read.
- The load estimates in F6/F7 come from the doc figures (WROOM TX peak, gate charge), not from measurement.
- How the J7 module physically mates (F5): needs the module PCB and assembly orientation, or a photo.
- No simulation was run. PCB checks were limited to parsing pad nets and footprints; DRC/parity was not run because the PCB is open in KiCad.
