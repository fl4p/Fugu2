// ============================================================================
// Fugu2 enclosure — printed ASA shroud over the PCB, heatsink is the floor
// ============================================================================
//
// Design rule from doc/Enclosures.md §0:
//   "keep the finned face in free ambient air — make the heatsink a *wall* of
//    the enclosure rather than a component inside it."
// So this is a shroud, not a box: no printed floor, the 100x100 aluminium
// heatsink closes the bottom and its fins stay outside in free air.
//
// Material: ASA. doc/Enclosures.md §3 — the heatsink runs 51-61 C in normal
// operation; PLA gives at 60 C and PETG at 80 C (loaded-jig screening), ASA at
// 110 C. No UL flame class is claimed: a printed part's rating is a property of
// material + printer + parameters, not of the filament's yellow card.
//
// COORDINATE FRAME — board-local mm, = KiCad coords minus the Edge.Cuts origin
// (28.74, 31.00) from Fugu2.kicad_pcb.
//   bx  0 .. 50   0 = left edge  (Q1 tab / coil side), 50 = right edge (antenna)
//   by  0 .. 88   0 = USB-C end  ("top"),              88 = terminal end
//   z   0 = heatsink top face;  PCB underside at `standoff`
//
// HANDEDNESS. KiCad's PCB Y axis points DOWN, OpenSCAD's points UP, so `by`
// used directly as +Y builds a LEFT-HANDED copy of the board — and a printed
// part is chiral, so that would export the wrong hand. Everything below is
// modelled in that (bx, by) design frame, and the top-level dispatch wraps it
// in world(), which mirrors Y once to put the parts in the real board's hand.
// The KiCad mesh is already right-handed (its export negates Y), so its
// placement composes to a pure translation — see board_mesh().
//
//   part = "frame" | "lid" | "assembly" | "collision" | "none"
//
// The frame is its own drill jig: bolt nothing, set it on the heatsink, and
// drill through its six own screw holes. No separate template part.
// ============================================================================

part = "frame";

// --- Variant ---------------------------------------------------------------
// "asbuilt"  the board where it sits today, with a sill across the terminal end
// "shifted"  board moved 10 mm toward the terminal end so the terminals reach
//            the heatsink edge; no sill (there is no metal left under it), and
//            the USB-C end gains enough bare heatsink for a proper plinth
variant = "asbuilt";

// --- MEASURE ---------------------------------------------------------------
// Physical interface dimensions of an object that already exists. These are
// NOT design choices and the defaults below are NOT design values — they are
// placeholders so the geometry can be previewed. Set them with a caliper and
// flip `measured = true`, or render provisionally with -D provisional=true.

measured    = false;   // set true once the five values below are real
provisional = false;   // -D provisional=true to preview with the placeholders

standoff     = 5.0;    // MEASURE heatsink top face -> PCB underside
                       //   (set by the flat TO-220 bodies + the gap pad)
stack_h      = 33.0;   // MEASURE heatsink top face -> highest point FORWARD OF
                       //   THE TERMINAL BAY (by < bay_y) — that is what the lid
                       //   has to clear. Include the fat wire loops off the
                       //   electrolytics. The terminals themselves are in the
                       //   open bay and do not drive this.
hs_gap_right = 2.0;    // MEASURE heatsink right edge -> board right edge
hs_gap_top   = 2.7;    // MEASURE heatsink top edge   -> board top edge
hs_thk       = 18.0;   // MEASURE total heatsink thickness

assert(measured || provisional,
       "UNMEASURED: set standoff / stack_h / hs_gap_right / hs_gap_top / hs_thk from calipers and set measured=true, or preview with -D provisional=true");

// --- Design parameters -----------------------------------------------------
wall        = 3.0;   // 62109-1 cl.13.7.3 puts a 7 J impact test on polymeric
                     // enclosures; 3 mm is 7-8 perimeters at 0.4 mm nozzle
