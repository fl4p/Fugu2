# Gate driver

IR2104 delivers 130 mA / 270 mA.
a pin-compatible replacements are:

| MPN                                                        | Vr   | I        | inputs  |
|------------------------------------------------------------|------|----------|---------|
| TI LM2104                                                  | 107  | 0.5/0.8A | HIN/SD* |
| [EG2104](https://www.lcsc.com/product-detail/C186697.html) | 600  | 2A       | HIN/SD* |
| EG3114                                                     | 600V | 4A       | HIN/LIN |


eg micro drivers: https://www.egmicro.com/products/filter_drive?category_id=28

# HS Switch
using fetlib those parts have a the lowest loss (40khz, Vin=72, Vout=27, Iout=22A, rgTotal=4.7Ω):
- IPP055N08NF2S (80V, Ploss=2.2W)
- PSMP050N10NS2 (100V, Ploss=2.3W)
- IPA050N10NM5S (100V, Ploss=2.3W)

# LS Switch
- TODO