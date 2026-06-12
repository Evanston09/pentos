# Docker Klipper, Moonraker, and Gazebo

This setup keeps Klipper firmware source out of this repository. Klippy and
Moonraker run from the published `mkuf` Docker images, while the ROS 2/Gazebo
simulation remains in `sim/ros/`.

```text
G-code client
  -> Moonraker at http://127.0.0.1:7125
  -> Klippy socket at printer_data/run/klipper.sock
  -> ROS 2 klipper_gazebo_bridge
  -> Gazebo position controller
  -> Pentos model movement
```

## Files

- `docker-compose.klipper.yml`: Klipper and Moonraker containers.
- `ros/docker-compose.yml`: ROS 2/Gazebo development container.
- `printer_data/config/printer.cfg`: Klipper printer config.
- `printer_data/config/moonraker.conf`: Moonraker config.
- `printer_data/run/`: Klipper socket and tty, generated locally.
- `printer_data/gcodes/`: local G-code storage.
- `printer_data/logs/`: Klipper and Moonraker logs.

Only the four Docker image volume directories are used under `printer_data`:
`config`, `run`, `gcodes`, and `logs`.

## Start Klipper and Moonraker

Run this from `sim/`:

```bash
docker compose -f docker-compose.klipper.yml up
```

The Klipper container uses:

```text
mkuf/klipper:latest
```

The Moonraker container uses:

```text
mkuf/moonraker:latest
```

Moonraker talks to Klippy through:

```text
/opt/printer_data/run/klipper.sock
```

Verify the API:

```bash
curl -s 'http://127.0.0.1:7125/server/info'
curl -s 'http://127.0.0.1:7125/printer/objects/query?toolhead=position,homed_axes'
```

## Start Gazebo and the Bridge

Start the ROS container from `sim/ros/`:

```bash
docker compose up -d ros
docker compose exec ros bash
```

Inside the container:

```bash
cd /workspaces/pentos
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
colcon build --symlink-install --base-paths pentos
source install/setup.bash
ros2 launch pentos sim.launch.py enable_klipper_bridge:=true
```

The bridge connects to:

```text
ws://127.0.0.1:7125/websocket
```

If Moonraker runs elsewhere:

```bash
ros2 launch pentos sim.launch.py \
  enable_klipper_bridge:=true \
  moonraker_url:=ws://192.168.1.50:7125/websocket
```

## Send a Test Move

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"script":"SET_KINEMATIC_POSITION X=0 Y=0 Z=0"}' \
  http://127.0.0.1:7125/printer/gcode/script

curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"script":"G1 X25 Y10 Z5 F1200"}' \
  http://127.0.0.1:7125/printer/gcode/script
```

Check state:

```bash
curl -s 'http://127.0.0.1:7125/printer/objects/query?toolhead=position,homed_axes'
```

## Notes

`mkuf/klipper:latest` is a Klippy runtime image. It removes the need to keep a
Klipper source checkout in this repository. If the simulation later needs
Klipper's old file-backed fake MCU mode, add that as a separate container/image
instead of bringing the firmware source tree back into this repo.
