# fheat1

<img src="../doc/img/fugu2.webp" width="600"/>

fugu2 board mounted on heat-sink

## heat-sink

- 160 x 83 x 25 AK-EL83-160 from [ebay](https://www.ebay.de/itm/145019865089)
- 6.6 °C/W ? ( [heatsinkcalculator](https://www.heatsinkcalculator.com/heat-sink-size-calculator.html) )
- TODO epc calc

## Coil

```
15 Turns, 2 Strands, d=2mm?
L0 = 126µH
```

## Inductor Core

* [Ljf T184-S-125A BK](https://www.semic-shop.de/ljf-t184-s-125a-bk-de/)
* Material: KS (Sendust, Micrometals:MS, Magnetics:77 Series Koolµ(K))
* µ = 125
* A_L = 281 nH/
* DØ = 47.63 mm , D1 = 23.32 mm , H = 18.92 mm
* Micrometals Equivalent: MS-184125-2
* [Micrometal Analyzer Tool](https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=30&vin_rms_min=45&vin_rms_max=30&f_switching=40000&ambient_temp=40&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=2&full_ratio=0.90&min_awg=12&pct_win_fill_max_e=100&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=15&partnumber=MS-184125-2&awg=12)
    * 6W loss @ 30Adc, 75Vin, 30Vout, f=40khz

**MS-184090-2 vs. OE-184090-2**

* OE has higher Ipp (MS Ipp=13A, OE=11A)
* OE has higher Ldc (MS 41uH, vs OE=35uH )
* MS has lower loss (2.1 vs 2.7)
* MS is cheaper (1.3 vs 1.6)
