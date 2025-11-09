<img src="../img/todo.webp" width="500">

- Board: Fugu HW 2.2
- Switches: (both 100V breakdown)
    - Low: 2p IPA050N10NM5S?  (gdrv: 4.7R)
    - HS: 2x  (gdrv: 4.7R, discharge: 0R)
- Inductor:
    - codacoa high sat 70µH
- Caps:
    - in: 2x Rubycon ZLH 470uF 100V 16mmx31mm (Z=33mΩ each)
    - out: 1x "




```
power loop
Isupply=2.05A
Iout=33A
V=73.8/26.10 I=xxx   xxW 68℃44℃ 443sps  0㎅/s CCM(H|L|Lm)= 786|1261|1261 st= MANU,1 lag=3126㎲ N=2080320 rssi=-50

now cold:
V=74.4/26.06 I=xxx   xxW 28℃28℃  0sps  0㎅/s CCM(H|L|Lm)= 786|1261|1261 st= MANU,1 lag=3090㎲ N=7797 rssi=0
Iout=34.4
Isupply=2.02A

```



```
eff 97.95% (std=0.000353)   loss=16.61W
   in power     812.028 W  (std 0.0255)   @ 71.519V
  out power     795.423 W  (std 0.0257)   @ 27.122V


eff 97.89% (std=0.170010,last=97.97)   loss=17.01W
   in power     788.086 W  (std 7.9790)   @ 71.578V
  out power     772.096 W  (std 8.3676)   @ 27.120V

voltage adcs: 2x ina228, isolated from each other
input current sensor: RSN20-50 with ina228 calibrated to <60ppm error with DCCT + HP3458A
output current sensor: DCCT and HP3458A .

   in power     788.620 W  (std 0.0287)   @ 71.577V
  out power     772.649 W  (std 0.0302)   @ 27.120V
eff 97.98% (std=0.000474,last=97.97)   loss=15.97W

eff 98.24% (std=0.005989,last=98.24)   loss=8.17W
   in power     465.221 W  (std 0.9677)   @ 72.299V
  out power     457.042 W  (std 0.9562)   @ 27.119V
  
  
the next day (and new ina228 chip):
eff 97.88% (std=0.013967,last=97.89)   loss=15.06W
   in power     709.154 W  (std 0.0703)   @ 73.888V
  out power     694.208 W  (std 0.0469)   @ 27.104V
  
  
eff 97.93% (std=0.001362,last=97.93)   loss=17.03W     <- yesterday it was 97.95%, so yeah so close!! (consider thermal)
   in power     821.922 W  (std 0.0713)   @ 73.950V
  out power     804.892 W  (std 0.0774)   @ 27.112V
  
  
now with the small 47u coil (lcsc):
eff 97.77% (std=0.002032,last=97.76)   loss=18.28W
   in power     818.743 W  (std 0.0407)   @ 71.434V
  out power     800.461 W  (std 0.0235)   @ 27.118V
  
after letting everything warm up and applied some forced heat to reach thermal steady state:
eff 97.69% (std=0.001544,last=97.69)   loss=18.70W
   in power     810.185 W  (std 0.0403)   @ 71.490V
  out power     791.442 W  (std 0.0350)   @ 27.126V
  
ms-184075 14T coil: TODO ripple
eff 98.12% (std=0.000000,last=98.12)   loss=15.11W
   in power     803.377 W  (std 0.0000)   @ 71.480V
  out power     788.265 W  (std 0.0000)   @ 27.121V
after warm-up:
eff 98.08% (std=0.001085,last=98.08)   loss=15.50W
   in power     805.414 W  (std 0.0607)   @ 71.524V
  out power     789.918 W  (std 0.0592)   @ 27.134V

```


```
ruishen 700 coil: (ipp=9.82A@39khz)
eff 98.03% (std=0.314417,last=97.91)   loss=16.10W
   in power     820.213 W  (std 2.4756)   @ 71.473V
  out power     803.070 W  (std 1.1517)   @ 27.133V
  
after warmup:
eff 97.88% (std=0.000539,last=97.88)   loss=17.35W
   in power     819.254 W  (std 0.0585)   @ 71.468V
  out power     801.910 W  (std 0.0560)   @ 27.127V
eff 97.87% (std=0.000305,last=97.87)   loss=17.42W
   in power     816.609 W  (std 0.0030)   @ 71.473V
  out power     799.209 W  (std 0.0038)   @ 27.126V
```

```
T184-075 with 2 big strands, 17? turns (ipp=13.86)
eff 96.51% (std=0.001071,last=96.51)   loss=28.95W
   in power     830.910 W  (std 0.3730)   @ 71.403V
  out power     801.941 W  (std 0.3624)   @ 27.119V
  
=> this coil is bad for some reason
```

