# Fugu2 printed enclosure

A **shroud**, not a box: the 100 × 100 mm aluminium heatsink is the floor, its fins stay
outside in free air. That follows the design rule in [`../doc/Enclosures.md`](../doc/Enclosures.md)
§0 — *"keep the finned face in free ambient air; make the heatsink a wall of the enclosure
rather than a component inside it."*

Two printed parts in **ASA**:

## Variants

`variant = "asbuilt" | "shifted"` — both are gated by `./check.sh`.

| | `asbuilt` | `shifted` |
|---|---|---|
| Board on the heatsink | where it sits today | moved **10 mm toward the terminal end** |
| Terminal end | 6 mm sill across the full width, 2 vertical screws | **no sill** — the terminals reach the heatsink edge, there is no metal left under a bar |
| USB-C end | 12 mm skirt down the heatsink edge, 2 lateral screws | that end now has ≥8 mm of bare heatsink, so a low chamfered **plinth** stands on it with 2 vertical screws |
| Screws into the heatsink | 6 | 4 |

The skirt/plinth choice is automatic (`top_plinth = hs_gap_top_e >= 8.0`), not a second switch —
a skirt would hang in mid air once the heatsink edge moves 10 mm away, so the geometry has to
follow the measurement.

| Part | Render with |
|---|---|
| Frame (walls, open bottom, bolts to the heatsink) | `part="frame"` |
| Lid (screws onto the frame) | `part="lid"` |
| Frame + lid + board + heatsink, for checking | `part="assembly"` |
| Frame ∩ board — must be empty | `part="collision"` |

Every outer surface is flat: the four lid-screw bosses are **inside**, and the only thing that
breaks the rectangle is the antenna bulge.

### Handedness

KiCad's PCB Y axis points **down**, OpenSCAD's points **up**. Mapping `by` straight onto +Y
builds a left-handed copy of the board — and a printed part is chiral, so that exports the wrong
hand while every clearance check still passes, because the shroud and the board are mirrored
together. Everything is modelled in the `(bx, by)` design frame and the top-level dispatch wraps
it in `world()`, which mirrors Y exactly once. The KiCad mesh is already right-handed (its export
negates Y), so its placement composes to a pure translation.

Material choice is not free: `../doc/Enclosures.md` §3 records the heatsink at **51–61 °C in
normal operation**, and a loaded-jig oven ramp where PLA gives at 60 °C, PETG at 80 °C and ASA
at 110 °C. **ASA is the floor** for anything mechanically attached to this heatsink. No UL flame
class is claimed — a printed part's rating is a property of material + printer + parameters, not
of the filament's yellow card.

## ⚠ Measure these five before you print anything

The model **refuses to render** until you do. They are interface dimensions of an object that
already exists on the bench; the values in the file are placeholders so the shape can be
previewed, not design values.

| Parameter | Placeholder | Measure |
|---|---|---|
| `standoff` | 5.0 | heatsink top face → PCB underside. The KiCad mesh puts the lowest bottom-side body at 4.54 mm below the board, so this is 4.54 + the compressed pad — but measure it |
| `stack_h` | 33.0 | heatsink top face → highest point **forward of the terminal bay** (`by < bay_y`), which is what the lid must clear. Include the fat wire loops off the electrolytics. The terminals are in the open bay and do not drive it |
| `hs_gap_right` | 2.0 | heatsink right edge → board right edge (antenna side) |
| `hs_gap_top` | 2.7 | heatsink top edge → board top edge (USB-C side) |
| `hs_thk` | 18.0 | total heatsink thickness |

Set them in the file and flip `measured = true`. To preview with the placeholders instead:

```bash
openscad -o /tmp/x.png -D provisional=true fugu2-enclosure.scad
```

`hs_gap_left` and `hs_gap_bottom` are derived (50 mm and 12 mm of overhang split between the
opposite edges), so you only measure two of the four.

