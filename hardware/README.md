# Pentos hardware

Pentos adds a tilting and rotating heated build platform to an Ender 3 V2 for
five-axis FDM printing. **A** is tilt; **B** is rotation. This folder contains
the printable parts, CAD assembly, bill of materials and assembly instructions.

**[Assembly manual (PDF)](pentos-assembly-manual.pdf)** ·
**[Bill of materials (CSV)](bom.csv)** ·
**[Full STEP assembly](Pentos.step)** ·
**[Pentos paper](https://github.com/Evanston09/pentos_paper)**

## What to print

Print **one of each** of these four parts:

| Part | Quantity | Model | Embedded magnet |
| --- | ---: | --- | --- |
| A-axis cradle | 1 | [3MF](printable-parts/a-axis-cradle.3mf) | One 12 mm diameter x 3 mm disc |
| A-axis holder, front / drive side | 1 | [3MF](printable-parts/a-axis-holder-front.3mf) | None |
| A-axis holder, back | 1 | [3MF](printable-parts/a-axis-holder-back.3mf) | None |
| B-axis bed base | 1 | [3MF](printable-parts/b-axis-base.3mf) | One 12 mm diameter x 3 mm disc |

The paper budgets **125 g of PLA, including fabrication supports**, for the
printed structure. Place the holders on their broad, flat triangular sides;
place the cradle and bed base on their flat bases. The raw Onshape exports
are Y-up; a +90-degree rotation about X puts that flat face on the print bed.

### Embed the magnets during printing

**Check polarity with the actual Hall sensor before insertion, mark the
working face TO SENSOR, and check it again before resuming the print.**
Confirm the homing input triggers near the magnet and releases when removed.
The marked face points toward the cradle's outer end wall for A, and down
toward the print bed for B. The manual shows both pocket orientations.

Use these pre-oriented PrusaSlicer reference projects for the two magnet parts:

| Part | Reference project | Pause before layer at Z | Object layer | Preview layer |
| --- | --- | ---: | ---: | ---: |
| A-axis cradle | [3MF with pause](manual/slicing/a-axis-cradle-magnet-pause.3mf) | **14.40 mm** | 72 | 108 |
| B-axis bed base | [3MF with pause](manual/slicing/b-axis-base-magnet-pause.3mf) | **4.20 mm** | 21 | 21 |

These heights use **0.20 mm first and subsequent object layers**, with no raft.
The cradle reference uses build-plate-only snug supports; the bed base uses
none. Support layers change the Preview numbering, so use **Z height** to
locate the pause. Select your actual printer and filament, confirm its pause
command, and re-slice before exporting G-code. At the pause, seat the magnet
below the next toolpath, then resume to enclose it.

See [print settings and pause verification](manual/slicing/README.md) for details.

## Bill of materials

Download **[bom.csv](bom.csv)** for quantities, specifications, suppliers and
estimated costs from the paper's [Bill of Materials table](https://github.com/Evanston09/pentos_paper/blob/main/main.tex).

| Scope | Paper estimate (USD) |
| --- | ---: |
| Retrofit parts | $165.01 |
| Priced-items total, including a $150 base-printer allocation | $482.77 |
| Priced items excluding the base printer | $332.77 |

These are the paper's reproduction estimates, not current quotes. Pack costs
are prorated to the quantities used; shipping and tax are excluded. Supplied
components are valued at estimated replacement cost. The CSV retains grouped
prices for the screw assortment and JST connectors because the paper does not
price those pieces individually. Each CSV cost is the **whole row's cost**;
sum the `Cost_USD` column for the paper's priced-items total.

Also account for **eight M3 motor-mounting screws** and hot glue for securing
the Hall sensors. These are not separately priced in the paper; the motor
screw length must suit the motor and printed mount. The mounting step reuses
the printer's four original M4 countersunk bed screws and leveling knobs.

## Assembly

Follow the **[illustrated assembly manual](pentos-assembly-manual.pdf)** after
printing the magnet-containing parts. It covers the bed, hubs, shafts and
bearings, both belt drives, Hall sensors, and mounting the completed mechanism
on the original Y gantry.

The documented build uses an **Ender 3 V2** with a **170 x 170 mm** bed-mounting
pattern. Other Ender 3 variants and clones require a geometry and clearance
check. Keep the bed wiring clear of both drives and allow slack for tilt and
rotation; B cannot rotate continuously because the bed has no slip ring.

Printer configurations are in [klipper_configs](../klipper_configs/).

## Files

| Path | Contents |
| --- | --- |
| [pentos-assembly-manual.pdf](pentos-assembly-manual.pdf) | Illustrated print preparation and assembly guide |
| [bom.csv](bom.csv) | BOM transcribed from the paper; one row per priced item or grouped set |
| [Pentos.step](Pentos.step) | Complete CAD assembly |
| [printable-parts/](printable-parts/) | Four printable 3MF models |
| [cad/](cad/) | Individual STEP exports and the shaft E-clip reference |
| [manual/slicing/](manual/slicing/) | PrusaSlicer reference projects and verified pause settings |
| [manual/](manual/) | Blender scenes, render assets and [manual rebuild instructions](manual/README.md) |
