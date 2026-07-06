#!/usr/bin/env python3
"""Does an external Schottky (D16, ST15100S) across the LS switch reduce body-diode
Qrr on the Fugu2 board? Tests two LS packages via their transfer-loop inductance:

  TO-220  Q2 : FET leads Ld=2.5n Ls=2n  -> D16 transfer loop ~7.5 nH
  TDSON-8    : FET leads Ld=0.5n Ls=0.5n -> D16 transfer loop ~3 nH

LS = ideal channel switch || explicit body diode (Si, with Qrr via TT), behind the
FET leads. Schottky sits across the PCB pads (ld<->0) via its own branch L. DPT:
30 A freewheel, 100 ns deadtime, HS turn-on at 1.0 us.
"""
import os, subprocess
import numpy as np
from spicelib import RawRead

LT = "/Applications/LTspice.app/Contents/MacOS/LTspice"
HERE = os.path.dirname(os.path.abspath(__file__))
ILOAD, VIN = 30.0, 80.0

# Schottky models, inlined (mac -b can't resolve absolute .include)
def load_model(fname):
    txt = open(os.path.join(HERE, "..", "models", fname), encoding="latin-1").read()
    body = "\n".join(l.rstrip("\r") for l in txt.splitlines()
                     if l.startswith((".MODEL", "+")))
    name = body.split()[1]      # ".MODEL <name> D ("
    return body, name

DIODES = [load_model("ST15100S.lib"), load_model("SVT15100UB.lib")]

def netlist(ldl, lsl, ld16, schottky, sch_body, sch_name, dt_ns=100):
    d16 = (f"LD16 ld n16 {ld16}n\nDsch 0 n16 {sch_name}\n") if schottky else ""
    SCH = sch_body
    t_lsoff = 1.0 - dt_ns / 1000.0            # LS off time (us); HS on at 1.0us
    return f"""* LS parallel-Schottky Qrr test
{SCH}
.model DBODY D(Is=2e-9 N=1.1 Rs=4m CJO=0.5n VJ=0.7 M=0.5 BV=100 TT=6n)
.model SWMOD SW(Ron=2.2m Roff=1e6 Vt=5 Vh=1)
Vin vin 0 {VIN}
Lfeed vin vi 150n Rser=8m
Cbulk vi 0 940u
Cin vi 0 2u Rser=3m Lser=2n
L5 vi hd 2n Rser=1m
SHS hd sw hg 0 SWMOD
L4 sw ld 2n Rser=1m
LdL ld ldd {ldl}n
LsL lss 0 {lsl}n
Schan ldd lss lg 0 SWMOD
Dbody lss ldd DBODY
{d16}Iload ld 0 {ILOAD}
Rpar ld 0 100k
Vlsg lg 0 PWL(0 10 {t_lsoff:.4f}u 10 {t_lsoff+0.002:.4f}u 0)
Vhsg hg 0 PWL(0 0 1.0u 0 1.002u 10)
.tran 0 1.15u 0 0.05n
.end
"""

def run(cir):
    open(os.path.join(HERE, "_t.cir"), "w").write(cir)
    for e in ("_t.raw", "_t.log"):
        p = os.path.join(HERE, e)
        if os.path.exists(p): os.remove(p)
    subprocess.run([LT, "-b", "_t.cir"], capture_output=True, cwd=HERE)
    return RawRead(os.path.join(HERE, "_t.raw"))

def analyze(r):
    t = np.abs(r.get_trace("time").get_wave())
    ib = np.real(r.get_trace("I(Dbody)").get_wave())   # +forward, -reverse
    vsw = np.real(r.get_trace("V(sw)").get_wave())
    # forward freewheel current in body diode just before HS turn-on
    i_fwd = ib[np.argmin(np.abs(t - 0.99e-6))]
    # Qrr = charge of ONLY the first reverse-recovery lobe: from where the body
    # diode current first crosses to negative (after HS on) until it returns to 0.
    k0 = np.searchsorted(t, 1.0e-6)
    i = k0
    while i < len(ib) and ib[i] >= 0:   # find start of first negative excursion
        i += 1
    j = i
    while j < len(ib) and ib[j] < 0:    # end of that lobe
        j += 1
    if i < j:
        qrr = -np.trapezoid(ib[i:j], t[i:j])
        i_rr_peak = ib[i:j].min()
    else:
        qrr, i_rr_peak = 0.0, 0.0
    sw_peak = vsw.max()
    return i_fwd, qrr * 1e9, i_rr_peak, sw_peak     # A, nC, A, V

cases = [
    ("TO-220  no-Schottky", 2.5, 2.0, None, False),
    ("TO-220  + D16 (loop 7.5n)", 2.5, 2.0, 3.0, True),
    ("TDSON-8 no-Schottky", 0.5, 0.5, None, False),
    ("TDSON-8 + D16 (loop 3n)", 0.5, 0.5, 2.0, True),
]
for sch_body, sch_name in DIODES:
    print(f"\n########## Schottky = {sch_name} ##########")
    for dt in (40, 100, 300):
        print(f"\n=== deadtime {dt} ns ===")
        print(f"{'case':28s} {'Ibody_fwd':>10s} {'divert':>7s} {'Qrr(nC)':>9s} {'Irr_pk':>8s} {'SWpeak':>8s}")
        base = {}
        for name, ldl, lsl, ld16, sch in cases:
            r = run(netlist(ldl, lsl, ld16 or 0, sch, sch_body, sch_name, dt_ns=dt))
            i_fwd, qrr, irr, swpk = analyze(r)
            tag = name.split()[0]
            divert = f"{100*(1-i_fwd/ILOAD):.0f}%"
            if not sch:
                base[tag] = qrr; red = ""
            else:
                red = f"  ({100*(1-qrr/base[tag]):+.0f}% Qrr)"
            print(f"{name:28s} {i_fwd:9.1f}A {divert:>7s} {qrr:8.1f} {irr:7.1f}A {swpk:7.1f}V{red}")
for e in ("_t.cir", "_t.raw", "_t.log", "_t.op.raw"):
    p = os.path.join(HERE, e)
    if os.path.exists(p): os.remove(p)
