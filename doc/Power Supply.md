# 3.3C

ESP32-S3 WROOM
802.11g, 54 Mbps, @18 dBm peak 297 mA
https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf#page=18

AVG with wifi 120 mA

# OV Protection

- ZVS + Fuse

Fuses
0679L0375-05

xl7005
LV5144RGYR

https://www.digikey.de/short/83bbnbjn (buck 75V)

|                   | Vin(max) | Iout(max)          | eff (80Vin, 150mA) |                                                                                                                                                       |
|-------------------|----------|--------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| TPP00031-ES1R     | 100      | 300 mA             |                    |                                                                                                                                                       |
| LMR38010FDDAR     |          |                    |                    |                                                                                                                                                       |
| RAA2118034GP3#JA0 | 80       | 300mA (3.3V fixed) | 70%   (3.3Vout)    | [PDF](https://www.renesas.com/en/document/dst/raa211803-805-datasheet?r=25449141)                                                                     |
| LM5009A           | 95       | 300                | 78%  (10Vout)      | [PDF](https://www.ti.com/lit/ds/symlink/lm5009a.pdf)                                                                                                  |
| LM5169/8          | 120      | 650/300            | 77%                | Sync, Fly-Buck™ [PDF](https://www.ti.com/lit/ds/symlink/lm5168.pdf)                                                                                   |
| XL7005            | 70       | 500                | 64% (15Vout)       | [PDF](http://www.ksmcu.com/pdf/XL7005%20datasheet.pdf)                                                                                                |
| MP4541            | 80       | 800                | ~75%  (10Vout)     | [PDF](https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MP4541GN/document_id/9688/) |
| LM5164            | 80       |                    | 84                 | [PDF](https://www.ti.com/lit/ds/symlink/lm5164.pdf)                                                                                                   |                                                                           
| LM5163            | 100      | 500                | 82                 | [PDF](https://www.ti.com/lit/ds/symlink/lm5163.pdf)                                                                                                   |
| XL7015            | 100      | 300                | 70                 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2409271802_XLSEMI-XL7015E1_C73013.pdf)                                                            |
| XL7005            | 80       |                    | 60                 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1811081614_XLSEMI-XL7005A_C50848.pdf)                                                             |
| TX4139            |          |                    | 75%                |                                                                                                                                                       |
| LM5116            | 100      |                    |                    |                                                                                                                                                       |
| LM5007            | 80       | 700                | 79%                |                                                                                                                                                       |

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