## Coordinate frame

Board-local mm = KiCad coordinates minus the Edge.Cuts origin `(28.74, 31.00)`.

* `bx` 0…50 — 0 is the **left** edge (Q1 tab / coil side), 50 the **right** edge (ESP32 antenna)
* `by` 0…88 — 0 is the **USB-C** end, 88 the **terminal** end
* `z` 0 is the heatsink top face

## What each side does

**Left (coil side)** — wall inner face 2.5 mm off the board edge, and it stays there: the Q1
TO-220, which overhangs the board by 7.08 mm, escapes through a **slot in the bottom 6.5 mm of
the wall** rather than pushing the whole wall outward. The tab lies flat on the heatsink *under*
the board, so the slot costs nothing above the PCB. That is the tightest this side can be, and it
leaves the widest possible strip of bare heatsink for the toroid.

At 0.2 mm the wall fouls the M3 heads at H1/H3/H4, which sit only 1.96 mm in from the board edge
and so reach `bx −1.04` — an 0.84 mm overlap the collision gate catches. Rather than move the
whole wall out, the **inner** face is pocketed locally at those three points (depth derived from
the head, `head_clear` = 0.6 mm), so the outer surface stays flat and only three spots lose wall
thickness. An `assert` fails the render if a pocket would take the wall below the 1.2 mm FDM
minimum.

This wall is **deliberately left solid over its whole length** — no vents, no ribs. Drill the two
coil-wire holes wherever they land. The pads are J3 at `by 21.7` and J6 at `by 44.75`; wires
leave at PCB top, so drill around `z 8…14`.

**Right (antenna side)** — the board sits only ~2 mm from the heatsink edge here, so there is
nowhere for a wall to stand. The wall instead hangs *alongside* the heatsink, continuing 12 mm
down its side face, and is bolted in laterally at `by 30` and `by 75`. Over `by 2…24` it bows
out to put **≥3.3 mm of air around the ESP32 antenna** (which overhangs the board by 5.69 mm,
i.e. ~3.7 mm past the heatsink). The bulge is derived from the antenna extents in the source and
guarded by an `assert`, so it cannot silently close up.

**Top (USB-C end)** — a 14 × 8 mm opening sized for a plug overmould, not just the receptacle.
This wall also runs 12 mm down the heatsink's top edge face with two more lateral bolts.

**Bottom (terminal end)** — an open bay. Only a 6 mm sill crosses the full width; everything
above it is open, so both terminal blocks *and* the J5 CAN/UART socket are reachable, wires enter
freely, and a screwdriver goes straight down onto all four terminal screws. The bay side walls
ramp down to 20 mm past the lid.

**Vents** — right wall, top wall and lid only, and **nothing below z = 12**. IEC 62109-1 cl.
9.1.4.3 wants the bottom of a fire enclosure to retain flaming or molten material; the aluminium
floor does that only if the side openings are not at board level.

## Fixing to the heatsink — the frame is its own drill jig

Six M3 into the heatsink, none of them on the coil side:

| Where | Position | Direction |
|---|---|---|
| Right side face | `by 30`, `by 75`, `z −6` | lateral |
| Top side face | `bx 8`, `bx 42`, `z −6` | lateral |
| Sill | `bx 5`, `bx 45` | vertical, counterbored |

Print the frame, set it on the heatsink, centre-punch through its own six holes, then drill
Ø2.5 and tap M3. No separate template part — the frame *is* the template, which is the only way
to guarantee the holes and the part agree.

The two sill screws take **M3×14 pan head** (no counterbore — an M3 head is wider than the
6 mm sill). The four lateral screws bear on the 3 mm skirt.

Lid: 4 × M3 into heat-set inserts (Ø4.6 × 6 mm blind) in **internal** bosses — two in the top
wall, one each in the left and right walls; countersunk M3 flat heads in the lid.

