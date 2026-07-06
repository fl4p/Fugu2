# spice-fit — datasheet-fit diode models + application benches

Build and validation for the datasheet-fit SPICE models in [`../models/`](../models/),
plus Fugu2 application benches that use them. Repo overview: [`../README.md`](../README.md).

## Part fits (one subdir each)

| Part | Fit dir | VF@15 A, 25 °C |
|---|---|---|
| SMC **ST15100S** | [`st15100s/`](st15100s/README.md) | 0.68 V typ |
| PANJIT **SVT15100UB** | [`svt15100ub/`](svt15100ub/README.md) | **0.61 V typ** (lower loss) |

Each subdir: the digitized `datasheet_points.py`, `plot_validation.py` (model-vs-
datasheet overlay), any `trace_*.py` / `val_*.cir`, and a `reference/` with the
datasheet PDF + curve crops. The full **datasheet-over-vendor-model** write-up
(with the SMC ST15100 evidence) lives in [`st15100s/README.md`](st15100s/README.md).

## Application benches (Fugu2)

- [`ls_schottky_test.py`](ls_schottky_test.py) — does an external LS Schottky
  (ST15100S) across the switch reduce body-diode Qrr? DPT, TO-220 vs TDSON-8
  transfer-loop inductance.
- [`loss_budget_schottky.py`](loss_budget_schottky.py) — loss budget of a parallel
  SVT15100UB across the LS net (deadtime conduction + Qrr + added Coss) vs simply
  shortening the deadtime.

## Running

Use the repo venv: `../../venv/bin/python3` (numpy, scipy, pillow, matplotlib,
spicelib; LTspice for the benches). **LTspice-macOS gotcha:** run headless with
`LTspice -b file.cir` — never `-Run` (hangs the GUI); absolute `.include` paths
don't resolve in `-b`, so use a relative path or inline the `.MODEL`.