lid_t       = 3.0;
lip_h       = 2.0;   // lid register lip depth
lip_w       = 2.5;
lip_tol     = 0.30;  // declared default, printer profile is NOT measured
clear_top   = 1.0;   // air above the tallest component, under the lip

skirt_h     = 12.0;  // how far the right/top walls reach down the heatsink side
skirt_clear = 0.30;  // air between skirt and heatsink side face
skirt_t     = 3.0;

sill_h      = 6.0;   // height of the stub wall across the open terminal bay
sill_w      = 6.0;   // its depth in by, wide enough for a hold-down screw

bay_y       = 72.5;  // lid is cut away beyond this: the open terminal bay.
                     // Set at the terminal screws. The block bodies start at
                     // by 66.05 and the lid passes OVER them: sliced from the
                     // KiCad mesh they are <= 24.6 mm tall below by 74, and only
                     // the screw towers at by 74..86 reach 35.9.
step_y0     = 70.0;  // bay side walls ramp down from here ...
step_y1     = 78.0;  // ... to here
step_z      = 20.0;  // ... to this height

m3_free     = 3.4;   // M3 clearance
m3_head     = 6.4;
insert_d    = 4.60;  // M3 heat-set insert, brass, standard short
insert_h    = 6.0;

vent_w      = 3.0;
vent_pitch  = 6.0;

$fn = 48;
eps = 0.02;
use_board_mesh = true;   // assembly view: real KiCad mesh vs. analytic mock

// --- Board / heatsink geometry (from Fugu2.kicad_pcb — do not edit) --------
board_w = 50.0;   board_l = 88.0;   pcb_t = 1.6;
hs      = 100.0;

pcb_z0  = standoff;
pcb_z1  = standoff + pcb_t;

board_shift_y = (variant == "shifted") ? 10.0 : 0.0;   // toward the terminal end
terminal_sill = (variant != "shifted");

hs_gap_top_e  = hs_gap_top + board_shift_y;            // as actually assembled
hs_gap_left   = hs - board_w - hs_gap_right;
hs_gap_bottom = hs - board_l - hs_gap_top_e;
hs_x0 = -hs_gap_left;      hs_x1 = board_w + hs_gap_right;
hs_y0 = -hs_gap_top_e;     hs_y1 = board_l + hs_gap_bottom;

// Hard features the shroud has to respect
q1_x0 = -7.08;  q1_x1 =  8.89;  q1_y0 = 24.66;  q1_y1 = 34.76;  // TO-220, bottom side
q1_screw = [-4.01, 29.71];                                      // its M4 tab screw, off-board
ant_x1   = 55.69;  ant_y0 = 4.14;  ant_y1 = 22.26;              // ESP32 antenna overhang
usb_x0   = 17.74;  usb_x1 = 26.78;                              // USB-C opening
term_x0  =  3.45;  term_x1 = 44.19;  term_y0 = 70.41;           // screw terminals
term_body_top  = 24.60;   // measured off the KiCad mesh (design z)
// Mounting-screw heads. Real hardware, and the closest metal to the left wall:
// H1/H3/H4 sit ~1.96 mm in from the board edge, so an M3 head reaches bx -1.04.
mnt_holes = [[1.99, 2.02], [37.66, 25.24], [1.96, 38.27], [1.96, 74.50], [47.96, 74.50]];
m3_head_d = 6.0;   // M3 pan head
m3_head_h = 2.4;
head_clear = 0.6;  // air around a head where the wall has to be relieved
term_screw_top = 35.90;   // the screw towers, by 73.8..86.2

// --- Derived wall faces ----------------------------------------------------
gap_left = 0.2;                              // board edge -> left wall inner face
inL  = -gap_left;                            // left wall inner (coil / Q1 side)
outL = inL - wall;

// Right wall cannot stand on the heatsink (the board sits ~2 mm from its edge),
// so it hangs alongside and bolts into the heatsink's side face.
inR  = max(board_w + 2.3, hs_x1 + skirt_clear);
outR = inR + wall;

