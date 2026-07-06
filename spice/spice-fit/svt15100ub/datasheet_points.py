"""PANJIT SVT15100UB datasheet reference points (SVT15100UB-REV.02, 2025-12-10).

Forward: table values (guaranteed) + Fig-4 digitized (gridline-calibrated raster
trace, calibration validated against the 25C table anchors). The datasheet table
gives VF@125C only at 1A and 5A; the 15A/30A 125C points are from Fig-4.
Capacitance: Fig-2 digitized. Reverse/BV from the table.
"""

# Forward (IF [A], VF [V]) typical
FWD_25C = [(1, 0.38), (2, 0.414), (3, 0.436), (5, 0.47), (7, 0.503),
           (10, 0.542), (15, 0.61), (20, 0.652), (30, 0.751)]      # table@1/5/15
FWD_125C = [(1, 0.25), (5, 0.40), (15, 0.54), (30, 0.65)]          # table@1/5; Fig-4@15/30

# Table anchors (guaranteed), VF @ pulse
VF_TABLE = {25: {1: 0.38, 5: 0.47, 15: (0.61, 0.66)},   # 15A = (typ, max)
            125: {1: 0.25, 5: 0.40}}                     # no 15A@125C in table

# Junction capacitance (VR [V], CJ [pF]) typical, from Fig-2
CAP = [(1, 2000), (3, 1450), (5, 1250), (7, 900), (10, 600), (20, 330), (50, 190)]

# Ratings
VBR = 100          # V, min @ IR=0.5mA
IR_100V = {25: 80e-6, 125: 15e-3}   # A: 80uA max @25C, 15mA typ @125C
IFSM = 250         # A
