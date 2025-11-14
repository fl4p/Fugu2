# Ceramic

MLCC have can have poor DC bias performance, resulting capacity drop of around 80% at 80V (100V rated voltage).

https://docs.google.com/spreadsheets/d/1vxxJvD4m8UsKfiyYFJieKQtYqnGDK7agQkgYiSCFPeM/edit?usp=sharing

* X7S (and C0G ?) has lower DC-bias capacitance drop
    * good for snubbers, input caps

|                                 |      |      |     |      | 80V dc-bias | R@1kHz | R@50Khz | px              |                                                                                                   |
|---------------------------------|------|------|-----|------|-------------|--------|---------|-----------------|---------------------------------------------------------------------------------------------------|
| murate GRM31cr60e227            |      |      |     |      |             |        |         |                 |                                                                                                   |
| murata GRM32EC72A106KE05        | 10uF | 100V | X7S | 1210 | 1.4uF       |        | 5mΩ     |                 | [link](https://www.murata.com/en-global/products/productdetail?partno=GRM32EC72A106KE05%23)       |
| tdk C5750X7S2A106K230KB         | 10uF | 100V | X7S |      | 2.22uF      | 162mΩ  | 6.3mΩ   |                 | [link](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A106K230KB) |
| tdk CKG57NX7R2A106M500JH        | 10uF | 100V | X7R |      | 3.6uF       | 104mΩ  | 5.3mΩ   |                 | 5mm MEGACAP!  expensive                                                                           |
| tdk C3216X6S2A106K160AC         | 10uF | 100V | X6S |      | 0.8uF       |        | 4mΩ     |                 |                                                                                                   |
| yuden HMK212BC7105KGHTE (smps)  | 1uF  | 100V | X7S | 0805 | -83%        | 762Ω   | 20m     | 100 : 0,14650 € | [link](https://ds.yuden.co.jp/TYCOMPAS/ut/detail?pn=MMASH21GBC7105KTCA01&u=M)                     |
| murata GRJ21BC72A105ME11L       | 1uF  | 100V |     |      | 0.165uF     | 1.5k   | 40m     | 100 : 0,10120 € |                                                                                                   |
| yuden HMR212CC7105KG-T (bypass) | 1uF  | 100V | X7S | 0805 | -82%        | 724    | 20m     | 100 : 0,12090 € |                                                                                                   |
| yuden HMK316AC7225KL-TE (smps)  | 2.2  | 100V |     |      |             |        | 10m     | 100 : 0,16320   |                                                                                                   |

# Electrolytic

$$ C_{in} >= \frac{D \cdot (1-D) \cdot I_O}{ \Delta V_{in} \cdot f_{sw} }$$

[ref: TIDA-010042 400-W GaN-Based MPPT Charge Controller](https://www.ti.com/lit/ug/tiduej8c/tiduej8c.pdf#page=13)

How to select input capacitors for a buck converter https://www.ti.com/lit/pdf/slyt670

TDK has a
good [parametric search](https://product.tdk.com/de/search/capacitor/ceramic/mlcc/list#ref=characteristic&1a_dcbias%5Bt%5D=80&1a_dcbias%5Bl%5D=1&1a_dcbiasc_f%5Bt%5D=0.15&1a_dcbiasc_t%5Bt%5D=1&1a_dcbiasc_t%5Bl%5D=1.00E-06&_l=100&_p=1&_c=2el_dcbias_meas-2el_dcbias_meas&_d=1&_106=1)

[Digikey aluminium elec. caps D=16mm](https://www.digikey.de/short/dhw78pnf)

See parts datasheet for rated ripple current. Manufacturers usually specify it at 100khz, 105°C.
You'll usually find impedance as well, which gives you an idea how much power lost in the capacitor.

Loss is proportional to HF impedance, usually specified in the data sheet at 100 kHz.

## Rubycon

* [Rubycon Catalog](https://www.rubycon.co.jp/wp-content/uploads/catalog/aluminum-catalog.pdf)
* [Rubycon PX Series](https://www.digikey.de/en/htmldatasheets/production/1059592/0/0/1/16px100mefc5x11)

* ZL low imp.
    * ZLH long life
        * ZLJ high ripple
        * ZLQ mini (up to 35V)

## Selection

| mfr, series   | cap  | v   | D  | L    | ripple @100khz | imp@20°C/100khz | px100  | MPN                                                    |
|---------------|------|-----|----|------|----------------|-----------------|--------|--------------------------------------------------------|
| rubycon PX    | 470µ | 100 | 16 | 26   | 1.06           | <60mΩ  ?        |        |                                                        |
| nichicon HE(M | 470µ | 100 | 16 | 36   | 1.9            | 45mΩ            |        |                                                        |
| rubycon ZLH   | 470µ | 100 | 16 | 31.5 | 2.4@100khz     | 33mΩ            |        |                                                        |
| rubycon ZLJ   | 470µ | 100 | 16 | 31.5 | 2.65           | 32mΩ            | $1.5   |                                                        |
| rubycon ZLJ   | 470µ | 100 | 18 | 25   | 2.5            | 36mΩ            | $1.3   |                                                        |
| BERYL RC      | 470µ | 100 | 16 | 26   | 1.98           | 60mΩ            |        | LCSC C365811                                           |
| samyoung NXA  | 470µ | 100 | 16 | 31.5 | 1.85           | 32mΩ            |        | [pdf](https://www.samyoung.co.kr/download/new/NXA.pdf) |
| Chengx KM     |      | 100 | 16 | 25   | 0.918          |                 |        |                                                        |
| Chemi-Con KZN | 560µ | 100 | 18 | 26.5 | 2.75           | 27mΩ            |        |                                                        |
| Chemi-Con KZN | 680µ | 100 | 16 | 35.5 | 3.15           | 20mΩ            | 1.05 € | EKZN101ELL681MLP1S                                     |

