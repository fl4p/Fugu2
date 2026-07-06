#!/usr/bin/env python3
"""Overlay the fitted ST15100S model (LTspice) on the digitized datasheet
points. Produces ST15100S_validation.png. Run: venv python plot_validation.py
"""
import os, subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from spicelib import RawRead
import datasheet_points as ds

LT = "/Applications/LTspice.app/Contents/MacOS/LTspice"
HERE = os.path.dirname(os.path.abspath(__file__))
# Inline the .MODEL directly (LTspice-macOS -b can't resolve absolute .include).
_lib = open(os.path.join(HERE, "..", "..", "models", "ST15100S.lib")).read().splitlines()
MODEL = "\n".join(l for l in _lib if l.startswith((".MODEL", "+")))


def run(cir_text, raw):
    open(os.path.join(HERE, "_tmp.cir"), "w").write(cir_text)
    for e in (raw, os.path.join(HERE, "_tmp.log")):
        if os.path.exists(e):
            os.remove(e)
    subprocess.run([LT, "-b", "_tmp.cir"], capture_output=True, cwd=HERE)
    return RawRead(raw)


def forward():
    cir = f"""* val
{MODEL}
Idrv 0 a 1
D1 a 0 ST15100S
.dc Idrv 0.2 42 0.2
.step temp list 25 125
.end
"""
    r = run(cir, os.path.join(HERE, "_tmp.raw"))
    ax = r.get_trace(r.get_trace_names()[0]); V = r.get_trace("V(a)")
    out = {}
    for si, T in zip(r.get_steps(), (25, 125)):
        out[T] = (np.real(V.get_wave(si)), np.real(ax.get_wave(si)))
    return out


def cap():
    vrs, cs = list(range(0, 11)), []
    for vr in vrs:
        cir = f"""* val
{MODEL}
Vr k 0 {vr} AC 1
D1 0 k ST15100S
.ac list 1meg
.end
"""
        r = run(cir, os.path.join(HERE, "_tmp.raw"))
        w = r.get_trace("I(Vr)").get_wave()
        cs.append(abs(complex(w[0]).imag) / (2 * np.pi * 1e6) * 1e12)
    return vrs, cs


fwd = forward()
vrs, cs = cap()
for e in ("_tmp.cir", "_tmp.raw", "_tmp.log", "_tmp.op.raw"):
    p = os.path.join(HERE, e)
    if os.path.exists(p):
        os.remove(p)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))

# forward
for T, c, dpts in [(25, "tab:blue", ds.FWD_25C), (125, "tab:red", ds.FWD_125C)]:
    Vm, Im = fwd[T]
    a1.semilogy(Vm, Im, "-", color=c, label=f"model {T}°C")
    dv = [v for _, v in dpts]; di = [i for i, _ in dpts]
    a1.semilogy(dv, di, "o", color=c, mfc="none", label=f"datasheet {T}°C")
    typ, mx = ds.VF_TABLE[T]
    a1.semilogy([typ], [15], "*", color=c, ms=14)
a1.set(xlim=(0.2, 1.15), ylim=(1, 50), xlabel="VF (V)", ylabel="IF (A)",
       title="Forward  (★ = table VF@15A typ)")
a1.grid(True, which="both", alpha=0.3); a1.legend(fontsize=8)

# cap
a2.loglog(np.array(vrs) + 1e-3, cs, "-", color="tab:green", label="model 25°C")
a2.loglog([v for v, _ in ds.CAP], [c for _, c in ds.CAP], "o",
          color="tab:green", mfc="none", label="datasheet 25°C")
a2.set(xlim=(0.1, 10), ylim=(100, 10000), xlabel="VR (V)", ylabel="CT (pF)",
       title="Junction capacitance @1MHz")
a2.grid(True, which="both", alpha=0.3); a2.legend(fontsize=8)

fig.suptitle("ST15100S datasheet fit validation (LTspice model vs datasheet)")
fig.tight_layout()
out = os.path.join(HERE, "ST15100S_validation.png")
fig.savefig(out, dpi=110)
print("wrote", out)
