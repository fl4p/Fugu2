- li-ion batteries with bms require external power supply (e.g. the solar panel)
  use source follower as in https://github.com/LibreSolar/mppt-2420-hc/blob/main/build/mppt-2420-hc_schematic.pdf
  to limit supply voltage (from 100V solar)
- use lower voltage buck converter for 12V/3.3V supply
- protection against voltage transient
- when battery voltage (up to 60V) is available, switch
- esp32s3 has 300mA peak current consumption
- expect solar input (80V, or more?) at battery terminal
    - another charger connected in parallel might be faulty passing through solar voltage (happended to me with Victron)
      and when battery is disconnected (e.g. BMS cut-off)

# 3.3C

ESP32-S3 WROOM
802.11g, 54 Mbps, @18 dBm peak 297 mA
https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf#page=18

AVG with wifi 120 mA

Suitable Surge Supression

## Clamping

- TVS (or ZVS)
    - combined with PTC, Coil, Fuse (see Renesas Book)
- MOV
- MOSFET
    - ICs exist (LTC4364)

## Source Follower (common-drain)

- like in https://github.com/LibreSolar/mppt-2420-hc/blob/main/build/mppt-2420-hc_schematic.pdf
    - as soon as output voltage is available (LV≤60V) the circuit turns-off the source follower
    - uses a charge pump powered by LV to generate voltage above supply input to switch on a transistor (T2), which
      turns-off the
      source follower MOSFET Q4
    - it only protects from surge voltages at the solar input
- simple voltage regulator
- protects against surge voltages, even longer times
- can implement soft-start
- min voltage drop: Vgs_th. choose a mosfet with low Vgs_th!

# OV Protection

- surge voltage (voltage spike, voltage transient)

- ZVS + Fuse

Fuses
0679L0375-05

xl7005
LV5144RGYR

https://www.digikey.de/short/83bbnbjn (buck 75V)

