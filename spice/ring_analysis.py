#!/usr/bin/env python3
"""Switch-node ring <-> commutation-loop inductance <-> RC snubber.

Companion to PARASITIC_MODELING.md and extract/ (FastHenry copper extraction).
Purpose: turn a *measured* switch-node ring frequency into a loop inductance,
and a loop inductance into snubber values -- using the real Coss(V) curves of
the fitted FETs rather than a single datasheet point.

Why Coss(V) and not the datasheet scalar: the tank capacitance is the
charge-equivalent Coss averaged over the ring's own voltage excursion, and
Coss varies ~5x across that excursion. Using Coss(50 V) alone moves f_ring by
tens of percent.

Two edges, two different tanks (this is the useful part):

  HS turn-ON  (SW rises 0 -> Vin, hard, Qrr-excited -- the loud one)
      LS channel and body diode are off; HS channel is on and shorts its own
      Coss. Tank C = N_LS * Coss_LS(V ~ Vin).

  HS turn-OFF (SW falls Vin -> 0, then LS body diode clamps -- the quiet one)
      LS is shorted by its conducting body diode/channel.
      Tank C = N_HS * Coss_HS(V ~ Vin).

SPECULATIVE -- the turn-off row is a model, not an observation. Three caveats,
none of them small:
  * The separation is small. For the measured build the two predicted rings are
    only ~11% apart (59.9 / 66.5 MHz at 72 V) and both sit inside the "~55-65
    MHz" band the No-Coil study already reports -- not resolvable.
  * It is not a non-circular check. Both C's come from the same digitized curve
    set, so a uniform Coss scale error moves both frequencies by 1/sqrt(k) and
    the "two-equation" test passes unchanged. It tests the HS/LS Coss RATIO,
    never the absolute scale -- which is the actual open question. Use `dfreq`.
  * A free turn-off ring may not exist at the SW node at all. Once SW falls past
    -Vf the LS body diode CLAMPS it (doc/SW Phases.md), giving one negative
    spike and a plateau rather than the free decay you get at turn-ON where the
    LS diode is reverse-biased. It is also load-dependent: Qoss(0-72V) = 131 nC
    (LS) + 108 nC (2x HS) gives a 7 ns current-driven fall at 33 A but ~90 ns at
    2.6 A -- soft, no ring. The No-Coil study saw one ring only, but it ran with
    no coil or at 2.6 A, so that is not evidence either way.
Do not fit the turn-off snubber row without first seeing the ring on a scope.

Coss(V) knots: digitized from Infineon Diagram 11 (VGS=0, f=1 MHz) -- by
`dsdig` for IPP039N10N5 and IPA050N10NM5S, by `dslib/coss_digitizer.py` for
IPP024N08NF2S and IPP055N08NF2S, and by the dcdc-tools vector-first digitizer
for IPP022N12NM6 and IPP050N10NF2S. Snapshotted 2026-09-06 from
  ~/dev/pv/pwr-mosfet-lib/dslib/coss_curves.py
where each entry is anchored to the datasheet Coss/Crss/Ciss scalars and
Qoss-validated against the datasheet table. Values are pF vs V.
"""

from __future__ import annotations

import argparse
import math

