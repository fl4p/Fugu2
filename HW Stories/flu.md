
# flu

As-built config (parts, gate drive, Cin, coil): [dcdc-tools `loss/examples/flu.yaml`](https://github.com/fl4p/dcdc-tools/blob/main/loss/examples/flu.yaml)

FETs:
- HS: 2x IPP050N10NF2S at Q1, Q3 (TO-220, metal tab = drain = Solar+)
- LS: 1x IPP022N12NM6 in the D9 land, gate wired to Q2.1; Q2 empty

Gate drive:
- HS on: R4/R6 4.7Ω
- HS off: R5/R7/D1 not fitted
- LS: R10 4.7Ω

coil:
1s KDM-K184-125 3strands 1.8mm
* 17 turns
* 2.76mΩ (DMM6500 4W)
* L0=83µH

Caps:
- Input:
  - 1x rubycon ZLH 470u 100v
  - 1x ChemiCon KZE 560uF
  - 1x ChemiCon KZE 680uF

Heat sink: 100x100x18mm aluminium 


![img_3.png](img_3.png)

## 2026-10-11: Q3 screw short, ESP32 dead

- The Q3 (HS) mounting screw touched copper on the front side. Bench PSU, 1.1 A current limit.
- Result: ESP32 dead. Gate driver U1 is not yet checked.
- Cause: the screw is at Solar+ through the metal tab. On the front side, the screw head
  covers U1's input-side pads, measured from the hole centre:
  - U1.4 GNDI: 2.60 mm
  - U1.5 DIS/SD (= GPIO47): 2.72 mm
  - U1.3 VCCI (+3.3V): 2.84 mm
  - R1 (DT/GND): 2.8–3.0 mm
  - C2 (+3.3V/GND): 3.1 mm

  An M3 head has about a 2.75 mm radius and a washer about 3.5 mm, so it reaches all of these.
  Which pad was actually hit has not been confirmed. Look for a mask scratch or burn mark.
- 1.1 A is far beyond what any pin clamp can take, and DZ1 (SM2T3V3A) cannot clamp a DC source.
- To check or replace: U2 ESP32, U1 (replace even if it still switches), DZ1 (likely failed
  short), R1, C2, and the rest of the +3.3V rail (U5 AP3012, U6 AS333, U7, U8, D2 WS2812B).
- Mitigation: insulate the Q1 and Q3 screws with a shoulder washer under the head. Next layout:
  move U1 out from under the screw head and keep copper at least about 4 mm from the hole
  centre on both layers.