|                   |              | Vin(max) | Iout(max)          | Iq    | eff (80Vin, 150mA) | eff in:75V out:12V,100mA | eff 12Vin/3.3V,100mA | $px(100)            |                                                                                                                                                       |
|-------------------|--------------|----------|--------------------|-------|--------------------|--------------------------|----------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| TPP00032          |              | 100      | 300                | 100μA |                    | 72%                      |                      | 0.56 (out of stock) | low stock, sync, FET: 0.75 Ω and 0.4 Ω , light-load operation                                                                                         |
| TPP00031-ES1R     |              | 100      | 300 mA             |       |                    | 56%                      |                      | 0.22                | sync, FET: 0.75Ω and 0.4 Ω   [PDF](https://static.3peak.com/res/doc/ds/Datasheet_TPP0003x.pdf)                                                        |
| LMR38010FDDAR     |              | 80       |                    | 40µ   |                    |                          |                      | 1.81                |                                                                                                                                                       |
| LMR38020          |              | 100      |                    |       |                    |                          |                      |                     | prog fsw, SPREAD SPECTRUM (EMI)                                                                                                                       |
| RAA2118034GP3#JA0 | var freq,DCM | 80 (84)  | 300mA (3.3V fixed) |       | 70%  (3.3Vout)     |                          |                      | 0.87                | [PDF](https://www.renesas.com/en/document/dst/raa211803-805-datasheet?r=25449141)                                                                     |
| TI LV2862XLVDDCR  |              | 60 (65)  | 600                |       |                    |                          | 83%                  | 0.51                | 0.7mhz                                                                                                                                                |
| SCT2A22STER       |              | 100      |                    |       |                    | 70%                      |                      |                     | Forced PWM                                                                                                                                            |
| *SCT2600*         |              | 80       |                    |       |                    | 65%?                     |                      | $.24                | pulse skipping (light-load)                                                                                                                           |
| SCT2A12           |              | 100      |                    | 49uA  |                    | 85%                      |                      |                     |                                                                                                                                                       |
| TI LM5009A        |              | 95       | 300                |       | 78%  (10Vout)      |                          |                      | 1.33                | [PDF](https://www.ti.com/lit/ds/symlink/lm5009a.pdf)                                                                                                  |
| TI LM5169/8       |              | 120      | 650/300            |       | 77%                |                          |                      | 1.33                | Sync, Fly-Buck™ [PDF](https://www.ti.com/lit/ds/symlink/lm5168.pdf)                                                                                   |
| XL7005            |              | 70       | 500                |       | 64% (15Vout)       |                          |                      |                     | [PDF](http://www.ksmcu.com/pdf/XL7005%20datasheet.pdf)                                                                                                |
| MP4541            |              | 80       | 800                |       | ~75%  (10Vout)     |                          |                      | 1.20                | [PDF](https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MP4541GN/document_id/9688/) |
| LM5164            |              | 100      | 1000               |       | 84                 | 83%                      |                      | 2.35                | sync, FET: 0.725Ω and 0.34Ω, [PDF](https://www.ti.com/lit/ds/symlink/lm5164.pdf)                                                                      |                                                                           
| *LM5163DDAR*      |              | 100      | 500                |       | 82                 | 83% (60Vin)              |                      | 1.61                | sync, FET: 0.725Ω and 0.34Ω, [PDF](https://www.ti.com/lit/ds/symlink/lm5163.pdf)                                                                      |
| XL7015            |              | 100      | 300                |       | 70                 |                          |                      |                     | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2409271802_XLSEMI-XL7015E1_C73013.pdf)                                                            |
| XL7005            |              | 80       |                    |       | 60                 |                          |                      |                     | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1811081614_XLSEMI-XL7005A_C50848.pdf)                                                             |
| TX4139            |              |          |                    |       | 75%                |                          |                      |                     |                                                                                                                                                       |
| LM5116            |              | 100      |                    |       |                    |                          |                      | 3.80                |                                                                                                                                                       |
| LM5007            |              | 80       | 700                |       | 79%                |                          |                      | 2.11                |                                                                                                                                                       |
| LMR16006X         |              | 60       | 600                |       |                    |                          |                      | 1.96                | LibreSolar/mppt-2420-hc                                                                                                                               |
| LMR51606XDBVR     |              | 65       | 600                |       |                    |                          |                      | 0.58                |                                                                                                                                                       |

Good drop-in for 3.3 and 12V rails, 80,100V:

* LMR38020SDDAR ($1.86 PFM, 80V, prog fsw)
* LM5163DDAR ($1.6, COT, 100V, prog fsw) <-- pick
* SCT2A12 ($.35 marketplace, PFM, 100V, 390khz
  fs) https://www.silicontent.com/uploads/admin/file/20240809/20240809110531_16687.pdf
*
* LM5009A (150mA)

PFM: better light-load eff (pulse skipping)
FPWM: lower ripple, tighter regulation  (forced pwm)

MP4541

12 -> 3.3V: @ 100 mA
https://www.digikey.de/short/bpfjh3m8

AP63203WU-7: 88%, 22µA Iq, 2A max, 0.5 € (100x)
TPS62172DSGT: 84%
TPS560430: 84%
TPS51383: 92 %, 80-μA Iq, 8A max, 0.53€ (100x)
RAA2118034GP3#JA0

LM5146 (external fets)

Diodes

- DFLS1100

# 3.3V ZVC protection

ESP32 has internal ESD protection. we need ZVS for lightning and voltage transient protection.
usually these diodes have a peak power of 600 W.

|                       |     | Vrwm | Vbr | Vcl  | Ippm |      |
|-----------------------|-----|------|-----|------|------|------|
| **Littlefuse SMF3.3** | .4€ | 3.3  | 3.4 | 6.8  | 30A  | 200W |
| Vishay SMBJ3V3-E3/52  | .4€ | 3.3  | 4.1 | 10.3 | 200A | 600W |
| **ST SM2T3V3A**       | .6€ | 3.3  | 3.6 | 6.8  | 30A  |      |
| ST SMLVT3V3           | .8€ | 3.3  | 4.1 | 10.3 | 200A | 600W |
| NXP PTVS3V3S1UR,115   | .4€ | 3.3  | 5.2 | 8    | 44A  | 350W |

* Vishay SMBJ3V3-E3/52 (.4€)
*

Surge Protect:
https://ir.canterbury.ac.nz/items/e7c8c3da-042c-4d4a-9b7b-2b93970b0d82

# Boost 3.3 -> 12V .

* one FET needs ~< 50mW gate-drive power
* 4 FETs at 10V need 20 mA @ 40 kHz
* 20mA@12V = 240mW, 20mA@80V = 1.6W
* AP3012KTR-G1 @ 20mA has 75% eff.
    * $.24 + 10uH(.4$) + D=1N5819 (C: X5R or X7R Dielectric, L: SUMIDA CDTH3D14/HPNP-100NC or Equivalent)
    * ⇒ for <$1 a 75% eff. solution (better than using another 100v→10V buck)
    * consider using using a 100V diode maybe after C_out to protect any HV

|              |      |   |
|--------------|------|---|
| AP3012KTR-G1 | $.25 |   |
|              |      |   |
