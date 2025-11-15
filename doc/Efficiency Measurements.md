# Power-loop test rig

I build this test rig to test & measure DC-DC converters.
It is powered by a 27V, 3A power supply and uses a boost converter to create a higher voltage.
This voltage is then fed into the buck DUT, and the output of the buck is fed back into the boost input.
This way we can test converters up to 1000W, with only ~60W of supply and without any super expensive bi-directional
power supplies.

The boost runs in forced PWM mode for good voltage stabilization. Additional we can put 1 or 2 isolated power modules
(such as the BMR6852300/001) to decouple the inputs and outputs. Without isolation, any ground-side current measurement
will be just garbage. The isolated modules will probably inject some noise, which can affect precision measurements.

PWM signals of the boost and the DUT should be synchronized, otherwise any clock drift can cause significant
current noise.

* Supply power: 27V
* High voltage output (source): 15 ~ 80V
* Low voltage input (sink): 12 ~ 60V
* Max current: 38A
* Max power: 1000W

![img.png](img.png)

* DUT: ftall
    * high-side switch: 2p IPA050N10NM5S
        * gate drive: 4.7R
    * low-side switch: 2p ???
    * coil: core: 2 stack MS184075, 14 turns, 9 strands, 1.8mm copper wire coil
* voltage sensors: 2x isolated INA228
    * gain and offset calibrated, reference: HP3458A
    * estimated INL<10ppm
* current sensors
    * LV (output): Danisense DS200ID DCCT (2 primary turns) + HP3458A (reference)
    * HV (intput): Riedon RSN20-50 + INA228 (calibrated gain and)
        * forced air cooled
        * linearity calibrated with 2nd order polyfit
        * gain and offset calibrated
        * estimated INL<100ppm

* Vin=71.5 Vout=27.1 Iout=29.1A
    * efficiency: 98.12% (+-0.02% uncertainty)
    
    

