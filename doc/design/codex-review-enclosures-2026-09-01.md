# Codex adversarial review — doc/Enclosures.md — 2026-09-01

Model: codex-cli 0.149.1, `codex exec`, 9 numbered attack targets. Findings below are the
model's raw output (file:/// wrappers stripped). Verification verdicts are recorded in
`doc/Enclosures.md` § Review history — several findings were downgraded or rejected after
checking against primary sources.

FINDINGS

1. (c) [doc/Enclosures.md:8](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:8) misstates the product output as 27 V/33 A, whereas [README.md:51](/Users/fab/dev/ee/hw/Fugu2/README.md:51) specifies 12–60 V and 32 A maximum; replace it with the rated range and identify 27 V/32 A only as a tested operating point.

2. (c) [doc/Enclosures.md:22](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:22) turns two uncontrolled runs at different throughput—not measured dissipated power—into a universal prohibition on enclosed fins and a prediction that the coil limits power, although [doc/Thermal tests.md:14](/Users/fab/dev/ee/hw/Fugu2/doc/Thermal%20tests.md:14) supplies no coil temperature and a conductive sealed enclosure could outperform cardboard; require equal-operating-point A/B tests with input/output loss and coil, heatsink, enclosure, ambient, and equilibrium temperatures before adopting either rule.

3. (c) [doc/Enclosures.md:36](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:36) strengthens the meltdown record into “40 min before runaway,” while [doc/Thermal tests.md:48](/Users/fab/dev/ee/hw/Fugu2/doc/Thermal%20tests.md:48) says only that the heatsink melted, 80 °C was maintained manually for 40 minutes, and temperature later dropped then increased; reproduce that wording and do not infer runaway.

4. (c) [doc/Enclosures.md:64](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:64) treats the VX 22’s ≤12 W mains-consumption rating as an enclosure thermal rating without its permitted temperature rise, ambient, mounting, or solar-load conditions; retain 20/12 = 1.67 only as a rough heat-input comparison and call the housing capacity unqualified pending measurement.

