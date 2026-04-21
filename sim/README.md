# Pentos Sim

This workspace now runs the sim directly from the checked-in `pentos` ROS 2 package.

Run the commands below from the [`sim/`](/home/evank/code/rphys/pentos/sim) directory. The launch file name is `sim.launch.py`.

## Build

```bash
cd /workspaces/pentos/sim
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
scripts/run_pentos_sim.sh
```

Or launch the package directly:

```bash
cd /workspaces/pentos/sim
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
source install/setup.bash
ros2 launch pentos sim.launch.py
```

The sim uses:

- `pentos/urdf/pentos.urdf` as the single checked-in robot description
- `package://pentos/...` mesh URIs
- `pentos/config/pentos_controllers.yaml` for `gz_ros2_control`