inT  = -1.5;                                 // USB-C end; connector face is at -0.23
// With the board shifted, the heatsink edge at this end moves 10 mm away, so a
// skirt would hang in mid air. Given >= 8 mm of bare metal, stand on it instead:
// a low plinth along the whole wall carrying two vertical screws.
top_plinth = hs_gap_top_e >= 8.0;
plinth_d   = 7.0;                            // how far the plinth reaches out
// The plinth's chamfer becomes an overhang when the frame is printed inverted,
// so rise must equal run: at 4 mm over 7 mm it was a 60 degree overhang.
plinth_h   = plinth_d;                       // 45 degrees, self-supporting
outT = top_plinth ? inT - wall
                  : min(inT - wall, hs_y0 - skirt_clear - skirt_t);

inB  = 90.8;                                 // terminal end sill (terminals reach by 89.36)
outB = terminal_sill ? min(inB + sill_w, hs_y1 - 0.5) : inB;   // no sill -> no back wall

// Antenna bulge — the wall bows out so the antenna sits in air, not plastic.
// Derived from the antenna extents so the margin cannot silently vanish.
ant_air = 2.5;                               // air around the antenna, all sides
bul_cy0 = ant_y0 - ant_air;                  // cavity, by
bul_cy1 = ant_y1 + ant_air;
bul_in  = ant_x1 + 3.3;                      // cavity, bx
bul_y0  = min(inT, bul_cy0 - wall);
bul_y1  = bul_cy1 + wall;
bul_out = bul_in + wall;

frame_top = stack_h + clear_top + lip_h;
lid_z0    = frame_top;
lid_z1    = frame_top + lid_t;

// Fixings into the heatsink: 2 lateral in the right face, 2 lateral in the top
// face, 2 vertical through the sill. Nothing on the left — that edge is kept
// clear so the toroid gets the widest possible strip of bare heatsink.
side_screw_y = [30, 75];      // through the right wall/skirt, z = -screw_z
                              // (both must clear the bulge gap in the skirt)
top_screw_x  = [8, 42];       // through the top wall/skirt
sill_screw_x = [5, 45];       // vertical through the sill
screw_z      = -6.0;

// Lid screws: heat-set inserts in bosses INSIDE the enclosure, so every outer
// surface stays flat. There is no room for them at board level — the walls sit
// 1.5-2.5 mm off the board edge and the edge strip is full of connectors,
// fuses, headers and mounting-screw heads. But the insert only needs material
// in the top 6 mm, and up there the only things near a wall are the
// electrolytics, which stand no closer than 6 mm to any wall. So each boss is
// flush with the wall at board level and tapers inward at 45 degrees above the
// components, reaching full width just under the insert.
//   [along-wall centre, wall]   wall: 0 = top (bx), 1 = left (by), 2 = right (by)
lid_boss  = [[8, 0], [42, 0], [52, 1], [52, 2]];
boss_in   = 6.0;                    // intrusion past the wall's inner face
boss_len  = 11.0;                   // length along the wall
boss_z1   = frame_top;
boss_z0   = frame_top - insert_h;   // full width from here up: the insert zone
boss_zr   = boss_z0 - boss_in;      // 45 degree ramp starts here

// --- Sanity gates ----------------------------------------------------------
assert(wall >= 1.2, "wall below FDM minimum");
assert(!terminal_sill || outB - inB >= m3_free + 2.4,
       "sill pinched too narrow for its hold-down screw — check hs_gap_top");
assert(!top_plinth || outT - plinth_d > hs_y0 + 0.5,
       "top plinth runs off the heatsink — check hs_gap_top");
assert(bul_in >= ant_x1 + 3.0, "antenna bulge too tight in bx");
assert(bul_cy0 <= ant_y0 - 2.0 && bul_cy1 >= ant_y1 + 2.0, "antenna bulge too tight in by");
assert(gap_left >= 0.15, "left wall would touch the board edge");
for (h = mnt_holes)
    assert(wall - max(0, (inL - (h[0] - m3_head_d/2)) + head_clear) >= 1.2,
           "screw-head relief would leave the left wall below the FDM minimum — raise gap_left");
