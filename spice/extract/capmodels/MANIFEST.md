# Vendor SPICE models for the input (Cin) ceramics

Pulled from vendor tools using the MPNs in `../../bom-list.csv`. These are the
HF input capacitors that carry the commutation (hot) loop current. Refdes →
extracted copper-path L is from the FastHenry per-cap sweep (`../results.md`).

| Refs | Value | BOM MPN | Vendor P/N (current) | Pkg | Model file(s) | C0 | ESL | ESR floor | copper-path L (FastHenry) |
|---|---|---|---|---|---|---|---|---|---|
| C17, C18 | 220 nF 100 V X7S | HMK107C7224KAHTE | MCASH168SC7224KTCA01 (Taiyo Yuden) | 0603 | `vendor/MCASH168SC7224_TCA01_LT.cir` (+`.asy`, DC-bias/temp) ; `vendor/c17c18_220n_0603_std.cir` (0-bias) | 212 nF | 0.47 nH | 12.2 mΩ | 4.2 / 4.3 nH |
| C9, C16 | 1 µF 100 V X7S | HMK212BC7105KGHTE | MMASH21GBC7105KTCA01 (Taiyo Yuden) | 0805 | `vendor/MMASH21GBC7105_TCA01_LT.cir` (+`.asy`, DC-bias/temp) ; `vendor/c9c16_1u_0805_std.cir` (0-bias) | 977 nF | 0.35 nH | 5.3 mΩ | 4.6 / 4.8 nH |
| C21, C22 | 10 µF 100 V X7S | GRM32EC72A106KE05L | GRM32EC72A106KE05 (Murata) | 2220 | `vendor/c21c22_10u_2220_GRM32EC72A106KE05.mod` (0-bias) | 9.73 µF | ~0.08 nH+ladder | 1.6 mΩ | 5.4 / 6.7 nH |

## Notes
- **Taiyo Yuden `_LT.cir`** = encrypted **temperature / DC-bias** model (real C
  derating vs Vds) + LTspice `.asy` symbol → use these in LTspice for the ring.
  The `_std.cir` / `.mod` are the unencrypted 0-bias RLC-ladder equivalents
  (portable to ngspice, no bias derating).
- **Murata** publishes only the 0-bias `.mod` in the series netlist ZIP; its
  DC-bias model lives in SimSurfing / the LTspice EDA library (separate). The
  10 µF bulk caps are the *least* important for the fast loop (highest loop L),
  so the 0-bias model is acceptable here; note the derating is significant at
  60–80 V and can be added later if needed.
- In LTspice each ceramic = its vendor model **in series with its extracted
  copper-path L** (the FastHenry number), forming the parallel bypass branches.
  Do NOT lump them into one cap — placement (loop L) is why C17/C18 dominate.
