#!/usr/bin/env python3
"""Reconnaissance: dump power-net geometry from Fugu2.kicad_pcb.

Run with KiCad's bundled python (has pcbnew):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 recon.py

Read-only. Prints a summary of tracks, vias, zones and pads on the power nets
(Solar+, SW, BuckGND, GND) plus the power-device footprints, so we can design
the FastHenry extractor with real numbers instead of guesses.
"""
import pcbnew

PCB = "/Users/fab/Documents/open.pe/hw/Fugu2/Fugu2.kicad_pcb"
POWER_NETS = ["Solar+", "SW", "BuckGND", "GND"]


def mm(v):
    return pcbnew.ToMM(v)


def main():
    board = pcbnew.LoadBoard(PCB)
    ni = board.GetNetInfo()
    netcodes = {}
    for name in POWER_NETS:
        net = ni.GetNetItem(name)
        netcodes[name] = net.GetNetCode() if net else None
    print("net codes:", netcodes)
    code2name = {c: n for n, c in netcodes.items() if c is not None}

    # ---- tracks & vias ----
    from collections import defaultdict
    tcount = defaultdict(int)
    vcount = defaultdict(int)
    widths = defaultdict(set)
    tlen = defaultdict(float)
    for t in board.GetTracks():
        code = t.GetNetCode()
        if code not in code2name:
            continue
        name = code2name[code]
        if t.Type() == pcbnew.PCB_VIA_T:
            vcount[name] += 1
        else:
            tcount[name] += 1
            widths[name].add(round(mm(t.GetWidth()), 3))
            tlen[name] += mm(t.GetLength())
    for name in POWER_NETS:
        print(f"\n[{name}] tracks={tcount[name]} totlen={tlen[name]:.1f}mm "
              f"vias={vcount[name]} widths(mm)={sorted(widths[name])}")

    # ---- zones ----
    print("\n=== ZONES on power nets ===")
    for z in board.Zones():
        code = z.GetNetCode()
        if code not in code2name:
            continue
        layers = [board.GetLayerName(l) for l in z.GetLayerSet().Seq()]
        area = 0.0
        try:
            area = mm(mm(z.GetFilledArea()))
        except Exception:
            pass
        print(f"  zone net={code2name[code]:8} layers={layers} "
              f"outline_pts={z.Outline().Outline(0).PointCount() if z.Outline().OutlineCount() else 0} "
              f"fill_area~={area:.0f}mm^2")

    # ---- power device footprints ----
    print("\n=== power footprints (Q1..Q6, big caps, D3) ===")
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        fpid = fp.GetFPID().GetLibItemName().wx_str()
        is_pwr = (ref in ("D3",) or ref.startswith("Q")
                  or "TO-" in fpid or "TO_" in fpid or "CP_Radial" in fpid)
        if not is_pwr:
            continue
        cx, cy = mm(fp.GetPosition().x), mm(fp.GetPosition().y)
        layer = board.GetLayerName(fp.GetLayer())
        pads = []
        for p in fp.Pads():
            pc = p.GetNetCode()
            pname = code2name.get(pc, p.GetNetname())
            px, py = mm(p.GetPosition().x), mm(p.GetPosition().y)
            pads.append(f"{p.GetPadName()}:{pname}@({px:.1f},{py:.1f})")
        print(f"  {ref:4} {fpid:32} layer={layer} pos=({cx:.1f},{cy:.1f})")
        print(f"        pads: {', '.join(pads)}")


if __name__ == "__main__":
    main()