assert(standoff > 4.0, "standoff below a flat TO-220 body — re-measure");
assert(bay_y <= 73.8 - 1.2, "lid edge too close to the terminal screw towers (they start at by 73.8)");
assert(bay_y <= 66.05 || frame_top - lip_h >= term_body_top + 1.0,
       "lid passes over the terminal blocks but does not clear them — raise stack_h");
for (b = lid_boss) assert(b[1] == 0 || b[0] + boss_len/2 < bay_y,
       "a lid boss runs past the open bay, where there is no lid to screw down");
for (y = side_screw_y)
    assert(y > bul_y1 + 2 || y < bul_y0 - 2,
           "a lateral screw lands in the skirt's bulge gap, where there is no skirt");
assert(boss_zr > pcb_z1 + 16.5,
       "lid bosses start low enough to foul the fuses/headers — raise frame_top or shrink boss_in");
echo(str("Frame bbox  bx ", outL, " .. ", bul_out,
         "   by ", outT, " .. ", outB,
         "   z ", -skirt_h, " .. ", frame_top));
echo(str("Total height above heatsink face: ", lid_z1, " mm"));
if (part == "assembly" && use_board_mesh)
    echo("assembly: use F5 Preview. F6 Render SILENTLY DROPS the KiCad mesh - it is not a closed mesh, so CGAL refuses it. Set use_board_mesh=false to see the analytic mock under F6.");
echo(str("Bare heatsink strip left of the shroud (for the toroid): ",
         -hs_x0 + outL, " mm, uniform (no external pads)"));

// ============================================================================
// 2D profiles
// ============================================================================
module box2d(x0, y0, x1, y1) { translate([x0, y0]) square([x1 - x0, y1 - y0]); }

module outer2d() {
    offset(r = 1.5) offset(r = -1.5) union() {
        box2d(outL, outT, outR, outB);
        box2d(inR,  bul_y0, bul_out, bul_y1);       // antenna bulge
    }
}
module inner2d() {
    union() {
        box2d(inL, inT, inR, inB);
        box2d(inR - eps, bul_cy0, bul_in, bul_cy1);
    }
}
module wallband2d() { difference() { outer2d(); inner2d(); } }

// ============================================================================
// Frame
// ============================================================================
// Boss footprint. full=false gives the same patch of the bare wall band, which
// is what the 45 degree taper starts from.
module boss2d(i, full = true) {
    c = lid_boss[i][0];  w = lid_boss[i][1];
    if (w == 0) box2d(c - boss_len/2, outT, c + boss_len/2, full ? inT + boss_in : inT);
    if (w == 1) box2d(outL, c - boss_len/2, full ? inL + boss_in : inL, c + boss_len/2);
    if (w == 2) box2d(full ? inR - boss_in : inR, c - boss_len/2, outR, c + boss_len/2);
}
function boss_insert_xy(i) =
    lid_boss[i][1] == 0 ? [lid_boss[i][0], (outT + inT + boss_in) / 2] :
    lid_boss[i][1] == 1 ? [(outL + inL + boss_in) / 2, lid_boss[i][0]] :
                          [(inR - boss_in + outR) / 2, lid_boss[i][0]];

module lid_bosses() {
    for (i = [0 : len(lid_boss) - 1]) {
        translate([0, 0, boss_z0]) linear_extrude(boss_z1 - boss_z0) boss2d(i, true);
        hull() {   // 45 degree taper down onto the wall: prints without support
            translate([0, 0, boss_z0 - eps]) linear_extrude(eps) boss2d(i, true);
            translate([0, 0, boss_zr])       linear_extrude(eps) boss2d(i, false);
        }
    }
}