5. (c) [doc/Enclosures.md:95](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:95) correctly removes a ≤72 V-all-ports design from LVD scope but incorrectly says it would categorically “land under GPSR” with no harmonised standard, because GPSR applies only to consumer or foreseeably consumer-used products and other EU legislation remains; state those conditions and say only that the LVD presumption-of-conformity route would disappear ([GPSR Arts. 1–3](https://eur-lex.europa.eu/eli/reg/2023/988/oj/eng)).

6. (c) [doc/Enclosures.md:118](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:118) and [doc/Enclosures.md:136](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:136) drop the medium-confidence, three-report bound and state categorically that IEC 62109-1 is “not glow wire,” even though the unvalidated EN preview’s normative-reference list names IEC 60695-2-11 and IEC 60695-11-5; retain only that glow-wire results do not establish a required UL/IEC flame class and mark the exact clause-9.1.3.2 acceptance route `unverified`.

7. (c) [doc/Enclosures.md:59](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:59), [doc/Enclosures.md:116](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:116), and [doc/Enclosures.md:145](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:145) overclaim that generic FR-4 is necessarily V-0 and aluminium makes all flammability and impact questions disappear, while [Fugu2.kicad_pcb:52](/Users/fab/dev/ee/hw/Fugu2/Fugu2.kicad_pcb:52) records only “FR4”; require the actual PCB laminate/fabricator flammability evidence and say metal resolves only enclosure-material requirements, not internal polymers, fire containment, openings, bonding, or the metal mechanical test.

8. (c) [doc/Enclosures.md:175](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:175) treats one loaded-jig oven ramp on specific Prusament prints and heatsink temperatures—including an 80 °C destructive test—as continuous-use limits for arbitrary enclosure parts; use those values only for screening and qualify PLA/PETG from measured part temperature, actual stress and geometry, creep duration, normal/single-fault conditions, and the chosen filament/process ([CNC Kitchen method](https://www.cnckitchen.com/blog/comparing-pla-petg-amp-asa-feat-prusament)).

9. (c) [doc/Enclosures.md:228](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:228) and [doc/Enclosures.md:230](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:230) reject Hammond KHD and Bopla ABP by comparing the board’s 88 mm side with enclosure width, although the 88 mm side can run along the 160/200 mm length and Hammond publishes a 159 × 74 mm maximum PCB for KHD and 159 × 97 mm for NHD; mark KHD as planarly fitting, NHD as planarly fitting with published limits, and ABP plan/height fit as unverified rather than “too narrow” ([KHD specification](https://www.hammfg.com/part/1455KHD1601)).

10. (c) [doc/Enclosures.md:215](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:215) ranks finned candidates and [doc/Enclosures.md:256](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:256) says their fins “do the work” without a thermal resistance, orientation, allowable temperature rise, or 20 W test for any candidate; mark every enclosure thermally unqualified until vendor data or a controlled calorimetric test establishes its 20 W performance.

11. (c) [doc/Enclosures.md:266](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:266) correctly recognizes an accessible-metal insulation hazard but incorrectly implies the pad becomes safety-critical only then and omits the protection-class decision, protective bonding, semiconductor tabs and fasteners, edge creepage, compression/puncture/aging, and the rated 80 V plus transients; describe it as an already safety-relevant dual thermal/insulation interface and specify either Class I basic insulation plus verified PE bonding or Class II double/reinforced insulation for the complete assembly.

12. (c) [doc/Enclosures.md:217](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:217) assigns an AWA12-7-9SS price to the AWA12-7-12SS row, while [doc/Enclosures.md:244](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:244) calls an unpriced scavenged VX 22 cheaper than every listed option; obtain the exact AWA12-7-12SS price and either document a VX 22 market price or remove that ranking.

SURVIVED

1. Attack 1 — The 80 V rated PV input is sufficient for LVD scope because official guidance uses input or output voltage; the lower output voltage does not negate it, internal transient voltage is not the governing rating, and no Annex II exclusion fits this charge controller ([doc/Enclosures.md:88](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:88), [README.md:51](/Users/fab/dev/ee/hw/Fugu2/README.md:51)).

2. Attack 2 — Both thermal runs do sit under the same Vin, Vout, ambient, heatsink, MOSFET, and T130-coil condition block, and `(760−470)/760 = 38.16%` plus `61−51 = 10 °C` are correct ([doc/Thermal tests.md:1](/Users/fab/dev/ee/hw/Fugu2/doc/Thermal%20tests.md:1)).

3. Attack 3 — UL/IEC flame classifications and glow-wire temperatures are different results and cannot be converted into one another ([doc/Enclosures.md:120](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:120)).

4. Attack 4 — `20/12 = 1.67`, and essentially all CATV amplifier mains input ultimately becomes enclosure heat because RF output power is negligible; only the further thermal-capacity inference fails ([doc/Enclosures.md:64](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:64)).

5. Attack 5 — The Takachi AWA12-7-12SS dimensions are correct, its 96.7 × 120.6 mm plan accommodates the 88 × 50 mm PCB, and the document explicitly leaves its 46 mm vertical clearance provisional pending a stack-height measurement ([doc/Enclosures.md:217](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:217), [doc/Enclosures.md:283](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:283)).

6. Attack 6 — The PLA, PETG, and ASA temperatures are accurately transcribed from the stated Prusament loaded-jig oven test, and the document correctly identifies that method rather than calling it HDT or Vicat ([doc/Enclosures.md:177](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:177)).

7. Attack 7 — The Fischer ≈€25–30, Hammond ≈€41, ABPH ≈€69, and 1590Z ≈€38 summary values agree arithmetically with their table entries ([doc/Enclosures.md:221](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:221), [doc/Enclosures.md:242](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:242)).

8. Attack 9 — Making the heatsink an accessible enclosure wall does require a documented insulation system with creepage/clearance and dielectric/impulse verification; the defect is that the discussion stops before defining the complete protection system ([doc/Enclosures.md:264](/Users/fab/dev/ee/hw/Fugu2/doc/Enclosures.md:264)).
