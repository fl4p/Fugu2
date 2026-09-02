// Clearance / access probe harness for fugu2-enclosure.scad.
// Renders the intersection of the shroud with a caller-supplied box.
// Empty result = that volume is clear; non-empty = something is in the way.
include <fugu2-enclosure.scad>
with_lid = false; px0=0; py0=0; pz0=0; px1=1; py1=1; pz1=1;
intersection() {
    union() { frame(); if (with_lid) lid(); }
    translate([px0, py0, pz0]) cube([px1-px0, py1-py0, pz1-pz0]);
}
