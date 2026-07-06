#!/usr/bin/env python3
"""Fugu2 power-loss budget at the measured operating point.

Every input is sourced, not guessed:
  * Operating point : README measured efficiency point (Vin=72, Vout=27, Iout=32A,
                      eta=98.17%) and firmware pwm_freq=39000 (test_buck.cpp kFsw).
  * Power MOSFETs   : real board parts (BOM) with specs from the parts_db in
                      ~/dev/pv/pwr-mosfet-lib (Rds, Qg, Qsw, Qrr, Coss). Values are
                      embedded below as a fallback so this script runs standalone;
                      pass --parts-db to re-pull live and cross-check.
  * Inductor        : 2x stacked Micrometals Sendust T184 (MS-184125-2), 12 turns
                      of 10-strand AWG16.8 (~50uH). DCR computed from that geometry.

The measured total loss (Pout*(1/eta-1) ~ 16.1 W) is the ground truth. Silicon +
inductor-copper are computed; inductor core is an estimate; the remainder
(caps ESR + low-side shunt + battery backflow eFuse FET + terminals/wiring) is the
balance to the measured total.

Usage:  python3 loss_budget.py [--parts-db PATH_TO_pwr-mosfet-lib]
Output: prints the table and writes fugu2_loss_budget.png next to this file.
"""
import argparse
import math
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# --------------------------------------------------------------------------- #
# Operating point (measured -- Fugu2 README) + firmware switching frequency
# --------------------------------------------------------------------------- #
VIN, VOUT, IOUT = 72.0, 27.0, 32.0          # V, V, A  (README INA228 measurement)
ETA = 0.9817                                # measured efficiency at this point
FSW = 39_000.0                              # Hz -- firmware pwm_freq (=80MHz/2048)
VDRV = 10.0                                 # gate-drive voltage (UCC21330)
TJ_HOT_FACTOR = 1.4                         # Rds(on) rise, Tj ~ 100 C vs 25 C spec
N_HS = 2                                    # Q1||Q3 high-side FETs in parallel

D = VOUT / VIN
POUT = VOUT * IOUT
PLOSS_MEAS = POUT * (1.0 / ETA - 1.0)

# --------------------------------------------------------------------------- #
# MOSFET specs -- from parts_db (~/dev/pv/pwr-mosfet-lib). Embedded fallback.
# key: Rds_on [ohm], Qg/Qsw/Qrr [C], Coss [F] @ Coss_Vds [V], Vsd [V]
# --------------------------------------------------------------------------- #
FET_FALLBACK = {
    ("infineon", "IPP055N08NF2S"): dict(   # HS x2 (80 V)
        Rds_on=5.5e-3, Qg=36e-9, Qsw=13e-9, Qrr=154e-9, Coss=420e-12, Coss_Vds=40.0, Vsd=0.94),
    ("onsemi", "FDPF2D3N10C"): dict(        # LS x1 (100 V)
        Rds_on=2.3e-3, Qg=108e-9, Qsw=41.8e-9, Qrr=191e-9, Coss=4.49e-9, Coss_Vds=50.0, Vsd=0.9),
}
HS_KEY = ("infineon", "IPP055N08NF2S")
LS_KEY = ("onsemi", "FDPF2D3N10C")


def load_fets(parts_db_path=None):
    """Return {key: specs-dict}. Try live parts_db, else embedded fallback."""
    if not parts_db_path:
        return dict(FET_FALLBACK), "embedded (parts_db snapshot)"
    import sys
    sys.path.insert(0, parts_db_path)
    from dslib.store import load_parts  # noqa
    parts = load_parts()
    out = {}
    for key in (HS_KEY, LS_KEY):
        s = parts[key].specs
        out[key] = dict(Rds_on=s.Rds_on, Qg=s.Qg, Qsw=s.Qsw, Qrr=s.Qrr,
                        Coss=s.Coss, Coss_Vds=s.Coss_Vds, Vsd=s.Vsd)
    return out, f"live parts_db ({parts_db_path})"


