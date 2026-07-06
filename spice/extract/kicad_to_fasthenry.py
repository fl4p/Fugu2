#!/usr/bin/env python3
"""Extract the Fugu2 buck commutation-loop copper into a FastHenry model.

Run with KiCad's bundled python (has pcbnew):
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
  "$KPY" kicad_to_fasthenry.py [--pitch 1.0] [--out loop.inp]

Model (see plan + channel discussion):
  * Power nets Solar+, SW, BuckGND on F.Cu (z=0) and B.Cu (z=-Z_SEP) are the
    current-carrying copper (the pours dominate; thin signal tracks ignored).
  * Each (net,layer) filled zone polygon is meshed into a filament grid clipped
    to the real polygon at PITCH -> captures current crowding / spreading L.
  * Vias stitch F.Cu<->B.Cu meshes of the same net.
  * Switches are ideal-ish device *bridges* (short segments across drain->source
    pads) so loop L = copper + via + pad geometry.  FET package internal L is
    added SEPARATELY in LTspice, NOT here (FastHenry only sees copper).
  * ONE model, all conductors present, so HS<->LS and return mutuals are captured.
  * Port (.external) across the closest HF ceramic (C16) to the switches ->
    Im(Z)/w is the commutation-loop inductance seen by that cap.

The layout is a compact SMD half-bridge (Infineon PG-TDSON-8) on B.Cu:
  HS = Q1 || Q3 (Solar+ -> SW),  LS = Q2 (SW -> BuckGND),
  LS rectifiers D9 (TO-220 horiz) + D16 (TO-277) parallel Q2 (SW -> BuckGND).
"""
import argparse
import math
import sys

import pcbnew

PCB = "/Users/fab/Documents/open.pe/hw/Fugu2/Fugu2.kicad_pcb"

# --- physical constants / stackup (verified from board) ---
CU_T = 0.035          # copper thickness [mm] (1 oz)
Z_SEP = 1.545         # F.Cu->B.Cu centerline separation [mm] (1.51 diel + 0.035 cu)
SIGMA = 5.8e4         # copper conductivity [1/(mm*Ohm)] = 5.8e7 S/m
Z_F = 0.0
Z_B = -Z_SEP

# --- region of interest: the commutation cluster (mm) --------------------
# Covers Q1/Q2/Q3 (HS/LS), D9/D16 (LS rect), and HF ceramics C16..C22/C27.
ROI = dict(x0=28.0, y0=38.0, x1=56.0, y1=72.0)

NETS = ["Solar+", "SW", "BuckGND"]
LAYERS = [("F.Cu", Z_F), ("B.Cu", Z_B)]

# Device bridges: (ref, padnet_a, padnet_b) shorted drain->source for loop meas.
# TO-220 D9 additionally gets a vertical lead stub (see LEAD_STUB).
HS_FETS = ["Q1", "Q3"]                 # Solar+ -> SW
# D9/D16 are DNP, so the physically-correct LS bridge is Q2 only. But the SW pour
# is fragmented in the mesh and the HS-side / Q2-side SW fragments were only joined
# through the diode copper -> Q2-only currently disconnects the port (the
# connectivity prune reports this cleanly). Until the SW-mesh connectivity is
# fixed, run the full set: this ADDS parallel LS paths that aren't populated, so it
# slightly UNDER-estimates the loop L (real Q2-only L is a bit higher). Since the
# FET leads (~9nH) dominate the ~13nH loop, this <1nH copper difference is minor.
LS_DEVS = ["Q2", "D16", "D9"]          # SW -> BuckGND  (see DNP caveat above)
LEAD_STUB = {"D9": 4.0}                # extra vertical lead length [mm] for THT parts

# Port: inject across the closest HF ceramic to the switches.
PORT_CAP = "C16"                       # 0805, B.Cu, Solar+ | BuckGND


def mm(v):
    return pcbnew.ToMM(v)


def nm(v):
    return pcbnew.FromMM(v)


def in_roi(x, y):
    return ROI["x0"] <= x <= ROI["x1"] and ROI["y0"] <= y <= ROI["y1"]


