# Power Conversion Efficiency Optimization

To improve conversion efficiency we first need to understand where power is lost and quantify it.
For quantification we can model power loss or measure it.
There is plenty of literature about modeling power loss in a DC-DC converter.
[fetlib](https://github.com/fl4p/fetlib) can model switch loss, inductor loss and capacitor loss.

Literature: [TI slvaeq9](https://www.ti.com/lit/an/slvaeq9/slvaeq9.pdf) TODO more

The are multiple ways for power loss measurement:

- Measure temperature rise of components using a thermal imager or thermal probe. This will give you can idea where
  most power is lost. If you know the thermal resistance between a component and ambient, you can calculate the power
  loss in watts.
- Measure total converter power loss using power two power meters, one at the input and one the output.
- Measure component loss using a multimeter (static i2r loss)
  or [oscilloscope](https://www.tek.com/en/documents/application-note/circuit-measurement-inductors-and-transformers-oscilloscope).
  Needs careful probe calibration and de-skew.

Some points to consider:

* main losses are usually switch loss and inductor loss
* measure coil ripple current. dc core saturation can lead to significant inductance drop and extreme current peaks,
  increasing loss in capacitors and switches.
* Check coil core material loss in datasheet. Use bigger core.
* Use inductor design tool, such as
  the [micrometals designer](https://www.micrometals.com/design-and-applications/design-tools/inductor-designer/)
* Use multi strand wires to reduce AC losses (skin effect, proximity effect)
* cheap caps with higher impedance can get hot (especially C_in). Find better caps, place caps in parallel to reduce ESR
* Reduce switching times: smaller gate resistors, stronger driver. Make sure there is no severe ringing at switching
  node and at the gates. Consider using a faster Mosfet (low Qsw)
* Place Schottky diode in parallel to LS switch. this can decrease reverse-recovery loss
* LS cascode of 2 MOSFETs (an additional low-voltage MOSFET) can help decreasing reverse-recovery effects
* Use a second HS switch in parallel (with separate gate drive resistor)
* Use short & wide PCB traces, maybe 4-layer PCB.




# Advanced topics
* negative Voff (there is a simple circuit using a capactor and a diode TODO)
* LS cascode for Qrr relief
* staged/framed switching
* todo zener clamp over bootstrap C ?