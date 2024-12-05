
# MCU board

During prototyping and testing the MCU might get damaged (over-voltage, faulty currents, water).
Once the ESP32-WROOM is soldered to the PCB, it is tricky to remove.

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
- via-less solution preferred
- programmer on external board


https://www.digikey.de/en/products/filter/rectangular-connectors/


https://www.lcsc.com/product-detail/Female-Headers_HOAUC-2343U-240CNG1MNT01_C343632.html
https://www.lcsc.com/product-detail/Female-Headers_Yxcon-F136-1104S3CMUB2_C20071191.html

Samtec SSM-107-L-SV

USB-C

Standing https://www.lcsc.com/product-detail/USB-Connectors_XUNPU-TYPEC-303-ACP16_C720628.html
SMD https://www.lcsc.com/product-detail/USB-Connectors_SHOU-HAN-TYPE-C-16P-QTGM027_C2681552.html


# Power Connectors
* preferably cross-head screws
* connectors with 51A or 65A have good wire gauge
https://ihiconnectors.com/PCB-Technical-Information.htm#B2A-B2C-PCB
https://www.digikey.de/en/products/filter/terminal-blocks/wire-to-board/371
https://www.digikey.de/en/products/detail/amphenol-anytek/VP0285850000G/4957853
https://www.digikey.de/en/products/detail/altech-corporation/MV-1002/9457249