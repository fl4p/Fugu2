# Kicad Plugin Parasitics

- 10 nH/cm
* STP110N8F6_V2:  Ldrain= 1nH ,Lsource=2nH and Lgate=2.5nH
* 
https://www.analog-praxis.de/abschaetzung-der-induktivitaet-von-leiterbahnen-a-535549/

https://artist-3d.com/how-to-calculate-the-inductance-of-pcb-trace/
https://resources.altium.com/p/pcb-trace-inductance-and-width-how-wide-too-wide
https://resources.system-analysis.cadence.com/blog/msa2021-is-there-a-pcb-trace-inductance-rule-of-thumb

# Tools
https://saturnpcb.com/saturn-pcb-toolkit/
https://saturnpcb.com/thank-your-pcb-toolkit/


bypass caps

voltage signal traces
- vulnerable to L coupling
- place a resistor at the end

current signal traces
- vulnerable to C coupling
- 


Layout Guidelines
- "To avoid large negative transients on the switch node VSSA (HS) pin, the parasitic inductances between the
source of the top transistor and the source of the bottom transistor must be minimized." (UCC21330x)
- 