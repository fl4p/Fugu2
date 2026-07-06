#!/usr/bin/env python3
"""Render exactly what FastHenry sees, colored by net — the best parse-bug catcher.

Parses a loop*.inp and draws every segment (in-plane copper, vias, device
bridges) colored by net/type, with the excitation port marked. Run with system
python3 (needs matplotlib):

  python3 debug_plot.py loop_p1.0.inp [out.png]
"""
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NET_COLOR = {"Solarp": "#d62728", "SW": "#2ca02c", "BuckGND": "#1f77b4"}


def net_of(nodename):
    m = re.match(r"N_([A-Za-z]+)_", nodename)
    return m.group(1) if m else "?"


def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "loop_p1.0.inp"
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace(".inp", ".png")
    nodes, segs, ext = {}, [], []
    for line in open(inp):
        s = line.strip()
        m = re.match(r"(N\S+)\s+x=([-\d.]+)\s+y=([-\d.]+)\s+z=([-\d.]+)", s)
        if m:
            nodes[m[1]] = (float(m[2]), float(m[3]), float(m[4]))
            continue
        m = re.match(r"E\d+\s+(N\S+)\s+(N\S+)\s+w=([\d.]+)", s)
        if m:
            segs.append((m[1], m[2], float(m[3])))
            continue
        m = re.match(r"\.external\s+(N\S+)\s+(N\S+)", s)
        if m:
            ext.append((m[1], m[2]))

    fig, ax = plt.subplots(figsize=(11, 12))
    drawn_labels = set()
    for a, b, w in segs:
        if a not in nodes or b not in nodes:
            continue
        (xa, ya, za), (xb, yb, zb) = nodes[a], nodes[b]
        na, nb = net_of(a), net_of(b)
        if za != zb:                                   # via (vertical)
            ax.plot(xa, ya, "x", color="purple", ms=5,
                    label="via" if "via" not in drawn_labels else None)
            drawn_labels.add("via")
        elif na != nb:                                 # device bridge
            ax.plot([xa, xb], [ya, yb], color="black", lw=2.2,
                    label="device bridge" if "bridge" not in drawn_labels else None)
            drawn_labels.add("bridge")
        else:                                          # in-plane copper
            c = NET_COLOR.get(na, "gray")
            ls = "-" if za == 0 else "--"              # F.Cu solid, B.Cu dashed
            lbl = f"{na} ({'F.Cu' if za==0 else 'B.Cu'})"
            ax.plot([xa, xb], [ya, yb], color=c, lw=max(0.5, w), ls=ls, alpha=0.5,
                    label=lbl if lbl not in drawn_labels else None)
            drawn_labels.add(lbl)
    for p, n in ext:
        for node, mk in ((p, "^"), (n, "v")):
            x, y, _ = nodes[node]
            ax.plot(x, y, mk, color="orange", ms=14, mec="k",
                    label="PORT" if "PORT" not in drawn_labels else None)
            drawn_labels.add("PORT")

    ax.set_aspect("equal")
    ax.invert_yaxis()                                  # KiCad y-down
    ax.set_title(f"FastHenry geometry — {inp}\n(solid=F.Cu, dashed=B.Cu, "
                 "black=device bridge, x=via, orange=port)")
    ax.set_xlabel("x [mm]"); ax.set_ylabel("y [mm]")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"wrote {out}  ({len(nodes)} nodes, {len(segs)} segs)")


if __name__ == "__main__":
    main()
