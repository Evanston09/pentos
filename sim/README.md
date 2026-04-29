# Pentos Sim

This workspace now runs the sim directly from the checked-in `pentos` ROS 2 package.

All ROS and Gazebo commands are intended to run inside the `ros` Docker Compose
service defined in this directory. Run host commands from
[`sim/`](/home/evank/code/rphys/pentos/sim), then enter the container with
`docker compose exec ros bash`. The launch file name is `sim.launch.py`.

## Build

```bash
cd /workspaces/pentos
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
cd /workspaces/pentos
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
source install/setup.bash
ros2 launch pentos sim.launch.py
```

## Run with Klipper bridge

For the full startup order, fake MCU setup, Moonraker commands, and test G-code,
see [`../docs/sim-klipper-moonraker.md`](../docs/sim-klipper-moonraker.md).

The ROS/Gazebo workspace runs in the `ros` Docker Compose service. The compose
file uses host networking, so a Moonraker instance running on the same host is
available at `ws://127.0.0.1:7125/websocket` from inside the container.

```bash
cd /workspaces/pentos
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch pentos sim.launch.py enable_klipper_bridge:=true
```

If Moonraker runs elsewhere:

```bash
ros2 launch pentos sim.launch.py \
  enable_klipper_bridge:=true \
  moonraker_url:=ws://192.168.1.50:7125/websocket
```

The v1 bridge mirrors Klipper XYZ into Gazebo and keeps A/B at fixed defaults:

```bash
ros2 launch pentos sim.launch.py \
  enable_klipper_bridge:=true \
  a_default:=0.0 \
  b_default:=0.0
```

The sim uses:

- `pentos/urdf/pentos.urdf` as the single checked-in robot description
- `package://pentos/...` mesh URIs
- `pentos/config/pentos_controllers.yaml` for `gz_ros2_control`