# --- Coss(V) [ (V, pF) ] ------------------------------------------------------
COSS = {
    # 100 V OptiMOS5, TO-220. Anchors @50V: Coss=560pF (+1.0%). Qoss(0-100V)=66.4nC.
    "IPA050N10NM5S": [
        (0, 3143), (0.6871, 2968), (1.982, 2414), (8.273, 1876), (18.27, 1441), (31.59, 1094),
        (37.88, 889.7), (43.8, 723.7), (50, 565.5), (50.46, 555.9), (52.5, 537.1),
        (73.04, 431.9), (100.1, 380.7),
    ],
    # 120 V OptiMOS6, TO-220. Anchors @60V: Coss=2400pF. Qoss(0-60V)=266.9nC vs 267nC table.
    "IPP022N12NM6": [
        (0.0594872, 8651.99), (1.05894, 8132.24), (2.05839, 7487.49), (5.45652, 6479.73),
        (19.6487, 4954.12), (31.0425, 4199.7), (42.836, 3346.3), (52.4307, 2778.74),
        (68.222, 1956.07), (75.8179, 1591.1), (106.401, 1108.54), (119.994, 959.334),
    ],
    # 100 V StrongIRFET2, TO-220.
    "IPP050N10NF2S": [
        (0.0495652, 3177.92), (0.715866, 3018.02), (2.21504, 2404.74), (6.21285, 1996.88),
        (27.5345, 1179.38), (31.6989, 1097.15), (36.363, 939.726), (40.8605, 804.892),
        (49.689, 566.595), (53.8534, 532.559), (64.5142, 470.497), (99.9947, 382.711),
    ],
    # 80 V StrongIRFET2, TO-220 -- LS of the board measured in
    # "No-Coil SW Ring (Bench vs SPICE).md". Anchors @40V; Qoss graph ~4% over table.
    "IPP024N08NF2S": [
        (0.0396554, 6217.56), (0.705956, 5904.71), (1.9053, 4954.12), (2.83812, 4704.84),
        (8.96808, 3672.17), (15.4978, 3018.02), (21.8943, 2237.07), (25.2258, 1838.56),
        (25.8921, 1782.48), (28.5573, 1511.04), (32.0221, 1203.99), (43.0827, 949.48),
        (53.6102, 838.831), (79.9957, 741.077),
    ],
    # 80 V StrongIRFET2, TO-220 -- HS (2x) of that same board.
    # Anchors: Coss=420pF@40V, Crss=20pF@40V (exact), Ciss=2500pF@40V.
    "IPP055N08NF2S": [
        (0.0396554, 2611.82), (2.83812, 1956.07), (8.96808, 1526.73), (15.7644, 1241.87),
        (22.1608, 901.705), (26.0254, 725.931), (29.7567, 584.421), (32.0221, 495.425),
        (42.2831, 398.849), (53.6102, 345.167), (79.9957, 298.71),
    ],
    # 100 V OptiMOS5, TO-220. Anchors @50V: Coss=830pF (knot 849.8). Overlay human-verified.
    "IPP039N10N5": [
        (0, 4696), (0.6871, 4486), (1.4272, 4187), (2.9075, 3566), (3.8327, 3179),
        (7.9034, 2770), (16.23, 2228), (26.037, 1791), (32.513, 1561), (39.729, 1227),
        (50, 849.8), (51.757, 802.4), (55.642, 757.7), (77.106, 623.4), (100.05, 562.3),
    ],
}

# Which parts are on the board. The schematic Value fields and the physical
# build have diverged at least once -- see the note in doc/EMI Precompliance.md.
BUILDS = {
    # The board actually on the scope in doc/"No-Coil SW Ring (Bench vs SPICE).md":
    # LS IPP024N08NF2S, HS 2x IPP055N08NF2S (80 V StrongIRFET), Rg = 15 ohm.
    # That FET pair matches exactly one board in HW Stories/ -- fetlib.md
    # "testboard1" ("HS: 2p IPP055 / LS: IPP024 (no external diode)"), whose
    # missing LS diode independently corroborates the study's D9-DNP freewheel.
    "measured": dict(hs=("IPP055N08NF2S", 2), ls=("IPP024N08NF2S", 1)),
    # Fugu2.kicad_sch Value fields (Q1/Q3 HS, Q2/Q10 LS) as of 2026-09-06.
    "schematic": dict(hs=("IPA050N10NM5S", 2), ls=("IPP022N12NM6", 1)),
    # "THE PART ACTUALLY FITTED ... confirmed by Fab 2026-08-11" per the
    # pwr-mosfet-lib coss_curves.py comment: LS is 2x IPP039N10N5 (Q2 + the D9
    # footprint), HS is 2x IPP050N10NF2S. This set is *ftall* (HW Stories/
    # ftall.md:6-7) -- a DIFFERENT board from the one that was scoped, which is
    # why it disagrees with "measured". Both annotations are true; they describe
    # different hardware. Do not use this build to interpret the bench ring.
    "fitted": dict(hs=("IPP050N10NF2S", 2), ls=("IPP039N10N5", 2)),
}

