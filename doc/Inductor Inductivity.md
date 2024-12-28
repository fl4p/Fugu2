# Inductivity value

* Todo formular
* Lower inductivity -> higher ripple -> more loss in other components
* Lower inductivity needs faster OC response

# Finding the coil

Designing the coil is a multi-target optimization between size, cost, efficiency.

[TI AN-1197](https://www.ti.com/lit/an/snva038b/snva038b.pdf) gives an overview of inductor current waveform
characteristics and how to estimate L for given converter requirements. It covers inductor energy handling capabilities
and power loss.

Micrometals has a
good [primer to inductor design](https://www.micrometals.com/design-and-applications/core-design-considerations/#inductor-design-basics).

## Design Approach

* Choose switching frequency
    * if space and weight don't matter its good to start low at a 40 kHz
    * going below 20 kHz increases risk of audible coin whine
    * higher frequencies increase switching loss. placing another transistor in parallel
      usually does not decrease switching loss, since slight production variances will cause one switch to take the full
      transient (it always decreases conduction loss)
    * if you can't find a coil design that fits weight, cost (copper+core) or space constraints: increase switching
      frequency
* With input voltage, output voltage and output current requirements and the switching frequency compute the minimum
  inductivity for a given ripple current. A good design has a coil ripple current in the range 0.25 - 0.5 at full load.
    * Effects of higher ripple current:
        * causes higher voltage ripple at the output
        * increases inductor core loss
        * emits increased EMI
        * increases control fet turn-off switching stress
* With the computed inductivity and current requirement, you can try to find off-the-shelve inductors. if you don't find
  any, its time to roll your own. Micrometals has an excellent designer to help you find the core material, core
  geometry and winding. [DC guide](https://www.micrometals.com/design-and-applications/software-guide/#DC-Inductor)
    * consider ID window area. for 2 strands the designer appears to estimate the window usage too low, so the wires
      would not fit in reality
    * if you only find inductors too big or too heavy, increase the switching frequency

# Materials

Material selection is a trade-off between core loss, price and saturation robustness.
Care must be taken about temperature dependency of A_l and core saturation.

|                | micrometals | KDM          | mag-inc |   |
|----------------|-------------|--------------|---------|---|
| Sendust        | MS          | KS           | KoolMµ  |   |
| Optimized Loss | OC          | KAH Nanodust | 79      |   |
| Optimized Eco  | OE          | KNF Neu Flux |         |   |
| High Flux      |             |              |         |   |

MPP: low core loss
high flux: slightly lower loss than sendust. applications with high DC-bias current. limited choices

* [Micrometals Materials](https://www.micrometals.com/products/materials/)
* [KDM - Material Overview & Crossreference ](https://semic.cz/!old/files/pdf_www/Ljf_KDM.pdf)
* [Powder Core Materials Properties](https://www.cwsbytemark.com/mfg/sendust.php)

## Sendust

* much lower core loss than iron powder
* a little more expensive than iron powder
* very high saturation level
* lower permeability: https://www.micrometals.com/design-and-applications/core-design-considerations/#inductor-losses
    * reduce ac flux density and core loss
    * increase in copper loss due to more windings

## choosing µi

Notice that µi is the initial permeability. Effective permeability might be much lower, depending on DC bias current
(DC magnetization force) and the material's characteristic DC bias curve.

- A_L ~ µ so higher µ needs less turns, less copper loss (or smaller core, less space) for same inductivity value
- Bpk does not depend on µ
- higher µ increases /or decreases Ipp (same core geometry and number of turns)
- a core with a smaller µ can have a higher Ldc at high DC bias current
- higher µ reduces core loss (although Ipp increases) TODO or increases
- higher µ cores saturate earlier
- lower Ipp means lower core loss *and* lower copper loss (P~I2R)
- a higher µ usually means lower light-load efficiency (and higher eff at high-load)
- a higher µ with same winding does usually not increase Ldc
- if you have a core with hight µi and you are not satisfied with the dc bias performance, stack cores
- big cores with ⁄

for an application with Idc=30A, 75V/30V µ <= 125 appears to be a good choice.

# Off-the-shelf inductors

many off-the-shelf inductors have flat wire winding for decreased ESR. with optimal copper/air ratio manufactureres
can make coils with different inductance values but the ESR and package size.
despite the heavy price tag, it might be useful to take a look what coils are available on digikey.
this way you can learn about whats physically possible, the data-sheet contain useful information
and might even give a clue about expected core loss.

https://content.kemet.com/datasheets/KEM_LF0051_SHBC.pdf

* SHBC Series (Fe-Si-Al)
  SHBC24N-2R1B0039V 30 39 21.2 6.8 50 2.1 x 2 Parallel 135
  SHBC24W-2R1B0065V 30 65 40.7 6.2 50 2.1 x 2 Parallel 217
* why does the 65uH parts has a lower ESR?
* price100: $12

| MFR       | MPN             | px100 | L | DCR | Isat10/20/30 | DC bias 30A                                                        |
|-----------|-----------------|-------|---|-----|--------------|--------------------------------------------------------------------|
| würth     | 7443763540470   |       |   |     |              |                                                                    |
| codaca    | CPEX4141L-500MC | $25   |   |     | ?/?/44A      | 90% https://www.codaca.com/Private/pdf/CPEX4141L.pdf               |
| coilcraft | AGP4233-223ME   |       |   |     |              |                                                                    |
| itg       | L201316Q-470MHF |       |   |     |              |                                                                    |
| KDM       | KS184125A       |       |   |     |              | https://www.kdm-mag.com/uploads/file/20200930/1601429594941622.pdf |

[digikey](https://www.digikey.de/short/vhjtjb2n)

core size vs ripple https://www.richtek.com/Design%20Support/Technical%20Document/AN009#Ripple%20Factor
![img_5.webp](img/img_5.webp)

# Tools

# MicroMetals Inductors 66Vin/27V/33A

Iripple=8.76A

2stacked:
OC-157090-2 https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=buck66V-27V-33A-2s&inductor_type=D&l=46.4&iavg=33&vin_rms_min=39&vin_rms_max=27&f_switching=40000&ambient_temp=40&max_temp_rise=40&temp_rise=0.5&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=5&full_ratio=0.45&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=16&strandsxawg=5xAWG%2314&partnumber=OC-157090-2&awg=13

## Toroid Cores

|                     | µ  | Al  | OD   | Height |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|---------------------|----|-----|------|--------|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| OC-134090-2         | 90 | 153 | 33mm | 18mm   | 50µH: 15N,5xAWG#14(d=1.6mm)<br/>        | https://datasheets.micrometals.com/OC-134090-2-DataSheet.pdf                                                                                                                                                                                                                                                                                                                                                                                      |
| OC-132060-2         | 60 | 65  | 33   | 12     |                                         | https://datasheets.micrometals.com/OC-132060-2-DataSheet.pdf                                                                                                                                                                                                                                                                                                                                                                                      |
| Ljf T132-AM-090A GK | 90 | 97  | 33   | 12     |                                         | https://www.semic.info/ljf-t132-am-090a-gk-en/                                                                                                                                                                                                                                                                                                                                                                                                    |
| OC-199090-2         |    |     |      |        |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| OC-184125-2         |    |     |      |        |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| OC-184090-2         | 90 | 184 |      |        | 3.4W loss @ 50uH, 30Adc, V=45/30, 50khz | https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=30&vin_rms_min=45&vin_rms_max=30&f_switching=50000&ambient_temp=40&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=6&full_ratio=0.75&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=18&strandsxawg=6xAWG%2314&partnumber=OC-184090-2&awg=14 |
|                     |    |     |      |        |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

MS-250147-2
T184-S-075A BK (MS-184-S-07A)
T184-AH-125A BU

2s MS-184-S-125

https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=55&iavg=30&vin_rms_min=45&vin_rms_max=30&f_switching=50000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=6&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=85&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=19&strandsxawg=6xAWG%2314&partnumber=OC-184090-2&awg=14

### T184 Designs

DC-DC operating point: 26Adc, 45/30Von/off, 60khz

* OC-184125-2 2.6W (1.1 +
  1.5W), [analyzer](https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=6&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=16&strandsxawg=6xAWG%2314&partnumber=OC-184125-2&awg=14)
* **OC-184090-2 2.6W** (1W +
  1.6W), [analyzer](https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=6&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=17&strandsxawg=6xAWG%2314&partnumber=OC-184090-2&awg=14)
* MS-184090-2
  3.5W () [analyzer](https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=5&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=22&strandsxawg=5xAWG%2314&partnumber=MS-184090-2&awg=14)
* MS-184125-2 3.4W
* 2s MS-184125-2
  2.8W  https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=11&full_ratio=0.75&min_awg=16&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=12&strandsxawg=11xAWG%2316&partnumber=MS-184125-2&awg=16

# 2stack T132 Designs

* MS-132090-2: 4.6W (1.8 + 2.7W) N=15
* MS-132125-2: 4.6W
* OC-132090-2: 3.6W (1.1 + 2.5W) N=17
* OC-132125-2: 3.7W (1.5+2.2)(KDM: KAH130-125A , 5.5€)

# T134 Designs

26Adc, 45/30Von/off, 60khz

* OC-134090-2 5.1W (0.6W +
  4.5W), https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=3&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=26&strandsxawg=3xAWG%2314&partnumber=OC-134090-2&awg=14
* 2S OC-134090-2 3W (1 +
  2W) https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=5&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=14&strandsxawg=5xAWG%2314&partnumber=OC-134090-2&awg=14
* OC-134125-2
  3W  https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=5&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=14&strandsxawg=5xAWG%2314&partnumber=OC-134090-2&awg=14

# T199

*

MS-199125-2 https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=27&f_switching=60000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=9&full_ratio=0.75&min_awg=16&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=17&strandsxawg=9xAWG%2316&partnumber=MS-199125-2&awg=16

* OC-199090-2, 2.3W

# T250

* MS-250147-2
  2.3W https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=11&full_ratio=0.75&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=14&strandsxawg=11xAWG%2314&partnumber=MS-250147-2&awg=14
  * 13T https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=40&iavg=30&vin_rms_min=45&vin_rms_max=27&f_switching=50000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=10&full_ratio=0.5&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=13&strandsxawg=10xAWG%2314&partnumber=MS-250147-2&awg=14

SP-226090-2H305
1.8W https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=10&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=12&strandsxawg=10xAWG%2314&partnumber=SP-226090-2H305&awg=14

SP-292090-2
1.5W https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=22&full_ratio=0.85&min_awg=14&pct_win_fill_max_e=75&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=14&strandsxawg=22xAWG%2314&partnumber=SP-292090-2&awg=14

# References

* [TI AN-1197](https://www.ti.com/lit/an/snva038b/snva038b.pdf)
* [Powder Core Materials Properties](https://www.cwsbytemark.com/mfg/sendust.php)
* [KDM - Material Overview & Crossreference ](https://semic.cz/!old/files/pdf_www/Ljf_KDM.pdf)
* "Induktivitäten in DC-DC
  Wandlern" https://wfm-publish.blaetterkatalog.de/frontend/mvc/catalog/by-name/ELE?catalogName=ELE2415D
* [Micrometals Core Design Considerations](https://www.micrometals.com/design-and-applications/core-design-considerations/#inductor-losses)
* Core Manufacturers
    * [Micrometals](https://micrometals.com/) (dist [tme](https://www.tme.eu/))
    * [KDM](https://www.kdm-mag.com/) (dist: [semic](https://www.semic.info/))
    * Coilcraft
    * Mag-inc
    * [Chang Sung Corp](https://changsung.com/)

# Coils

Choosing the inductor is a trade-off between size and power loss. Larger cores have a larger A_L value, requiring
less copper wire (turns) for the same inductivity (note: L = A_L * N^2) and reducing i2r loss.
Core loss is ~ f^a * B^b * Ve  (Steinmetz equation)
(f = frequency, B = peak flux density in gauss, Ve = eff. core volume, a = const. b = const)

with B = V*t/A (V = voltage per turn, t = pulse width, A = core area)
and f = 1 / (2*t), V = Vl/n, keeping non-inductor parameters const.:
Pcore ~ Ve/(n*A)^b x

# https://www.cwsbytemark.com/CatalogSheets/MPP%20PDF%20files/13.pdf

A well designed inductor has a core/copper loss ratio of
20/80 ([micrometals](https://www.micrometals.com/design-and-applications/core-design-considerations/#inductor-design-basics)).

If we design under this assumption, a bigger core is always better, because it reduces copper wire length.

https://www.mouser.com/pdfDocs/Coilcraft_inductorlosses.pdf
https://www.psma.com/sites/default/files/uploads/tech-forums-magnetics/presentations/is17-core-loss-modeling.pdf
https://www.cwsbytemark.com/CatalogSheets/MPP%20PDF%20files/13.pdf
https://www.mag-inc.com/design/design-guides/powder-core-loss-calculation
"Transformer and Inductor Design Handbook"

Higher switching frequency reduces turn-on time, so we can use a smaller inductivity while maintaining an inductor peak
current below core saturation.

For the 30A MPPT application, a switching frequency of 40-60 kHz turns out to be practible.
With higher frequency, switch loss increases, so we would need to decrease switching times, which often requires a very
dense,
integrated design. PCB with more than 2 layers is common. Hardware becomes less maintainable.
And we don't have a tight space and weight requirements. With 40 kHz and the given voltage and current requirements
an inductor with at least 50uH is needed.

Off-the-shelve inductors exists for 30A output current, but mostly with inductivity < 20uH and they are
pricy.

So we opt to build our own induutor.

## Inductivity

- Choose inductivity L (link TODO)
    - lower inductivity, higher ripple current
    - higher voltage -> steeper current slope -> need higher inductivity
    - consider max flux density and prevent core saturation

## Core Geometry

- toroids have low stray inductance but a hard to wind.
- PQ-Core

## Core Size

- Depends on the power needs and switching frequency
- The Bigger the better
    - reduces flux density and core loss (but higher copper loss)
    - less thermal issues
    - but: more expensive, need more space
- toroid sizes that make sense: T130, T184, T225/T226
- You can easily stack toroidss

## Geometry

- Choose core geometry and size (depends on power needs). Choose core materials.
  Sendust aka KoolMu is a good choice. It is an alloy powder, composite of metal and plastic, distributed air gap.

    - sendust has high saturation current, so T130 works. however, wire diameter is limited because it just doesn't fit
      through
    - smaller cores have smaller A_l value, so need more turns => more copper loss
- Choose wire gauge and strands (consider DC loss and skin effect)
- Compute num windings with A_L value and target L
- Designers: [micrometals](https://www.micrometals.com/design-and-applications/design-tools/inductor-designer/)
- The bigger the better (usually)
- Wire easier to cool than core. Power loss ratio core/wire:
  20/80 [micrometals core design considerations](https://www.micrometals.com/design-and-applications/core-design-considerations/#inductor-design-basics)
- Higher initial permeability increases A_L, reduces num windings, moves loss from wire to core

- Sendust Toroid 60u - 125u


- T184 (OD=1.84in/46.7mm) 125u A_l=281 https://www.semic-shop.de/ljf-t184-s-125a-bk-de/
- 17-20 turns of 5xAWG15 (1.45mm)
- T225 / T226 (OD=2.25in/57.15mm)

T130

- a single T130 with A_l=61 needs a lot of windings
- stack 2 cores to reduce windings by 2^.5. for same inductivity
- using 2 strands of 1.8mm wire (140cm length each) works
- TODO test cores:
    - Ljf T130-S-125A BK
    - Ljf T130-S-075A BK
    - Ljf T130-NF-125A BR

# Materials

three opt spots: saturation vs loss vs costs

* Sendust (black, power supply, 10,5kGauss)
* Super Sendust (PV inverter, 12kGauss
* Sendust Plus
* Neu FLUX

## Advantages of bigger cores

- bigger volume => less magnetic flux density (TODO: replace volume with Ae?)
- more surface => better cooling
- usually higher A_l => need less windings
    - less copper loss due to reduced length **and** thicker wires
- can fit thicker wires and/or more strands

## disadvantages

- more loss, scales proportional to core size (TODO source)
- cost, size, weight

https://www.micrometals.com/design-and-applications/material-selection-application/

## Coil designs

* T184 sendust (u_i=125, A_L=281)
* N=17
* 5xAWG15 (d=1.45mm) or 3x (d=1.9mm)
* 130cm wire length for 17 turns on T184 (17 * 65mm)

Strands Formular: d_b = (d_a**2 * n_a/n_b)**.5 # d_b = diameter, n_b = num strands

# FEMM

# 60 Khz

* MS-184125-2, N17, AWG14, 1stack, 5strands (30A, 45/30V: Ipp=9A, Ploss=3.8W)
* MS-184090-2 N22

# Core Suppliers

+ semic
+ https://www.cwsbytemark.com/index.php?main_page=index&cPath=206_220&page=1&sort=field&sortby=data6&sortorder=a
    + only a few cores up to T184 (good selection)
+ https://www.spulen.com/ferrite-iron-powder-cores/toroids/micrometals.html?___store=english&___from_store=english

# Soldering Litz wires

<img src="img.png" width=300 />

https://www.e-magnetica.pl/doku.php/litz_wire

# Specific Cores

|      | Al     | OD     | ID | HT | mat          | µi | Micrometals | KDM | Mag-Inc                                                                                             |   |   |
|------|--------|--------|----|----|--------------|----|-------------|-----|-----------------------------------------------------------------------------------------------------|---|---|
| T184 | 139 nH | 46.7mm |    |    | KoolMu Ultra | 60 |             |     | [DK](https://www.digikey.de/en/products/detail/magnetics-a-division-of-spang-co/0070439A7/22033014) |   |   |



CSC Winding Table
![img_1.png](img_1.png)
from https://mrccomponents.com/images/downloads_csc/pdf/OD467.pdf

CSC Shapes
https://mrccomponents.com/en/products/material-core-materials-csc/toroidal-cores/highflux




**Wire**

To eliminate (reduce) ac resistance loss, choose a copper wire with d=1.2mm and multiple strands.
This decreases the resistance rise due to skin and proximity effects. It is also easier to wind than a thick 2.5mm
single
strand coils.

Make sure the copper you buy is made for electrical coils or motors. This is commonly referred as *W210 (Grade 2)*,
*DIN EN 60317-13*, *V180* or *IEC 60317-51*  and has a typical conductivity of 58.5 MS/m.
Another commonly traded copper wire material is *CW024A*, *2.0090*, *C12200*, *Cu-DHP* or *C106*.
This copper is intended for use with low demands on electrical conductivity, e.g. water/gas pipes. Expect this to
have an increased resistivity by 28% as compared to the W210 copper.

**Core Material**

Chose sendust with initial permeability 60µ, 75µ, 90µ or 125µ.
Materials with higher permeability tend to suffer from increased dc bias saturation (i.e. inductivity drop) and
increased light-load loss. Use micrometals designer to find the right core for a given load condition.

[Overview](https://semic.cz/!old/files/pdf_www/Ljf_KDM.pdf)
http://shindokogyo.com/products/toroidalCore
https://www.cwsbytemark.com/mfg/sendust.php
https://mhw-intl.com/products/magnetics/csc-powder-cores/

|                                                                                                    | apps                              | Alloy    | Bsat/Gs | loss | µi      | Micrometals   | KDM                                                    | mag-inc                 |   |   |
|----------------------------------------------------------------------------------------------------|-----------------------------------|----------|---------|------|---------|---------------|--------------------------------------------------------|-------------------------|---|---|
| Sendust  <br/>Cost eff. low loss                                                                   |                                   | Fe-Si-Al | 10000   | 1    | 25~125  | MS (14~160µi) | [KS](https://semic.cz/!old/files/pdf_www/Ljf_KS.pdf)   | KoolMµ                  |   |   |
| Fe-Si, Mega Flux<br/>improved DC bias perf.                                                        | buck/boost, solar, high-end       | Fe-Si    | 16000   |      | 14~90   | FS FluxScan   | [KSF](https://semic.cz/!old/files/pdf_www/Ljf_KSF.pdf) | 78 Series XFLUX (X)     |   |   |
| High Flux<br/>best DC bias perf.                                                                   |                                   | Fe-Ni    | 15000   | <1   |         | HF, GX        | KH                                                     | 58 Series High Flux (H) |   |   |
| Neu Flux, Optimized Economy<br/>Lowest Cost, half loss than Fe-Si. Cheap replacement for High Flux |                                   |          | 16000   | ~.5  | 26~xx90 | OE            | KNF                                                    |                         |   |   |
| Nanodust, SenMax<br/>audibly quiet, MHz operation                                                  |                                   |          | 13000   |      |         | SM            | KAM                                                    |                         |   |   |
| Nanodust                                                                                           |                                   |          |         |      |         | OC            | KAH                                                    |                         |   |   |
| MPP  <br/>lowest loss, highest temp. stability                                                     | high Q, aero, mil, med, high temp | Ni-Fe-Mo | 8000    |      | 26~550  |               |                                                        |                         |   |   |

**Core Shape**

Toroids have least leakage flux and are good choice.
Use two stacked T132 cores (1 core is only suitable for power below ~400W).

| T184 | OD     | ID     | HT   | A_e     | l_e    | Wa      | V       | CSC                                                                   |    |   |   |
|------|--------|--------|------|---------|--------|---------|---------|-----------------------------------------------------------------------|----|---|---|
| T184 | 46.7mm | 24.1mm | 18mm | 1.99cm2 | 10.7cm | 4.27cm2 | 21.4cm3 | [OD467](https://mrccomponents.com/images/downloads_csc/pdf/OD467.pdf) |    |   |   |
|      |        |        |      |         |        |         |         |                                                                       |    |   |   |

Use T184 for currents up to 30A. Micrometals: MS-184090-2, KDM: ???.

| Core                | Wire           | Num Strands | Turns | L0   | Rdc | Rac@50kHz | notesl    |
|---------------------|----------------|-------------|-------|------|-----|-----------|-----------|
| 2 stack MS-184125-2 | AWG17 (⌀1.2mm) | 10          | 12    |      |     |           | up to 35A |
| MS-184125-2         |                | 12 AWG 16?  | 10    |      |     |           |           |
| MS-184090           |                | 40          | 15    |      |     |           |           |
| 2 stack MS-130060-2 |                | 20?         | 21    | 55µH |     |           |           |




Fugu1 T134 20A Inductor
- 25 turns, 3x1.45mm, MS-134075-2
https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=40&iavg=20&vin_rms_min=45&vin_rms_max=27&f_switching=39000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=1&wire_strands=3&full_ratio=0.45&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=25&strandsxawg=3xAWG%2315&partnumber=MS-134075-2&awg=15
