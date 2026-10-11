# Reviews of doc/INSTALLATION.md (commit 2b7a7e8), 2026-10-11

Two independent reviewers looked at the first draft:
- **Codex** (`codex exec`, xhigh, detached). It had network access, a scratch Chrome and
  on-demand access to Fab's Chrome. The log is in `~/codex-reviews/install-doc-20261011/`.
- **A separate Claude reviewer.** It read the draft as a test lab, an installer and a notified
  body would.

Both were read-only. Every finding below was checked against the PCB at HEAD and the EMC study
before the fix went in.

**Access note:**
- The Codex log contains no token value.
- Codex reports that one of its tool responses contained a `token=` URL. It says it suppressed
  the token, but the token may still have reached its model.
- Codex also made one fetch through Fab's Chrome before re-checking its grant.

Fab has been told, so that he can decide whether to rotate the extension token.

## Disposition (all fixed in the revision, except where marked OPEN in the document)

| Finding | Reviewer | Fix |
|---|---|---|
| The "dedicated cable" wording presented the §3.8 NOTE reading as settled | Codex 1, Claude H2 | The design table now says it "supports, but does not settle" the reading, names the residual risk, and cites the 2006 §3.8 / 2011 §3.1.8 editions. OPEN 1 lists the hardware alternative. |
| The battery wording would bypass a separate BMS or battery shunt | Claude H1 | The cable now lands on the battery's system side, after the battery fuse, BMS disconnect and shunt. Raw cell terminals are forbidden where a BMS or shunt is separate. |
| F3 is rated 58 V on a PV input specified to 80 V; no Voc or Isc limits | Codex 2, Claude H4 | Added a ratings table and a fuse note. Voc, Isc and the fuse are OPEN 2 (safety). |
| The H1 heatsink rule was inverted and C14's fitted state was missing | Codex 3, Claude H3 | Replaced by the current data: as built −6.62 dB, nylon screw −7.36 dB; C14 = 1 µF ∥ R17 200 kΩ at HEAD. Marked OPEN, not to be acted on until the path is extracted or measured. |
| CAN and RS-485 were declared categorically not wired network ports | Codex 4 | Classification now depends on the declared topology; §8.7 applies to a wired network port. |
| The USB row named the MCU head; P2 on the main board was missing; Vusb is a power input | Codex 5, Claude M1 | The row is now P2 on the main board, with Vusb noted. The head's USB-C is OPEN 6. |
| Essential ratings, safety and lab test conditions were missing | Codex 6, Claude H6 | Added a ratings table, polarity and connection-order rules, and OPEN 8 and 9 (62109-1 §5.3; a lab test specification per EN 301 489-1 Annex C). |
| A product-page link alone doesn't meet 62109-1 delivery | Codex 7 | OPEN 10. |
| "Never connected to the mains, through any converter" conflicted with a USB host or an inverter-charger | Codex 8, Claude M2 | Reworded to "not a grid-connected power converter … does not feed or draw power from an AC mains network itself". |
| Fuse selectivity was implied by the larger rating | Codex 9, Claude M5 | The battery-end fuse must be rated for DC voltage and prospective fault current (Class T or MEGA); selectivity is OPEN 4; the F1 voltage rating is OPEN 3. |
| Fixed installation was not declared | Codex 10 | Added "fixed installation, wall-mounted, terminals facing down" (`plans/ext-comms-port.md` Q3). |
| J6's net is `BflowS`, not L_out | Codex 11 | Corrected. |
| PV− and battery− are distinct nodes; no grounding section | Claude H5 | Added a Grounding section: the R26 shunt joins them; no external link; single earth at battery−; do not earth PV conductors. |
| "Or other local DC power source" loosened the battery row | Claude M3 | Qualified with "through the dedicated connection described in the table". |
| README boost mode with swapped terminals undermines "solely" | Claude M4 | Intended use now says boost is not an intended use; reconciling the README is OPEN. |
| J5 adapters don't exist; non-isolated ground | Claude M6 | Adapters marked not built (OPEN 5); grounding note added. |
| The table permitted an unfused battery cable | Claude M7 | "Through a fuse at the battery end" is now in the table cell. |
| "No hardware protection" on J5 overstated | Claude L1 | Now names exactly what is missing: pin 4 short-circuit and back-feed protection. |
| Inconsistent fuse net naming; mixed private path styles | Claude L2, L3 | Each terminal now lists its nets; references now name the private `pv/ee/dcdc-tools` repository. |
| "USB may not need a cable-length declaration" was unsupported | Claude L4 | Removed. |
| Twisting large cables is impractical | Claude L5 | Now "bundled tightly, twisted where practical". |