# Loop-inductance anchors. The measurement-reconciled decomposition in
# doc/"No-Coil SW Ring (Bench vs SPICE).md" supersedes the older ~13 nH total
# (PARASITIC_MODELING.md TL;DR: ~4 nH copper + ~9 nH leads; this repo's own
# FastHenry extract/results.md gives 5.3 nH for the copper):
#   ~4 nH board copper (the "golden" DPT-solver figure; the 8.2 nH out_cinnet
#     L_loop is flagged there as a non-authoritative-revision outlier, and this
#     repo's own FastHenry extract/results.md gives 5.3 nH)
# + ~1 nH drain tab (horizontal bottom-heatsink mount solders the tab flat to
#     the SW pour -- not a ~2.5 nH vertical stub)
# + ~4 nH source common-source inductance, a MEASURED TO-220 package floor
#     (Aikawa et al., IFEEC 2017, DOI 10.1109/IFEEC.2017.7992207: 3.9-5.7 nH,
#     low end for high-current dies with more source bond wires)
# = ~9.2 nH, which is what the bench ring actually fits.
L_ANCHOR_NH = 9.2
L_COPPER_NH = 4.2   # the "golden" DPT-solver figure, No-Coil...:236
L_LEADS_NH = 5.0

# Bench ring, loaded, from that doc's table (Fab on-scope periods 27/18.6/17.1 ns).
# (Vin, f_ring Hz, SW peak V) -- peak sets the chord over the real ring swing.
# Peaks: 24.1 and 74.1 V are table rows; the 40 V peak exists only as "~54 V@40 V"
# in that doc's prose (No-Coil...:34), so it is a coarser datum than the other two.
BENCH_RING = [(20.0, 37.0e6, 24.1), (40.0, 53.8e6, 54.0), (60.0, 58.5e6, 74.0)]


def coss_pf(part: str, v: float) -> float:
    """Small-signal Coss at bias `v`, log-log interpolated between knots."""
    pts = COSS[part]
    v = max(v, pts[0][0] if pts[0][0] > 0 else 1e-3)
    if v <= pts[0][0]:
        return pts[0][1]
    if v >= pts[-1][0]:
        return pts[-1][1]
    for (v0, c0), (v1, c1) in zip(pts, pts[1:]):
        if v0 <= v <= v1:
            if v0 <= 0:
                return c0 + (c1 - c0) * (v - v0) / (v1 - v0)
            t = math.log(v / v0) / math.log(v1 / v0)
            return c0 * (c1 / c0) ** t
    return pts[-1][1]


def qoss_nc(part: str, v_lo: float, v_hi: float, n: int = 400) -> float:
    """Charge moved on Coss between two biases, nC (trapezoid on a log grid)."""
    lo = max(v_lo, 1e-3)
    step = (v_hi / lo) ** (1.0 / n)
    q = 0.0
    v = lo
    for _ in range(n):
        v2 = v * step
        q += 0.5 * (coss_pf(part, v) + coss_pf(part, v2)) * (v2 - v)
        v = v2
    return q * 1e-3  # pF*V -> nC


def c_eff_pf(part: str, v_center: float, v_swing: float) -> float:
    """Charge chord Qoss/dV over the ring excursion v_center +/- v_swing.

    OPEN QUESTION -- do not treat this as settled. For a resonator with a
    strongly nonlinear C(v) the period-equivalent capacitance is defined by the
    exact anharmonic period integral, and it is not obvious that the charge
    chord is it. The No-Coil study endorses the chord (...:306-308) and it is
    certainly right to reject the 0->V charge equivalent (+120% here), but a
    reviewer's independent integration put the chord 4-9% low and the plain
    small-signal Coss(v_center) within 1% -- my own attempt to reproduce that
    had a broken integrator, so neither model is confirmed.

    A second, separate defect: callers pass the chord over [Vin, Vpk] only,
    i.e. the UPPER excursion. The ring swings below Vin as well, into steeply
    higher Coss, and that half is currently ignored.

    Both issues bias `bias`'s per-point L in a bias-dependent way, so they do
    NOT cancel in the fit. `dfreq` is immune -- it uses no datasheet Coss.
    """
    lo = max(v_center - v_swing, 0.5)
    hi = v_center + v_swing
    if hi <= lo:
        return coss_pf(part, v_center)
    return qoss_nc(part, lo, hi) * 1e3 / (hi - lo)