module skirt() {
    // Right face — hangs alongside the heatsink, carries the lateral screws.
    // It is INTERRUPTED across the antenna bulge: there the wall is displaced
    // outward to bx bul_in..bul_out and this band is open cavity, so a skirt
    // segment here would have nothing above it in the design frame and becomes
    // an ISLAND floating 36 mm up when the frame is printed inverted. That cost
    // ~2 cm3 of tree support until it was found by mapping the support tower
    // in the sliced G-code back into design coordinates.
    translate([inR, outT, -skirt_h])
        cube([wall, bul_y0 - outT, skirt_h + eps]);                 // before the bulge
    translate([inR, bul_y1, -skirt_h])
        cube([wall, max(outB, inB) - bul_y1, skirt_h + eps]);       // after it
    // top (USB-C) face — only when there is no metal to stand on there
    if (!top_plinth)
        translate([outL, outT, -skirt_h]) cube([outR - outL, skirt_t, skirt_h + eps]);
}

// Low chamfered foot along the USB-C wall, used instead of the skirt when the
// board has been shifted and that end has bare heatsink under it.
module plinth() {
    if (top_plinth)
        hull() {
            translate([outL, outT - plinth_d, 0]) cube([outR - outL, plinth_d, eps]);
            translate([outL, outT - eps, 0])      cube([outR - outL, eps, plinth_h]);
        }
}

module frame_solid() {
    union() {
        linear_extrude(frame_top) wallband2d();
        skirt();
        plinth();
        lid_bosses();
    }
}

module frame_cuts() {
    // --- open terminal bay: remove the back wall above the sill -------------
    // start 1 mm inside the (empty) cavity so the cut does not leave a
    // zero-thickness face coplanar with the sill's inner plane
    translate([outL - 5, inB - 1, sill_h]) cube([outR - outL + 10, sill_w + 6, frame_top + 5]);

    // --- bay side walls ramp down after the lid ends ------------------------
    translate([outL - 5, 0, 0]) rotate([90, 0, 90])
        linear_extrude(bul_out - outL + 20)
            polygon([[step_y0, frame_top], [step_y1, step_z],
                     [outB + 10, step_z], [outB + 10, frame_top + 5],
                     [step_y0, frame_top + 5]]);

    // --- Q1 TO-220 tab pokes through the lower left wall --------------------
    // The tab lies flat on the heatsink UNDER the board, so the slot lives
    // below the PCB and the outer wall face stays at outL: tightest possible.
    translate([outL - 2, q1_y0 - 2.4, -eps])
        cube([-outL + 2 + 2, (q1_y1 - q1_y0) + 4.8, standoff + 1.5]);

    // --- relief for mounting-screw heads --------------------------------------
    // At gap_left = 0.2 the heads at H1/H3/H4 overlap the wall by 0.84 mm. Pocket
    // the INNER face locally rather than moving the whole wall out — the outer
    // surface stays flat and only these three spots lose wall thickness.
    for (h = mnt_holes) {
        d = (inL - (h[0] - m3_head_d/2)) + head_clear;   // depth needed, if any
        if (d > 0)
            translate([inL - d, h[1] - (m3_head_d/2 + head_clear), pcb_z1 - 0.5])
                cube([d + eps, m3_head_d + 2*head_clear, m3_head_h + 2.0]);
    }

    // --- USB-C ---------------------------------------------------------------
    translate([usb_x0 - 2.5, outT - 2, pcb_z1 - 0.5])
        cube([(usb_x1 - usb_x0) + 5.0, -outT + 4, 8.0]);

