
# Design Principles

Keeping it simple, minimum number of components
Only 2 layer PCB so this can be made at home
Not using too small SMD components, mostly 0805
Using TO220 switches for the buck for easy maintenance
Keeping it dense. This reduces parasitic L and R.


Using 2 Input electrolytic for longer life-time, less heat and higher efficiency.



# Compared to the original design:
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
- Out-source 3.3V and 12V power-supply
- Out-source programmer
- Improved voltage and current sense PCB Design (voltage divider & filter caps close to ADC)



# PCB Design Notes
* Current sense: INA226 datasheet https://www.ti.com/lit/ds/symlink/ina226.pdf#page=30
* Current sense: INA226 datasheet https://www.ti.com/lit/ds/symlink/ina226.pdf#page=30

# Schematics Design Notes
* Current sense filtering https://www.ti.com/lit/ds/symlink/ina226.pdf#page=14

TI: Fundamentals of MOSFET and IGBT Gate Driver Circuits https://www.ti.com/lit/ml/slua618a/slua618a.pdf?ts=1691532999585


# Mosfets
- HS don't use CDS19505
- Q_rr


# Coils
- Choose inductivity L (link TODO)
- Choose core geometry (toroids have low stray inductance) and size (depends on power needs). Choose core materials. Sendust aka KoolMu is a good choice. It is an alloy powder, composite of metal and plastic, distributed air gap.
  - toroid sizes that make sense: T130, T184, T225/T226
  - sendust has high saturation current, so T130 works. however, wire diameter is limited because it just doesn't fit through
  - smaller cores have smaller A_l value, so need more turns => more copper loss
- Choose wire gauge and strands (consider DC loss and skin effect)
- Compute num windings with A_L value and target L
- Designers: [micrometals](https://www.micrometals.com/design-and-applications/design-tools/inductor-designer/)
- The bigger the better (usually)
- Wire easier to cool than core. Power loss ratio core/wire: 20/80 [micrometals core design considerations](https://www.micrometals.com/design-and-applications/core-design-considerations/#inductor-design-basics)
- Higher initial permeability increases A_L, reduces num windings, moves loss from wire to core

- Sendust Toroid 60u - 125u



- T184 (OD=1.84in/46.7mm) 125u A_l=281 https://www.semic-shop.de/ljf-t184-s-125a-bk-de/
- 17-20 turns of 5xAWG15 (1.45mm)
- T225 / T226 (OD=2.25in/57.15mm)

# Materials
* Sendust (black, power supply, 10,5kGauss)
* Super Sendust (PV inverter, 12kGauss
* Sendust Plus
* Neu FLUX


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
* IR2104 has a rated output current of 290mA, which is suitable for 33ohm or 47ohm gate resistors. For power >500W this is a bit slow.
* IR2184 has 1.9A. still can still be a bit weak, causing voltage bounce at the driver output
* 2ED2748S01G 


# Eff Opt
* use thermal imager and start with the components that produce the most heat
* cheap caps with higher ESR can get hot (especially C_in). Find better caps, place caps in parallel to reduce ESR
* Check coil core material loss in datasheet. Use bigger core.
* Use thicker copper wires. To reduce AC losses (skin effect) use multiple strands in parallel
* Reduce switching times: smaller gate resistors, stronger driver. Make sure there is no severe ringing at switching node and at the gates. Consider using a faster Misfit (low Qgd, low t_rise, low Qrr)
* Place Schottky diode in parallel to LS switch
* Use a second HS switch in parallel (with separate gate drive resistor)
* Use short & wide PCB traces, maybe 4-layer PCB.
#


# Current Sensor
Reject Noise
* 50hz inverter
* 39 kHz pwm
* 380Hz Power supply


# IR2184 and TK6R8A08QM
I want the charger to be efficient, small and without a fan. No fan and high efficiency is both reducing loss. Si Mosfets waste most of the energy during switching. The faster the switching, the less energy is wasted. Need high gate drive current, because the gate is like a capacitor. For simplicity and safety, want a driver with dead-time, Infineon strongest driver from the IR series is IR21x4, almost 2 A current. Considering power level of 800W. Choose a fast MOSFET with low Qg and Qrr.


# Snubber
* C0G caps are more temperature stable than X7R.
* Resistor should handle 2W power


* Load output

