we can estimate the losses with a SPICE simulation.
Carefully looking at the currents and voltages at the mosfets we can indentify conduction loss P_rds, switching loss
P_sw, reverse recovery loss P_rr, self turn-on loss P_sto, and dead-time loss P_dt.



## LT Spice
LTSpice comes with a visual editor
- can load PSpice libraries


## pyspice
- use kicad schematic editor to create netlist
- or http://geda-project.org/
- macos: `brew install geda-gaf`
sudo port install ngspice