# Basic Klipper Setup

This setup uses a standard Raspberry Pi connected to an Ender 3 V2 motherboard, along with an SKR Turbo v1.4 and two TMC2130 motor drivers on an external motor board to control the two additional stepper motors.

## Sim-only Klipper

Use `sim-printer.cfg` when Klippy should pretend to have an MCU and publish
motion for the ROS/Gazebo bridge through Moonraker. Keep `printer.cfg` for the
real hardware.

The complete sim runbook is in
[`../docs/sim-klipper-moonraker.md`](../docs/sim-klipper-moonraker.md).
