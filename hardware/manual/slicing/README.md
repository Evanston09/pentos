# Embedded magnet print preparation

Open these as **projects** in PrusaSlicer (not geometry-only imports):

- [A cradle, with pause](a-axis-cradle-magnet-pause.3mf)
- [B bed base, with pause](b-axis-base-magnet-pause.3mf)

These are layer-reference projects, not machine-ready G-code. Select the actual
printer and filament presets, confirm the printer's configured pause command,
then re-slice and inspect the pocket before exporting. The reference pause
command is M601; firmware support must match the selected printer. Keep the
orientation and layer heights below when using these numbers.

| Part | Last open object layer | First cover / pause before | Object layer | Reference Preview layer |
|---|---|---|---|---|
| A cradle | 71, Z 14.20 mm | Z **14.40 mm** | 72 | 108 |
| B base | 20, Z 4.00 mm | Z **4.20 mm** | 21 | 21 |

PrusaSlicer 2.9.6, 0.20 mm first layer and all object layers, 0.4 mm nozzle,
0.45 mm extrusion width, 3 perimeters, 15% rectilinear infill, no raft. The A
cradle uses snug supports from the build plate only; B uses no supports.
Support layers explain why A's Preview index differs from its object-layer
index. Preview 106 is A's last open object layer; Preview 107 is support only.
Use **Z height** as the primary reference when changing support settings.

Both source Onshape 3MF models are Y-up, with coordinates in meters. The
reference rotates +90 degrees about X, preserving scale and placing the flat
native Y=0 face on the print bed. In print coordinates the models measure
210 x 76.65 x 73.5 mm (A) and 70 x 70 x 5 mm (B).

A's rectangular enclosed pocket is 3.2 x 12.2 x 12.2 mm, from print Z 1.9 to
14.1 mm. Its 12 x 3 mm disc magnet stands vertically, with the tested sensor
face toward the outer end wall (+X). B's cylindrical pocket is approximately
12.2 mm diameter x 3.2 mm deep, from Z 0.8 to 4.0 mm. Its magnet lies flat,
with the tested sensor face DOWN (-Z), toward the print bed and eventual sensor.
The manual's section views remove walls to expose the magnet; the full-part
views show the final enclosure and print orientation.

**Polarity must be tested with the actual Hall sensor and homing input before
insertion, marked TO SENSOR, and checked again at the print pause.** Do not
assume a north/south face. Confirm both trigger and release with the sensor
presented in its final orientation. Finish both magnet-containing prints before
mechanical assembly.

## Verification and regeneration

`magnet-pause-results.json` records source SHA-256 hashes, cavity geometry,
actual closure heights and support settings. `prepare_magnet_references.py`
extracts extrusion segments from Prusa G-code, checks the last open layer has
no extrusion through the pocket interior, checks enclosed pocket layers contain
no support, and identifies the first closing **bridge**. Thus the values are
sliced results, not rounding the CAD roof height. Toolpath illustrations in the
manual use these actual extracted segments.

To recreate the raw reference files, from the hardware directory:

```bash
mkdir -p tmp/pdfs/magnet-slicing
prusa-slicer --load manual/slicing/a-axis-cradle-reference.ini --rotate-x 90 --center 110,110 --export-gcode --output tmp/pdfs/magnet-slicing/a-axis-cradle.gcode printable-parts/a-axis-cradle.3mf
prusa-slicer --load manual/slicing/magnet-layer-reference.ini --rotate-x 90 --center 110,110 --export-gcode --output tmp/pdfs/magnet-slicing/b-axis-base.gcode printable-parts/b-axis-base.3mf
prusa-slicer --rotate-x 90 --center 110,110 --export-3mf --output tmp/pdfs/magnet-slicing/a-axis-reference.3mf printable-parts/a-axis-cradle.3mf
prusa-slicer --rotate-x 90 --center 110,110 --export-3mf --output tmp/pdfs/magnet-slicing/b-axis-reference.3mf printable-parts/b-axis-base.3mf
python3 manual/slicing/prepare_magnet_references.py
python3 manual/slicing/verify_pause_projects.py
PENTOS_OCIO=$(python3 manual/configure_color_management.py)
OCIO="$PENTOS_OCIO" blender --background -t 6 -noaudio --python manual/render_magnet_preparation.py
python manual/build_manual.py
```

The round-trip verification slices each saved project again, confirms 0.20 mm
settings survived, and checks the pause occurs before any extrusion on the
expected first-cover layer, with bridge infill following it. This verifies the
saved projects, not a physical test print or a printer's firmware behavior.

[Prusa's pause instructions](https://help.prusa3d.com/article/insert-pause-or-custom-g-code-at-layer_120490)
specify that the pause executes before the selected layer.