There is no room for those bosses at board level: the walls sit 1.5–2.5 mm off the board edge and
that edge strip is full of connectors, fuses, headers and mounting-screw heads. A scan of the
board mesh plus the component mock found **no** position on the right wall at all. But an insert
only needs material in the top 6 mm, and up there the nearest thing to any wall is an
electrolytic, 6 mm away. So each boss is flush with the wall at board level and tapers inward at
45° above the components (`boss_zr` = 24 mm), reaching full width just under the insert. The 45°
underside prints without support, and an `assert` fails the render if `frame_top` ever drops far
enough for a boss to reach down into the fuses.

The lid's register lip is interrupted where a boss occupies the same height, and the top wall
carries no vents — a slot there would saw straight through the two bosses in it. Airflow is the
right wall (which dodges its own boss) plus the lid.

## Print settings (ASA) — and a warning about the printer

**Bambu says ASA is not for the P1P.** Their ABS/ASA/PC usage guide's hardware-compatibility
table reads *"Requires an enclosed printer; not compatible with P1P or A models"*, and the
filament guide table lists ASA on an open-frame printer (A Series, **P1P**) as *"Not
Recommended"*. Their warping page is blunter: *"Large flat models printed in ABS, ASA, or PC will
almost always warp without an enclosure."* This frame is a 75 × 97 mm part with a flat 841 mm²
first layer — exactly the case they mean. `printer-profile.scad` records the printer as a
**Bambu Lab P1P**, which is open-frame.

That is a decision for the bench, not for this file, but it has to be made before printing:

1. **Enclose the P1P** (official or DIY) and print ASA. Bed 100 °C for 15 min before starting
   raises the chamber, which is the substitute for active chamber heating on X1E/H2/X2D.
2. **ASA-CF instead.** OrcaSlicer ships `Bambu ASA-CF @BBL P1P` (275 °C) — fibre-filled grades
   shrink far less, and Bambu ships a P1P profile for ASA-CF, ASA-Aero, ABS-GF and PC FR while
   shipping none for their unfilled counterparts.
3. **Print it in PETG and accept the temperature limit.** `../doc/Enclosures.md` §3 has PETG
   giving at 80 °C against a heatsink that sits at 51–61 °C — margin, but not much.

### Profile and parameters

Use **`Bambu ASA @BBL X1C 0.4 nozzle`**. Despite the name it declares
`Bambu Lab P1P 0.4 nozzle` in its `compatible_printers`, so it is the P1P-legal ASA profile;
compatibility lives in that field, not in the filename.

| | |
|---|---|
| Nozzle | **270 °C** (wiki range 240–280 ±10) |
| Bed / plate | **100 °C** on Textured PEI, Smooth PEI/High-Temp or Engineering plate, **+ glue stick** |
| **Never** | Cool Plate / PLA Plate — "Not recommended" for ASA, and it is the stock default |
| Fan | 10–35 %, off for the first 3 layers |
| Dry first | 80 °C × 8 h; ASA is hygroscopic |
| Brim | 8 mm outer — `auto_brim` produced `brim_width = 0` here |
| Layer | 0.2 mm, 0.4 mm nozzle. Hardened steel not required |

### Orientation — both parts print INVERTED

As modelled neither part sits on a flat face, and the slicer will not tell you:

| | as modelled | inverted |
|---|---|---|
| Frame | rests on two 12 mm skirt strips, **286 mm²**, with 899 mm² of wall bottom hanging 12 mm in the air | wall-top ring on the bed, **841 mm²** |
| Lid | rests on its 2 mm register lip, **516 mm²**, whole 3333 mm² plate bridging above it | flat outer face down, **3762 mm²** |

`for_print = true` (the default) bakes that flip into `part="frame"` and `part="lid"`, so the
exported STL is already bed-ready. Set `for_print = false` for the design-frame pose. Inverted,
no overhang is steeper than the 45° boss tapers and the plinth chamfer — that chamfer was 4 mm
rise over 7 mm run, a 60° overhang, and is now `plinth_h = plinth_d`. The lid needs no support at
all; the frame needs ~1 cm³, see below.

