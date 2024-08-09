View this project on [CADLAB.io](https://cadlab.io/project/28046). 

# TODO
* use 2 current sense resistors in parallel
* fugu reverse battery protection
* The metal cover ESP32-S3-WROOM can be a condensation trap in humid environments. Especially when power saving at night and the chip cools down. 

This is inspired by Fugu MPPT. The design has been optimized with real life experience, for example fixed EMI issues,
replaced hall sensor with shunt resistor, faster switching. See the list below for more changes.

* Solar voltage: 12 ~ 80V
* Battery voltage: 12 ~ 60V
* Max battery current: 30 A

Explore KiCad project schematic and PCB at [Cadlab](https://cadlab.io/project/28046/main/files)

# Design Principles

* Keeping it simple with minimum number of components, while keeping EMI in mind 
* Only 2 layer PCB and not using too small SMD components, mostly 0805  so this can be made at home
* Using TO220 switches for the buck for easy maintenance
* Keeping it dense. This reduces parasitic L and R 

## Compared to the original design:

- Multiple input caps to increase life-time, efficiency and (hopefully) reduce EMI
- 2 HS switches in parallel to reduce heat and increase efficiency
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
- off-board programmer
- Improved voltage and current sense PCB Design (voltage divider & filter caps close to ADC)

# PCB Design Notes

* Current sense: INA226 datasheet https://www.ti.com/lit/ds/symlink/ina226.pdf#page=30
* Current sense: INA226 datasheet https://www.ti.com/lit/ds/symlink/ina226.pdf#page=30

# Schematics Design Notes

* Current sense filtering https://www.ti.com/lit/ds/symlink/ina226.pdf#page=14

TI: Fundamentals of MOSFET and IGBT Gate Driver
Circuits https://www.ti.com/lit/ml/slua618a/slua618a.pdf?ts=1691532999585

# High Side Mosfet

- suffers from switching stress
- short switching times to lower switching losses but increase potential ringing (EMI)
- design switch node RC snubber circuit
- Consider switching loss to be higher than i2r loss. when choosing the component, consider switching times, and reverse
  recovery characteristics of the body diode
- Driven in quadrant ?
- Choose a High-Side switch with low Q_rr (TODO src) [how to compute qrr](https://www.ti.com/lit/ta/ssztc00/ssztc00.pdf)
- Qrr rises with increasing temperature
- don't use CDS19505, better TK3R3A06PL

# Low Side Switch

Current through the LS Switch always flows from source to drain (4th quadrant of their V-I plane),
which makes the gate drive signal rather irrelevant. It is much easier to switch than the HS, ringing is generally
not an issue. [gate drive fudamentals](https://www.ti.com/lit/ml/slua618a/slua618a.pdf#page=22) 
Switching happens near zero voltage, as the body diode is usually already/still conducting when switching on/off.

Choose a MOSFET that is designed for synchronous rectification. Q_rr can be high (>200 nC).
Prefer low body diode forward voltage. CDS19505 is a suitable choice.

# Coils

## Inductivity

- Choose inductivity L (link TODO)
    - lower inductivity, higher ripple current
    - higher voltage -> higher inductivity
    - max flux (core saturation)

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

- bigger volume => less magnetic flux density
- more surface => better cooling
- usually higher A_l => need less windings
    - less copper loss due to reduced length **and** thicker wires
- can fit thicker wires and/or more strands

## disadvantages

- more loss, scales proportional to core size
- cost, size, weight

https://www.micrometals.com/design-and-applications/material-selection-application/

## Coil designs

* T184 sendust (u_i=125, A_L=281)
* N=17
* 5xAWG15 (d=1.45mm) or 3x (d=1.9mm)
* 130cm wire length for 17 turns on T184 (17 * 65mm)

Strands Formular: d_b = (d_a**2 * n_a/n_b)**.5 # d_b = diameter, n_b = num strands

# Gate Drivers

Higher gate drive current -> faster switching -> less switching losses/heat, but more EMI/ringing

* Careful with mosfet body diodes that have a high Q_rr
* Measure ringing from switch-node to GND and place snubber if needed
* IR2104 has a rated output current of 290mA, which is suitable for 33ohm or 47ohm gate resistors. For power >500W this
  is a bit slow.
* IR2184 has 1.9A. still can still be a bit weak, causing voltage bounce at the driver output
* 2ED2748S01G

# Eff Opt

* losses in sync buck https://www.ti.com/lit/an/slvaeq9/slvaeq9.pdf
* main losses are switch loss and inductor loss
* use thermal imager and start with the components that produce the most heat
* cheap caps with higher ESR can get hot (especially C_in). Find better caps, place caps in parallel to reduce ESR
* Check coil core material loss in datasheet. Use bigger core.
* Use thicker copper wires. To reduce AC losses (skin effect) use multiple strands in parallel
* Reduce switching times: smaller gate resistors, stronger driver. Make sure there is no severe ringing at switching
  node and at the gates. Consider using a faster Misfit (low Qgd, low t_rise, low Qrr)
* Place Schottky diode in parallel to LS switch
* Use a second HS switch in parallel (with separate gate drive resistor)
* Use short & wide PCB traces, maybe 4-layer PCB.

#

# Current Sensor

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
Use an RC-Filter to measure average switch node voltage. With this V_sw_avg, Vo and the coil ESR we can compute the current.
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
* 


# TODO

* use 2 current sense resistors in parallel
* fugu reverse battery protection
* The metal cover ESP32-S3-WROOM can be a condensation trap in humid environments. Especially when power saving at night
  and the chip cools down.