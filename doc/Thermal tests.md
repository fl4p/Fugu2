Condition:
- Vin: 61V
- Vout: 26V
- Ambient Temp: 24-25 C
- Heatsink: 160 x 83 x 25 AK-EL83-160
- 2p TK6R8A08QM (ir2184 and 22r gate drive)
- Coil: 2 stacked sendust cores T130 (KDM KS130-060A), 19.5 turns, 1x1.8mm wire


## lying on wood
![Fugu 2](../img/fugu2-2T130-heatsink.webp "Fugu2")

![Fugu 2](img/TR000132-fugu2-T130.JPG "Fugu2 T130 heat image")
*^the coil get very hot^*

* Average Power 760W
* heatsink equilibrium temp: 51 C


## in a cardbox
![Fugu 2](../img/fugu2-cardbox.jpg "Fugu2 in cardbox")

* avg power: 470W
* heatsink equi temp: 61 C


## T180 Coil
* 15.5 turns, 2x1.8mm wire
* avg power (in the card box): 483W  (+13W than with other coil)

![Fugu 2](img/TR000135-fugu2.JPG "Fugu2 in cardbox")
*^ No forced cooling ^*


![Fugu 2](img/TR000137-fugu2-fan.JPG "Fugu2 Fan cooled")
*^ Cooled with a fan ^*




# Thermal meltdown
* running for an hour, Vin=75V, Vout=27, Iout=32A
* on 10x10 cm heatsink


temperature measured with TMP117 attached to heatsink:
![img_2.png](../../../../../dev/pv/fugu-mppt-doc/img_2.png)
* the HS melted at arround 00:28
* not sure what happend at 00:08
* i adjusted the output power manually to keep the temperature at 80°C, which worked for 40minutes
* then temperature dropped, and increased. 

![img_3.png](../../../../../dev/pv/fugu-mppt-doc/img_3.png)

