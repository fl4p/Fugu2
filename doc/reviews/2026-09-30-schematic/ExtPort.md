# ExtPort schematic review: J5 VE.Direct-pinout comms port

Reviewer: independent schematic review (Claude), 2026-09-30. The project was only read, never modified.
Scope: `ExtPort.kicad_sch`, reviewed against `plans/ext-comms-port.md`, with the interfaces followed into uC (U2) and the +3.3V rail.

## Inputs and evidence

- Vision gate: `VISION-PROBE-PASS` in this session. The rendered sheet `/tmp/fugu_split/work/svg/Fugu2-ExtPort.png` was reviewed visually.
- Netlist: `/tmp/fugu_split/repo.net` (Eeschema 10.0.5, 83 nets), parsed with an s-expression parser (`review_ExtPort/nets.py`). `work/ExtPort.kicad_sch` is byte-identical to the repo file.
- ERC: `/tmp/fugu_split/work/erc_after.rpt` (errors, warnings and exclusions). The `/ExtPort/` section is empty. The project sets only `footprint_filter`, `four_way_junction`, `simulation_model_issue` and `single_global_label` to ignore. None of the 420 messages in the report names an ExtPort symbol or an EXT_* label.
- Datasheets, all read from the downloaded PDF (`%PDF` magic checked) and kept in `/tmp/fugu_split/review_ExtPort/`:
  - SN74LVC1G125, TI SCES223U (rev. Aug 2026): §5.1 Abs Max p4, §5.3 ROC p5, Ioff (EC table), §7.3.2.
  - SN74LVC1G17, TI SCES351Y (rev. Oct 2025): §5.1 Abs Max, §5.3 ROC, Table 5-1 VT+/VT−, Ioff.
  - LESD5D5.0CT1G, LRC Rev.A May 2025: §4 Max Ratings p1, §6 Electrical Characteristics p2.
  - VE.Direct Protocol 3.34 (victronenergy.com): "Physical interface" p2–3, connector table, revision history (3.22 "Swapped RX & TX in the pinout").
  - VE.Direct Protocol FAQ (victronenergy.com/live/vedirect_protocol:faq): Q4 3.3/5 V levels, Q5 power-pin current, isolation of the USB/RS232 interfaces.
  - ESP32-S3 Series Datasheet v2.2: Table 2-1 pin power domain and reset state, note 4 (GPIO47/48 at 1.8 V on R8V/R16V).
  - SM2T3V3A (DZ1 on +3.3V), ST DocID11738 Rev 3, Table 4. **Access path:** st.com was blocked through rung 5, a headed scratch Chrome over CDP after warming on the ST product page (`ERR_HTTP2_PROTOCOL_ERROR` on the PDF). The document was then fetched from an alternate document host, the chipdip.ru mirror `static.chipdip.ru/lib/448/DOC029448958.pdf`: a real PDF, ST DocID11738 Rev 3, Aug 2015.

## Connectivity as captured (netlist)

| J5 pin | Net | Path |
|---|---|---|
| 1 GND | GND | Direct to logic GND. D20/D21, U7/U8 and C33/C35 return here. |
| 2 RX | Net-(D21-A2) | D21 (to GND) at the connector → R49 220 Ω → U8.2 (A), with R50 47 k to +3.3V on the IC side → U8.4 → EXT_RX → U2.30 (GPIO37) |
| 3 TX | Net-(D20-A2) | D20 (to GND) at the connector ← R48 220 Ω ← U7.4 (Y). U7.2 (A) = EXT_TX = U2.29 (GPIO36), R47 100 k pull-up. U7.1 (/OE) = EXT_TX_OE_N = U2.25 (GPIO48), R46 10 k pull-up. |
| 4 V+ | +3.3V | Direct to the rail. C33 1 µF to GND. No series part and no TVS. |

