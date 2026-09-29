# HV Fuse (F3, Solar+ terminal)

F3 sits between the HV terminal (`T_HV+`) and `Solar+`. In buck mode the HV side is a current-limited PV string,
so a fuse there is optional. In boost mode (board reversed, battery on the HV terminal) it is the only thing
that clears a battery short, e.g. a shorted HS mosfet feeding the battery through the coil into the LV side.
The backflow switch does not help in that case: current in that direction passes through its body diode.

Status 2026-09-29: F3 is in the schematic (commit `5411551`), but the `cs-opa` merge (`1b13241`) took the
PCB wholesale and dropped it. Re-sync the schematic to the PCB and place F3 again.

## Requirements

* DC voltage rating ≥ max battery voltage. 58 V parts cover 16S LFP only if charged to ≤ 3.625 V/cell (3.65 V/cell = 58.4 V). Anything higher needs
  **80 V rated** parts.
* Breaking capacity ≥ battery short-circuit current. All parts below: 1 kA. A big LFP pack can exceed that;
  then use a cartridge/MEGA style fuse.
* Current: boost ~900 W → ~15 A @ 60 V, ~25 A @ 36 V. Buck: ~12 A PV @ 72 V. → **25–30 A**.
* Inrush: connecting a battery to 3×470 µF input caps gives a current spike. Consider a precharge, or check I²t.
* Standard ATO/ATOF/MINI (32 V DC) are **not usable**.

## Parts

Prices are net (excl. VAT) EUR, checked 2026-09-29.

### 80 V ATO (fits the existing `Fuse_Blade_ATO_directSolderThin` footprint)

| Part                    | Rating       | R_cold  | I²t      | Source / price                                   | Notes                                    |
|-------------------------|--------------|---------|----------|--------------------------------------------------|------------------------------------------|
| **ESKA 340.032-80V**    | 25 A, 80 V   | n/a     | n/a      | Conrad 3304227: 2.76 € @1, 2.55 € @10, 363 stock | 1 kA @ 80 V. Also 20 A (340.031), 30 A (340.033), up to 35 A |
| OptiFuse ANR80-UL-25A   | 25 A, 80 V   | 1.9 mΩ  | 813 A²s  | TME: 7.59 € @1, 6.33 € @10, 4.64 € @100, 281 stock | UL, 1 kA @ 80 V. **Operating temp only −40…85 °C** |
| OptiFuse ANR80-UL-30A   | 30 A, 80 V   | 1.65 mΩ | 1530 A²s | TME: 7.59 €, 0 stock                             |                                          |
| OptiFuse ANR80-UL-40A   | 40 A, 80 V   | 1.25 mΩ | 3200 A²s | TME: 6.64 €, 0 stock, 12 wk lead                  |                                          |
| Littelfuse FKS-80 166.7000.525x | 25 A, 80 V | 2.27 mΩ | 950 A²s | DigiKey: obsolete, only ≤15 A left (6.75 €)     | Dead end                                 |

### 58 V (not enough margin for 60 V)

| Part                    | Size    | Rating     | R_cold  | I²t     | Source / price                     | Notes                                  |
|-------------------------|---------|------------|---------|---------|------------------------------------|----------------------------------------|
| ESKA 340.032-58V        | ATO     | 25 A, 58 V | 2.5 mΩ  | n/a     | Bürklin 46G3316: 0.263 € @10, 0.213 € @500 (incl. VAT), 750 stock | Fits ATO footprint. Zinc-alloy contacts (80 V version: Cu). Series 2–40 A; 30 A 1.9 mΩ, 40 A 1.4 mΩ. Bürklin has no 80 V version |
| Littelfuse 0997025.WXN  | MINI    | 25 A, 58 V | 2.36 mΩ | 625 A²s | DigiKey: 0.89 €, ~5300 stock       | Rejection feature against 32 V fuses; fit in our mini footprint unchecked |
| Littelfuse 0891025.NXS  | LP-MINI | 25 A, 58 V | 2.56 mΩ | 613 A²s | DigiKey: 0.51 €, ~4700 stock       | A 32 V MINI fits the same holder        |
| Littelfuse TAC 142.6185.525x | ATO | 25 A, 58 V | 2.3 mΩ | 600 A²s | DigiKey: obsolete, 0 stock        | Dead end                               |

