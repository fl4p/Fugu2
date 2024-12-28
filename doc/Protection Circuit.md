We want to protect battery terminals (with the BMS) against over voltage (OV).
Damaged MPPT chargers (with short HS mosfet) can short the SOLAR+ to BAT+. When the battery is full and the BMS OV
protection cuts the battery, battery terminal voltage will rise to solar voltage, eventually destroying a connected
load.

Clamp circuits with MOV (Varistor) or TVS supressor are out, because of our current requirement of 50 A at 24 V bat.
If this is clamped at 30V and 50A, the clamp device must desipate 1500W of heat!
A cooler solution is to cut the battery and short the MPPT output with a mosfet. This will pull down solar voltage and
power to zero.

This is a small walk through designing an (analog) circuit.

We choose N-ch power mosfet with low R(ds)on, switching times doesn't really matter.
We start with the clamp fet:

Now we put the battery fet. Note that this usually operates in reverse conduction mode, body diode on.
Leaving the fet off will not stop charging current and the voltage drop across the body diode can cause excessive heat (
which can lead to meltdown completly shorting the junction forever).

We must place a fuse in case both mosfets turn on at the same time (shoot through). The diode will likely not protect
our Mosfets from dying, it is there to prevent a fire.

We can arrange the circuit as a half-bridge:

Now we think about the voltage sense cicuit and gate driving circuits.

* Voltages of BAT and PV both range from 0-80V
* The lower fet body diode will conduct

if potential (SW) < (BAT-),  
First we find a suitable GND node for the measurement circuit, there are PV- or BAT-.
Trying PV(-):
driving the bat fet source is a bit tricky because source is below our ground.

* use an opto-coupler for turn off
* isolated dcdc for gate turn on. consider dcdc idle power. burst mode?

* However, if this opto-coupler fails, it will destroy the whole circuit

Trying BAT(-):
now it looks like a half-bridge topology. the special case is switch node below GND (when PV>bat)
LS body diode will clamp this to 1V or so.
Half bridge drivers with bootstrapping still work here. HS can stay on indefinely when there is battery voltage, becauseConsider their dead-times, maybe add gate discharge diode for
fast turn off.
Turn on of battery fet (Low-side) can be slow.
Gate driver's logic inputs are schmitt triggered and some have a programmable delay.

We chose BAT- because PV- would give us negative voltages 