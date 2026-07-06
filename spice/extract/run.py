#!/usr/bin/env python3
"""Drive the Fugu2 commutation-loop extraction: mesh -> FastHenry -> L(f),R(f).

Runs with the SYSTEM python3 (no pcbnew here). Shells out to KiCad's bundled
python for the geometry step and to the locally-built fasthenry for the solve,
then parses Zc.mat and reports the loop inductance.

Speed (all applied here, no source changes):
  * default solves only the ~10-100 MHz plateau (FastHenry rebuilds its
    preconditioner PER FREQUENCY, so fewer freqs ~= linear speedup),
  * uses the cheaper `-p diag` preconditioner,
  * runs the independent pitch solves CONCURRENTLY across cores (the binary is
    single-threaded, so parallelism comes from running many solves at once).

Usage:
  python3 run.py                 # parallel convergence sweep, write results.md
  python3 run.py --pitch 1.0     # single pitch
  python3 run.py --full          # full L(f) curve (slower) for results.md
"""
import argparse
import math
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
KPY = ("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/"
       "Versions/Current/bin/python3")
FASTHENRY = "/Users/fab/dev/vendor/FastHenry2/bin/fasthenry"
EXTRACTOR = os.path.join(HERE, "kicad_to_fasthenry.py")

PLATEAU_LO = 1e7
PLATEAU_HI = 1e8


def extract(pitch, inp, full):
    cmd = [KPY, EXTRACTOR, "--pitch", str(pitch), "--out", inp]
    if full:
        cmd.append("--full")
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    if p.returncode != 0:
        sys.exit(f"extractor failed (pitch={pitch}):\n{p.stderr}")
    stats = {}
    for line in p.stdout.splitlines():
        m = re.search(r"nodes=(\d+) segs=(\d+) vias=(\d+)", line)
        if m:
            stats = dict(nodes=int(m[1]), segs=int(m[2]), vias=int(m[3]))
    return stats


def solve(inp, suffix):
    """fasthenry with the cheap diag preconditioner; -S gives a unique Zc file
    so concurrent solves don't clobber each other."""
    p = subprocess.run([FASTHENRY, inp, "-p", "diag", "-S", suffix],
                       capture_output=True, text=True, cwd=HERE)
    zc = os.path.join(HERE, f"Zc{suffix}.mat")
    if p.returncode != 0 or not os.path.exists(zc):
        sys.exit(f"fasthenry failed ({inp}):\n{p.stdout[-400:]}\n{p.stderr[-400:]}")
    return zc


def parse_zc(path):
    rows, freq = [], None
    with open(path) as f:
        for line in f:
            m = re.search(r"frequency = ([0-9.eE+-]+)", line)
            if m:
                freq = float(m[1])
                continue
            if "nan" in line.lower() and freq is not None:
                freq = None  # solver failed at this frequency; skip
                continue
            m = re.match(r"\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)j", line)
            if m and freq is not None:
                rows.append((freq, float(m[1]), float(m[2])))
                freq = None
    return rows


def to_LR(rows):
    return [(f, R, X / (2 * math.pi * f) * 1e9) for f, R, X in rows]  # L in nH


def plateau(lr):
    vals = [(R, L) for f, R, L in lr if PLATEAU_LO <= f <= PLATEAU_HI]
    if not vals:
        vals = [(lr[-1][1], lr[-1][2])]  # fall back to highest freq
    Lp = sum(L for _, L in vals) / len(vals)
    Rp = max(R for R, _ in vals)
    return Rp, Lp


def run_one(pitch, full):
    suffix = f"_p{pitch}"
    inp = os.path.join(HERE, f"loop{suffix}.inp")
    stats = extract(pitch, inp, full)
    zc = solve(inp, suffix)
    lr = to_LR(parse_zc(zc))
    if not lr:
        return pitch, stats, [], None  # solver returned NaN at all freqs
    return pitch, stats, lr, plateau(lr)


def fmt_table(lr):
    lines = ["| freq | R (mΩ) | L (nH) |", "|---|---|---|"]
    for f, R, L in lr:
        lines.append(f"| {f/1e6:g} MHz | {R*1e3:.2f} | {L:.2f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pitch", type=float, default=None,
                    help="single pitch [mm]; default = parallel convergence sweep")
    ap.add_argument("--full", action="store_true", help="full L(f) curve")
    args = ap.parse_args()

    # 0.5mm needs the slow `cube` preconditioner (diag/seg -> NaN on the large
    # fine mesh); these three all solve fast and bracket the answer.
    pitches = [args.pitch] if args.pitch else [2.0, 1.0, 0.7]

    # run all pitches concurrently: the binary is single-threaded but the
    # solves are independent, so this uses all cores.
    with ThreadPoolExecutor(max_workers=len(pitches)) as ex:
        results = list(ex.map(lambda P: run_one(P, args.full), pitches))
    results.sort(key=lambda r: -r[0])  # coarse -> fine

    ok = [r for r in results if r[3] is not None]
    for P, stats, lr, pl in results:
        if pl is None:
            print(f"pitch={P}mm  nodes={stats['nodes']} segs={stats['segs']}  "
                  f"-> NaN (needs -p cube)")
            continue
        Rp, Lp = pl
        print(f"pitch={P}mm  nodes={stats['nodes']} segs={stats['segs']}  "
              f"L_plateau(10-100MHz)={Lp:.2f}nH  R_hf={Rp*1e3:.1f}mΩ")

    Ls = [r[3][1] for r in ok]
    Lmin, Lmax = min(Ls), max(Ls)
    Lnom = sum(Ls) / len(Ls)
    spread = (Lmax - Lmin) / Lnom * 100 if Lnom else 0
    conv = (f"Pitch scatter over {[r[0] for r in ok]}mm: "
            f"L = {Lmin:.1f}–{Lmax:.1f} nH (nominal {Lnom:.1f} nH, ±{spread/2:.0f}%). "
            f"Gridded-filament plane approximation; treat as the uncertainty band.")
    print(conv)

    # report from the mid (1.0mm) run as nominal
    Pf, statsf, lrf, plf = min(ok, key=lambda r: abs(r[0] - 1.0))
    Rpf, Lpf = plf
    with open(os.path.join(HERE, "results.md"), "w") as f:
        f.write("# Fugu2 commutation-loop parasitic extraction — results\n\n")
        f.write("FastHenry MQS extraction of the power commutation loop (SMD "
                "half-bridge Q1‖Q3 / Q2, port across nearest ceramic C16).\n\n")
        f.write(f"**Loop inductance ≈ {Lnom:.1f} nH** "
                f"(pitch band {Lmin:.1f}–{Lmax:.1f} nH), "
                f"HF loop resistance ≈ {Rpf*1e3:.0f} mΩ. "
                f"Nominal from {Pf} mm mesh.\n\n")
        f.write(f"L(f) at {Pf} mm pitch:\n\n" + fmt_table(lrf) + "\n\n")
        f.write(conv + "\n\n")
        f.write("## Suggested LTspice values (buck_parasitcs.asc)\n\n")
        f.write(f"- Hot-loop copper L (one calibrated element in the commutation "
                f"path): **{Lnom:.1f} nH** (band {Lmin:.1f}–{Lmax:.1f})\n")
        f.write("- FET package internal L (~1–3 nH/FET): SEPARATE lumped element "
                "(FastHenry sees copper only).\n")
        f.write("- Cin electrolytic ESL: separate slow-path element, not in this "
                "fast loop.\n")
    print(f"wrote {os.path.join(HERE, 'results.md')}")


if __name__ == "__main__":
    main()