### Support, and the island that caused it

Printed inverted the frame needed **2.06 cm³** of tree support, and it was not angle-driven —
identical at threshold 30°, 20° and auto, with `bridge_no_support` both ways. Mapping the support
tower out of the sliced G-code back into design coordinates found it: `bx 52.3…55.3, by 0.3…22.1,
design z ≈ 0`, i.e. the right wall band over the antenna bulge.

**The bulge does not add to the wall, it displaces it.** Over `by 1.6…24.8` the wall moves out to
`bx 59…62` and the 52.3…55.3 band becomes open cavity — but the skirt ran that band for the full
length, so 23 mm of skirt had nothing above it in the design frame and became an island floating
36 mm up when the part is inverted. The skirt is now **interrupted across the bulge**, with an
`assert` keeping both lateral screws out of the gap. That removed a quarter of the support and
made the part itself lighter.

What remains (~1.0–1.5 cm³) is the **USB-C window's edge** at `bx 16…28.5, design z ≈ 6.2…7.6`:
inverted, the top of any window is a bridge, here 14 mm wide, which is routine. Turning support
off entirely is a defensible choice — it saves 6 minutes and the bridge is well within what FDM
spans.

### One unresolved tension

The 3 mm wall wants 8 perimeters, which is what `62109-1` cl. 13.7.3's 7 J impact test pushes
toward. Bambu's warping guidance pushes the other way: *"avoid a fill rate above 50 % and wall
count greater than 6 layers to reduce shrinkage"*, with 2 walls + 15 % infill as their default.
Both are real. 8 walls is kept here because the wall thickness is a design requirement, not a
slicer preference — but it is a warping risk on an unenclosed machine and it is the first thing
to trade away if the first article lifts.

Clearances come from `~/.claude/skills/openscad/templates/printer-profile.scad`, where
`profile_measured` is **false** — `lip_tol = 0.30` for the lid register lip is a declared
default, not a measurement. The first print is the one that tells.

### Sliced result — `shifted` variant, both parts, one plate

OrcaSlicer 2.4.2, P1P 0.4 nozzle, `0.20mm Standard @BBL P1P` + the overrides above:

| | time | volume | support |
|---|---|---|---|
| No support | 1 h 41 m | 38.84 cm³ | — |
| Auto tree, Orca defaults | 1 h 51 m | 40.39 cm³ | 1.55 cm³ |
| **Auto tree, 15° / plate-only / 0.4 z-gap** | **1 h 47 m** | **39.85 cm³** | **1.01 cm³** |

240 layers, 48.00 mm tall. The project file `fugu2-shifted-P1P-ASA.3mf` carries the last row.

Verified in the emitted G-code, not just the preset: `filament_type = ASA`,
`nozzle_temperature = 270`, `curr_bed_type = Textured PEI Plate`, and `M140 S100` for the bed.
That check matters — the first attempt silently fell back to **PLA at 200 °C on a Cool Plate**
because `Generic ASA.json` lists only X1/X1C/P1S in `compatible_printers` and OrcaSlicer
dropped it without an error. `openscad-slice-check.sh <gcode> --plate "Textured PEI Plate"
--filament ASA` catches exactly that.

## Verification

```bash
./check.sh     # everything: both variants, manifold, collision, clearances, probes
```

`check.sh` is the gate. It runs, for **each variant**: frame and lid are single manifold solids;
no collision with the board; all components clear by ≥1.2 mm; and the two deliberately-tight
interfaces hold their own declared clearance — the bare board edge at `gap_left` and the screw
heads at `head_clear`, which get their own `grow_pcb`/`grow_head` knobs precisely so the general
1.2 mm margin cannot report the design intent as a fault. It then checks that the unmeasured
default still refuses to render, and runs `probe.sh`.