## Codex final block (verbatim)

## ACCESS

- Initial `git log --oneline -1`: `2b7a7e8 doc/INSTALLATION.md: draft installation text that carries the EMC port declarations`.
- Playwright fetched Victron’s homepage: **“Victron Energy | Independent energy systems engineered to outlast”**.
- `pdftotext` successfully read the supplied ETSI PDF. Relevant standards passages and tables were also checked against rendered pages.
- Littelfuse returned an Akamai denial in Playwright; its PDF was subsequently recovered through fabchrome. A tool response contained a `token=` URL; the token was suppressed. **One recovery fetch ran before I re-observed the renewed grant—a protocol error.** Browser-created tabs were closed and the request marker removed.
- No source files were edited. Three automatically generated MCP artifacts were moved out of the repository. HEAD advanced during the review to `b00f036`; the reviewed installation document, PCB, fuse notes, and MCU submodule were unchanged.
- EN 55011:2016+A1 was checked **second-hand through STANDARD-BASIS §8.0**, as requested. No hardware measurements or simulations were run.

## FINDINGS

**The document does not yet establish the intended exemption reliably.** Its strongest problems are the battery interpretation, the incomplete heatsink build specification, and the 58 V PV fuse.

1. **HIGH — (a) The dedicated-cable wording overstates the battery exemption.**  
   [INSTALLATION.md:50](doc/INSTALLATION.md:50), also lines 26, 38–39 and 61–65.

   The quoted fragment is verbatim in IEC 61000-6-3:2006 §3.8, printed p.9. But it describes a link supplying one piece of equipment; it does **not** establish that moving the charger’s dedicated cable from a shared busbar to battery posts shared with loads changes the classification. The permitted installation can retain the same electrical network.

   Charging the battery makes application of the note less straightforward, but does not by itself prove the exemption unavailable. **Neither automatic exemption nor mandatory testing follows from power-flow direction alone.** The defect is presenting the favourable interpretation as settled when the cited project basis explicitly retains lab-disagreement risk (`STANDARD-BASIS.md:703`).

   The 2011 IDT text retains the definition and note: GOST PDF pp.11–12, **§3.1.8**, rather than §3.8. State the edition and preserve the interpretation caveat. Obtain a classification covering the actual shared-battery topology, or retain the Table 3 design requirement.

2. **HIGH — (c) F3 is voltage-underrated for the stated PV operation.**  
   [INSTALLATION.md:25](doc/INSTALLATION.md:25).

   HEAD specifies **25 A, 58 V** at [Fugu2.kicad_pcb:29859](Fugu2.kicad_pcb:29859). The selected Littelfuse 0997 datasheet confirms **58 V DC and 1 kA interruption at 58 V** (p.1). Meanwhile, committed `README.md:51–58` advertises 80 V solar input and reports operation at 72 V.

   The installation table suppresses the voltage rating and supplies no maximum cold-array open-circuit voltage. Current-limited PV does not establish interruption capability above the fuse’s rating. Reconcile the fitted fuse and maximum permitted PV voltage; selecting a replacement requires the actual worst-case Voc and fault-current requirements.

3. **HIGH — (c) The metal H1 screw does not reproduce the cited bonded build.**  
   [INSTALLATION.md:84](doc/INSTALLATION.md:84).

   H1 connects to `Net-(C14-Pad2)`, while C14 connects that node to BuckGND and is specified as **1 µF, 100 V X7S** (`Fugu2.kicad_pcb:18675,54101,54336,54345`). The cited Declaration C assumes **C14 bridged**; `BUILD-CONSTRAINTS-fugu2.md:94–106` expressly distinguishes the bridge from the capacitor.

   Specify the complete intended path—including C14’s configuration and conductive heatsink contact—and associate the analysis with that configuration. A metal screw against an insulating finish also does not guarantee continuity. This is a reproducibility defect; it does not establish that the capacitor-equipped build necessarily fails.

