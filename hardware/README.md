# Pentos Hardware Bill of Materials

[Illustrated assembly manual (PDF)](pentos-assembly-manual.pdf) | [Manual sources and rebuild instructions](manual/README.md)

BOM transcribed from the **Bill of Materials** section (`tab:bom`) in
[the Pentos paper](../../pentos_paper/main.tex). Costs are the paper’s estimates in USD,
not current supplier quotes. Pack costs are prorated to the quantities used;
shipping and tax are excluded. Supplied hardware is valued at estimated replacement cost.

## Retrofit parts

| Components and quantities | Supplier / brand | Cost |
| --- | --- | ---: |
| Pulleys and belts: 2 PowerGrip 2GT pulleys, 20T, 5mm bore, 6mm belt ($3.99 each); GT2 pulleys, 2mm pitch, 8mm REX bore: 1 each, 20T ($7.99) and 40T ($9.99); 2 GT2 belts, 6mm wide, 184mm pitch length, 92T ($3.19 each). | Gates; goBILDA | $32.34 |
| Shafts: stainless-steel 8mm REX with E-clips; 2 × 32mm ($3.89 each), 1 × 52mm ($4.39). | goBILDA | $12.17 |
| Hubs: 2 × 1309 Series Sonic Hub, 8mm REX bore ($7.99 each). | goBILDA | $15.98 |
| Bearings: 2 packs of 1611 flanged bearings, 8mm REX ID, 14mm OD, 5mm thick, 2 per pack ($5.99/pack); 1 thrust bearing, 12mm ID, 21mm OD, 5mm thick ($4.99). | goBILDA | $16.97 |
| Motors: 2 × NEMA 17, 42STH48-1684MAC ($19.49 each). | LDO | $38.98 |
| Mounting hardware: 4 silicone spacers ($3.00; a 12-pack costs $8.99); 4 M3 standoffs, 15mm ($2.85; one 4-pack); 8 M4 heat-set inserts ($1.74; a 50-pack costs $10.90). | Amazon; REV Robotics; CNC Kitchen | $7.59 |
| Screws: 8 M4 × 12mm; 1 M3 × 8mm; 4 M3 × 35mm; 1 M4 × 16mm. | Bolts and Nuts | $2.56 |
| Heated platform: 1 heatbed tile ($24.99); 1 Garolite plate, 90 × 90mm ($0.65; two 12 × 12in sheets cost $15). | Prusa Research; Amazon | $25.64 |
| Printed structure: 125g PLA, including fabrication supports ($2.25; filament costs $17.99/kg). | PLA filament | $2.25 |
| Connector: 1 Clickmate, 4-pin, 1.5mm pitch, 0151350402. | Molex | $3.69 |
| JST connectors: 4 XHP-3 housings; 1 XHP-2 housing; 14 crimp contacts. | JST | $2.13 |
| Wire: 21.5ft of 22 AWG stranded wire ($4.71; a 50ft spool costs $10.95). | Pololu | $4.71 |
| **Retrofit-parts subtotal** | | **$165.01** |

## Supplied hardware: estimated replacement costs

| Components and quantities | Supplier / brand | Cost |
| --- | --- | ---: |
| Base printer: 1 Ender 3 or compatible clone (budget allocation). | Creality / clone | $150.00 |
| Controller: 1 SKR 1.4 Turbo with 5 TMC2208 drivers. | BIGTREETECH | $65.79 |
| Host: 1 Pi 4 Model B, 4GB, board only. | Raspberry Pi | $100.00 |
| Homing components: 2 magnets, 12 × 3mm ($0.67; a 30-pack costs $9.99); 2 A3144 Hall-effect sensors ($1.30; a 10-pack costs $6.49). | Amazon | $1.97 |
| **Total including retrofit parts** | | **$482.77** |

The total excluding the base printer is **$332.77**.

## Printed parts

The files below are the available printed components. Quantities are assumed to be
one of each per build; confirm against the assembly before printing. The paper budgets
**125 g of PLA including fabrication supports ($2.25)** for the complete printed
structure. That cost is already included above; individual part masses are not specified.

| Part | Qty per build (assumed) | Printable model | STEP model |
| --- | ---: | --- | --- |
| A-axis cradle | 1 | [3MF](printable-parts/a-axis-cradle.3mf) | [STEP](cad/a-axis-cradle.step) |
| A-axis holder, back | 1 | [3MF](printable-parts/a-axis-holder-back.3mf) | [STEP](cad/a-axis-holder-back.step) |
| A-axis holder, front | 1 | [3MF](printable-parts/a-axis-holder-front.3mf) | [STEP](cad/a-axis-holder-front.step) |
| B-axis base | 1 | [3MF](printable-parts/b-axis-base.3mf) | Not included |

Garolite cost is based on plate area and excludes cutting waste.

## Assembly notes

Before assembly, embed both homing magnets during printing. Add slicer pause
commands immediately before the layers that close their pockets, place each
magnet with the correct polarity, and resume printing to enclose it.

At 0.20 mm first and object layers, the verified first-cover heights are
Z 14.40 mm for the A cradle and Z 4.20 mm for the B base. See the
[PrusaSlicer reference projects and settings](manual/slicing/README.md).
Test each magnet with its Hall sensor, mark the working face, and recheck
polarity at the pause before resuming.

Assembly references use **A-axis for tilt** and **B-axis for rotation**, including
when the STEP assembly's internal part names use U and V.

Fastener locations clarified by the builder:

| Fastener | Location / purpose |
| --- | --- |
| M3 × 8 mm | Sonic Hub hardware, as specified by the builder; separate from the M4 cradle attachment screws. |
| M4 × 12 mm | Four cradle attachment screws per Sonic Hub (eight total), matching the CAD mounting holes. |
| M3 bed screws | Bed attachment; the paper lists four M3 × 35 mm screws. |
| Short M3 screws | Motor mounting: four per motor in the assembly drawings. Exact length and quantity are not specified in the paper. |
| Longer M4 screw | Installed underneath the bed to attach the pulley and sandwich the A-axis cradle with the B-axis bed; the paper lists one M4 × 16 mm screw. |
| Pulley grub screws | Supplied with the pulleys. |

These location notes supplement the paper's BOM. Motor mounting screws need to be
accounted for separately because the paper does not list them explicitly.