    // --- heatsink fixings ---------------------------------------------------
    for (y = side_screw_y)                                  // lateral, right face
        translate([inR - 4, y, screw_z]) rotate([0, 90, 0])
            cylinder(d = m3_free, h = wall + 8, center = false);
    if (top_plinth)                                         // vertical, plinth
        for (x = top_screw_x)
            translate([x, outT - plinth_d/2, -eps]) cylinder(d = m3_free, h = plinth_h + 1);
    else                                                    // lateral, top face
        for (x = top_screw_x)
            translate([x, inT + 2, screw_z]) rotate([90, 0, 0])
                cylinder(d = m3_free, h = skirt_t + 8, center = false);
    // Vertical, through the sill. No counterbore: an M3 head is wider than the
    // sill and a counterbore would break out of both its faces. M3x14 pan head
    // sits on top of the sill instead — nothing above it needs the room.
    if (terminal_sill)
        for (x = sill_screw_x)
            translate([x, inB + sill_w/2, -eps]) cylinder(d = m3_free, h = sill_h + 1);

    // --- lid inserts --------------------------------------------------------
    for (i = [0 : len(lid_boss) - 1])
        translate(concat(boss_insert_xy(i), [frame_top - insert_h]))
            cylinder(d = insert_d, h = insert_h + eps);

    // --- vents: right wall and top wall only --------------------------------
    // The LEFT wall is deliberately left solid over its whole length so the two
    // coil wire holes can be drilled wherever they land (pads J3 by 21.7,
    // J6 by 44.75). Nothing below z=12 anywhere: 62109-1 cl.9.1.4.3 wants the
    // bottom of a fire enclosure to retain flaming or molten material.
    for (y = [30 : vent_pitch : bay_y - 4])
        for (i = [0 : len(lid_boss) - 1])
            if (lid_boss[i][1] == 2 && abs(y - lid_boss[i][0]) > boss_len/2 + vent_w)
                translate([inR - 2, y - vent_w/2, 12]) cube([wall + 4, vent_w, 18]);
    // No vents in the top wall: the two lid bosses live in it and a slot would
    // saw straight through them. The right wall and the lid carry the airflow.
}

module frame() { difference() { frame_solid(); frame_cuts(); } }

// ============================================================================
// Lid
// ============================================================================
module lid_outline2d() { intersection() { outer2d(); box2d(outL - 20, outT - 20, bul_out + 5, bay_y); } }
module lid_lip2d() {
    intersection() {
        difference() {
            offset(r = -lip_tol) inner2d();
            offset(r = -(lip_tol + lip_w)) inner2d();
            // the lip is interrupted where a boss occupies the same height
            for (i = [0 : len(lid_boss) - 1]) offset(r = lip_tol) boss2d(i, true);
        }
        box2d(outL - 20, outT - 20, bul_out + 5, bay_y);
    }
}
module lid_backrib2d() {
    intersection() { offset(r = -lip_tol) inner2d();
                     box2d(inL, bay_y - lip_w, inR, bay_y); }
}

module lid() {
    difference() {
        union() {
            translate([0, 0, lid_z0]) linear_extrude(lid_t)
                lid_outline2d();
            translate([0, 0, lid_z0 - lip_h]) linear_extrude(lip_h)
                union() { lid_lip2d(); lid_backrib2d(); }
        }
        // screw holes, countersunk for M3 flat head
        for (i = [0 : len(lid_boss) - 1]) { p = boss_insert_xy(i);
            translate([p[0], p[1], lid_z0 - 1]) cylinder(d = m3_free, h = lid_t + 2);
            translate([p[0], p[1], lid_z1 - 1.6])
                cylinder(d1 = m3_free, d2 = m3_head, h = 1.6 + eps);
        }
        // boot button poke hole (SW1 at bx 26.16, by 10.60)
        translate([26.16, 10.60, lid_z0 - 1]) cylinder(d = 4.5, h = lid_t + 2);
        // vent field over the electrolytics
        for (y = [22 : vent_pitch : 54])
            hull() {
                translate([4,  y, lid_z0 - 1]) cylinder(d = vent_w, h = lid_t + 2);
                translate([46, y, lid_z0 - 1]) cylinder(d = vent_w, h = lid_t + 2);
            }
    }
}

