
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