# --------------------------------------------------------------------------- #
# Inductor: 2x T184 Sendust, 12 turns, 10-strand AWG16.8, ~50 uH
# --------------------------------------------------------------------------- #
L0 = 50e-6
N_STRANDS = 10
STRAND_DIA = 1.18e-3            # AWG16.8, m
STRAND_LEN = 2.0               # m per strand (README: "20 m total = 10 x 2 m")
SIGMA_CU = 58.5e6              # S/m (W210 grade-2 Cu)
CORE_LOSS_EST = 2.0           # W -- Sendust @39kHz, ~9A ripple (estimate, flag)


def inductor_copper_loss(irms):
    area = N_STRANDS * math.pi / 4 * STRAND_DIA ** 2
    dcr20 = STRAND_LEN / (SIGMA_CU * area)          # all strands parallel, 2 m path
    dcr_hot = dcr20 * (1 + 0.0039 * 60)             # ~80 C winding
    return irms ** 2 * dcr_hot, dcr20, dcr_hot


def ripple_irms():
    dipp = VOUT * (1 - D) / (L0 * FSW)              # peak-peak ripple current
    irms = IOUT * math.sqrt(1 + (1 / 3) * (dipp / 2 / IOUT) ** 2)
    return dipp, irms


def eoss(spec):
    """Energy-related Coss -> Eoss at VIN, scaling Eoss ~ V^1.5 from spec point."""
    if not spec["Coss"] or math.isnan(spec["Coss"]):
        return 0.0
    vs = spec["Coss_Vds"]
    return 0.5 * spec["Coss"] * vs ** 2 * (VIN / vs) ** 1.5


