esp32 has wifi. we will need usb mostly for dev, jtag, hw config. system integration through usb is rather uncommon and usb hosts usually have bluetooth.
we can also put the esp32 i host mode and use a female connector for usb sticks etc.
to keep things simple & small, we chose for a 2.54 4-pin header connector (TOOD JST?)

the USB connector enables
- flashing/programming and serial console
- JTAG debugger
- USB mass storage, otg, host
board can read usb sticks or emulate one
TODO: feed vbus into PV inp? 
if we manage to get 20v 5A, the board can be a usb-c powered charger, power supply
- usb type c can (no PD) 15 W at 5 V / 3 A

TODO> have CC1 and CC2 NOT CONNECTED to each other, like RPI issue, see https://hackaday.com/2023/01/04/all-about-usb-c-resistors-and-emarkers/


to keep things simple, maybe just add another 4pin header, +5V, GND, D- D+ 
the extension board can then implement usb-connector (type C has many different footprint), protection diodes, resistors, even PD? 