```
other double strand coil KS184125A (KDM)
eff 97.92% (std=0.000000,last=97.92)   loss=17.00W      < wow this is supringly good for
   in power     816.153 W  (std 0.0000)   @ 71.483V     < a single T184 core
  out power     799.137 W  (std 0.0000)   @ 27.132V
after warm up:
eff 97.89% (std=0.001153,last=97.89)   loss=17.22W
   in power     814.696 W  (std 0.0588)   @ 71.491V
  out power     797.466 W  (std 0.0601)   @ 27.130V
```

```
"too many" turns coil (ipp=12.5A)
eff 97.79% (std=0.000000,last=97.79)   loss=18.16W
   in power     820.038 W  (std 0.0000)   @ 71.474V
  out power     801.878 W  (std 0.0000)   @ 27.139V
after warmup 2min:
eff 97.73% (std=0.000559,last=97.73)   loss=18.55W
   in power     818.913 W  (std 0.0226)   @ 71.466V
  out power     800.382 W  (std 0.0233)   @ 27.128V
eff 97.69% (std=0.000699,last=97.69)   loss=18.84W
   in power     815.913 W  (std 0.0333)   @ 71.476V
  out power     797.105 W  (std 0.0358)   @ 27.124V
```


```
2s T130-060 19 turns 13.2AWG, with "earthing" wire  ~7W loss?
eff 97.83% (std=0.000000,last=97.83)   loss=17.77W
   in power     817.746 W  (std 0.0000)   @ 71.440V
  out power     800.012 W  (std 0.0000)   @ 27.126V
warm:
eff 97.77% (std=0.005876,last=97.77)   loss=18.17W
   in power     815.107 W  (std 0.0707)   @ 71.439V
  out power     796.950 W  (std 0.0880)   @ 27.117V
  
micrometals analyzer:
Core Loss (W)	3.577
Rdc (Ω)	        0.008333                                < measured: 4.75Ω
Rac Factor	    7.921
Cu Loss (W)	    10.13
Total Loss (W)	13.71                                   < vs 18W total converter loss???, sth is wrong here)
```

```
another "unknown" 2stack T130 2strands
eff 97.81% (std=0.000000,last=97.81)   loss=17.96W
   in power     818.373 W  (std 0.0000)   @ 71.475V
  out power     800.430 W  (std 0.0000)   @ 27.135V

eff 97.76% (std=0.002451,last=97.76)   loss=18.25W
   in power     814.703 W  (std 0.1072)   @ 71.479V
  out power     796.424 W  (std 0.1213)   @ 27.129V  

```

```
another 2stack T130 1strand "dark" (high temp drift)
eff 97.31% (std=0.000000,last=97.31)   loss=22.18W
   in power     823.757 W  (std 0.0000)   @ 71.439V
  out power     802.031 W  (std 0.0000)   @ 27.127V
eff 97.15% (std=0.009163,last=97.14)   loss=22.71W
   in power     796.010 W  (std 0.6710)   @ 71.506V
  out power     773.237 W  (std 0.7197)   @ 27.112V
```
![img_6.png](img_6.png)


```
T130 2stack 6strands (ipp=22A)
eff 97.80% (std=0.000000,last=97.80)   loss=18.19W
   in power     825.300 W  (std 0.0000)   @ 71.456V
  out power     807.063 W  (std 0.0000)   @ 27.127V
warm:
eff 97.69% (std=0.000396,last=97.69)   loss=18.87W
   in power     818.586 W  (std 0.0473)   @ 71.463V
  out power     799.717 W  (std 0.0462)   @ 27.119V
```
![img_7.png](img_7.png)
![img_8.png](img_8.png)


```
codaca low loss (ipp=16.64A)
eff 98.07% (std=0.000000,last=98.07)   loss=15.85W      < vs "high sat" eff: 97.88%
   in power     821.925 W  (std 0.0000)   @ 71.498V
  out power     806.072 W  (std 0.0000)   @ 27.141V
warm:
eff 98.06% (std=0.003044,last=98.06)   loss=16.06W
   in power     827.109 W  (std 0.1596)   @ 71.510V
  out power     811.067 W  (std 0.1500)   @ 27.146V
after 30h mins:
eff 98.042% (std=0.000922,last=98.04)   loss=16.14W
   in power     824.321 W  (std 0.0473)   @ 71.502V
  out power     808.185 W  (std 0.0462)   @ 27.141V
  
put HS gate discharge resistor 2.2ohm:
eff 98.116% (std=0.001012,last=98.12)   loss=14.89W
   in power     790.514 W  (std 0.0354)   @ 71.587V
  out power     775.624 W  (std 0.0350)   @ 27.140V
```




![img_4.png](img_4.png)
![img_5.png](img_5.png)
eff over time samples. applied some forced heat during warm-up


Here's a plot over time of converter efficiency (sampling rate ~4 Hz).
![img_3.png](img_3.png)

The spikes are me touching the converter. Just before x=500 I put a fan next to the converter.
This increased eff by almost 0.05%. As you can see afterwards it takes a long time to reach the steady state of
thermal equilibrium. It also looks like the converter doesn't fall back to its initial 