def f_ring_hz(l_nh: float, c_pf: float) -> float:
    return 1.0 / (2 * math.pi * math.sqrt(l_nh * 1e-9 * c_pf * 1e-12))


def l_from_f_nh(f_hz: float, c_pf: float) -> float:
    return 1.0 / ((2 * math.pi * f_hz) ** 2 * c_pf * 1e-12) * 1e9


def z0(l_nh: float, c_pf: float) -> float:
    return math.sqrt((l_nh * 1e-9) / (c_pf * 1e-12))


def tanks(build: str, vin: float, swing: float):
    """(label, part, n, C_tank_pF) for the turn-on and turn-off rings."""
    b = BUILDS[build]
    out = []
    for label, key in (("HS turn-ON  (loud)", "ls"), ("HS turn-OFF (quiet)", "hs")):
        part, n = b[key]
        out.append((label, part, n, n * c_eff_pf(part, vin, swing)))
    return out


def cmd_predict(a):
    print(f"build={a.build}  Vin={a.vin:g} V  ring swing +/-{a.swing:g} V\n")
    for l_nh, tag in ((L_ANCHOR_NH, "bench-reconciled anchor"),
                      (L_COPPER_NH + L_LEADS_NH, "golden copper + leads")):
        print(f"L_loop = {l_nh:.1f} nH  [{tag}]")
        print(f"  {'edge':22} {'FET':16} {'C_tank':>9} {'f_ring':>9} {'Z0':>7} {'dV@Icomm':>9}")
        for label, part, n, c in tanks(a.build, a.vin, a.swing):
            f = f_ring_hz(l_nh, c)
            zz = z0(l_nh, c)
            print(f"  {label:22} {n}x {part:13} {c:6.0f} pF {f/1e6:6.1f} MHz "
                  f"{zz:5.2f} R {zz*a.icomm:6.1f} V")
        print()
    print("dV@Icomm is the hard-commutation bound Z0*I -- an upper bound on overshoot;")
    print("real Miller/gate-charge feedback couples only a fraction of I into the tank.")


def cmd_bias(a):
    """Fit ONE loop inductance to the measured f_ring-vs-bias series.

    This is the cheap half of breaking the L/C degeneracy. A single frequency
    admits a one-parameter family of (L, C) -- the trap that produced the
    retracted "solved at 8.2 nH" claim. Three biases do not: the datasheet
    Coss curve fixes the C *ratios*, so a single L must reproduce all three
    frequencies or the loop model is wrong. It still inherits the datasheet
    Coss's absolute accuracy -- `dfreq` is what removes that dependence.
    """
    part, n = BUILDS[a.build]["ls"]
    print(f"build={a.build}   LS tank = {n}x {part}\n")
    print(f"  {'Vin':>5} {'V_pk':>6} {'chord C':>9} {'f_meas':>9} {'L implied':>11}")
    ls = []
    for vin, f, vpk in a.points:
        c = c_eff_pf(part, 0.5 * (vin + vpk), 0.5 * (vpk - vin)) * n
        l = l_from_f_nh(f, c)
        ls.append(l)
        print(f"  {vin:5.0f} {vpk:6.0f} {c:6.0f} pF {f/1e6:6.1f} MHz {l:8.2f} nH")
    l_fit = sum(ls) / len(ls)
    spread = (max(ls) - min(ls)) / l_fit
    print(f"\n  best single L = {l_fit:.2f} nH   (spread {spread*100:.1f}%)\n")
    print(f"  {'Vin':>5} {'f_meas':>9} {'f @ L_fit':>11} {'err':>7}")
    for (vin, f, vpk), _ in zip(a.points, ls):
        c = c_eff_pf(part, 0.5 * (vin + vpk), 0.5 * (vpk - vin)) * n
        fp = f_ring_hz(l_fit, c)
        print(f"  {vin:5.0f} {f/1e6:6.1f} MHz {fp/1e6:8.1f} MHz {100*(fp-f)/f:+6.1f}%")
    print(f"\n  vs anchor {L_ANCHOR_NH} nH (4 copper + 1 drain + 4 source CSI): "
          f"{l_fit/L_ANCHOR_NH:.2f}x")
    print(f"  vs 8.2 nH out_cinnet copper + 5 nH leads = 13.2 nH: {l_fit/13.2:.2f}x")


