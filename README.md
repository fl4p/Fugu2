Links: [github](https://github.com/fl4p/Fugu2) | [cadlab](https://cadlab.io/project/28046) | schematics | IBOM | HW dev
docs & testing

View this project on [CADLAB.io].

<img src="doc/img/fugu-metal.webp"/> <img src="doc/img/fugu2.webp" width=400 />

## Specs

* Solar voltage: 12 ~ 80V
* Battery voltage: 12 ~ 60V (LiFePo4 4s ~ 16s)
* Max battery current: 30 A

Explore KiCad project schematic and PCB at [Cadlab](https://cadlab.io/project/28046/main/files)

This is inspired by [Fugu MPPT](https://www.instructables.com/DIY-1kW-MPPT-Solar-Charge-Controller/).
The design has been optimized with real life experience, considering signal noise and EMI issues,
replaced hall sensor with shunt resistor, faster switching. See the list below for more changes.

# How to build

* order PCB (or make @home)
* assemble PCB
* build inductor
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
- Much higher 1.4 A gate drive current (previously 130mA) to reduce switching losses (less heat but more ringing)
- Introducing snubber circuit to reduce EMI and MOSFET stress
- TVS protection circuit
- off-board 3.3V and 12V power-supply
- USB break-out and off-board programmer (ESP PROG Header)
- Improved voltage and current sense PCB Design (voltage divider & filter caps close to ADC)
- Using LM5163 for power supply. XL7005A explodes at surge voltages ~80V. Seems to be vulnerable at temps >~70°C.

## Power loss reduction

* 4A gate driver UCC21330BQDRQ1 with programmable dead-time
    * fast switching (high-side)
    * optimized dead-time, reduce free-wheeling losses (low-side)
* dense half-bridge circuitry for minimum parasitic inductance
* short and min-area gate-drive tracks for minimum gate drive inductance
* low-side rectifier Schottky barrier diode to reduce free-wheeling loss and reverse-recovery loss
* cascade of input capacitors: 220nF, 1uF, 10uF, 470uF input caps to minimize capacitor ESR-loss
* optimized coil designs: R_ac considerations


# Inductor Quick Start Guide

**Wire**

To eliminate (reduce) ac resistance loss, choose a copper wire with d=0.5mm (AWG#24) with many strands.

Make sure the copper you buy is made for electrical coils or motors. This is commonly referred as "W210 (Grade 2)" or
"DIN EN 60317-13", "V180", "IEC 60317-51"  and has a typical conductivity of 58.5 MS/m.
Another commonly traded copper wire material is "CW024A", "2.0090", "C12200", "Cu-DHP" or "C106".
This copper is intended for use whithout high demands on electrical conductivity, e.g. water/gas pipes. Expect this to
have an increased resistivity by 28% as compared to the W210 copper.

**Core Material**

Chose sendust with initial permeability 60µ or 90µ.
Materials with higher permeability tend to suffer from increased dc bias saturation (i.e. inductivity drop) and
increased light-load loss.

**Core Shape**

Toroids have least leakage flux and are good choice.
Use two stacked T132 cores (1 core is only suitable for power below ~400W).

Use T184 for currents up to 30A. Micrometals: MS-184090-2, KDM: ???.

| Core           | Strands(Awg24) | Turns | L0   | Rdc | Rac@50kHz |
|----------------|----------------|-------|------|-----|-----------|
| MS-184090      | 40             | 15    |      |     |           |
| 2s MS-130060-2 | 20?            | 21    | 55µH |     |           |




# Mosfet Selection

Use fetlib for an extensive parametric search and ranking by power loss estimation.
See [Toshibas Product Guide on pg. 16](https://www.mouser.com/datasheet/2/408/toshiba%20america%20electronic%20components,%20inc._bce008-1209380.pdf#page=16).

## High Side Mosfet (HS)

- suffers from switching stress
- short switching times to lower switching losses (small Qsw) but increase potential ringing (EMI)
- low Rds_on
- body diode never conducts


## Low Side Switch (LS)
- Choose a mosfet with low Q_rr ([how to compute qrr loss](https://www.ti.com/lit/ta/ssztc00/ssztc00.pdf))
  - Qrr rises with increasing temperature, current and current transient
- low Rds_on
- low Qgd, Qgd/Qgs
- low r_g
- don't use CDS19505, better TK3R3A06PL

Current through the LS Switch always flows from source to drain (4th quadrant of their V-I plane),
which makes the gate drive signal rather irrelevant. It is much easier to switch than the HS, ringing is generally
not an issue. [gate drive fudamentals](https://www.ti.com/lit/ml/slua618a/slua618a.pdf#page=22)
Switching happens near zero voltage, as the body diode is usually already/still conducting when switching on/off.

Choose a MOSFET that is designed for synchronous rectification.
Prefer low body diode forward voltage.

# EMI
- design switch node RC snubber circuit


# General Eff Optimization

* losses in sync buck https://www.ti.com/lit/an/slvaeq9/slvaeq9.pdf
* main losses are switch loss and inductor loss
* use thermal imager and start with the components that produce the most heat
* cheap caps with higher ESR can get hot (especially C_in). Find better caps, place caps in parallel to reduce ESR
* Check coil core material loss in datasheet. Use bigger core.
* Use copper litz wires to reduce AC losses (skin effect, proximity effect)
* Reduce switching times: smaller gate resistors, stronger driver. Make sure there is no severe ringing at switching
  node and at the gates. Consider using a faster Mosfet (low Qsw)
* Place Schottky diode in parallel to LS switch
* Use a second HS switch in parallel (with separate gate drive resistor)
* Use short & wide PCB traces, maybe 4-layer PCB.


# Current Sensor

TODO

Temperature drift of components (resistor and amplifier) might be greater than accuracy of the sensor, so choose a small
burden resistor. Use large copper areas and thermal vias to increase heat dissipation.
For 30A it should be smaller than 1mOhm, e.g. 0.5mOhm . The INA226 is quite precise (16bit) but can suffer from
temperature
instability if placed close the burden resistor (and potentially any other components that heat up).
With a 1mOhm I experienced a temp drift of 80mA at about 70°C (30Amps) which is about 2W at 24V.

Reject Noise

* 50hz inverter
* 39 kHz pwm
* 380Hz Power supply

A loss-less technique to measure average output current:
Use an RC-Filter to measure average switch node voltage. With this V_sw_avg, Vo and the coil ESR we can compute the
current.
Note that copper has temp coeff a = 0.0043/°C (https://cirris.com/temperature-coefficient-of-copper/), so a temperature
change of 30°C results about 13% error. For an MPPT this is fairly enough, not for precise energy metering though.

https://sci-hub.se/10.1109/MWSCAS.2002.1186927

INA226
INA229

# IR2184 and TK6R8A08QM

I want the charger to be efficient, small and without a fan. No fan and high efficiency is both reducing loss. Si
Mosfets waste most of the energy during switching. The faster the switching, the less energy is wasted. Need high gate
drive current, because the gate is like a capacitor. For simplicity and safety, want a driver with dead-time, Infineon
strongest driver from the IR series is IR21x4, almost 2 A current. Considering power level of 800W. Choose a fast MOSFET
with low Qg and Qrr.

# Snubber

* C0G caps are more temperature stable than X7R.
* Resistor should handle 2W power


* Load output

# Scaling up input voltage

* input caps
* remove PV supply diode
* bigger inductivity
* change mosfets HS & LS V_GS(breakdown) to 150V
* voltage sense resistors

# Water Robustness Considerations

* Add a clear varnish coat to the PCB and components (especially the current sensor circuit, Supply DCDC converters)
* Choose low R_filt for the anti-aliasing filter at the current sensor (INA226) inputs to avoid destruction of the
  chip's amplifiers.
* Take extra care with installation of the 3.3V and 12V supply.
* If using a (almost) sealed enclosure (aluminium box), add a bag silica to compensate internal humidity. When the
  converter is cooling down at night it'll suck water into the enclosure. The ESP32 WROOM metallic case is not sealed.
  Consider placing a membrane? Sticker on its breathing hole.

# Board Connectors

* Solar +/- (screw terminal)
* Battery +/-
* USB 4 pin connector (2.54mm) flashing, jtag, mass storage, usb host
    * USB type-c connector (DNP)
* UEXT (SPI and I2C) for displays, additional sensors, can etc

# Sensors

- P3T1755DPZ
- MC74A5-33SNTR
- SHTC3 (Temp + Humidity
- MVH4004D

# TODO

* aluminium case dimensions
* use 2 current sense resistors in parallel
* reverse battery protection
* The metal cover ESP32-S3-WROOM can be a condensation trap in humid environments. Especially when power saving at night
  and the chip cools down.

* use 2 current sense resistors in parallel
* fugu reverse battery protection
* The metal cover ESP32-S3-WROOM can be a condensation trap in humid environments. Especially when power saving at night
  and the chip cools down.

https://yaqwsx.github.io/KiKit/latest/multiboard/#multi-board-workflow-with-kikit