// ============================================================================
// Board mock — used only to check clearances, never exported
// ============================================================================
grow = 0;   // -D grow=0.8 turns the collision check into a clearance check
// Two interfaces are deliberately tight and carry their own declared clearance,
// so they get their own margins instead of the general component one: the bare
// board edge (gap_left, 0.2 mm) and the mounting-screw heads in their wall
// pockets (head_clear, 0.6 mm). Growing those by the component margin would
// report the design intent as a fault.
grow_pcb  = 0;
grow_head = 0;
module blk(x0, y0, x1, y1, z0, z1)
    { translate([x0-grow, y0-grow, z0-grow]) cube([x1-x0+2*grow, y1-y0+2*grow, z1-z0+2*grow]); }
module cyl(x, y, d, z0, z1)
    { translate([x, y, z0-grow]) cylinder(d = d + 2*grow, h = z1 - z0 + 2*grow); }

module fastener(x, y, d, h) {
    translate([x, y, pcb_z1 - grow_head])
        cylinder(d = d + 2*grow_head, h = h + 2*grow_head);
}
module mock_fasteners() {
    color("gray") {
        for (h = mnt_holes) fastener(h[0], h[1], m3_head_d, m3_head_h);
        fastener(9.73, 3.75, 7.0, 2.8);                  // Q3 tab M4 head
    }
}

module board_components() {
    mock_fasteners();
    color("green") translate([-grow_pcb, -grow_pcb, pcb_z0 - grow_pcb])       // PCB
        cube([board_w + 2*grow_pcb, board_l + 2*grow_pcb, pcb_t + 2*grow_pcb]);
    color("dimgray") {
        blk(q1_x0, q1_y0, q1_x1, q1_y1, 0, standoff);                        // Q1 TO-220
        cyl(q1_screw[0], q1_screw[1], 7.0, 0, 3.0);                          // its M4 head
        blk(4.46, 0.90, 15.01, 16.65, 0, standoff);                          // Q3
        blk(24.04, 11.07, 39.79, 21.17, 0, standoff);                        // Q2
        blk(24.04, 21.48, 39.79, 31.58, 0, standoff);                        // D9
    }
    color("silver")  blk(30.07, ant_y0, ant_x1, ant_y1, pcb_z1, pcb_z1+3.1); // ESP32 + antenna
    color("silver")  blk(usb_x0, -0.23, usb_x1, 8.4, pcb_z1, pcb_z1+3.2);    // USB-C
    // Electrolytics at their part-number length (D16xL26 / D18xL25); the KiCad
    // mesh shows only 18.1 mm here, i.e. a generic short body. Larger wins.
    color("sienna") {
        cyl(30.35, 33.31, 18, pcb_z1, pcb_z1 + 26);                          // C10
        cyl(15.08, 41.39, 16, pcb_z1, pcb_z1 + 26);                          // C11
        cyl(18.06, 58.65, 18, pcb_z1, pcb_z1 + 26);                          // C12
    }
    // J10/J9, stepped, sliced out of the KiCad mesh in 2 mm bands. The block is
    // <= 24.6 mm tall everywhere below by 74; only the screw towers at
    // by 73.8..86.2 reach 35.9. That is what lets the lid run up to the screws.
    // The footprint is the envelope of the fab outline (bx 3.45..44.19,
    // by 70.41..88.79) and the mesh (bx 2.82..44.19, by 66.05..89.36); where the
    // two disagree the larger wins — a mock that understates is the dangerous
    // direction.
    color("whitesmoke") {
        blk(2.82, 66.05, 44.19, 89.36, pcb_z1, term_body_top);
        blk(2.82, 73.80, 44.19, 86.20, term_body_top, term_screw_top);
    }
    color("black") {
        blk(45.46, 76.81, 49.06, 88.06, pcb_z1, pcb_z1 + 11);                // J5
        blk(32.75, 47.88, 39.31, 68.43, pcb_z1, pcb_z1 + 16);                // F1
        blk( 2.08, 49.58,  8.64, 70.12, pcb_z1, pcb_z1 + 16);                // F3
        blk(23.38,  8.88, 28.93, 12.33, pcb_z1, pcb_z1 + 3.5);               // SW1
        blk(32.32,  6.23, 50.34, 19.34, pcb_z1, pcb_z1 + 3.0);               // J4
        blk(39.89, 25.63, 48.13, 27.87, pcb_z1, pcb_z1 + 8.0);               // J2
        blk(45.05, 30.36, 47.83, 38.22, pcb_z1, pcb_z1 + 8.0);               // J7
        blk(44.10, 63.29, 49.72, 70.71, pcb_z1, pcb_z1 + 1.6);               // D2
    }
}
// The board as KiCad sees it. DISPLAY ONLY: the export is not a closed mesh,
// so OpenSCAD cannot boolean with it — the clearance gate stays analytic
// (part="collision" against board_components()). It is also incomplete: no
// 3D model exists on this machine for the horizontal TO-220s (Q1/Q2/Q3) or the
// ATO fuses (F1/F3), which are exactly the parts that drive this design. Those
// keep their mock blocks, drawn in red so the substitution stays visible.
// Regenerate with ./export-board-mesh.sh
board_mesh_file = "fugu2-board.stl";