- The U7 pinout (1 /OE, 2 A, 3 GND, 4 Y, 5 VCC) and the U8 pinout (1 NC, 2 A, 3 GND, 4 Y, 5 VCC) match DBV SOT-23-5. U8.1 is marked NC.
- The U2 pin functions (GPIO36, GPIO37, GPIO48) match the plan.
- The pinout matches the VE.Direct *Producer* pinout (Protocol 3.34: 1 GND, 2 VE.Direct-RX, 3 VE.Direct-TX, 4 Power+). Fugu is a producer like an MPPT, so pin 2 is an input and pin 3 an output. **Confirmed.**
- The TVS diodes sit on the connector side of the series resistors, and R50 is on the IC side of R49. This placement is correct: the pull-up does not add to fault current and the resistor is downstream of the clamp.
- Default states are correct:
  - ESP32-S3 datasheet v2.2 Table 2-1 gives GPIO36, GPIO37 and GPIO48 as "IE" only at reset, with no internal pull. R46 therefore holds /OE high and TX is Hi-Z through reset.
  - R47 holds U7.A high.
  - R50 idles RX high with nothing plugged in.

## Power-state matrix

In-scope peers (GX, VE.Direct-USB, the planned adapters) are all *consumers* powered from J5.4. When Fugu is unpowered they are unpowered too, so Fugu-off/peer-on can only happen with an out-of-scope, independently powered peer.

| Case | Path | Bound | Verdict |
|---|---|---|---|
| Fugu off; external 5 V source drives pin 2 | R49 → U8.A (Ioff ±10 µA at 5.5 V) and R49 + R50 → unpowered rail | 5 V / 47.2 k ≈ 0.1 mA into the rail | OK (confirmed) |
| Fugu off; peer pull-up on pin 3 | U7.Y in the power-off state (Ioff ±10 µA; VO abs max 6.5 V) | µA | OK |
| Fugu on, U7 enabled low, 5 V peer on pin 3 | R48 | 5/220 = 22.7 mA < ±50 mA IO abs max | OK. R48 dissipates 114 mW (see F4). |
| Fugu on, U7 enabled high, 5 V peer on pin 3 | R48 → U7 PMOS → +3.3V | ≈ 7 mA; Y stays ≈ VCC + small drop < VCC + 0.5 | OK (estimate: PMOS on-resistance not taken from the datasheet) |
| Pin 4 driven by a peer (e.g. a producer-to-producer miswire with a 5 V Victron MPPT) | Straight into +3.3V (ESP32, U1 VCCI, U3, U5, WS2812) | Only DZ1 SM2T3V3A: VBR **min** 3.6 V at 1 mA, VCL 6.5 V at 25 A; no VBR max given | Rail overvoltage is not bounded below the 3.6 V ESP32 limit. Accepted by Fab (Q15) and open as qualification item 3. See F3. |
| Pin 4 shorted | +3.3V rail (LM5163, 0.5 A) | Rail brownout | Accepted (Q15). See F5 for the scope of the brownout. |

## Findings (most severe first)

### F1 — major, confirmed (math from datasheets): the TVS cannot hold an Ioff pin below its 6.5 V absolute maximum

Refdes and nets: D20 on Net-(D20-A2), U7.4; D21 on Net-(D21-A2), U8.2.

- LESD5D5.0CT1G: VBR = 5.6–**7.8 V** at IT = 1 mA. VC is 11.6 V typ at 5 A and 18.6 V max at 9.4 A (8/20 µs). There is no continuous (DC) power rating (LRC Rev.A p1–2).
- SN74LVC1G17 input and SN74LVC1G125 output (Hi-Z or power-off): the absolute maximum is 6.5 V, and the recommended maximum is 5.5 V. TI's footnote (2) allows only the **negative**-voltage ratings to be exceeded when the current ratings are observed. Positive excursions are hard limits (SCES351Y and SCES223U §5.1).
- These pins are Ioff structures: there is no diode to VCC. With U8, or with U7 disabled or unpowered, no current flows through R49/R48, so the 220 Ω divides nothing. The IC pin sees the full TVS voltage.

Consequences:
- Any sustained source on pin 2 or 3 above about 6.5 V (a 12 V miswire, or a failed adapter transceiver passing bus voltage to RXD) can put up to about 7.8 V or more on U8.A or U7.Y. That exceeds the absolute maximum while the TVS is still only leaking at the mA level.
- On a 58 V source, about 0.23 A flows through the 220 Ω. That is roughly 12 W in an 0805. D20/D21 have no DC rating at all.