def cmd_dfreq(a):
    """External-cap delta-f test -- the non-circular L/C separation.

    Solder a known C0G across the switch node, re-measure the ring, and both
    unknowns fall out with no reliance on the datasheet Coss at all:
        (2*pi*f1)^-2 = L*C          (2*pi*f2)^-2 = L*(C + Cadd)
        => C = Cadd / ((f1/f2)^2 - 1),   L = 1 / ((2*pi*f1)^2 * C)
    This is open item #1 in doc/"No-Coil SW Ring (Bench vs SPICE).md".
    """
    if a.f2 is None:
        part, n = BUILDS[a.build]["ls"]
        c = c_eff_pf(part, a.vin, a.swing) * n
        l = a.l_nh
        f1 = f_ring_hz(l, c)
        print(f"PLAN  build={a.build}  expected C_tank {c:.0f} pF, L {l:g} nH\n")
        print(f"  {'C_add':>8} {'f1':>9} {'f2':>9} {'shift':>8}  note")
        for cadd in (100, 220, 470, 1000, 2200):
            f2 = f_ring_hz(l, c + cadd)
            note = "" if 0.55 < f2 / f1 < 0.85 else "  (too small/large a step)"
            print(f"  {cadd:5d} pF {f1/1e6:6.1f} MHz {f2/1e6:6.1f} MHz "
                  f"{100*(f2/f1-1):+7.1f}%{note}")
        print("\n  Aim for a 20-45% shift: big enough to beat cursor error, small")
        print("  enough that C_add stays >> its own parasitics and the tank Q survives.")
        print("  Use C0G/NP0 (X7R loses most of its value at 60 V DC bias), and mount")
        print("  it exactly where the ring is -- drain tab to source, shortest path.")
        print("  Its own ESL adds to L, so keep the package small (0402/0603) and")
        print("  treat the extracted L as an upper bound by ~0.5-1 nH.")
        return
    ratio2 = (a.f1 / a.f2) ** 2
    if ratio2 <= 1.0:
        raise SystemExit("f2 must be BELOW f1 (adding C lowers the ring)")
    c = a.c_add / (ratio2 - 1.0)
    l = l_from_f_nh(a.f1, c)
    print(f"SOLVE  f1={a.f1/1e6:g} MHz  f2={a.f2/1e6:g} MHz  C_add={a.c_add:g} pF\n")
    print(f"  C_tank = {c:7.0f} pF   (no datasheet Coss used)")
    print(f"  L_loop = {l:7.2f} nH   (includes C_add's own ESL -> upper bound)")
    print(f"  Z0     = {z0(l, c):7.2f} ohm")
    part, n = BUILDS[a.build]["ls"]
    c_ds = c_eff_pf(part, a.vin, a.swing) * n
    print(f"\n  datasheet chord C for {n}x {part} at {a.vin:g}+/-{a.swing:g} V: "
          f"{c_ds:.0f} pF ({100*(c/c_ds-1):+.0f}%)")
    print(f"  anchor L {L_ANCHOR_NH} nH: {l/L_ANCHOR_NH:.2f}x")


def cmd_solve(a):
    print("WARNING: one frequency cannot pin L -- f = 1/2pi*sqrt(LC) has a")
    print("one-parameter family of solutions, and this is exactly how the")
    print("retracted 'solved at 8.2 nH' claim happened. Use `dfreq` or `bias`.\n")
    print(f"build={a.build}  Vin={a.vin:g} V  measured f_ring={a.f_ring/1e6:g} MHz\n")
    print(f"  {'assumed edge':22} {'FET':16} {'C_tank':>9} {'L_loop':>9}  vs anchor")
    for label, part, n, c in tanks(a.build, a.vin, a.swing):
        l = l_from_f_nh(a.f_ring, c)
        print(f"  {label:22} {n}x {part:13} {c:6.0f} pF {l:6.1f} nH  "
              f"{l/L_ANCHOR_NH:5.2f}x")
    print(f"\nTake the row whose L lands near the {L_ANCHOR_NH} nH anchor to identify")
    print("which edge you are looking at -- but see the warning above.")


