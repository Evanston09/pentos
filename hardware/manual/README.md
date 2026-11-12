# Pentos assembly manual

[Assembly PDF](../pentos-assembly-manual.pdf)

## Rebuild

```bash
PENTOS_OCIO=$(python3 manual/configure_color_management.py)
OCIO="$PENTOS_OCIO" blender --background -t 6 -noaudio --python manual/render_blender.py
python manual/build_manual.py
```

Existing stage images are reused. Add `-- --force` after changing geometry,
materials or cameras. To refresh selected views, also add
`--only=03-holders,06c-screw-detail` after the `--` separator.

PDF generation requires ReportLab, Pillow and Open Sans fonts in
`/usr/share/fonts/open-sans/`. The Blender scene is saved as
`pentos-assembly.blend`; rendered views, labels and guides are in
`assets/blender/`.

## Geometry and assembly views

The Blender script reads `assets/meshes.npz`, exported from `Pentos.step`,
preserving fitted positions and converting Y-up to Z-up. The earlier
`render_assembly.py` importer requires `cadquery-ocp==7.9.3.1.1`, NumPy and VTK.
Delete the mesh cache and run the importer after replacing the STEP assembly.

The twelve steps cover the bed, cradle hubs, holders, A drive, cradle bearing,
B motor and assembled thrust bearing, joining the cradle to the holders, bed
installation, B drive, final tightening, homing parts, and attachment to the original Ender Y gantry.

Both holder shafts approach from their clipped sides. Factory-fitted E-clips
remain attached. The 52 mm shaft, its clip and 40T pulley move together in the
holder view. The clip is also available as
[`rex-shaft-e-clip.step`](../cad/rex-shaft-e-clip.step), extracted from the assembly.

Hub attachment screws enter from inside the cradle. The four M3 x 35 mm bed
screws enter from below the B-axis base. The assembled flanged bearing enters
the cradle seat from below; the thrust bearing stays assembled. The cradle is
omitted during A-motor installation and fitted between the holders afterward.
The B-drive screw view includes the complete bed.

Additional screws and belts are schematic Blender geometry. Screw mount centers
come from CAD hole loops in `assets/fastener-anchors.json`. Motor screw drawings
use nominal 8 mm shanks; the manual specifies M3 without asserting a confirmed
length. Hardware specifications otherwise follow the paper BOM and builder
corrections.

Dotted guides join exploded positions to fitted positions through the same
camera. Separation distances are illustrative. PDF cropping transforms the
images, labels and guides together. Labels sit outside the image bounds.

The A motor pulley is shifted 2.7 mm outward on its shaft to match the driven
pulley's tooth band. Its 6 mm belt is centered in both 7 mm grooves, leaving
0.5 mm at each edge. Both pulley axes are fitted from circular CAD flange
rings; the belt thickness extends outward from the pitch line. The renderer
asserts groove clearance and that the shifted pulley remains on the motor
shaft. These are assembly adjustments; the original STEP is unchanged.

The B belt uses a shared axial plane within both CAD tooth bands. Its 6 mm
width is checked against both groove limits; pulley centers are derived from
the circular flanges rather than the overall part bounding boxes.

Preparations 00, 00A and 00B show polarity testing and separate print-pause guides
for the actual A cradle and B base. At 0.20 mm first and object layers, verified
PrusaSlicer first-cover heights are Z 14.40 mm (A) and Z 4.20 mm (B). Blender
pocket sections show the tested sensor-facing magnet faces; toolpath panels
come from actual PrusaSlicer extrusion paths.

[Reference projects and verification](slicing/README.md) include the saved
pause events, profile assumptions, source hashes and regeneration commands.
Select the actual printer/filament and verify its pause command before export.
The homing step mounts sensors only; magnets are enclosed during printing.

To refresh the preparation renders, use the same OCIO environment:

```bash
OCIO="$PENTOS_OCIO" blender --background -t 6 -noaudio --python manual/render_magnet_preparation.py
python manual/build_manual.py
```

`render_style.py` shares physical materials and studio lighting between both
renderers. Printed parts use matte blue/orange material with subtle 0.20 mm
layer relief; metals use reflective silver, and the build surface uses muted
gold. AgX handles highlights, and Freestyle outlines are disabled. The local
OCIO helper adapts the installed Blender config's newer metadata for this
system's OCIO 2.4 library while retaining the installed color transforms/LUTs.

Instructions contain assembly actions and essential checks; notes are kept
only for the belt specification. Numbered markers and paragraph text share
the same first-line baseline.


## Ender gantry mounting

The final page uses the supplied `Creality-Ender3-V2 - Y-Gantry.step` and
`Creality-Ender3-V2 - Bed Level Knob.step`. The gantry's four mounting axes form
a 170 x 170 mm square, matching the holder feet. Registration is a translation
only: the plate top meets the holder soles, and the knob tops meet the plate
underside. The plate is 4 mm thick and the printed feet are 8 mm thick.

`prepare_gantry_mount.py` meshes both STEP files, records source hashes in
`assets/ender-mount-registration.json`, and checks all four axes against the
actual holder mesh. The holder countersinks are 90 degrees, 7 mm across,
leading into 4 mm bores. `render_gantry_mount.py` loads the assembled Blender
scene, adds the gantry and four copies of the original knob, and renders a
complete mounted view and an exploded corner detail. The mounted scene is
saved separately as `pentos-mounted.blend`.

The manual specifies reusing the four original M4 countersunk bed screws and
leveling knobs, with the heads above and knobs below. The STEP files do not
include the screws. Their illustration uses a cross recess, a 90-degree head
matched to the holder countersink, M4 x 0.7 threads and an illustrative 30 mm
overall length; the PDF does not prescribe a replacement screw length.
The [Ender 3 V2 disassembly guide, step 5](https://www.ifixit.com/Guide/1.+BLV+Ender+3+V2+Disassembly/152316)
identifies the four original bed fasteners as M4 countersunk screws. Stock bed
springs are omitted so the rigid holder feet seat directly against the gantry.

```bash
python manual/prepare_gantry_mount.py
PENTOS_OCIO=$(python3 manual/configure_color_management.py)
OCIO="$PENTOS_OCIO" blender --background manual/pentos-assembly.blend -t 6 -noaudio --python manual/render_gantry_mount.py
python manual/build_manual.py
```


## Title page

The cover uses `assets/pentos-paper-render.png`, copied without alteration from
`pentos_paper/assets/pentos-printer.png`, the full-printer render used on the
paper's title page. The paper credits Evan Kim, SOLIDWORKS Visualize, 2026.
Only transparent margins are cropped during PDF layout. The cover contains
PENTOS and Assembly manual; preparation and assembly step numbers are unchanged.