module board_mesh() {
    // mesh_y = -(pcb Y) already, so this composes with world()'s mirror into a
    // pure translation: world = (mesh_x - 28.74, mesh_y + 31, mesh_z + standoff)
    color("darkolivegreen")
        translate([-28.74, -31.0, standoff]) mirror([0, 1, 0])
            import(board_mesh_file, convexity = 10);
}

// Refs the KiCad mesh is missing — kept as blocks so nothing is silently lost
module mock_missing() {
    color("red", 0.7) {
        blk(q1_x0, q1_y0, q1_x1, q1_y1, 0, standoff);                        // Q1
        cyl(q1_screw[0], q1_screw[1], 7.0, 0, 3.0);                          // Q1 M4 head
        blk(4.46, 0.90, 15.01, 16.65, 0, standoff);                          // Q3
        blk(24.04, 11.07, 39.79, 21.17, 0, standoff);                        // Q2
        blk(32.75, 47.88, 39.31, 68.43, pcb_z1, pcb_z1 + 16);                // F1
        blk( 2.08, 49.58,  8.64, 70.12, pcb_z1, pcb_z1 + 16);                // F3
    }
}

module heatsink() { color("lightsteelblue") translate([hs_x0, hs_y0, -hs_thk]) cube([hs, hs, hs_thk]); }

// ============================================================================
// world() turns the left-handed design frame into the real board's hand.
// Everything that leaves this file as geometry goes through it.
module world() { mirror([0, 1, 0]) children(); }

// Print orientation. As modelled, NEITHER part sits on a flat face: the frame
// would rest on its two 12 mm skirt strips (286 mm^2) with 899 mm^2 of wall
// bottom hanging 12 mm in the air, and the lid would rest on its 2 mm register
// lip (516 mm^2) with the whole 3333 mm^2 plate bridging above it. Both print
// INVERTED, which puts the frame on its wall-top ring (841 mm^2) and the lid
// flat on its outer face (3762 mm^2), and leaves no overhang steeper than the
// 45 degree boss tapers. Set for_print=false to get the design-frame pose.
for_print = true;
module print_orient(ztop) {
    if (for_print) translate([0, 0, ztop]) rotate([180, 0, 0]) children();
    else children();
}

if (part == "frame")      print_orient(frame_top) world() frame();
else if (part == "lid")   print_orient(lid_z1)   world() lid();
else if (part == "assembly") world() {
    frame();
    color("skyblue", 0.55) lid();
    if (use_board_mesh) { board_mesh(); mock_missing(); } else board_components();
    heatsink();
}
else if (part == "collision")
    world() intersection() { union() { frame(); lid(); } board_components(); }
else if (part == "none") ;   // library use: probe scripts include this file
else assert(false, "part must be frame | lid | assembly | collision | none");
