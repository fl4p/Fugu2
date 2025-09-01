
MMPT Charger for residual applications.
- cost efficient
- not too heavy
- wireless RF interface


In our MPPT application we target batteries of 12, 24 and 48 V (nominal).
This the effective output voltage range is 10 ~ 59V.

Standard residual solar panels have open-circuit volages between 16 and 40 V.
-> Buck topo


For a power MOSFETS 80 V, 100 V, 120 V, 150 V, 200V
We pick 80 V.

For 2x 450W panels and a 24V battery we should accept currents up to 40A.

Hi
* improves panel matching and partial shading performance
* incresed failure safety 
* conversion ratios closer to 1 means higher efficiency
* convential microcontrollers (with RF) have limited PWM precision
* GaN usually needs >2-layers design (+cost)
  * fast switching requires good gate drive design
  * 

GaN?

GaN 

dsPIC33



Hihgher:
One of the most important design objective of DC-DC converters is conversion efficiency.
The higher the eff. the lower the power loss reducing the need of cooling.

Varying load points (operating point, working point) should be considered in thermal design
and component selection. If we want to optimize total efficiency across the whole working range
we measure would use the weighted average.

For compact designs with thermal it might be sufficient to just evaluate the highest load point.
