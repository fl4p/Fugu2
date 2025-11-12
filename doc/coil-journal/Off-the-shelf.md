


# Ruishen RSEQ32-470M

```
# Datasheet
L0@100khz = 47
DCR = 3(typ) | 4.5(max) mΩ
40°C temp rise current: 40 A 
Isat: 17A(20%drop) | 25A (30% drop)

```

```
Coil
turns: 18
dcr(hot) = 3.8mΩ (measured with 5A excertation current)
```

```
# tests in fbanana:

Idc=32.6A
Ipp=11.9A
V=73.6/27.1
> compute_L(73.6,27.1,39e3, 11.9)*1e6
36.8 µH (78% of L0)

Idc=14A
Ipp=10.65A
41.2 uH

Idc=6.9A
IPP=10.44A
42 µH

```

The saturation performance is good, at 32A L drops by 22%.
Versus the datasheet 25A with 30% drop.



# ftall coil inductivity

we can compute the actual inductivity with dc bias if we know Vin/Vout and the ripple current.
We can measure the ripple current with a current probe clamp and an oscilloscope. 

```
Idc=32.5A
Ipp=11.5A
V=73.6/27V
f=39khz
>>> compute_L(73.6, 27, 39e3, 12)
38.12 µH

Idc= 18.4 A
Ipp= 10.2 A
=> L = 43 µH


Idc=10.4A
Ipp=9.7A
=> L = 45 µH


Idc=5.2A
Ipp=9.5A
=> L = 46 µH


```


^ was this coodaca high sat?
# Codaca 2434 CPEX4141L-500 (high sat)
- rdc=2.27mΩ

# Codacoa

- in boost converter
- I=31A, Ipp = 14.8A
- Ploss = 4.9W std=0.33
  ![img.png](codaca-wf.webp)![img_1.png](codaca-wf1.webp)
- Power Measurements
    - 26/73V I=35.5A ipp=15A