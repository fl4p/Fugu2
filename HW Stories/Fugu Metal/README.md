fugu metal in a aluminium case

G107-IP67 Gehäuse 125x80x40mm Alu-Spritzguss-Gehäuse IP67 https://www.ebay.de/itm/163117581325
Computed Thermal Resistance (40mm height, 100cm2 area) https://www.omnicalculator.com/physics/thermal-resistance
https://www.heatsinkcalculator.com/heat-sink-thermal-resistance-calculator.html
R = 0.016547 K/W

Alloy Thermal Conductivity: 110 - 120 130 - 160
W/mK https://www.bopla.de/technische-daten/technische-informationen/materialinformationen-aluminium/eigenschaften-von-aluminiumlegierungen

Input Caps

- 2x Beryl 100V 470µF D16xL26mm (china)
- 2x 10UF 100V X7S 2220 (TDK C5750X7S2A106K230KB) 2.2uF @
  80V [dc-bias](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A106K230KB)
- 2x 1uF 100V X7R 1206 (TDK C3216X7R2A105K160AA)
- 2x .22uF 100V X7S 0603 (TY HMK107C7224)

Inductor / Coil

* Core: 2x stacked KS130-060A (33.8mm * 2x11.6mm)
    * sendust toroidal core from [semic-shop](https://www.semic.info/ljf-t130-s-060a-bk-en/)
        * micrometals equivalent: MS-132060-2 (optimized OC-132060-2)
        * https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=26&iavg=26&vin_rms_min=45&vin_rms_max=27&f_switching=40000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=2&full_ratio=0.75&min_awg=13&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=19&strandsxawg=2xAWG%2313&partnumber=MS-132060-2&awg=13
    * Al=61nH, BSAT=1050 mT (per Core)
    * f33.83xf19.30x11.61mm
* Wire: 2 strands of 1.8mm (AWG#13) copper, 140cm (with σCu=58 we compute ESR=4.7mΩ)
    * turns=19.5 Turns
* Computed Inductivity = 2*61nH * 19.5^2 = 46.4 uH

Optimizations:

* Use OC with higher µ: OC-132090-2 @26Aout  : 6.3W -> 5.2W Coil Loss (4cu,1.1 Core)
  https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=26&iavg=26&vin_rms_min=45&vin_rms_max=27&f_switching=40000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=2&full_ratio=0.75&min_awg=13&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=19&strandsxawg=2xAWG%2313&partnumber=OC-132090-2&awg=13
* increase f_sw from 40khz to 60khz:
    * OC-132090-2 loss: 5.2W ->  4.7W. (3.9W cu loss)
      * 4.3W https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=50&iavg=26&vin_rms_min=45&vin_rms_max=30&f_switching=60000&ambient_temp=30&max_temp_rise=50&temp_rise=1&min_l=40&part_type=A&winding=F&num_cores=2&wire_strands=3&full_ratio=0.45&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=20&strandsxawg=3xAWG%2314&partnumber=OC-132090-2&awg=14
    * reducing turn from 19 to 17: 4.5W
    * with MS-132090-2: 5.4W

Snubber: C0805C222K2GEC7800 2.2nF 200V C0G

- the aluminium enclose is a humdity trap
- wifi connection with the ESP32-WROOM-1 (PCB antenna) still possible `WiFi.rssi()` returns -88 ~ -80

- gate driver ir2184
- LS gate drive resistor 15ohm
- HS gate charge resistor 22 dis: 5ohm

HS: 2p TK6R8A08QM
LS switch [FDP027N08B]()

left it outisde at night it was raining
suced water inside. found water on the pcb and chips
ESP32 metal shield looks oxidated. Have problems to communicate with INA226 and external IC2 display whic i connected
for testing.

Sometimes it worked, sometimes not. I could see the device in the battery current graph turning on and off.

I heated the PCB with a hear dryer for some minutes but it didnt help. Now my idea is to turn on WiFi so the ESP32
generates some heat that will eventually evaporate the water from the inside.
THe only problem was, I didn"t have the right firmware version at hand (my laptop died 2 weeks ago),
so before flashing a new firmware that enables the WiFi hardware, I tried to create a flash dump with esptool.py (
read_flash).
That didn't work, it just didn't start to download after it uploaded the stub.

Next effort: try to run a binary from RAM
https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/advanced-commands.html#load-ram
esptool.py --no-stub load_ram ./test/images/helloworld-esp8266.bin

* validate image with image_info

October 2024:

- recovered some firmware code from backups
- replaced the ESP32S3 chip, and the charger was running again
  the 2nd day at 14:00 it ran into power-derating at 600W, 75°C. After a periodic sweep it took some time until current
  calibration passed (temperature drift), but it failed to start the conversion again. I found the 10V power supply
  XL7005A chip to be smoked, including the IR2184 gate driver. replaced both, successful test run at 20V. then 75V solar
  input, after 30 seconds noticed some weird data on serial console about when the INA226 alert pin interrupt was
  set-up. then a little explosion near the 3.3V power supply. now the other XL7005A burned, killing the ESP32S3. need to
  use a better chip, e.g. LM5163 .

Some log lines from that day, picked at different hours:

```
19°C ambient:
V=68.20/25.57 I= 3.5/ 9.04A 240.8W 30°C 124sps  0kbps PWM(H|L|Lm)= 791|1243|1243 MPPT(st= MPPT,1) lag=67.3ms N=92158 rssi=-84
V=66.97/26.89 I= 6.2/14.95A 412.6W 45°C 124sps  0kbps PWM(H|L|Lm)= 867|1168|1168 MPPT(st= MPPT,1) lag=67.3ms N=110781 rssi=-79
V=63.66/27.43 I= 8.8/19.89A 562.2W 70°C 123sps  0kbps PWM(H|L|Lm)= 933|1102|1102 MPPT(st= MPPT,1) lag=10023.8ms N=45069 rssi=-79
V=63.26/27.50 I= 9.4/21.06A 598.6W 74°C 124sps  0kbps PWM(H|L|Lm)= 938|1097|1097 MPPT(st= MPPT,1) lag=10023.8ms N=110973 rssi=-86
de-rating:
V=63.43/27.50 I= 9.5/21.18A 600.5W 75°C 124sps  0kbps PWM(H|L|Lm)= 936|1099|1099 MPPT(st=   CP,1) lag=10023.8ms N=115814 rssi=-82
V=67.70/27.33 I= 7.9/19.05A 536.9W 76°C 124sps  0kbps PWM(H|L|Lm)= 877|1158|1158 MPPT(st=   CP,1) lag=10023.8ms N=136672 rssi=-83

```

the sweep before the 10V power supply burnt

* todo: why not re-starting mppt after sweep? and controlMode=0 (st=N/A)

```
V=66.52/27.22 I= 8.4/19.96A 560.2W 75°C 124sps  0kbps PWM(H|L|Lm)= 889|1146|1146 MPPT(st= MPPT,1) lag=10023.8ms N=151197 rssi=-81
I (56831968) mppt: periodic zero-current calibration
I (56831971) mppt: Start sweep
I (56831974) mppt: Start calibration
I (56831977) sensor: U_in_raw reset calibration
I (56831979) sensor: Io reset calibration
I (56831983) sensor: U_out_raw reset calibration
I (56832003) store: Wrote /littlefs/stats (size 32)
I (56832006) flash: Wrote flash value /littlefs/stats
PWM disabled (duty cycle was 888)
I (56832333) sampler: Sensor U_in_raw calibration: avg=77.4220 std=0.003713
I (56832339) sampler: Sensor Io calibration: avg=0.1864 std=0.001848
I (56832342) sampler: Sensor Io midpoint-calibrated: 0.186386
I (56832351) sampler: Sensor U_out_raw calibration: avg=26.7787 std=0.000010
I (56832354) sampler: Calibration done!
V=77.52/  nan I= nan/  nanA   nanW 75°C  0sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=0 rssi=-87
buck: CCM -> DCM (vr=0.9900, pwmMaxLs=0.0, lsCCM=2047)
Backflow switch disabled
V=77.27/26.70 I=-0.0/-0.10A  -2.7W 76°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=495 rssi=-82

I (56838317) main: received serial command: ''
I (56838320) main: unknown or unexpected command
V=77.21/26.70 I=-0.0/-0.12A  -3.3W 77°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=990 rssi=-84
V=77.18/26.69 I=-0.0/-0.14A  -3.8W 77°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=1488 rssi=-86
V=77.21/26.68 I=-0.1/-0.15A  -4.1W 77°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=1984 rssi=-88
V=77.44/26.67 I=-0.1/-0.16A  -4.3W 77°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=2480 rssi=-88
V=77.10/26.67 I=-0.1/-0.16A  -4.5W 77°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=2976 rssi=-88
V=77.35/26.67 I=-0.1/-0.17A  -4.7W 76°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=3472 rssi=-85
V=77.24/26.66 I=-0.1/-0.17A  -4.8W 76°C 164sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=3967 rssi=-84
V=77.24/26.66 I=-0.1/-0.18A  -4.9W 76°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=4464 rssi=-81
V=77.27/26.65 I=-0.1/-0.18A  -5.0W 76°C 165sps  0kbps PWM(H|L|Lm)=   0|   0| 123 MPPT(st=  N/A,1) lag=10023.8ms N=4961 rssi=-81
```


# V2
- Caps
  - the beryl cap is poor, high impedance
  - https://www.digikey.de/short/b9pp4zc5
  - KYOCERA REF1625471M100B has 45mΩ with 16mm.
  - maybe change to 18mm caps
    - chemi con EKZN101ELL561MM25S
    - ruby con 100ZLJ470M18X25 (18mm dia)
- Inductor
  - OE-130090-2 https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=35&iavg=26&vin_rms_min=27&vin_rms_max=42&f_switching=50000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=33&part_type=A&winding=F&num_cores=2&wire_strands=3&full_ratio=0.45&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=19&strandsxawg=3xAWG%2314&partnumber=OE-130090-2&awg=14
  - SM-130060-2 (KAM* nanodust, Ljf T130-AM-060A-E14 GK) https://www.micrometals.com/design-and-applications/design-tools/inductor-analyzer/?name=&inductor_type=D&l=35&iavg=26&vin_rms_min=27&vin_rms_max=42&f_switching=50000&ambient_temp=40&max_temp_rise=40&temp_rise=1&min_l=33&part_type=A&winding=F&num_cores=2&wire_strands=3&full_ratio=0.45&min_awg=14&pct_win_fill_max_e=55&energy_cost=0.2&continuous_use=0.5&conductor_material=Cu&n=19&strandsxawg=3xAWG%2314&partnumber=SM-130060-2&awg=14
  - 2s HS-130060 (58071A2-2)
    - 19Turns, 1.18mmCu, 5strands
  - 2s GX-130125-2
    - 15/16 turns, 1.18mmCu 6strands
    - got 18 turns (L0=90µH with 6strands), very tight!
      - micrometals analyzer with 16,8AWG says ID use=0.47 (for awg17=0.44)

- Switches:
  - Low: IPP022N12NM6AKSA1 (gdrv: 4.7R) and  ST15100S Trench MOS Schottky Rectifier (SMD)
  - HS: 2x IPP040N08NF2SAKMA1 (gdrv: 4.7R, discharge: 4.7R/2)