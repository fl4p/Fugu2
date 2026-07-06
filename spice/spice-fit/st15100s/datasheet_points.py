"""ST15100S datasheet reference points (N2219 Rev.-).

Forward curves digitized from Figure 1 with trace_fwd.py (gridline-calibrated
raster trace); the 15A point is the guaranteed table value, not the trace.
Capacitance from Figure 3 + the table CT=650pF@5V. Reverse from the table.
"""

# Forward: (IF [A], VF [V]) typical
FWD_25C = [(2, 0.417), (3, 0.445), (5, 0.493), (7, 0.537), (10, 0.596),
           (15, 0.680), (20, 0.752), (30, 0.893), (40, 1.029)]
FWD_125C = [(2, 0.323), (3, 0.366), (5, 0.434), (7, 0.484), (10, 0.536),
            (15, 0.600), (20, 0.641), (30, 0.711), (40, 0.767)]

# Table anchors (guaranteed): VF @15A pulse
VF_TABLE = {25: (0.68, 0.71), 125: (0.60, 0.64)}   # (typ, max)

# Junction capacitance: (VR [V], CT [pF]) typical, 1 MHz, 25C
CAP = [(0, 2200), (1, 1600), (2, 1071), (4, 850), (5, 650), (6, 590),
       (8, 490), (10, 420)]

# Reverse leakage @ VR=100V (rated): (typ, max) mA
IR = {25: (0.01, 0.5), 125: (7.5, 50)}
