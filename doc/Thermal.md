

we can compute device power loss if we know the temperature at a given point in the device and its thermal resistance to
the heat source and ambient, and the ambiet temperature.


lets assume a solid aluminium block. somewhere inside this block there is a heat source, and a temperature sensor.
for simplicity, we assume that the thermal resistance of the metal is much smaller than the metal-to-air resistance,
so we assume a homogenous temperature within the material. position of the heat source and temp sensor don't matter
any more, surface temperature equals heat source temperature.

Heat is transferred from metal to air in 3 ways: (heat-sink-design-for-thermal-analysis.pdf)
https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=F51974C9A6D544F1A7D8F119514B67FF
- air conductivity 26.02 mW/m (@22°C, 1bar) (https://www.engineeringtoolbox.com/air-properties-viscosity-conductivity-heat-capacity-d_1509.html)

- 
- https://www.heatsinkcalculator.com/blog/how-to-calculate-the-temperature-rise-in-a-sealed-enclosure/
- https://www.heatsinkcalculator.com/enclosure_temperature_rise_calculator.html

[1] R Simons, “Simplified Formula for Estimating Natural Convection Heat Transfer Coefficient on a Flat Plate”, in: Electronics Cooling, Issue: August 2001


Toshiba offers CFD (CFD (Computational Fluid Dynamics))

# Tools
- https://explore.partquest.com/
- https://www.poweresim.com/calculator.jsp
- https://www.heatsinkcalculator.com/

# Sensors

- P3T1755DPZ
- MC74A5-33SNTR
- SHTC3 (Temp + Humidity
- MVH4004D