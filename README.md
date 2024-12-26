Links: [github](https://github.com/fl4p/Fugu2) | [cadlab](https://cadlab.io/project/28046) | [docs](doc/) | schematics |
IBOM | HW dev | firmware
[additional documentation & resources](https://github.com/fl4p/fugu-mppt-doc)

## Gallery

| <img src="doc/img/fugu-metal.webp" width=400/> | <img src="doc/img/fugu2.webp" width=400 /> |
|:----------------------------------------------:|:------------------------------------------:|
|           Small aluminium enclosure            |                on heatsink                 |

| <img src="doc/img/fheat2.webp" width=400 /> | <img src="img/fisi.webp" width=400 /> |
|:-------------------------------------------:|:-------------------------------------:|
|                                             |      [fisi](HW Stories/fisi.md)       |

## Specs

* Solar input voltage: 12 ~ 80V (higher voltage configurations possible, please create an issue if you need help with
  component selection)
* Battery output voltage: 12 ~ 60V (LiFePo4 4s ~ 16s)
* Max battery current: 32 A
* Efficiency
    * Vin=72 Vout=27 Iout=32A: 98.17% (measured with INA228 & Riedon
      SSA-100, [smart-shunt](https://github.com/open-pe/smart-shunt-fw))

This is inspired by [Fugu MPPT](https://www.instructables.com/DIY-1kW-MPPT-Solar-Charge-Controller/).
The design has been optimized with real life experience, considering signal noise and EMI issues,
replaced hall sensor with shunt resistor and faster switching. See the list below for more changes.

## How to build

* order PCB (or make @home)
    * 1x `Fugu2.kicad_pcb`
    * 2x `psu/buck100.kicad_pcb` (one for 3.3V and one for 12V)
    * 1x `mcu-head/Fugu2-esp32s3-wroom-head.kicad_pcb` (optional. alternatively place the ESP32(-S3) directly on the
      Fugu2 board)
* assemble PCBs
* build inductor
    * order core and copper wire
    * wind the coil
* flash firmware

## Design Principles

* Simplicity with minimum number of components, while keeping EMI and efficiency in mind
* Only 2-layer PCB and using mostly 0805 SMD components, so this can be made at home
* Using TO220 switches for the buck for easy maintenance
* Dense PCB design to reduces parasitic L and R

## Compared to the original design:

- Multiple input caps to increase life-time, efficiency and reduced EMI
- 2 high-side switches in parallel to reduce heat and increase efficiency
- Using ESP32 ADC to sense input voltage, INA226 for bat voltage
- Using current sense resistor with INA226 (immunity against magnetic fields, less drift)
- Current sense on the battery side (less noise, can detect bat reverse current)
- Low-side current sensing because it supports up to 60V battery voltage (for 16s lifepo4 48V batteries)
- Backflow switch on battery side (bat eFuse if sth goes wrong, can safely handle a short of the high-side switches)
- Backflow switch powered by HS charge pump from the IR2184 (no extra DCDC)
- Much higher 4 A gate drive current (previously 130mA and 1.4 A) to reduce switching losses
- Introducing RC snubber circuit to reduce EMI and MOSFET voltage stress
- TVS protection circuit
- off-board 3.3V and 12V power-supply
- USB break-out and off-board programmer (ESP PROG Header)
- Improved voltage and current sense PCB Design (voltage divider & filter caps close to ADC)
- Using LM5163 for power supply. (XL7005A explodes at surge voltages ~80V. Seems vulnerable at temps >~70°C)

## Power loss reduction

* 4A gate driver UCC21330BQDRQ1 with programmable dead-time
    * fast switching (high-side)
    * optimized dead-time, reduce free-wheeling losses (low-side)
* dense half-bridge PCB design for minimum parasitic inductance
* short and min-area gate-drive tracks for minimum gate drive inductance
* low-side rectifier Schottky barrier diode to reduce free-wheeling loss and reverse-recovery loss
* cascade of input capacitors: 220nF, 1uF, 10uF, 470uF input caps to minimize capacitor ESR-loss
    * low impedance electrolytics
* optimized coil designs
    * optimized core flux density and core power loss
    * multi-strand coil for reduced R_dc and R_ac (considering skin & proximity effect)

# Inductor Quick Start Guide

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

|                                                                                                         | Bsat     | µi      | Micrometals   | KDM                                                    |   |   |   |
|---------------------------------------------------------------------------------------------------------|----------|---------|---------------|--------------------------------------------------------|---|---|---|
| Sendust  <br/>Cost eff. low loss                                                                        | 10500 Gs | 25~125  | MS (14~160µi) | [KS](https://semic.cz/!old/files/pdf_www/Ljf_KS.pdf)   |   |   |   |
| Fe-Si<br/>improved DC bias perf.                                                                        | 16000 Gs | 26~90   | FS            | [KSF](https://semic.cz/!old/files/pdf_www/Ljf_KSF.pdf) |   |   |   |
| High Flux<br/>best DC bias perf.                                                                        | 15000 Gs |         | HF, GX        | KH                                                     |   |   |   |
| Neu Flux, Optimized Economy<br/>Lowest Cost, half core loss than Fe-Si. Cheap replacement for High Flux | 16000 Gs | 26~xx90 | OE            | KNF                                                    |   |   |   |
| Nanodust, SenMax<br/>audibly quiet, MHz operation                                                       | 13000 Gs |         | SM            | KAM                                                    |   |   |   |
| Nanodust                                                                                                |          |         | OC            | KAH                                                    |   |   |   |

**Core Shape**

Toroids have least leakage flux and are good choice.
Use two stacked T132 cores (1 core is only suitable for power below ~400W).

Use T184 for currents up to 30A. Micrometals: MS-184090-2, KDM: ???.

| Core                | Wire           | Num Strands | Turns | L0   | Rdc | Rac@50kHz | notesl    |
|---------------------|----------------|-------------|-------|------|-----|-----------|-----------|
| 2 stack MS-184125-2 | AWG17 (⌀1.2mm) | 10          | 12    |      |     |           | up to 35A |
| MS-184125-2         |                | 12 AWG 16?  | 10    |      |     |           |           |
| MS-184090           |                | 40          | 15    |      |     |           |           |
| 2 stack MS-130060-2 |                | 20?         | 21    | 55µH |     |           |           |

# Mosfet Selection

Use [fetlib](https://github.com/fl4p/fetlib) for an extensive parametric search and ranking by power loss estimation.
See [Toshibas Product Guide on pg. 16](https://www.mouser.com/datasheet/2/408/toshiba%20america%20electronic%20components,%20inc._bce008-1209380.pdf#page=16).

## High Side Mosfet (HS)

- suffers from switching stress
- short switching times to lower switching losses (small Qsw) but increase potential ringing (EMI)
- low Rds_on
- body diode never conducts
- picks:
    - IPP055N08NF2SAKMA1 (80V 5.5mΩ Qsw=13nC)
    -

## Low Side Switch (LS)

- Choose a mosfet with low Q_rr ([how to compute qrr loss](https://www.ti.com/lit/ta/ssztc00/ssztc00.pdf))
    - Qrr rises with increasing temperature, current and current transient
    - Qrr ringing and loss can be reduced with external Schottky diode
      or [cascode configuration](https://www.researchgate.net/publication/378199983_Improving_the_Reverse-Recovery_Performance_of_Si_SJ-MOSFETs_with_a_Low-Voltage_GaN_HEMT_in_a_Cascode_Configuration).
- low Rds_on
- low Qgd, Qgd/Qgs
- low r_g

Current through the LS Switch always flows from source to drain (4th quadrant of V-I plane),
which makes the gate drive signal rather irrelevant. It is much easier to switch than the HS, ringing is generally
not an issue. [gate drive fudamentals](https://www.ti.com/lit/ml/slua618a/slua618a.pdf#page=22)
Switching happens near zero voltage, as the body diode is usually already/still conducting when switching on/off.

Choose a MOSFET that is designed for synchronous rectification. Consider switch node ringing and choose a higher voltage
fet to avoid channel break-down if needed.

# Power Conversion Efficiency Optimization

* losses in sync buck https://www.ti.com/lit/an/slvaeq9/slvaeq9.pdf
* main losses are switch loss and inductor loss
* use thermal imager and start with the components that produce the most heat
* cheap caps with higher impedance can get hot (especially C_in). Find better caps, place caps in parallel to reduce ESR
* Check coil core material loss in datasheet. Use bigger core.
* Use inductor design tool, such as
  the [micrometals designer](https://www.micrometals.com/design-and-applications/design-tools/inductor-designer/)
* Use copper litz wires to reduce AC losses (skin effect, proximity effect)
* Reduce switching times: smaller gate resistors, stronger driver. Make sure there is no severe ringing at switching
  node and at the gates. Consider using a faster Mosfet (low Qsw)
* Place Schottky diode in parallel to LS switch
* Use a second HS switch in parallel (with separate gate drive resistor)
* Use short & wide PCB traces, maybe 4-layer PCB.

# Higher input voltages

* input caps
* remove PV supply diode
* bigger inductivity to keep ripple current in a reasonable level
* change mosfets HS & LS V_GS(breakdown) to 120V, 150V or 200V
* voltage sense resistors

# Water Robustness Considerations

* Add a clear varnish coat to the PCB and components (especially the current sensor circuit, Supply DCDC converters)
* Choose low R_filt for the anti-aliasing filter at the current sensor (INA226) inputs to avoid destruction of the
  chip's amplifiers.
* If using a (almost) sealed enclosure (aluminium box), add a bag silica to compensate internal humidity. When the
  converter is cooling down at night it'll suck water into the enclosure. The ESP32 WROOM metallic case is not sealed.
  Consider placing a membrane? Sticker on its breathing hole.
