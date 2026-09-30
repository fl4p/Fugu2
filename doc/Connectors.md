# MCU board

During prototyping and testing the MCU might get damaged (over-voltage, faulty currents, water).
Once the ESP32-WROOM is soldered to the PCB, it is tricky to remove on the field without the right tools.

For a break-out connector, we need at least these signals:

1. GND
2. 3.3V
3. ADC Vin
4. NTC
5. Half Bridge SD
6. Half Bridge HIN
7. Half bridge LIN
8. Bflow SD
9. SDA
10. SCL
11. ALERT
12. LED


- 2.54mm pitch might be too clunky
- 1.27mm appears to be a good fit
- via-less solution preferred (SMD pin headers)
- programmer interface and USB on external board

https://www.digikey.com/en/products/category/rectangular-connectors/2027

https://www.lcsc.com/product-detail/Female-Headers_HOAUC-2343U-240CNG1MNT01_C343632.html
https://www.lcsc.com/product-detail/Female-Headers_Yxcon-F136-1104S3CMUB2_C20071191.html

Samtec SSM-107-L-SV

USB-C

Standing https://www.lcsc.com/product-detail/USB-Connectors_XUNPU-TYPEC-303-ACP16_C720628.html
SMD https://www.lcsc.com/product-detail/USB-Connectors_SHOU-HAN-TYPE-C-16P-QTGM027_C2681552.html

PD-chip HUSB238 (https://kicanvas.org/?github=https%3A%2F%2Fgithub.com%2Fblinken%2Fpower-rail-probe)

# Power Connectors, Lugs

* preferably cross-head (Phillips) screws
* connectors with 51A or 65A have good wire gauge
  https://ihiconnectors.com/PCB-Technical-Information.htm#B2A-B2C-PCB
  https://www.digikey.de/en/products/filter/terminal-blocks/wire-to-board/371
  https://www.digikey.de/en/products/detail/amphenol-anytek/VP0285850000G/4957853
  https://www.digikey.de/en/products/detail/altech-corporation/MV-1002/9457249

Terminal Lug
CBS35-36-C
![lug.webp](img/lug.webp)CB35-36-CY
CXS35-36-C

https://lugsdirect.com/single-wire-lugs.htm


# Standards
- UEXT
- Pmod https://digilent.com/reference/_media/reference/pmod/pmod-interface-specification-1_2_0.pdf

![img.png](connector-pmod.png)
10 pin, 1.27mm pitch, SMD


from https://www.renesas.com/en/document/mae/ek-ra2l1-v1-users-manual?r=1398391 ::
1. Two Seeed Grove® system (I2C/Analog) connectors
2. SparkFun® Qwiic® connector
3. Two Digilent Pmod™ (SPI and UART) connectors
4. Arduino™ (Uno R3) connector
5. MikroElektronika™ mikroBUS connector

# External comms port (VE.Direct, JST-PH 4)

J5 on the ExtPort sheet is a JST PH 2.0 mm, 4-pin header in VE.Direct pinout
(1 GND, 2 RX, 3 TX, 4 V+). Design: `plans/ext-comms-port.md`.

JST makes the header through-hole and SMD. DigiKey.de prices, excl. VAT, checked 2026-09-30:

| Part | Mounting | 1 | 10 | 100 | 500 | 1000 | DigiKey stock |
|---|---|---|---|---|---|---|---|
| **S4B-PH-K-S** (on J5) | THT, side entry | €0.13 | €0.109 | €0.092 | €0.082 | €0.079 | 42,598 |
| S4B-PH-SM4-TB | SMD, side entry | €0.56 | €0.473 | €0.401 | €0.358 | €0.341 | 56,057 |
| B4B-PH-SM4-TB | SMD, top entry | €0.57 | €0.477 | €0.405 | €0.362 | €0.344 | 27,048 |

Bürklin lists S4B-PH-SM4-TB at about €0.45 for 5 and €0.39 for 200. All three mate the
same PHR-4 cable housing.

KiCad stock footprints:
- `Connector_JST:JST_PH_S4B-PH-K_1x04_P2.00mm_Horizontal` (on J5)
- `Connector_JST:JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal`
- `Connector_JST:JST_PH_B4B-PH-SM4-TB_1x04-1MP_P2.00mm_Vertical`

J5 stays through-hole:
- The SMD part is about 4x the price, roughly +€0.28 per board at 500.
- The SMD part is held only by its pads and two solder tabs. A cable pulled or levered
  at the board edge loads those pads; the THT pins go through the board.
- Going SMD only pays if J5 is the last through-hole part on the board.
