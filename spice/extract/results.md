# Fugu2 commutation-loop parasitic extraction — results

FastHenry MQS extraction of the power commutation loop (SMD half-bridge Q1‖Q3 / Q2, port across nearest ceramic C16).

**Loop inductance ≈ 5.3 nH** (pitch band 4.8–5.8 nH), HF loop resistance ≈ 21 mΩ. Nominal from 1.0 mm mesh.

L(f) at 1.0 mm pitch:

| freq | R (mΩ) | L (nH) |
|---|---|---|
| 10 MHz | 21.28 | 4.82 |
| 100 MHz | 21.44 | 4.80 |

Pitch scatter over [2.0, 1.0, 0.7]mm: L = 4.8–5.8 nH (nominal 5.3 nH, ±9%). Gridded-filament plane approximation; treat as the uncertainty band.

## Suggested LTspice values (buck_parasitcs.asc)

- Hot-loop copper L (one calibrated element in the commutation path): **5.3 nH** (band 4.8–5.8)
- FET package internal L (~1–3 nH/FET): SEPARATE lumped element (FastHenry sees copper only).
- Cin electrolytic ESL: separate slow-path element, not in this fast loop.