The plan (qualification 7) already notes the ESD residual above 6.5 V. The DC case is not in the plan, which has no overvoltage contract for pins 2 and 3 beyond 5 V peers.

Feasible interval for any fix:
- The clamp must stay non-conducting at a 5.25 V peer (Victron 5 V MPPTs, VE.Direct FAQ Q4).
- It must hold ≤ 6.5 V at the maximum fault current, which R sets: 12 V/220 Ω ≈ 30 mA.
- The LESD5D5 does not fit that interval.

Options, which Fab would need to decide:
- A tighter clamp on the IC side of R48/R49 (for example a ±2 % 5.6 V Zener; check its rdyn and its leakage at 5 V).
- A larger series R, which lowers the fault current. This has to be checked against the CAN 500 kbit/s timing.
- Explicitly declaring the host port "logic-level only, not battery-fault tolerant" in the pin contract.

Also decide whether R48/R49 are meant to act as fusible elements. That is unverified.

### F2 — minor, plausible: pin 4 ESD goes straight into the shared 3.3 V rail, and U7 VCC is the first node hit

Refdes: C33, J5.4, U7.5, +3.3V.

- The plan's ESD argument is charge-based: 150 pF × 8 kV = 1.2 µC on 1 µF gives 1.2 V.
- Two points qualify it:
  - Even the charge figure lifts the rail node to about 4.5 V locally, above the ESP32's 3.6 V. This assumes the other rail capacitance, about 1.4 µF of ceramics on-board plus the PSU board, sits behind trace inductance.
  - The first nanoseconds are set by C33's ESL and via inductance, not its capacitance. An estimate of 0.5 nH × 30 A/0.8 ns gives about 19 V transient.
- Placing C33 "next to U7's VCC" puts U7.5 (6.5 V absolute maximum, 2 kV HBM) at the strike point.
- DZ1 (SM2T3V3A) is on the PowerSupply sheet, far away, and has no guaranteed VBR maximum.

Fab decided "no TVS on pin 4" (2026-09-29). Suggestion: add a **DNP** footprint for a low-capacitance 3.3 V-class TVS at J5.4, so that the outcome of qualification test 7 can be acted on without a respin. Make sure test 7 explicitly includes discharges to pin 4 and to GND pin 1.

### F3 — minor, accepted risk: no back-feed or current limit on pin 4

A peer that sources pin 4 drives +3.3V directly.

- The rail feeds U2, the U1 UCC21330 VCCI (the gate-driver primary), U3 INA226, U5 AP3012 IN and /SHDN, and D2 WS2812B.
- The only rail clamp is DZ1 SM2T3V3A, with VBR min 3.6 V and no maximum. It does not keep a 5 V source below the ESP32's 3.6 V absolute maximum.
- For in-scope peers (GX, VE.Direct-USB, adapters) this does not arise: they are consumers powered from pin 4. Victron's VE.Direct-USB and RS232 interfaces are galvanically isolated (Protocol 3.34 p3; FAQ).
- It does arise if Fugu is cabled to another *producer*, for example someone trying to read a SmartShunt or MPPT from Fugu.

This matches the plan's qualification item 3 and Q15. I am listing it so it stays visible, not as new information. Consider labelling the port "producer: do not connect to another Victron product" on the silkscreen.

### F4 — minor, confirmed against the plan: R48 rating not specified, and the 0805 footprint does not meet the plan's own derating rule

Refdes: R48 (and R49).

- Plan host change 3: a sustained 5 V short dissipates 114 mW in R48, so it needs "≥ 0.125 W after derating (1206 if in doubt)".
- As captured: `R_0805_2012Metric`, with MPN field = "220" (no part number, no power rating).
- A standard 0805 is 0.125 W at 70 °C. 114 mW is 91 % of that, which is not derated.
- Fix: use 1206, or specify a 0.25 W 0805 by MPN.
- R49 does not share this load: U8.A is high impedance, so R49 conducts only in the F1 clamp case. Leave R49's rating to the F1 decision.

### F5 — minor, plausible: the "accepted brownout" on a pin-4 short or adapter inrush reaches the gate driver

