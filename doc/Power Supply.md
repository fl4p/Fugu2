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

|                   | Vin(max) | Iout(max)          | eff (80Vin, 150mA) |                                                                                   |
|-------------------|----------|--------------------|--------------------|-----------------------------------------------------------------------------------|
| TPP00031-ES1R     | 100      | 300 mA             |                    |                                                                                   |
| LMR38010FDDAR     |          |                    |                    |                                                                                   |
| RAA2118034GP3#JA0 | 80       | 300mA (3.3V fixed) | 70%   (3.3Vout)    | [PDF](https://www.renesas.com/en/document/dst/raa211803-805-datasheet?r=25449141) |
| LM5009AMMX/NOPB   | 95       | 300                | 78%  (10Vout)      | [PDF](https://www.ti.com/lit/ds/symlink/lm5009a.pdf)                              |
| LM5169            | 120      | 650                | 77                 | Sync, Fly-Buck™                                                                   |
| LM5168            | 120      | 300                |                    |                                                                                   |
| XL7005            | 70       | 500                | 64 (15Vout)        | [PDF](http://www.ksmcu.com/pdf/XL7005%20datasheet.pdf)                            |

Diodes

- DFLS1100