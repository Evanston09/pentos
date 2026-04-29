# Pentos

A research project proposal developing an accessible, fully open-source pathway to 5-axis fused deposition modeling by integrating hardware and software contributions across the entire printing stack. On the hardware side, the work defines a low-cost retrofit of the consumer-grade Ender 3 platform into a functional 5-axis system for under $200 in parts, demonstrating that the mechanical and electronic barriers to multi-axis motion can be overcome with commodity components. On the software side, it introduces a custom kinematic extension to the open-source Klipper firmware that enables true simultaneous 5-axis coordinated motion, a capability absent from mainstream consumer 3D printing firmwares, alongside a multidimensional slicing framework capable of generating coordinated toolpaths for non-planar, supportless, and conformal deposition strategies. By orienting the build platform relative to the toolhead during printing, the system produces parts that are stronger along previously weak layer-bonding directions, smoother across curved surfaces by eliminating stair-stepping artifacts, and printable without support structures even for steep overhangs and complex geometries. Together, these contributions aim to lower the cost and technical barriers that currently restrict multi-axis additive manufacturing to industrial and academic settings, bringing advanced fabrication techniques within reach of hobbyists, makers, and researchers.

## ROS 2 Simulation

The ROS 2 workspace lives under [`sim/`](/home/evank/code/rphys/pentos/sim), not the repository root.

For the complete Klippy fake-MCU, Moonraker, ROS bridge, and Gazebo workflow,
see [`docs/sim-klipper-moonraker.md`](docs/sim-klipper-moonraker.md).

Build and launch from that directory:

```bash
cd sim
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
colcon build --symlink-install --base-paths pentos
source install/setup.bash
ros2 launch pentos sim.launch.py
```

`launch.sim.launch` is not a file in this package.