def cmd_snub(a):
    l_nh = a.l_nh
    print(f"build={a.build}  Vin={a.vin:g} V  L_loop={l_nh:g} nH  "
          f"fsw={a.fsw/1e3:g} kHz  Cs = k*C_tank\n")
    for label, part, n, c in tanks(a.build, a.vin, a.swing):
        print(f"{label}  ({n}x {part}, C_tank={c:.0f} pF)")
        print(f"  {'k':>4} {'Cs':>9} {'Rs':>8} {'f_damped':>10} {'P_snub':>9}  E12 pick")
        for k in (1.0, 2.0, 3.0, 4.0):
            cs = k * c
            rs = math.sqrt((l_nh * 1e-9) / (c * 1e-12))
            fd = f_ring_hz(l_nh, c + cs)
            p = cs * 1e-12 * a.vin ** 2 * a.fsw
            print(f"  {k:4.0f} {cs:6.0f} pF {rs:5.2f} R {fd/1e6:7.1f} MHz {p:6.2f} W"
                  f"   {_e12(cs):>6.0f}pF/{_e12(rs):g}R")
        print()
    print("Rs = sqrt(L/C_tank) = Z0 of the UNDAMPED tank -- the impedance-matching rule")
    print("from the Toshiba app note in doc/EMI Parasitics Snubbers.md. Solving the")
    print("actual L-C||(Rs+Cs) cubic, this is within a few % of the damping optimum")
    print("for k>=2. sqrt(L/(C_tank+Cs)) -- an earlier version of this script -- is")
    print("~2x too low and delivers about half the damping. P_snub = Cs*Vin^2*fsw")
    print("(both edges dissipate, hence V^2 not V^2/2). Size the resistor for >=2x")
    print("that, and check its pulse rating: each edge is a ~Vin/Rs amp spike.")


def _e12(x):
    """Nearest E12 value, same decade."""
    e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2, 10.0]
    d = 10 ** math.floor(math.log10(x))
    m = x / d
    return d * min(e12, key=lambda v: abs(math.log(v / m)))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--build", choices=sorted(BUILDS), default="measured")
    p.add_argument("--vin", type=float, default=72.0, help="switch-node plateau, V")
    p.add_argument("--swing", type=float, default=10.0,
                   help="ring amplitude +/- V, sets the charge-equivalent Coss")
    p.add_argument("--icomm", type=float, default=33.0, help="commutated current, A")
    p.add_argument("--fsw", type=float, default=39e3)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("predict", help="L_loop -> f_ring (do this before the bench)")
    sp.set_defaults(fn=cmd_predict)

    sb = sub.add_parser("bias", help="fit one L to the measured f(Vin) series")
    sb.add_argument("points", nargs="*", metavar="Vin,f_Hz,Vpk",
                    help="default: the three bench points from the No-Coil doc")
    sb.set_defaults(fn=cmd_bias)

    sd = sub.add_parser("dfreq", help="external-cap delta-f test: plan, or solve L and C")
    sd.add_argument("--l-nh", type=float, default=L_ANCHOR_NH)
    sd.add_argument("--f1", type=float, help="ring without the added cap, Hz")
    sd.add_argument("--f2", type=float, default=None, help="ring with the added cap, Hz")
    sd.add_argument("--c-add", type=float, default=470.0, help="added C0G, pF")
    sd.set_defaults(fn=cmd_dfreq)

    ss = sub.add_parser("solve", help="measured f_ring -> L_loop")
    ss.add_argument("f_ring", type=float, help="Hz, e.g. 33e6")
    ss.set_defaults(fn=cmd_solve)

    sn = sub.add_parser("snub", help="L_loop -> RC snubber values")
    sn.add_argument("--l-nh", type=float, default=L_ANCHOR_NH)
    sn.set_defaults(fn=cmd_snub)

    a = p.parse_args()
    if getattr(a, "cmd", None) == "bias":
        a.points = ([tuple(float(x) for x in s.split(",")) for s in a.points]
                    or BENCH_RING)
    a.fn(a)


if __name__ == "__main__":
    main()
