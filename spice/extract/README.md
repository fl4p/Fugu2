# Commutation-loop parasitic extraction (KiCad → FastHenry → LTspice)

Extracts the **power commutation-loop inductance** of the Fugu2 buck from the
real PCB copper and feeds it into `../buck_parasitcs.asc`, replacing the
hand-guessed lumped inductors.

The switch stage is a compact SMD half-bridge on **B.Cu**: HS = `Q1‖Q3`
(Solar+→SW), LS = `Q2` (SW→BuckGND) with rectifiers `D9`/`D16`. Because the FETs
are SMD (Infineon PG-TDSON-8), not TO-220, the loop is tight and mostly planar.

## Result

**Loop inductance ≈ 5.3 nH** (pitch band 4.8–5.8 nH), HF loop R ≈ 21 mΩ,
measured across the nearest HF ceramic `C16`. See `results.md`.

## Tools

- **FastHenry 3.0.1** (MQS PEEC inductance solver), built from source at
  `/Users/fab/dev/vendor/FastHenry2` (FastFieldSolvers fork). Legacy K&R C, so
  built with: `make fasthenry CFLAGS='-O -DFOUR -m64 -std=gnu89 -fcommon
  -Wno-implicit-function-declaration -Wno-implicit-int -Wno-return-type
  -Wno-deprecated-non-prototype'` → binary in `bin/fasthenry`.
- **KiCad 9 bundled python** (has `pcbnew`) for geometry extraction:
  `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`
- **system python3** for the runner/reducer.

## Run

```sh
cd spice/extract
python3 run.py            # parallel 2.0/1.0/0.7 mm convergence sweep, ~8 s
python3 run.py --pitch 1.0   # single pitch
python3 run.py --full        # full 100 kHz–100 MHz L(f) curve (slower)
```

`run.py` shells out to the KiCad python (`kicad_to_fasthenry.py`) and to
`fasthenry`, parses `Zc.mat`, and writes `results.md`.

## How it works

`kicad_to_fasthenry.py` reads `Fugu2.kicad_pcb` and, for nets `Solar+`, `SW`,
`BuckGND` on both layers inside the switch-cluster ROI:

- meshes each filled pour into a **filament grid clipped to the polygon**
  (tracks are Manhattan-routed into the same grid so narrow connections survive;
  a global per-cell occupancy prevents coincident cross-net nodes → no NaN),
- stitches layers with **via** segments,
- shorts each switch drain→source with a thin **device bridge** (loop L =
  copper only; FET package L is added separately in LTspice),
- excites one **port** across the closest ceramic `C16`.

## Speed notes

- FastHenry rebuilds its preconditioner **per frequency**, so we solve only the
  ~10–100 MHz plateau (2 points), not a full sweep — the biggest lever.
- `-p diag` preconditioner + running the independent pitch solves concurrently.
- The source has **no OpenMP** (single-threaded); parallelism comes from running
  many independent solves at once.
- `0.5 mm` pitch needs the slow `-p cube` preconditioner (`diag`/`seg` → NaN on
  the large fine mesh), so the default sweep stops at `0.7 mm`.

## Caveats

- The gridded-filament plane approximation does not converge monotonically with
  pitch (~±9% scatter here) — treat 4.8–5.8 nH as the uncertainty band, not a
  single exact value. A future refinement is FastHenry uniform ground-plane
  (`G`) elements for the broad pours.
- FastHenry is magnetoquasistatic (L/R only); Coss resonance / ringing stays in
  LTspice.
