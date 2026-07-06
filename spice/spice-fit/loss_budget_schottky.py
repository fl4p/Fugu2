#!/usr/bin/env python3
"""Loss-budget: does a parallel SVT15100UB Schottky across the LS net ahead?
Operating point from the Fugu2 loss budget: Vin=72V, I=32A, fsw=39kHz,
deadtime=297ns (2 per cycle), total loss ~15.5W, Qrr baseline ~0.64W.

Terms compared, body-diode-only vs +SVT15100UB:
  (1) deadtime conduction  -- steady-state diode split (LTspice DC @125C)
  (2) reverse-recovery Qrr -- baseline 0.64W scaled by sim diversion
  (3) Schottky Coss added
vs the alternative: just shorten the 297ns deadtime to 65ns (R_DT change).
"""
import os, subprocess
import numpy as np
from spicelib import RawRead

LT = "/Applications/LTspice.app/Contents/MacOS/LTspice"
HERE = os.path.dirname(os.path.abspath(__file__))
VIN, ILOAD, FSW, TDEAD, NDEAD = 72.0, 32.0, 39e3, 297e-9, 2
TDEAD_TRIM = 65e-9
QRR_BASE_W = 0.64          # datasheet body-diode Qrr loss (from loss budget)

def model(fname):
    t = open(os.path.join(HERE, "..", "models", fname), encoding="latin-1").read()
    return "\n".join(l.rstrip("\r") for l in t.splitlines()
                     if l.startswith((".MODEL", "+")))
SVT = model("SVT15100UB.lib")

def dc_split(with_sch, temp=125):
    # 32A forced through the freewheel diode(s); node V = forward drop.
    sch = "Dsch nd 0 SVT15100UB\n" if with_sch else ""
    cir = f"""* dc split
{SVT if with_sch else ''}
.model DBODY D(Is=2e-9 N=1.1 Rs=4m CJO=0.5n VJ=0.7 M=0.5 BV=100 TT=6n)
Iinj 0 nd {ILOAD}
Dbody nd 0 DBODY
{sch}Rl nd 0 1e7
.temp {temp}
.op
.end
"""
    open(os.path.join(HERE, "_l.cir"), "w").write(cir)
    for e in ("_l.raw", "_l.log"):
        p = os.path.join(HERE, e)
        if os.path.exists(p): os.remove(p)
    subprocess.run([LT, "-b", "_l.cir"], capture_output=True, cwd=HERE)
    r = RawRead(os.path.join(HERE, "_l.raw"))
    vnd = float(np.real(r.get_trace("V(nd)").get_wave()[0]))
    ib = float(np.real(r.get_trace("I(Dbody)").get_wave()[0]))
    isc = float(np.real(r.get_trace("I(Dsch)").get_wave()[0])) if with_sch else 0.0
    return vnd, ib, isc

def coss_charge(vin):
    # SVT: CJO=2.6n VJ=3.08 MJ=0.90 ; Q(0->Vin) = CJO*VJ/(1-MJ)*[(1+V/VJ)^(1-MJ)-1]
    CJO, VJ, MJ = 2.6e-9, 3.08, 0.90
    return CJO * VJ / (1 - MJ) * ((1 + vin / VJ) ** (1 - MJ) - 1)

# (1) deadtime conduction
v0, ib0, _ = dc_split(False)
v1, ib1, is1 = dc_split(True)
Pdt_no = v0 * ILOAD * TDEAD * NDEAD * FSW
Pdt_sch = v1 * ILOAD * TDEAD * NDEAD * FSW
# (2) Qrr: reduction from the DPT sim (TDSON-8, 300ns, SVT = 83%; TO-220 = 19%)
QRR_RED = {"TDSON-8": 0.83, "TO-220": 0.19}
# (3) Coss added (hard-switched, ~half of Q*V dissipated)
q = coss_charge(VIN)
Pcoss = 0.5 * q * VIN * FSW

print(f"Operating: Vin={VIN}V I={ILOAD}A fsw={FSW/1e3:.0f}kHz deadtime={TDEAD*1e9:.0f}ns x{NDEAD}\n")
print(f"(1) Deadtime conduction @125C:")
print(f"    body-diode only : Vf={v0:.3f}V -> {Pdt_no*1000:5.0f} mW")
print(f"    body + SVT      : Vnode={v1:.3f}V (body {ib1:.1f}A / SVT {is1:.1f}A) -> {Pdt_sch*1000:5.0f} mW"
      f"   (save {(Pdt_no-Pdt_sch)*1000:+.0f} mW)")
print(f"\n(2) Qrr (baseline {QRR_BASE_W*1000:.0f} mW):")
for pkg, red in QRR_RED.items():
    print(f"    +SVT on {pkg:8s}: {QRR_BASE_W*(1-red)*1000:5.0f} mW   (save {QRR_BASE_W*red*1000:+.0f} mW)")
print(f"\n(3) SVT Coss added (Q={q*1e9:.0f}nC @72V): {Pcoss*1000:+.0f} mW")

print(f"\n=== NET (body+SVT vs body-only) ===")
for pkg, red in QRR_RED.items():
    net = (Pdt_no - Pdt_sch) + QRR_BASE_W * red - Pcoss
    print(f"    {pkg:8s}: {net*1000:+.0f} mW  ({100*net/15.5:+.2f}% of 15.5W total)")

print(f"\n=== ALTERNATIVE: trim deadtime 297ns -> 65ns (R_DT change, no Schottky) ===")
Pdt_trim = v0 * ILOAD * TDEAD_TRIM * NDEAD * FSW
print(f"    deadtime conduction: {Pdt_no*1000:.0f} -> {Pdt_trim*1000:.0f} mW   (save {(Pdt_no-Pdt_trim)*1000:+.0f} mW)")
print(f"    + reduces Qrr too (less body-diode storage), no Coss/overshoot/extra part")
for e in ("_l.cir", "_l.raw", "_l.log", "_l.op.raw"):
    p = os.path.join(HERE, e)
    if os.path.exists(p): os.remove(p)
