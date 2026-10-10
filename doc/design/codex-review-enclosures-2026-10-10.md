# Codex review of doc/Enclosures.md — 2026-10-10

Reviewed commit efe83f2 via the codex-review skill (codex-cli 0.154.0, workspace-write + network, scratch Chrome over CDP, Fab's Chrome via the on-demand lock broker). Exit 0. Raw log kept outside the repo. Every finding below was re-checked against a primary source before being applied; see Review history in ../Enclosures.md.

The reviewer reported a TOKEN-SIGHTING: a fabchrome tool response exposed the extension connection token to the reviewer model. The log itself contains no token.

## ACCESS

- **curl — Hammond 1455KHD1601:** HTTP **200**; title **“1455KHD1601 - Hammond Mfg.”**
- **Playwright — Kikakurui:** title **“JIS C 62477-1 : 2017 半導体電力変換システム及び装置に対する安全要求事項－第１部：一般事項”**.
- Mouser and the Vietnamese adoption required the granted **fabchrome** session and became readable. The PEA/isuna PDF remained blocked in both browsers; its contents remain **unverified**.
- **TOKEN-SIGHTING:** A browser-tool response exposed an extension connection URL/token. It is not repeated here.
- Reviewed committed sources at **efe83f2**. No source files edited. Review and connection tabs closed; request marker removed.

## FINDINGS

1. **(c) The two principal “unverified” questions can now be substantially resolved.**  
   [Enclosures.md:155](../../doc/Enclosures.md:155), [377](../../doc/Enclosures.md:377), and [385](../../doc/Enclosures.md:385): the publicly visible portions of **TCVN 12231-1:2018**, whose foreword declares equivalence to IEC 62109-1:2010, include:
   - **9.1.3.1:** a **550 °C IEC 60695-2-11** test is an accepted alternative where **HB/HBF** is required.
   - **9.1.3.2:** **5VB** at the minimum significant wall thickness, or an end-product test, with additional dripping, afterburn and opening criteria.

   Thus, “paywalled text only,” blanket rejection of glow-wire substitution, and the present closure narrative need correction. This does **not** make glow-wire results universally convertible to flame classes or approve ASA. The preview has omissions, but these paragraphs are readable without login. [National-adoption preview, clauses 9.1.3.1–2](https://thuvienphapluat.vn/TCVN/Dien-dien-tu/TCVN-12231-1-2018-IEC-62109-1-2010An-toan-cua-bo-chuyen-doi-dien-Phan-1-918417.aspx).

2. **(c) JIS C 62477-1:2017 is not an identical adoption.**  
   [Enclosures.md:160](../../doc/Enclosures.md:160) and [457](../../doc/Enclosures.md:457): its scope note explicitly identifies **IEC 62477-1:2012 plus Amendment 1:2016, MOD**, not IDT. Correct the identity and qualify comparisons clause by clause. The relevant English wording can independently be checked in the public IEC62477_1C report. [JIS, §1 note 4](https://kikakurui.com/c60/C62477-1-2017-01.html); [TÜV report, cover](https://cdn.estg.eu/p/2/a/0/1/2a01dadde2642fd6cd72c6f34c3b95add704f353_SH3.0_6.0RS_62477_test_report.pdf).

3. **(c) The 62477 enclosure summary drops material qualifications and an alternative route.**  
   [Enclosures.md:161](../../doc/Enclosures.md:161): §4.6.3.2 permits the **finished-enclosure flammability test in §5.2.5.5**; 5VA at minimum thickness is a **without-test route**, not the exclusive plastic requirement. “Glass” is restricted to specified heat-resistant/tempered, wired or laminated forms. The glow-wire provision concerns insulation contacting live parts **above DVC As**. “It does not apply to the enclosure” is too absolute if an enclosure part also performs that insulation function. [Public English report, printed pp. 24 and 31](https://cdn.estg.eu/p/2/a/0/1/2a01dadde2642fd6cd72c6f34c3b95add704f353_SH3.0_6.0RS_62477_test_report.pdf).

4. **(c) The claimed committed PCB bounding box is wrong.**  
   [Enclosures.md:6](../../doc/Enclosures.md:6), [260](../../doc/Enclosures.md:260), and [395](../../doc/Enclosures.md:395): at **efe83f2**, Edge.Cuts coordinates span approximately **58.54 × 88.04 mm**, not 50 × 88 mm. They also contain disconnected endpoints, so that span must not be promoted to a verified manufactured outline. See committed [Fugu2.kicad_pcb:57815](../../Fugu2.kicad_pcb:57815), [57835](../../Fugu2.kicad_pcb:57835), and [57889](../../Fugu2.kicad_pcb:57889). Identify the actual board revision underlying the shroud dimensions. The larger span still fits within the stated Hammond rectangular capacities, but the claimed geometry provenance does not survive.

5. **(c) Hammond does publish thermal-resistance information.**  
   [Enclosures.md:255](../../doc/Enclosures.md:255) and [373](../../doc/Enclosures.md:373): the NHD page links a thermal calculation, technical introduction, and NHD/KHD resistance-versus-length charts. The calculation explicitly tabulates a 160 mm NHD example. Replace “none … publishes” with a discussion of the available data and its assumptions. The complete Fugu2 assembly remains thermally unqualified. [Hammond calculation](https://www.hammfg.com/files/products/1455nhd/thermal-transfer-coefficient.pdf); [mounting conditions](https://www.hammfg.com/files/products/1455nhd/technical-introduction.pdf).

6. **(c) “Blue Card … resin, not filament” is false.**  
   [Enclosures.md:245](../../doc/Enclosures.md:245): UL **E527425** covers **Prusament PETG V0**, explicitly furnished as filament and evaluated through material extrusion. Its scope specifies printers and processing parameters. This disproves the categorical exclusion; it does not establish suitability for the P1P, this thermal environment, or a 5VB fire enclosure. [UL certification record](https://iq.ul.com/ul/cert.aspx?ULID=104636411).

7. **(c) The “measured Rth” calibration is actually an estimate.**  
   [Enclosures.md:312](../../doc/Enclosures.md:312): the thermal log records throughput and heatsink temperature, not simultaneous loss measurement. The calculation imports approximately 98% efficiency and implicitly allocates whole-converter losses—including coil losses—to the heatsink. Therefore **1.75 K/W is not a measured heatsink thermal resistance**, and the inferred 14 K fin benefit is not experimental validation. Label both estimates and retain the missing heat-flow assumptions. Evidence: committed [Thermal tests.md:16](../../doc/Thermal tests.md:16) and [README.md:56](../../README.md:56).

8. **(c) A fixed vent-height threshold does not establish fire-containment compliance.**  
   [Enclosures.md:360](../../doc/Enclosures.md:360) and [400](../../doc/Enclosures.md:400): §9.1.4.2 treats side openings inside the specified **5° projection** as bottom openings; §9.1.4.1 applies the requirements in each intended orientation. “Above z = 12” is therefore a provisional design choice, not a demonstrated clause-compliance rule. [National adoption, clauses 9.1.4.1–3](https://thuvienphapluat.vn/TCVN/Dien-dien-tu/TCVN-12231-1-2018-IEC-62109-1-2010An-toan-cua-bo-chuyen-doi-dien-Phan-1-918417.aspx).

9. **(c) The purchasing recommendation omits elpro’s business-only restriction.**  
   [Enclosures.md:319](../../doc/Enclosures.md:319): “least hassle to buy in Germany” needs qualification for this hobby audience: elpro explicitly excludes consumer purchases. Its €40.69 price is **net**. Mouser’s search pages indeed omit a VAT label, but its published terms resolve the uncertainty: prices exclude VAT. State the basis rather than leave the comparison unresolved. [elpro terms, §§1 and 3](https://www.elpro.org/gb/content/6-sbt); [Mouser terms, §2](https://eu.mouser.com/en/saleterms/).

## SURVIVED

- **Normative reference:** IEC 60695-2-11 appears in Annex ZA, printed p. 4/PDF p. 6. The iTeh sample does not contain the operative clause. [iTeh sample](https://cdn.standards.iteh.ai/samples/21578/6a43bd4bc3254ac08c70b4c33b8855f2/SIST-EN-62109-1-2011.pdf).
- **62477 wording match:** the quoted glow-wire wording matches §5.2.5.3 and §4.4.7.8.2 in the public English report. Its placement within the inaccessible **isuna** PDF remains unverified; matching text is not direct inspection of that report.
- **Mouser prices and stock:** NHD **€48.33/41.79/39.35**, with **28 in stock**; KHD **€45.80/42.35/41.14**, with **24 factory-stock units**. The document’s transcriptions survive.
- **elpro price:** **€40.69**, currently **3 in stock**. [Product page](https://www.elpro.org/gb/hammond-1455hd-series/114765-1455nhd1601.html).
- **NHD IP54 attribution:** Mouser lists IP54, as the document says. **Hammond’s own inspected part page, series page and drawing do not substantiate it.** Manufacturer confirmation remains unverified; this is not proof that IP54 is false.
- **(b) Thermal-table assumptions reproduce its results:** horizontal characteristic length \(A/P\), vertical length 30 mm, and exclusion of the resting bottom from convection and radiation produce **26.45/33.61 K** and **33.81/42.77 K** at 15/20 W. Emissivity sensitivity also reproduces approximately **34/43/50 K**. These assumptions should be explicit.
- **Arithmetic:** 495 cm², 38.16%, 10 °C, and \(20/12=1.67\) survive. No material **(a)** arithmetic error confirmed.
- **Regulatory scope:** the 80 V rated input supports LVD scope when marketed; **EN 62109-1:2010** appears in the harmonised list. A Victron declaration alone would not prove harmonisation, but the official listing does. [LVD Article 1](https://eur-lex.europa.eu/eli/dir/2014/35/oj/eng); [harmonised list, entry 540](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02023D2723-20260430).
- **Remaining qualifications:** laminate flame class, physical stack height, and finished-assembly thermal performance correctly remain open. None of the surviving claims establishes that the printed ASA shroud is a compliant fire enclosure.
