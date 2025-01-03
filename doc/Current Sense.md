# PCB Design Notes

* Current sense: INA226 datasheet https://www.ti.com/lit/ds/symlink/ina226.pdf#page=30

# Schematics Design Notes

* Current sense filtering https://www.ti.com/lit/ds/symlink/ina226.pdf#page=14

# TODO paper about

Current-sensing techniques for DC-DC converters, H.P. Forghani-zadeh et
al. https://sci-hub.se/10.1109/MWSCAS.2002.1186927

https://rincon-mora.gatech.edu/publicat/cnfs/mw02_isns.pdf

* series sense resistor
* Rds sensing
* filter-sense inductor
* ![img_6.webp](img/img_6.webp)
* ![img_7.webp](img/img_7.webp)
* ![img_8.webp](img/img_8.webp)
* ![img_9.webp](img/img_9.webp)

|         |        | DC CMRR | CMRR @50 kHz | Gain err | TempDrift | Voff  | BW     | gains   | notes                 |
|---------|--------|---------|--------------|----------|-----------|-------|--------|---------|-----------------------|
| INA281  | +110 V | 120-dB  | 65-dB        | 0.5%     | 20ppm     |       | 1.3MHz | 20..500 | cheapest TI , $1.18   |
| INA310A | 110V   | 160dB   |              | 0.15%    | 10ppm     | 20uV  | 1.3MHz | 20..500 | int. Comparator $1.53 |
| INA310B | 110V   | 160dB   |              | 0.5%     | 20ppm     | 150uV | 1.3MHz | 20..500 | int. Comparator       |
| INA169  | 60V    |         |              |          |           |       |        |         | $1.22                 |
| INA791x |        |         |              |          |           |       |        |         | internal 50A EZ-Shunt |



Reject Noise

* 50hz inverter
* 380Hz Power supply
* 39 kHz pwm

A loss-less technique to measure average output current:
Use an RC-Filter to measure average switch node voltage. With this V_sw_avg, Vo and the coil ESR we can compute the
current.
Note that copper has temp coeff a = 0.0043/°C (https://cirris.com/temperature-coefficient-of-copper/), so a temperature
change of 30°C results about 13% error. For an MPPT this is fairly enough, not for precise energy metering though.

https://sci-hub.se/10.1109/MWSCAS.2002.1186927

INA226
INA229