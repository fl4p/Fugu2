#!/bin/bash
# Access/clearance gate for the Fugu2 shroud. Any openscad diagnostic other than
# a clean empty/non-empty verdict is a FAILED probe, never a pass.
cd "$(dirname "$0")"
fail=0
probe () {
  exp=$1; name=$2; shift 2
  out=$(openscad -o /tmp/probe-out.stl -D 'provisional=true' -D 'part="none"' \
        -D "with_lid=$1" -D "px0=$2" -D "py0=$3" -D "pz0=$4" \
        -D "px1=$5" -D "py1=$6" -D "pz1=$7" probe.scad 2>&1)
  if echo "$out" | grep -qEi "WARNING|ERROR"; then
      echo "  FAILED (probe did not run)  $name"; echo "$out" | grep -Ei "WARNING|ERROR" | head -2
      fail=1; return
  fi
  if echo "$out" | grep -q "top level object is empty"; then got=CLEAR; else got=BLOCKED; fi
  if [ "$got" = "$exp" ]; then echo "  ok      $got    $name"
  else echo "  FAIL    got=$got want=$exp  $name"; fail=1; fi
}
#      want    description                                   lid    x0    y0   z0    x1     y1   z1
probe CLEAR   "USB-C plug path through the top wall"          false 17.24 -14   6.9  27.28  2.0 13.3
probe CLEAR   "terminal bay open from above"                  true   3.45 74    7.0  44.19 99.0 30.0
probe CLEAR   "J5 CAN/UART socket reachable"                  true  45.46 74    7.0  49.06 99.0 20.0
probe CLEAR   "screwdriver straight down onto terminals"      true   5.0  74.5  8.0  43.0  86.0 60.0
probe CLEAR   "Q1 tab + M4 head exit slot"                    false -9.0  23.5  0.1  -2.6  36.0  4.6
probe CLEAR   "boot button poke hole"                         true  24.7   9.1 "lid_z0-1"  27.6  12.1 "lid_z1+1"
probe BLOCKED "left wall SOLID over by 15..55 (coil drill zone)" false -5.4 15  7.0  -2.6  55   30.0
probe BLOCKED "no wall opening below z=12 (62109-1 9.1.4.3)"  false 52.4  28    0.5  55.2  64    11.5
probe BLOCKED "lid actually closes over the electrolytics"    true   8    28   "lid_z0+0.5"  44    50   "lid_z1-0.5"
probe BLOCKED "antenna bulge is closed, not a window"         false 52.4   4   10.0  62.0  22   20.0
probe BLOCKED "frame top ring continuous under the lid rim"   false -5.4  18   "frame_top-1.5"  -2.6  22   "frame_top-0.1"
probe BLOCKED "lid plate present above that ring"             true  -5.4  18   "lid_z0+0.5"  -2.6  22   "lid_z1-0.5"
echo
[ $fail -eq 0 ] && echo "ALL PROBES PASSED" || echo "PROBE FAILURES — see above"
exit $fail
