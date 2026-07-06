#!/usr/bin/env python3
"""Digitize the ST15100S Figure-1 forward curves (25C and 125C) from the
datasheet raster, adapting the gridline-mask + dark-run tracing approach from
pwr-mosfet-lib/dslib/viz/raster_extract.py.

Two curves separate cleanly by VF at each current level (125C always the
lower-VF / left curve), so we trace by ROW: for each current gridline-row we
take the leftmost dark run = 125C and the rightmost = 25C. The in-chart
"125C"/"25C" label boxes are solid rectangles removed by a connected-component
fill-ratio filter (thin curves survive, filled boxes don't).

Calibration (from detected gridlines, 400 dpi crop f1_hi.png):
  VF(col) = 0.2 + (col-184)/1136.667      # linear, 0.1V per 113.67px
  IF(row) = 10**((1796-row)/922.0)        # log, decade=922px, 1A at row 1796
"""
import numpy as np
from PIL import Image
from scipy import ndimage

import os
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "reference", "ST15100S_fig1_forward_400dpi.png")
COL0, VPP = 184, 1136.667      # col of 0.2V, px per volt
ROW1, DEC = 1796.0, 922.0      # row of 1A, px per decade

def vf(col): return 0.2 + (col - COL0) / VPP
def iff(row): return 10 ** ((ROW1 - row) / DEC)

def main():
    im = np.asarray(Image.open(IMG).convert("L")).astype(np.int32)
    h, w = im.shape
    dark = im < 128

    # 1) strip gridlines/borders (rows/cols with high dark coverage)
    rowc, colc = dark.sum(1), dark.sum(0)
    bad_r = rowc > 0.45 * w
    bad_c = colc > 0.45 * h
    m = dark.copy()
    m[bad_r, :] = False
    m[:, bad_c] = False

    # 2) remove solid label boxes: connected comps with high bbox fill-ratio
    lbl, n = ndimage.label(m)
    for i in range(1, n + 1):
        ys, xs = np.where(lbl == i)
        bh, bw = np.ptp(ys) + 1, np.ptp(xs) + 1
        area = len(ys)
        fill = area / (bh * bw)
        # curves: long & thin (low fill). boxes/text: compact & filled.
        if area > 400 and fill > 0.35 and min(bh, bw) > 25:
            m[ys, xs] = False

    # plot interior in x (0.2V border .. ~1.15V), skip axis shoulders
    XLO, XHI = COL0 + 6, int(COL0 + VPP * (1.15 - 0.2))

    # 3) row-trace at each current gridline row. Two non-crossing curves ->
    #    the two widest dark runs; left = 125C, right = 25C.
    targets = [2, 3, 5, 7, 10, 15, 20, 30, 40]
    hot, cold, dbg = [], [], []          # (VF, IF)
    for I in targets:
        row = int(round(ROW1 - DEC * np.log10(I)))
        if row < 3 or row >= h:
            continue
        band = m[row - 2:row + 3, :].any(0)   # +-2px band
        xs = np.where(band)[0]
        xs = xs[(xs >= XLO) & (xs <= XHI)]
        if len(xs) == 0:
            continue
        runs = []
        s = xs[0]; p = xs[0]
        for x in xs[1:]:
            if x - p > 6:
                runs.append((s, p)); s = x
            p = x
        runs.append((s, p))
        runs = [(a, b) for a, b in runs if b - a >= 3]   # real strokes only
        if not runs:
            continue
        runs.sort(key=lambda r: r[1] - r[0], reverse=True)
        two = sorted(runs[:2], key=lambda r: r[0])       # by x
        cen = [0.5 * (a + b) for a, b in two]
        cold.append((round(vf(cen[-1]), 4), I))          # rightmost = 25C
        dbg.append((row, cen[-1]))
        if len(cen) >= 2:
            hot.append((round(vf(cen[0]), 4), I))        # leftmost = 125C
            dbg.append((row, cen[0]))
    # debug overlay
    ov = np.stack([im.astype(np.uint8)] * 3, -1)
    for r, c in dbg:
        ov[max(0, r - 4):r + 5, max(0, int(c) - 4):int(c) + 5] = [255, 0, 0]
    Image.fromarray(ov).save(IMG.replace("_forward_400dpi", "_traced"))
    return cold, hot

if __name__ == "__main__":
    cold, hot = main()
    print("# 25C forward (VF, IF):")
    for v, i in cold: print(f"  {v:.3f}  {i}")
    print("# 125C forward (VF, IF):")
    for v, i in hot: print(f"  {v:.3f}  {i}")
    # NOTE: the 15A row sits on the "125C"/"25C" label boxes and is discarded
    # (the guaranteed 15A value comes from the datasheet table, not the trace).
    # Sanity-check clean rows instead:
    d = dict((i, v) for v, i in cold)
    print(f"\ncross-check 25C VF@10A = {d.get(10)} V,  @20A = {d.get(20)} V")
    d2 = dict((i, v) for v, i in hot)
    print(f"cross-check 125C VF@10A = {d2.get(10)} V,  @20A = {d2.get(20)} V")
