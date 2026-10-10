DIY MACRO PAD MODEL — PROTOTYPE ONLY

Files:
- macro_base.stl : bottom enclosure shell, nominal 145 x 75 x 17 mm
- macro_top_plate.stl : removable top/switch plate, 145 x 75 x 3 mm
- tape_carrier_prototype.stl : printed carrier/jig with shallow generic tape channels, 139 x 69 x 1.6 mm
- macropad.scad : editable OpenSCAD source; change part="base", "top", "carrier", or "assembly"

Target assembled outside dimensions: 145 x 75 x 20 mm.

IMPORTANT LIMITATIONS:
- These are first-fit concept models, not verified component-specific footprints.
- The board shown as “RP2040 Pico USB-C” may be a Pico-compatible clone. Measure the actual board, header spacing, board edge and USB connector before final fitting.
- Display opening is an approximate 36 x 23 mm viewing window. Measure your exact 1.9-inch ST7789 module and active display area; mounting holes in the model are placeholders.
- Four 14 x 14 mm switch plate cutouts are nominal MX plate openings. Hot-swap sockets attach to a real PCB, not the printed carrier. Verify the exact Kailh socket model and switch plate compatibility.
- Encoder shaft hole is 7.2 mm as a starting estimate. Measure the EC11 bushing and anti-rotation tab/nut.
- RGB strip channel is not included because strip width, backing thickness and LED density are unknown. Use a case channel/adhesive path sized to your actual strip and allow a cable exit.
- The carrier STL is a mechanical jig/substrate only. Copper tape paths are generic grooves, NOT a tested circuit or electrical PCB. Route each net yourself; crossings need insulation/bridging wires. Do not use it as a mains or high-current board.
- Check USB power budget and LED strip voltage/current before wiring. WS2811/WS2812B/WS2813/WS2815 are not interchangeable: some are 5 V and some are 12 V. Identify the exact strip before powering it. Share ground with the controller, and use an appropriate level shifter for 5 V data where required.
- Print a low-cost draft first, test-fit the actual parts, then adjust macropad.scad before final printing.

Suggested print: PLA/PETG, 0.2 mm layers, 3 perimeters. Print the top plate flat. Check screw dimensions and add heat-set inserts or nuts as preferred.
