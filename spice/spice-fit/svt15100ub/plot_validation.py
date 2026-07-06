#!/usr/bin/env python3
"""Overlay the fitted SVT15100UB model (LTspice) on the digitized datasheet
points. Produces SVT15100UB_validation.png. Run: venv python plot_validation.py
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
MODEL = "\n".join(l for l in open(os.path.join(HERE, "..", "..", "models",
        "SVT15100UB.lib")).read().splitlines() if l.startswith((".MODEL", "+")))


def run(cir, raw):
    open(os.path.join(HERE, "_tmp.cir"), "w").write(cir)
    for e in (raw, os.path.join(HERE, "_tmp.log")):
        if os.path.exists(e):
            os.remove(e)
    subprocess.run([LT, "-b", "_tmp.cir"], capture_output=True, cwd=HERE)
    return RawRead(raw)


def forward():
    r = run(f"* v\n{MODEL}\nId 0 a 1\nD1 a 0 SVT15100UB\n"
            f".dc Id 0.2 32 0.2\n.step temp list 25 125\n.end\n",
            os.path.join(HERE, "_tmp.raw"))
    ax = r.get_trace(r.get_trace_names()[0]); V = r.get_trace("V(a)")
    return {T: (np.real(V.get_wave(s)), np.real(ax.get_wave(s)))  # (VF, IF)
            for s, T in zip(r.get_steps(), (25, 125))}


def cap():
    cs = []
    for vr in [1, 2, 3, 5, 7, 10, 15, 20, 30, 50]:
        r = run(f"* c\n{MODEL}\nVr k 0 {vr} AC 1\nD1 0 k SVT15100UB\n"
                f".ac list 1meg\n.end\n", os.path.join(HERE, "_tmp.raw"))
        w = r.get_trace("I(Vr)").get_wave()
        cs.append((vr, abs(complex(w[0]).imag) / (2 * np.pi * 1e6) * 1e12))
    return cs


fwd, cs = forward(), cap()
for e in ("_tmp.cir", "_tmp.raw", "_tmp.log", "_tmp.op.raw"):
    p = os.path.join(HERE, e)
    if os.path.exists(p):
        os.remove(p)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
for T, c, d in [(25, "tab:blue", ds.FWD_25C), (125, "tab:red", ds.FWD_125C)]:
    Vm, Im = fwd[T]
    a1.semilogy(Vm, Im, "-", color=c, label=f"model {T}°C")
    a1.semilogy([v for _, v in d], [i for i, _ in d], "o", color=c, mfc="none",
                label=f"datasheet {T}°C")
a1.semilogy([0.61], [15], "*", color="tab:blue", ms=15)   # table anchor
a1.set(xlim=(0.1, 0.9), ylim=(1, 40), xlabel="VF (V)", ylabel="IF (A)",
       title="Forward (★=table VF@15A typ)")
a1.grid(True, which="both", alpha=0.3); a1.legend(fontsize=8)

a2.loglog([v for v, _ in cs], [c for _, c in cs], "-", color="tab:green",
          label="model 25°C")
a2.loglog([v for v, _ in ds.CAP], [c for _, c in ds.CAP], "o", color="tab:green",
          mfc="none", label="datasheet 25°C")
a2.set(xlim=(1, 100), ylim=(100, 3000), xlabel="VR (V)", ylabel="CJ (pF)",
       title="Junction capacitance @1MHz")
a2.grid(True, which="both", alpha=0.3); a2.legend(fontsize=8)

fig.suptitle("PANJIT SVT15100UB datasheet fit validation (LTspice vs datasheet)")
fig.tight_layout()
out = os.path.join(HERE, "SVT15100UB_validation.png")
fig.savefig(out, dpi=110)
print("wrote", out)
