#!/bin/bash
# Regenerate fugu2-board.stl — the KiCad board mesh used by part="assembly".
#
# DISPLAY ONLY. The export is not a closed mesh, so OpenSCAD cannot boolean
# with it; the clearance gate is part="collision" against the analytic mock.
# It is also incomplete: no 3D model for the horizontal TO-220s (Q1/Q2/Q3) or
# the ATO blade fuses (F1/F3) exists on this machine, and those are exactly the
# parts that drive the enclosure. fugu2-enclosure.scad keeps mock blocks for
# them, drawn in red. Check the "Could not add 3D model" list this prints.
set -euo pipefail
cd "$(dirname "$0")"

KCLI=${KCLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
M=${KICAD_3DMODELS:-/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels}
P=${KICAD_3RDPARTY:-$HOME/Documents/KiCad/9.0/3rdparty}
[ -x "$KCLI" ] || { echo "kicad-cli not found at $KCLI"; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

"$KCLI" pcb export stl --force --no-dnp \
  -D KICAD6_3DMODEL_DIR="$M" -D KICAD7_3DMODEL_DIR="$M" \
  -D KICAD8_3DMODEL_DIR="$M" -D KICAD9_3DMODEL_DIR="$M" \
  -D KICAD7_3RD_PARTY="$P"   -D KICAD8_3RD_PARTY="$P" -D KICAD9_3RD_PARTY="$P" \
  -o "$tmp/board.stl" ../Fugu2.kicad_pcb 2>&1 | grep -E "Could not|File not found|created" | sort -u

# kicad-cli writes ASCII; OpenSCAD loads binary far faster (12 MB -> 3.9 MB)
python3 - "$tmp/board.stl" fugu2-board.stl <<'PY'
import struct, sys
src, dst = sys.argv[1], sys.argv[2]
tris = []; cur = []; nrm = (0.0, 0.0, 0.0)
for line in open(src):
    t = line.split()
    if not t: continue
    if t[0] == 'facet': nrm = tuple(float(x) for x in t[2:5])
    elif t[0] == 'vertex': cur.append(tuple(float(x) for x in t[1:4]))
    elif t[0] == 'endfacet':
        if len(cur) == 3: tris.append((nrm, cur))
        cur = []
with open(dst, 'wb') as f:
    f.write(b'Fugu2 board mesh, kicad-cli pcb export stl'.ljust(80, b'\0'))
    f.write(struct.pack('<I', len(tris)))
    for nrm, vs in tris:
        f.write(struct.pack('<3f', *nrm))
        for v in vs: f.write(struct.pack('<3f', *v))
        f.write(b'\0\0')
print(f"fugu2-board.stl: {len(tris)} triangles")
PY