class Model:
    def __init__(self, pitch):
        self.pitch = pitch
        self.nodes = {}       # name -> (x,y,z)
        self.segs = []        # (name, na, nb, w, extra)
        self.externals = []   # (np, nn, portname)
        self._seg_i = 0
        # per (net,layer) grid: (i,j) -> node name, plus origin
        self.grids = {}
        # global cell ownership (i,j,layer) -> net, so no two nets ever place
        # coincident nodes (identical x,y,z => singular mutual L => NaN).
        self.occupied = {}

    def node(self, name, x, y, z):
        if name not in self.nodes:
            self.nodes[name] = (x, y, z)
        return name

    def seg(self, na, nb, w, extra=""):
        self._seg_i += 1
        self.segs.append((f"E{self._seg_i}", na, nb, w, extra))

    # --- unified grid meshing: zones + tracks + pads all onto one grid ---
    def mesh_net_layer(self, board, net, netcode, layer_name, z):
        lid = board.GetLayerID(layer_name)
        P = self.pitch
        x0, y0, x1, y1 = ROI["x0"], ROI["y0"], ROI["x1"], ROI["y1"]
        nx = int(math.ceil((x1 - x0) / P)) + 1
        ny = int(math.ceil((y1 - y0) / P)) + 1
        pfx = f"N_{net.replace('+','p').replace(' ','')}_{layer_name.replace('.','')}"
        grid = {}
        self.grids[(net, layer_name)] = dict(origin=(x0, y0), P=P, cells=grid, z=z)

        def cell(x, y):
            return (int(round((x - x0) / P)), int(round((y - y0) / P)))

        def activate(i, j):
            if not (0 <= i < nx and 0 <= j < ny):
                return None
            if (i, j) not in grid:
                owner = self.occupied.get((i, j, layer_name))
                if owner is not None and owner != net:
                    return None  # cell already belongs to another net on this layer
                self.occupied[(i, j, layer_name)] = net
                name = f"{pfx}_{i}_{j}"
                self.node(name, x0 + i * P, y0 + j * P, z)
                grid[(i, j)] = name
            return grid[(i, j)]

        # (a) zone fill -> activate cells whose centre is inside copper
        polys = []
        for zone in board.Zones():
            if zone.GetNetCode() != netcode:
                continue
            ps = zone.GetFilledPolysList(lid)
            if ps.OutlineCount():
                polys.append(ps)

        def inside(x, y):
            pt = pcbnew.VECTOR2I(nm(x), nm(y))
            return any(ps.Contains(pt) for ps in polys)

        for i in range(nx):
            for j in range(ny):
                x, y = x0 + i * P, y0 + j * P
                if inside(x, y):
                    activate(i, j)

        # (b) tracks -> walk centreline, chain nearest cells (guarantees the
        #     narrow connections, e.g. HS source track down to the SW pour).
        #     Track edges are recorded with their real width; grid-plane edges
        #     get width ~pitch. A dedup set prevents double-counting copper.
        edges = {}  # frozenset({cellA,cellB}) -> width

        def add_edge(ca, cb, w):
            if ca == cb:
                return
            k = frozenset((ca, cb))
            edges[k] = max(edges.get(k, 0.0), w)

        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T or t.GetNetCode() != netcode:
                continue
            if board.GetLayerName(t.GetLayer()) != layer_name:
                continue
            ax, ay = mm(t.GetStart().x), mm(t.GetStart().y)
            bx, by = mm(t.GetEnd().x), mm(t.GetEnd().y)
            if not (in_roi(ax, ay) or in_roi(bx, by)):
                continue
            tw = max(mm(t.GetWidth()), 0.15)
            L = math.hypot(bx - ax, by - ay)
            steps = max(1, int(math.ceil(L / (P / 2))))
            prev = None
            for s in range(steps + 1):
                fr = s / steps
                x, y = ax + (bx - ax) * fr, ay + (by - ay) * fr
                c = cell(x, y)
                if activate(*c) is None:
                    continue
                if prev is not None and prev != c:
                    # Manhattan route prev->c so every in-plane segment stays
                    # axis-aligned (avoids FastHenry non-orthogonal-overlap NaNs).
                    (pi, pj), (ci, cj) = prev, c
                    if pi != ci and pj != cj:
                        mid = (ci, pj)
                        if activate(*mid) is not None:
                            add_edge(prev, mid, tw)
                            add_edge(mid, c, tw)
                        prev = c
                        continue
                    add_edge(prev, c, tw)
                prev = c

        # (c) pads of this net on this layer -> ensure a live cell under each
        for fp in board.GetFootprints():
            fp_layer = "B.Cu" if fp.IsFlipped() else "F.Cu"
            if fp_layer != layer_name:
                continue
            for p in fp.Pads():
                if p.GetNetCode() != netcode:
                    continue
                px, py = mm(p.GetPosition().x), mm(p.GetPosition().y)
                if in_roi(px, py):
                    activate(*cell(px, py))

        # 4-neighbour connect over ALL active cells (pour continuity)
        for (i, j) in list(grid.keys()):
            for di, dj in ((1, 0), (0, 1)):
                if (i + di, j + dj) in grid:
                    add_edge((i, j), (i + di, j + dj), P * 0.9)

        for k, w in edges.items():
            a, b = tuple(k)
            self.seg(grid[a], grid[b], w, f"* {net}/{layer_name}")
        return len(grid)

    def nearest(self, net, layer_name, x, y):
        """Nearest grid node of (net,layer) to (x,y). Returns node name or None."""
        g = self.grids.get((net, layer_name))
        if not g:
            return None
        x0, y0 = g["origin"]
        P = g["P"]
        i0 = int(round((x - x0) / P))
        j0 = int(round((y - y0) / P))
        best = None
        bestd = 1e9
        R = 10  # search radius in cells
        for di in range(-R, R + 1):
            for dj in range(-R, R + 1):
                nb = g["cells"].get((i0 + di, j0 + dj))
                if nb:
                    nx_, ny_, _ = self.nodes[nb]
                    d = (nx_ - x) ** 2 + (ny_ - y) ** 2
                    if d < bestd:
                        bestd, best = d, nb
        return best