def compute(fets):
    hs, ls = fets[HS_KEY], fets[LS_KEY]
    dipp, irms = ripple_irms()

    # --- semiconductors (datasheet / parts_db) ---
    r_hs = hs["Rds_on"] / N_HS * TJ_HOT_FACTOR
    r_ls = ls["Rds_on"] * TJ_HOT_FACTOR
    p_hs_cond = (D * IOUT ** 2) * r_hs
    p_ls_cond = ((1 - D) * IOUT ** 2) * r_ls

    ig = 1.7                                          # gate current at Miller plateau
    p_hs_sw = VIN * IOUT * (hs["Qsw"] / ig) * FSW     # ~ turn-on + turn-off

    p_coss = (eoss(ls) + N_HS * eoss(hs)) * FSW
    p_qrr = ls["Qrr"] * 1.5 * VIN * FSW               # 1.5x: app di/dt harsher than spec
    p_gate = (N_HS * hs["Qg"] + ls["Qg"]) * VDRV * FSW
    p_dt = ls["Vsd"] * IOUT * 2 * 30e-9 * FSW         # body-diode conduction, ~30 ns/edge

    semi = {
        "LS conduction (2.3 mΩ)": p_ls_cond,
        "HS conduction (2×5.5 mΩ)": p_hs_cond,
        "LS Qrr (191 nC)": p_qrr,
        "HS switching (Qsw 13 nC)": p_hs_sw,
        "Coss switch (LS 4.5 nF)": p_coss,
        "Gate drive": p_gate,
        "Deadtime": p_dt,
    }
    p_semi = sum(semi.values())

    # --- inductor copper (computed from winding geometry) ---
    p_cu, dcr20, dcr_hot = inductor_copper_loss(irms)

    # --- inductor core (estimate) + balance to measured total ---
    p_core = CORE_LOSS_EST
    p_other = PLOSS_MEAS - p_semi - p_cu - p_core     # caps/shunt/eFuse/wiring

    return dict(semi=semi, p_semi=p_semi, p_cu=p_cu, dcr20=dcr20, dcr_hot=dcr_hot,
                p_core=p_core, p_other=p_other, dipp=dipp, irms=irms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts-db", help="path to ~/dev/pv/pwr-mosfet-lib to re-pull live")
    args = ap.parse_args()

    fets, src = load_fets(args.parts_db)
    r = compute(fets)

    print(f"Fugu2 loss budget @ {VIN:.0f}V->{VOUT:.0f}V {IOUT:.0f}A "
          f"({POUT:.0f} W out, eta {ETA*100:.2f}%)")
    print(f"  FET specs source : {src}")
    print(f"  D={D:.3f}  fsw={FSW/1e3:.0f} kHz  ripple dIpp={r['dipp']:.1f} A  Irms={r['irms']:.1f} A")
    print(f"  inductor DCR     : {r['dcr20']*1e3:.2f} mΩ (20°C) -> {r['dcr_hot']*1e3:.2f} mΩ (hot)")
    print(f"  MEASURED Ploss   : {PLOSS_MEAS:.2f} W\n")
    rows = list(r["semi"].items()) + [
        ("Inductor copper (DCR, computed)", r["p_cu"]),
        ("Inductor core (Sendust, est.)", r["p_core"]),
        ("Caps/shunt/eFuse/wiring (balance)", r["p_other"]),
    ]
    for k, v in sorted(rows, key=lambda x: -x[1]):
        print(f"    {k:36s} {v:5.2f} W  ({v/PLOSS_MEAS*100:4.1f}%)")
    print(f"    {'-'*36} {'-'*5}")
    print(f"    {'TOTAL':36s} {sum(v for _,v in rows):5.2f} W  (vs measured {PLOSS_MEAS:.2f} W)")

    # -------- chart --------
    SEMI, MAG, OTH = "#d62728", "#8c564b", "#7f7f7f"
    items = [
        ("Inductor copper (DCR)", r["p_cu"], MAG),
        ("Caps/shunt/eFuse/wiring", r["p_other"], OTH),
        ("Inductor core (est.)", r["p_core"], "#a0522d"),
        ("LS conduction", r["semi"]["LS conduction (2.3 mΩ)"], "#ff7f0e"),
        ("HS conduction", r["semi"]["HS conduction (2×5.5 mΩ)"], "#ff9896"),
        ("LS Qrr", r["semi"]["LS Qrr (191 nC)"], "#9467bd"),
        ("HS switching", r["semi"]["HS switching (Qsw 13 nC)"], SEMI),
        ("Coss switching", r["semi"]["Coss switch (LS 4.5 nF)"], "#c5b0d5"),
        ("Gate drive", r["semi"]["Gate drive"], "#2ca02c"),
        ("Deadtime", r["semi"]["Deadtime"], "#98df8a"),
    ]
    items.sort(key=lambda x: x[1])
    lab = [i[0] for i in items]
    val = [i[1] for i in items]
    col = [i[2] for i in items]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    y = np.arange(len(lab))
    ax.barh(y, val, color=col, edgecolor="k", lw=.4)
    for yi, v in zip(y, val):
        ax.text(v + 0.08, yi, f"{v:.2f} W ({v/PLOSS_MEAS*100:.0f}%)", va="center", fontsize=8.5)
    ax.set_yticks(y)
    ax.set_yticklabels(lab, fontsize=9)
    ax.set_xlim(0, max(val) * 1.3)
    ax.set_xlabel("Power loss  [W]")
    ax.set_title(f"Fugu2 loss budget @ {VIN:.0f}V→{VOUT:.0f}V {IOUT:.0f}A "
                 f"({POUT:.0f} W, η={ETA*100:.2f}%, Σ≈{PLOSS_MEAS:.1f} W)", fontsize=10)
    ax.legend(handles=[Patch(color=SEMI, label="Semiconductor"),
                       Patch(color=MAG, label="Magnetics"),
                       Patch(color=OTH, label="Caps/wiring")],
              loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=.3)
    plt.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fugu2_loss_budget.png")
    plt.savefig(out, dpi=130)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