4. **HIGH — (a) CAN/RS-485 are not categorically exempt from wired-network testing.**  
   [INSTALLATION.md:56](doc/INSTALLATION.md:56), especially lines 67–70.

   ETSI §3.1 classifies the **intended interconnection**, not the signalling technology. A constrained local BMS connection can be a signal/control port. The blanket statement that allowing longer CAN/RS-485 buses adds “no emission test” is unsupported where those buses interconnect dispersed systems.

   For a wired-network classification, §8.7 applies without the asserted 3 m exemption. Section 9.8 additionally distinguishes outdoor network cables from indoor cables longer than 30 m. Calling the adapter a separate product does not automatically remove assessment of its intended combination with Fugu2 (§5). Sources: ETSI pp.13–14, 18, 23, 28–29.

   Declare the supported topology, endpoints, indoor/outdoor use, and complete cable extent per adapter.

5. **MEDIUM — (a) The USB inventory omits motherboard P2.**  
   [INSTALLATION.md:28](doc/INSTALLATION.md:28), also lines 71–72.

   HEAD contains USB-C **P2**, connected to `Vusb`, `USB_D±` and GND (`Fugu2.kicad_pcb:19153–19609`). The committed plan explicitly identifies motherboard USB as the product interface and head USB as development/service (`plans/ext-comms-port.md:46`). The pinned MCU head additionally contains P1 USB-C, USB1 and an ESP-PROG header.

   Identify the shipped assembly and accessible interfaces. Deciding only whether the head’s USB is reachable leaves the product USB unclassified.

