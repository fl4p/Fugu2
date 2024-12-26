Gate Driver ucc21330
drive voltage: 12.3V
dead-time: ?? R
LS: IPP022N12NM6AKSA1, 120V 4.7R
HqS: IPP040N08NF2SAKMA1 Gate Drive r??
    - replaced 2nd HS with IPP024N08N

## Gate Drive Times

Probes: LSgate: pcbite, HS: testec 7005, SW: pcbite

Vin=60, Vout=14, Idle
LS: gate driver tr=200ns, tf=15ns; gate: tr=690ns, tf=450ns ( 22r)

(scope capture LS: pcbite, hs: migsig 100mhz HV diff probe)
LS: gate driver tr=185ns, tf=17ns; gate: tr=280ns, tf=177ns; ( 7.5r)
HS: gate: tr=62ns, tf= (4.7R, 10.7V)

scope capture ..717: c1: l2, c3: hs migsig, c4 testec

scope capture ..820: 30Vin
..926: disconnected migsig probe
..005: @60Vin
..139: same but zoomed on HS
334 FIXED probe unit
HS: gate tr=105ns, tf=64ns @61V
HS gate tr=103ns, tf= 63ns @30V

61Vin, 54Vout, 3.6Aout, Ipp=1.27A (..944.png)
LS gate: tr=275ns tf=221ns  (c1)
HS gate: tr=11ns tf=83ns    (c3)
SWnode: tr=27ns tf=74ns     (c2)

V=62.7/56.6 I=15.4/16.6A 967.8W 25℃30℃ 461sps 0㎅/s PWM(H|L|Lm)=1904| 143| 143 st= MANU,1 lag=3430㎲ N=121601 rssi=0
(scope ..004.png) ![img.png](img.webp)
Ipp=1.76
LS gate: tr=259 tf=225ns  (c1)
HS gate: tr=67ns tf=61.5ns    (c3)
SWnode: tr=27ns tf=29ns     (c2)

2p HS:

V=72.5/27.7, I=~30A, pwmCtrl=820
LS gate: tr=260ns,tf=251ns
HS gate: tr=362/97ns
SW: tr=46/43ns

V=72.2/27.9 I=26A,
LS gate = 263/252
HS gate tr=365/99
SW: 47/46

V=70/27 I=20A
LS gate = 262/248
HS gate = 363/102
SW: 42/40

V=69.6/26.7  I=8
LS gate 246/240 
ls gate drv fall: 52ns
HS gate 354/129 HS2 gate: 253/104 
HS gate driver: 130ns rise
sw = 35/44

V=53.1/26.6  I=12,4A
LS 238/246
HS 361/136
SW 38/36x

V=68.7/26.7 I=13.2
compute LS


replaced one HS with IPP024N08N

V70/27 I=8A (pwm 820)
    HS IPP024 gate: tr=302ns tf=115
    HS  gate: tr=389ns tf=134



# HW Failures
dc 1900 -> dc 1, caused