def find_pad(board, ref, want_net):
    """Return (x,y,layer_name) of the first electrical pad of `ref` on `want_net`."""
    fp = board.FindFootprintByReference(ref)
    if not fp:
        return None
    for p in fp.Pads():
        if p.GetNetname() == want_net:
            x, y = mm(p.GetPosition().x), mm(p.GetPosition().y)
            # a pad may span layers; use footprint side for the copper layer
            layer = "B.Cu" if fp.IsFlipped() else "F.Cu"
            return (x, y, layer)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pitch", type=float, default=1.0, help="mesh pitch [mm]")
    ap.add_argument("--out", default="loop.inp")
    # default = just the HF plateau (2 pts): the preconditioner is rebuilt per
    # frequency, so fewer freqs is a near-linear speedup. Use --full for L(f).
    ap.add_argument("--fmin", default="1e7")
    ap.add_argument("--fmax", default="1e8")
    ap.add_argument("--ndec", default="1")
    ap.add_argument("--full", action="store_true",
                    help="full 100kHz-100MHz L(f) sweep (fmin=1e5 ndec=3)")
    ap.add_argument("--nwinc", type=int, default=3,
                    help="width-wise skin-effect filaments per segment")
    ap.add_argument("--port-cap", default=PORT_CAP,
                    help="ref of the ceramic to excite the loop across")
    ap.add_argument("--ls-devs", default=",".join(LS_DEVS),
                    help="comma list of LS SW->BuckGND bridges (e.g. Q2 for "
                         "sync-FET only, vs Q2,D16,D9 incl. freewheel diodes)")
    args = ap.parse_args()
    port_cap = args.port_cap
    ls_devs = [d for d in args.ls_devs.split(",") if d]
    if args.full:
        args.fmin, args.fmax, args.ndec = "1e5", "1e8", "3"

    board = pcbnew.LoadBoard(PCB)
    ni = board.GetNetInfo()
    codes = {n: ni.GetNetItem(n).GetNetCode() for n in NETS}

    m = Model(args.pitch)

    # 1) mesh the three power zones on both layers
    stats = {}
    for net in NETS:
        for lname, z in LAYERS:
            n = m.mesh_net_layer(board, net, codes[net], lname, z)
            if n:
                stats[(net, lname)] = n

    # 2) vias stitch F.Cu<->B.Cu meshes of the same net
    nvia = 0
    for t in board.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T:
            continue
        net = t.GetNetname()
        if net not in NETS:
            continue
        x, y = mm(t.GetPosition().x), mm(t.GetPosition().y)
        if not in_roi(x, y):
            continue
        nf = m.nearest(net, "F.Cu", x, y)
        nb = m.nearest(net, "B.Cu", x, y)
        if nf and nb:
            m.seg(nf, nb, 0.3, f"* via {net}")  # thin barrel (avoids overlap)
            nvia += 1

    # 3) device bridges (switches shorted for loop-L measurement)
    def bridge(ref, net_a, net_b, tag):
        pa = find_pad(board, ref, net_a)
        pb = find_pad(board, ref, net_b)
        if not (pa and pb):
            print(f"  ! {ref}: pad {net_a}/{net_b} not found", file=sys.stderr)
            return
        na = m.nearest(net_a, pa[2], pa[0], pa[1])
        nb = m.nearest(net_b, pb[2], pb[0], pb[1])
        if not (na and nb):
            print(f"  ! {ref}: no mesh node near pads", file=sys.stderr)
            return
        stub = LEAD_STUB.get(ref, 0.0)
        if stub:
            # raise both pad connections by a vertical lead stub (THT lead)
            za = m.nodes[na][2]
            ta = m.node(f"N_{ref}_a_top", pa[0], pa[1], za + stub)
            tb = m.node(f"N_{ref}_b_top", pb[0], pb[1], za + stub)
            m.seg(na, ta, 0.4, f"* {ref} lead A")
            m.seg(nb, tb, 0.4, f"* {ref} lead B")
            na, nb = ta, tb
        m.seg(na, nb, 0.5, f"* device bridge {tag} ({ref})")

    for q in HS_FETS:
        bridge(q, "Solar+", "SW", "HS")
    for d in ls_devs:
        bridge(d, "SW", "BuckGND", "LS")

    # 4) port across the closest HF ceramic
    pp = find_pad(board, port_cap, "Solar+")
    pn = find_pad(board, port_cap, "BuckGND")
    if not (pp and pn):
        sys.exit(f"port cap {port_cap} pads not found")
    np_ = m.nearest("Solar+", pp[2], pp[0], pp[1])
    nn_ = m.nearest("BuckGND", pn[2], pn[0], pn[1])
    if not (np_ and nn_):
        sys.exit(f"no mesh node near {port_cap} pads (check ROI/pitch)")
    m.externals.append((np_, nn_, "loop"))

    # --- connectivity prune: keep only the mesh reachable from the port ---
    # Floating copper islands (e.g. SW/BuckGND fragments left dangling once the
    # DNP D9/D16 bridges are gone) make FastHenry singular -> NaN. Drop them.
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r
    for en, na, nb, w, extra in m.segs:
        parent[find(na)] = find(nb)
    root = find(np_)
    if find(nn_) != root:
        sys.exit("port + and - are not connected (check device bridges)")
    kept = len(m.nodes)
    m.segs = [s for s in m.segs if find(s[1]) == root and find(s[2]) == root]
    m.nodes = {n: v for n, v in m.nodes.items() if find(n) == root}
    print(f"  connectivity prune: kept {len(m.nodes)}/{kept} nodes "
          f"(dropped {kept-len(m.nodes)} floating)")

    # --- write FastHenry input ---
    with open(args.out, "w") as f:
        f.write(f"* Fugu2 commutation-loop parasitic extraction\n")
        f.write(f"* pitch={args.pitch}mm  port across {port_cap}  ROI={ROI}\n")
        f.write(".units mm\n")
        # nhinc=2: 35um Cu is <2 skin depths at 10-100MHz, so a couple of
        # height filaments captures the thickness-wise skin effect cheaply.
        f.write(f".default sigma={SIGMA:g} nwinc={args.nwinc} nhinc=2 h={CU_T}\n\n")
        for name, (x, y, z) in m.nodes.items():
            f.write(f"{name} x={x:.4f} y={y:.4f} z={z:.4f}\n")
        f.write("\n")
        # NB: FastHenry does not allow trailing comments on element lines.
        for en, na, nb, w, extra in m.segs:
            f.write(f"{en} {na} {nb} w={w:.4f} h={CU_T}\n")
        f.write("\n")
        for np_, nn_, pn_ in m.externals:
            f.write(f".external {np_} {nn_} {pn_}\n")
        f.write(f".freq fmin={args.fmin} fmax={args.fmax} ndec={args.ndec}\n")
        f.write(".end\n")

    print(f"wrote {args.out}")
    print(f"  nodes={len(m.nodes)} segs={len(m.segs)} vias={nvia}")
    print(f"  mesh cells per (net,layer): "
          + ", ".join(f"{k[0]}/{k[1]}={v}" for k, v in stats.items()))
    print(f"  port: {m.externals[0][0]} -> {m.externals[0][1]}")


if __name__ == "__main__":
    main()