6. **MEDIUM — (c) Closing the listed OPEN items would still leave essential installation and test conditions unspecified.**  
   [INSTALLATION.md:59](doc/INSTALLATION.md:59).

   Missing items include battery type/range, PV ratings and permitted array grounding, terminal polarity/torque, disconnection instructions, environmental limits, and the enclosure/heatsink earthing arrangement. These extend beyond the acknowledged cable-size and fuse-rating decisions. IEC/EN 62109-1 §§5.3.1–5.3.2 addresses these categories; see the reproduced clauses in the [TÜV report, pp.31–33](https://solplanet.net/wp-content/uploads/2023/04/TR_IEC62109-1_ASW3-20K-LT-G2-Pro-704092007507-02TRF_TUV-MARK_CE_E_Part-1-1.pdf).

   For EMC, short cables do **not** remove §9.3 ESD assessment of exposed surfaces/interfaces. A service designation needs corresponding access/protective conditions, not merely a label. The lab also needs operating modes, ancillary equipment, functional monitoring and thermal limitations—ETSI Annex C, p.33. Provide a controlled companion test specification where this material does not belong in the installer sheet.

7. **MEDIUM — (a) A product-page link is not automatically equivalent to supplying the safety instructions.**  
   [INSTALLATION.md:76](doc/INSTALLATION.md:76).

   IEC 62109-1 §5.3.1.2 generally requires printed documentation delivered with the equipment; its electronic-only exception concerns equipment requiring a computer for **both installation and operation**. Optional USB configuration does not establish that exception. The cited TÜV report reproduces this requirement on p.31. Separate the EMC declaration’s availability from the safety-document delivery requirement.

8. **MEDIUM — (a) The absolute mains prohibition conflicts with the permitted computer connection.**  
   [INSTALLATION.md:16](doc/INSTALLATION.md:16), versus line 28.

   “Through any converter” can include USB connected to a mains-powered computer through its AC/DC supply. Neither the USB row nor the prohibition defines an exception or isolation condition. State precisely which power-system connections are prohibited and which computer/service connections are permitted.

9. **MEDIUM — (a) A larger upstream fuse rating does not establish selective operation.**  
   [INSTALLATION.md:74](doc/INSTALLATION.md:74).

   Choosing a battery-end fuse above 40 A does not guarantee F1 opens first. That requires the selected fuse characteristics, prospective fault current and coordination evidence. Keep cable protection mandatory, but replace the implied selectivity guarantee with a requirement to verify coordination.

10. **LOW — (b) Fixed installation is assumed but not declared here.**  
    [INSTALLATION.md:12](doc/INSTALLATION.md:12).

    The cited §8.3.1 applicability is for fixed use. Wall mounting is specified elsewhere (`plans/ext-comms-port.md:35`), so the assumption has support, but “off-grid” alone does not exclude vehicle installations. Carry the intended installation category into this document.

11. **LOW — (a) J6’s electrical net is misnamed.**  
    [INSTALLATION.md:89](doc/INSTALLATION.md:89).

    J6’s component value is `Conn_L_out`, but its pad is on **`BflowS`**, not an `L_out` net (`Fugu2.kicad_pcb:142,280`). J3 is correctly `SW`. Distinguish the functional connection name from the PCB net.

## SURVIVED

- **EN 55011 row, line 48:** The supplied secondary transcription supports both cited clause numbers and the GCPC limitation: §6.2.1.1, p.24; §8.2.2.2.1, p.53. This survives **at the explicitly permitted secondary-evidence level**, not as independent verification of the DRM original.

- **Battery length, line 51:** **2 m removes the cited local-battery length branches.** ETSI §8.3.1 says longer than 3 m. GOST Table 3 separately lists a local DC network and a local battery connected by a cable exceeding 30 m (PDF p.17). The network classification remains consequential.

- **CISPR battery wording, line 52:** This is a faithful paraphrase of §8.2.2.2.1’s installation-instruction exemption; CISPR 11 ed.7, printed p.60. It is a separate argument from IEC 61000-6-3’s single-equipment note.

- **Cable thresholds and arithmetic, line 54:** CISPR 11 Table 6 has `L < 3 m`, `3 m ≤ L < 30 m`, and `L ≥ 30 m`. Thus **60/29 = 2.06897 MHz** is correct. Exactly 30 m restores the full band. The generic standard’s battery threshold is instead **exceeding 30 m**; these boundaries should not be conflated.

- **EVVO practice:** Report BL-SZ19B0347-401 p.9 explicitly skips DC-port emissions because the cable is shorter than 30 m; p.24 reproduces the applicability note. That supports the stated example of lab practice, not a universal PV exemption. The dedicated-array reading in line 53 remains a defensible interpretation rather than an explicit PV carve-out.

- **PV immunity and the quotation, lines 55–56:** §§9.4 and 9.5 genuinely use the longer-than-3-m condition. The ellipsized quotation is accurate. A permitted 29 m PV cable triggers those tests; the declared 2 m battery cable does not. Skipped ports must be recorded. Section 9.8 does **not** itself impose a general PV DC-port surge test.

- **Environment:** Residential/commercial/light-industrial emissions and **EN 61000-6-2 industrial immunity are not inherently contradictory**. Victron’s supplied 2025 DoC lists that combination. The document should identify its chosen immunity basis; it should not automatically substitute 6-1 merely because the emissions environment is residential.

- **Main power connections:** J10 is `T_HV+ / BuckGND`; J9 is `BT+ / GND`; F3 is `T_HV+ → Solar+`, 25 A; F1 is `Bat+ → BT+`, 40 A. J5’s JST-PH four-pin identity is correct. Battery-end cable protection and paired power conductors are sound instructions.

- **Other boundaries:** TH1 is an onboard NTC, not a missing external sensor cable. `PWRGND1` is a test pad, not proof of a PE terminal. Keeping J3/J6 and the coil inside the enclosure addresses their external-port issue, provided the shipped construction actually does so.

- **Simulation numbers:** The quoted approximately **+4.3 dB failure / 2.4 dB passing margin** agree with the referenced report’s rated-point estimates. The KZN result retains an assumed sibling-model ESL; neither number is a hardware compliance measurement. No measured radiated-emission margin was established by this review.


