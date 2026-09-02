#!/bin/bash
# Full gate for the Fugu2 shroud. Every openscad run is inspected for
# diagnostics: a run that could not evaluate is a FAILURE, never a pass.
cd "$(dirname "$0")"
fail=0
run () {  # run <label> <expect: EMPTY|SOLID> <args...>
  label=$1; expect=$2; shift 2
  out=$(openscad -o /tmp/check-out.stl -D 'provisional=true' "$@" fugu2-enclosure.scad 2>&1)
  if echo "$out" | grep -qEi "ERROR|WARNING"; then
      echo "  FAILED (did not evaluate)  $label"
      echo "$out" | grep -Ei "ERROR|WARNING" | head -2 | sed 's/^/      /'
      fail=1; return
  fi
  if echo "$out" | grep -q "top level object is empty"; then got=EMPTY; else got=SOLID; fi
  if ! echo "$out" | grep -q "Simple:[[:space:]]*yes" && [ "$got" = SOLID ]; then
      echo "  FAIL   $label — result is not a simple (manifold) solid"; fail=1; return
  fi
  [ "$got" = "$expect" ] && echo "  ok     $got   $label" \
                         || { echo "  FAIL   got=$got want=$expect  $label"; fail=1; }
}
for v in asbuilt shifted; do
  echo "variant=$v"
  run "frame is one manifold solid"        SOLID -D "variant=\"$v\"" -D 'part="frame"'
  run "lid is one manifold solid"          SOLID -D "variant=\"$v\"" -D 'part="lid"'
  run "no collision with the board"        EMPTY -D "variant=\"$v\"" -D 'part="collision"'
  run "components clear by >= 1.2 mm"      EMPTY -D "variant=\"$v\"" -D 'part="collision"' -D 'grow=1.2'
  # the two deliberately-tight interfaces, checked against their declared clearance
  run "board edge keeps gap_left (0.2)"    EMPTY -D "variant=\"$v\"" -D 'part="collision"' -D 'grow_pcb=0.15'
  run "screw heads keep head_clear (0.6)"  EMPTY -D "variant=\"$v\"" -D 'part="collision"' -D 'grow_head=0.45'
done
echo "unmeasured default must refuse to render"
if openscad -o /tmp/check-out.stl fugu2-enclosure.scad 2>&1 | grep -q "Assertion.*measured"; then
  echo "  ok     refused"; else echo "  FAIL   rendered without measurements"; fail=1; fi
echo
./probe.sh || fail=1
echo
[ $fail -eq 0 ] && echo "=== ALL CHECKS PASSED ===" || echo "=== CHECK FAILURES — see above ==="
exit $fail