**Any openscad run that emits an ERROR or WARNING is a FAILURE, not a pass.** This bit the project
twice: once when `probe.scad` could not resolve its `include` from `/tmp` and all ten probes
passed vacuously, and once when a `-D gap_left` override tripped an `assert` and the abort was
read as "no collision".

`probe.sh` intersects the shroud with named boxes and asserts each is clear or blocked — USB-C
plug path, terminal-bay access, screwdriver reach, the Q1 slot, the boot-button hole, and
negatively: that the left wall really is solid across the drill zone, that no opening exists
below z = 12, that the lid really closes over the electrolytics, and that the antenna bulge is
closed rather than a window. **A probe that cannot run counts as a failure, not a pass.**

`part="collision"` intersects frame + lid with a mock of every significant component, built from
the real `Fugu2.kicad_pcb` coordinates. `-D grow=N` inflates the mock by N mm, turning the
collision test into a clearance test. Current state: **empty at grow = 1.2**, i.e. every
component clears the shroud by at least 1.2 mm.

## The KiCad board mesh — `fugu2-board.stl`

`part="assembly"` draws the real board, exported with `./export-board-mesh.sh`
(`kicad-cli pcb export stl`). It is a **visual cross-check, not a source of truth**, for two
reasons:

* **It cannot be a gate.** The export is not a closed mesh, so OpenSCAD refuses to boolean with
  it. The clearance gate stays the analytic mock.
* **It is incomplete and it disagrees with the fab outline in both directions.** No 3D model
  exists on this machine for the horizontal TO-220s (Q1/Q2/Q3) or the ATO blade fuses (F1/F3) —
  exactly the parts that drive this design — so those keep mock blocks, drawn **red** in the
  assembly view so the substitution stays visible. Where the mesh and the footprint data
  disagree, the mock takes whichever is **larger**: the mesh makes the Würth terminal blocks
  29.4 mm tall and 23.3 mm deep against a fab outline of ~17 × 18.4 (its screws are drawn fully
  backed out), while it shows the electrolytics as only 18.1 mm against the 25–26 mm their part
  numbers give. A mock that understates is the dangerous direction.

Adding the mesh paid for itself: it moved the terminal blocks' front face from `by 70.4` to
`by 66.05`, which left the lid edge 0.05 mm from them. `bay_y` is now 62.

No STL is committed. Export after you have measured:

```bash
openscad -o fugu2-frame.stl -D 'part="frame"' fugu2-enclosure.scad
openscad -o fugu2-lid.stl   -D 'part="lid"'   fugu2-enclosure.scad
```

## Open issue: the toroid does not fit beside the shroud as currently placed

The shroud leaves a **42.5 mm** strip of bare heatsink to the left of it (36 mm across the one
11 mm-long lid pad at `by 60`). In the build photos the toroid measures roughly **50 mm across**
and sits tangent to the board edge — i.e. it currently occupies space the wall needs. Options,
in the order I'd try them:

1. Let the toroid overhang the heatsink's left edge by ~8 mm. It is coupled through a 1.5–2 mm
   Shore-00 gap pad anyway (`../doc/Assembly.md`), so losing a crescent of contact area costs
   some of the ~0.6 K/W, not all of it. Measure the coil temperature before and after.
2. Move `lid_ins_y_L` (currently 60) to keep the one pinch point away from wherever the toroid
   lands — it is a one-line parameter.
3. A wider heatsink, or the toroid rotated to a lower-profile winding.

Nothing in the model is blocking here; it is a placement decision on the bench.

## Not addressed

The insulation system. `../doc/Enclosures.md` §5 is explicit that the gap pad is already a
safety-relevant dual thermal/insulation interface (heatsink likely at PE, switch node at 75 V),
and that a protection concept — Class I with verified bonding, or Class II — has to be chosen
for the whole assembly. A printed shroud does not change that and does not discharge it.