Q15 accepts that a pin-4 short browns out the 3.3 V rail. The netlist shows that the same rail supplies:
- the U1 UCC21330 VCCI (gate-driver input side),
- U5 AP3012 (the 12 V gate-drive boost: IN and /SHDN both on +3.3V),
- U3 INA226.

Adapter hot-plug inrush into the TCAN1042HV boost input capacitance lands here too. So a brownout is a power-stage event mid-switching, not just an MCU reset. The plan's qualification item 4 asks to "confirm the converter stays safe". The test plan should name U1's UVLO output state and U5's collapse explicitly. The UCC21330 datasheet was not checked in this review.

### F6 — nit: TX floats on the cable while disabled

With /OE high, J5.3 has no bias on the connector side (R47 is on U7's input side). This is intended for the adapters, which carry their own 10 k pull-up to V+. For a GX or VE.Direct-USB consumer, a floating RX during Fugu's boot depends on the consumer's input bias, which is not documented by Victron. A weak pull-up (for example 100 k to +3.3V) on the J5 side of R48 would keep the line idle-high without upsetting the adapter's DE logic. Its cost: about 33 µA and a back-feed path when the board is unpowered, bounded at 5 V/100 k.

### F7 — nit: BOM and documentation completeness

- The MPN fields of R46–R50, C33 and C35 hold the value strings ("10k", "1uF, X7R, 25V"). They are not orderable part numbers.
- `doc/Connectors.md` has no J5 / VE.Direct pin contract. The skill asks for the same pin truth in the schematic, the board markings and the integration document. The schematic note block and the plan cover it for now.

### F8 — nit: GPIO domain dependency on the module variant

GPIO36, GPIO37 and GPIO48 are VDD_SPI / VDD3P3_CPU-domain pins (ESP32-S3 datasheet v2.2, Table 2-1 and note 4). They are fine on the -N4 module, which has 3.3 V VDD_SPI. On an R8V/R16V (1.8 V VDD_SPI) variant, GPIO48 would swing 1.8 V, below U7's VIH of 2.0 V, and GPIO35–37 are taken by octal PSRAM. The plan already says to keep N4. Put that constraint on the BOM or the schematic note so a module substitution does not silently break /OE.

## Checked and OK

- VE.Direct pinout: pin 2 = RX in, pin 3 = TX out, producer view (Protocol 3.34). Pin 4 supplies the consumer.
- Victron consumers adapt their TX level to pin 4 (FAQ Q4), so 3.3 V is appropriate. The consumer draw is ≤ 10 mA average, 20 mA for 5 ms (FAQ Q5), well within the rail.
- /OE polarity: active low with R46 pull-up. The GPIO48 choice avoids the GPIO38/39 USB-OTG-download low. There is no internal pull at reset (Table 2-1).
- Contention through R48 is bounded at 22.7 mA, under the 50 mA IO absolute maximum.
- U8 input is 5.5 V-tolerant at any VCC (ROC VI 0–5.5 V). VT+ is at most 1.92 V and VT− at least 0.89 V at VCC = 3 V (SCES351Y Table 5-1), which suits both 3.3 V and 5 V peers.
- Negative excursions: D21 clamps near −VBR (−5.6…−7.8 V). U8.A then draws at most (7.8 − 0.5)/220 ≈ 33 mA, under the IIK of −50 mA, and the footnote permits exceeding the negative voltage rating under that current limit. OK for DC.
- Ground: J5.1 is logic GND = Bat−. With isolated Victron consumers and non-isolated adapters without a comms GND wire (the plan's proposal), J5.1 is not a parallel battery-return path.
- ERC: no messages on the ExtPort sheet.

## Unverified

- Behaviour of the ICs' internal ESD structures under the TVS residual (F1, F2). This needs qualification test 7.
- The U7 PMOS on-resistance used in the contention estimate.
- The UCC21330 UVLO behaviour on a brownout (F5).
- Whether Victron's VE.Direct cable is straight or crossed (plan qualification 3). Protocol 3.34 labels both ends identically and requires producer TX → consumer RX, which does not settle it.
- Layout: none exists yet. The C33 placement constraint (at J5.4 and at U7.5) implies that U7 sits at the connector.