### Time/current (fast blow, ISO 8820-3 style)

| I / I_N | ESKA 340-80V   | ANR80-UL        | MINI 58V (0997) |
|---------|----------------|-----------------|-----------------|
| 1.1     | ≥ 100 h        | carry           | ≥ 100 h         |
| 1.35    | –              | 0.75 s … 1 h    | 0.75 s … 600 s  |
| 1.5     | 0.5 s … 5 min  | –               | –               |
| 2       | 0.15 s … 20 s  | 0.15 s … 60 s   | 0.15 s … 5 s    |
| 3.5     | 40 … 500 ms    | 40 ms … 1 s     | 80 … 500 ms     |
| 6       | 20 … 100 ms    | 10 … 100 ms     | 30 … 100 ms     |

## Choice

Decided 2026-09-29: battery ≤ 58 V is fine (16S LFP charged to ≤ 3.625 V/cell; 3.65 V/cell = 58.4 V is 0.4 V over the rating) → **ESKA 340.032-58V (25 A)**, Bürklin 46G3316,
0.26 €. 58 V / 1 kA, 2.5 mΩ (~0.56 W at 15 A), fits the ATO footprint.

Changed 2026-09-29: F3 is now **Littelfuse 0997025.WXN** (MINI 58V, 25 A, 2.36 mΩ, 625 A²s, DigiKey 0.89 €) on
`open-pe:Fuse_Blade_Mini_directSolderThin`, for its smaller footprint and published I²t. ESKA 340.032-58V stays the ATO
alternative.

For batteries above 58 V use the 80 V parts: ESKA 340.032-80V (Conrad) or ANR80-UL-25A (TME, the only one with
published I²t).

## MINI footprint

`open-pe:Fuse_Blade_Mini_directSolderThin` (2026-09-29) is for the Littelfuse 0997 MINI 58V: 8.12 mm pitch,
3.2×1.1 mm plated slots, 5.5×3.6 mm pads. Pitch and blade size (2.78×0.82 mm) are measured from Littelfuse's
STEP `0997000_WXN_mini58V_Mal.stp`. KiCad's stock `Fuse_Blade_Mini_directSolder` uses 8.0 mm. A 3.45 mm-wide
root shoulder can't pass the slot, so the fuse sits on it about 0.7 mm above the board. The 0891 LP-MINI can't
be through-hole soldered: its terminals end about 0.8 mm below the body.

## Datasheets

* ESKA 340.000-58V: https://www.buerklin.com/Buerklin-Webshop-Site/rest;loc=de_DE/attachments/Buerklin-Webshop%253A%252FFiles_2e5%252F340022-58V-DE-EN.pdf
* ESKA 340.000-80V: https://asset.conrad.com/media10/add/160267/c1/-/en/003304227DS00/datenblatt-3304227-eska-340032-80v-kfz-standard-flachsicherung-25-a-weiss-1-st.pdf
* OptiFuse ANR80-UL (Rev D 07/2025): https://www.optifuse.com/optifuse_ecommerce_tools/datasheets/ANR80-UL.pdf
* Littelfuse MINI 58V (997): https://www.littelfuse.com/assetdocs/littelfuse-datasheet-997-mini58v?assetguid=f4bf5724-5a40-4a44-8f08-c52ae959a5ef
* Littelfuse LP-MINI 58V (891): https://www.littelfuse.com/assetdocs/littelfuse-datasheet-891-lp-mini?assetguid=748f2a1b-6fd1-43cb-b900-7178f45585a0
* Littelfuse TAC ATO 58V: https://www.mouser.com/datasheet/2/240/Littelfuse-Automotive-Blade-Fuse-TAC-ATO-58V-23798.pdf
* Littelfuse FKS ATO 80V: https://www.mouser.com/datasheet/2/240/littelfuse_fks_ato_80v_blade_fuses-523215.pdf

Access notes: TME is behind Cloudflare, so use a logged-in Chrome. Littelfuse assetdocs return an Akamai 403
to curl and to headless browsers; a headed browser works. Mouser PDFs need a headed browser.
