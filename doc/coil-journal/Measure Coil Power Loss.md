# Power Loss

## Temperature Rise

- with the thermal resistance to ambient and the part temperature we can calculate power loss
- if thermal resistance is unknown, generate known heat power in the part
    - for coils you can simply use dc current
- if heating the part is not possible, put it in an enclosure with known thermal resistance to ambient and measure
  temperature rise inside the enclosure. note that this might increase the operating temperature if the part


## i(t)*v(t) method
- measure coil current and voltage
- i(t) * v(i) = p(t)
- cycle mean p(t)

parts might have large voltage swings, to acquire an accurate power voltage measurement needs to have a low offset and low
linearity error (coils, mosfets). the voltage probe need to have good CMRR.
current measuring can be done with hall sensors.

https://www.tek.com/en/documents/application-note/circuit-measurement-inductors-and-transformers-oscilloscope
https://www.tek.com/en/datasheet/advanced-power-measurement-and-analysis

x-y mode oscilloscope

- picoscope!
- B-H curve

https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_application/pdfs/Working-with-acquired-waveform-data-in-Python_ac_en_3683-5700-92_v0100.pdf


# Net Loss Method

put the part in circuit where you know the other losses or keep them as low as possible.
e.g. for a coil you can use a highly efficient GaN half-bridge, and keep capicator loss low




# Measurement Results:
![img_1.png](img/coil-loss-ranking.webp)
coils with total converter efficiencies.
measured with ftall, 72vin/27vout P=~800W
[detailed measurement log](../../HW%20Stories/ftall.md)