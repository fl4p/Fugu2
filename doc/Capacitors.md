MLCC have can have poor DC bias performance, resulting capacity drop of around 80% at 80V (100V rated voltage).

https://docs.google.com/spreadsheets/d/1vxxJvD4m8UsKfiyYFJieKQtYqnGDK7agQkgYiSCFPeM/edit?usp=sharing

* X7S (and C0G ?) has lower DC-bias capacitance drop
    * good for snubbers, input caps

Electrolytic
Cin:

* (Fugu Metal)

https://www.ti.com/lit/ug/tiduej8c/tiduej8c.pdf#page=13

![img_3.webp](img/buck-cin.webp)

https://www.ti.com/lit/pdf/slyt670

|                          |      |      |     |      | 80V dc-bias |                                                                                                   |
|--------------------------|------|------|-----|------|-------------|---------------------------------------------------------------------------------------------------|
| murata GRM32EC72A106KE05 | 10uF | 100V | X7S | 1210 | -86%        | [link](https://www.murata.com/en-global/products/productdetail?partno=GRM32EC72A106KE05%23)       |
| tdk C5750X7S2A106K230KB  | 10uF | 100V | X7S |      | 2.22uF      | [link](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A106K230KB) |
| tdk CKG57NX7R2A106M500JH | 10uF | 100V | X7R |      | 3.6uF       | 5mm MEGACAP!  expensive                                                                           |
|                          |      |      |     |      |             |                                                                                                   |

tdk has a good parametric search
https://product.tdk.com/de/search/capacitor/ceramic/mlcc/list#ref=characteristic&1a_dcbias%5Bt%5D=80&1a_dcbias%5Bl%5D=1&1a_dcbiasc_f%5Bt%5D=0.15&1a_dcbiasc_t%5Bt%5D=1&1a_dcbiasc_t%5Bl%5D=1.00E-06&_l=100&_p=1&_c=2el_dcbias_meas-2el_dcbias_meas&_d=1&_106=1

[Digikey aluminium elec. caps D=16mm](https://www.digikey.de/short/dhw78pnf)

# Electrolytic Parts

See parts datasheet for rated ripple current. Manufacturers usually specify it at 100khz, 105°C.
You'll usually find impedance as well, which gives you an idea how much power lost in the capacitor.

Beryl 100V 470µF D16xL26mm (LCSC
C365811) https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_BERYL-Electronic-Tech-RC100M471LO16-26TH-2A1E_C365811.pdf

- 100khz ripple current: 1.9A
- generates more heat than rubycon equivalent

rubycon PX: https://www.digikey.de/en/htmldatasheets/production/1059592/0/0/1/16px100mefc5x11
rubycon https://www.rubycon.co.jp/wp-content/uploads/catalog/aluminum-catalog.pdf
samyoung NXA https://www.samyoung.co.kr/download/new/NXA.pdf

* ZL low imp.
    * ZLH long life
        * ZLJ high ripple
        * ZLQ mini (up to 35V)
            *

rubycon ZLJ:

| mfr           | cap  | v   | D  | L    | ripple @100khz | imp@20°C/100khz | px100  | MPN                |
|---------------|------|-----|----|------|----------------|-----------------|--------|--------------------|
| rubycon PX    | 470µ | 100 | 16 | 26   | 1.06           | <60mΩ  ?        |        |                    |
| nichicon HE(M | 470µ | 100 | 16 | 36   | 1.9            | 45mΩ            |        |                    |
| rubycon ZLH   | 470  | 100 | 16 | 31.5 | 2.4@100khz     | 33mΩ            |        |                    |
| rubycon ZLJ   | 470  | 100 | 16 | 31.5 | 2.65           | 32mΩ            | $1.5   |                    |
| rubycon ZLJ   | 470  | 100 | 18 | 25   | 2.5            | 36mΩ            | $1.3   |                    |
| BERYL RC      | 470  | 100 | 16 | 26   | 1.98           | 60mΩ            |        |                    |
| samyoung NXA  | 470  | 100 | 16 | 31.5 | 1.85           | 32mΩ            |        |                    |
| Chengx KM     |      | 100 | 16 | 25   | 0.918          |                 |        |                    |
| Chemi-Con KZN | 560  | 100 | 18 | 26.5 | 2.75           | 27mΩ            |        |                    |
| Chemi-Con KZN | 680  | 100 | 16 | 35.5 | 3.15           | 20mΩ            | 1.05 € | EKZN101ELL681MLP1S |

