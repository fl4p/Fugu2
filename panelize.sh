
#cat ../hw/precision-current-sensor/precision-current-sensor.kicad_pcb

#kikit panelize \
#  --layout 'plugin; code: panelize.py.Plugin; cols: 2; space: 2mm; boards: 1 * Fugu2.kicad_pcb, 2 * psu/buck100.kicad_pcb, 1 * ../hw/precision-current-sensor/precision-current-sensor.kicad_pcb' \
#  --tabs full \
#  --cuts vcuts \
# Fugu2.kicad_pcb panelized1.kicad_pcb

kikit panelize \
  --layout 'plugin; code: panelize.py.Plugin2; cols: 2; space: 2mm' \
    --tabs 'fixed; hwidth: 4mm; vwidth: 4mm' \
    --cuts vcuts \
    --post 'millradius: 1mm' \
  Fugu2.kicad_pcb panelized2.kicad_pcb

  # CHSXPPVA
#--tabs ...etc...
