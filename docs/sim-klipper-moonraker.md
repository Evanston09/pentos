# Simulated Klipper, Moonraker, and Gazebo

This runbook starts the complete simulation stack while keeping Klipper editable
from this checkout:

```text
G-code from curl or another Moonraker client
  -> Moonraker container at http://127.0.0.1:7125
  -> Klippy API socket at printer_data/run/klipper.sock
  -> local Klippy running with a fake/file-backed MCU
  -> Moonraker websocket at ws://127.0.0.1:7125/websocket
  -> ROS 2 klipper_gazebo_bridge running inside the ROS container
  -> Gazebo position controller
  -> Pentos model movement
```

Klippy is still the motion planner. The fake MCU mode only replaces the real
serial microcontroller with a file output stream, so Klippy can boot, accept
G-code, and publish position state without printer electronics.

Moonraker can run in Docker because it does not need to execute your local
Klipper code. Klippy should run locally from `klipper/` when you are modifying
Klipper.

## Components

- `klipper/`: Klipper source tree. Build the host-simulator MCU dictionary here.
- `klipper_config/sim-printer.cfg`: Minimal sim-only Klipper printer config.
- `docker-compose.moonraker.yml`: Containerized Moonraker.
- `printer_data/config/moonraker.conf`: Moonraker config mounted into Docker.
- `printer_data/run/`: Shared runtime directory for the Klippy socket.
- `printer_data/gcodes/`: Shared G-code directory.
- `sim/`: ROS 2 Docker workspace containing the Gazebo model and bridge node.
- `sim/pentos/pentos_klipper_bridge/`: Moonraker-to-Gazebo bridge code.

All ROS and Gazebo commands run inside the `ros` service from
`sim/docker-compose.yml`. Klippy runs on the host from the editable local
checkout. Moonraker runs in Docker from `docker-compose.moonraker.yml`.

Keep `klipper_config/printer.cfg` for real hardware. Do not use it for the fake
MCU simulation path.

## One-Time Setup

Create the runtime folders:

```bash
mkdir -p /home/evank/code/rphys/pentos/printer_data/run
mkdir -p /home/evank/code/rphys/pentos/printer_data/gcodes
mkdir -p /home/evank/code/rphys/pentos/printer_data/logs
mkdir -p /tmp/pentos-klippy-out
```

Build Klipper's host-simulator dictionary:

```bash
cd /home/evank/code/rphys/pentos/klipper
cp test/configs/hostsimulator.config .config
make olddefconfig
make
```

This creates `klipper/out/klipper.dict`, which Klippy needs when it runs with
`-o`.

Install Klippy's Python dependencies with `uv`:

```bash
cd /home/evank/code/rphys/pentos
uv sync
uv pip install -r klipper/scripts/klippy-requirements.txt
```

```bash
cd /home/evank/code/rphys/pentos/sim
docker compose up -d ros
docker compose exec ros bash
```

Then, inside that container:

```bash
cd /workspaces/pentos
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
colcon build --symlink-install --base-paths pentos
source install/setup.bash
```

## Start the Stack

Use three terminals.

### Terminal 1: Klippy with a fake MCU

```bash
cd /home/evank/code/rphys/pentos/klipper
uv run python klippy/klippy.py ../klipper_config/sim-printer.cfg \
  -I /tmp/pentos_printer \
  -a /home/evank/code/rphys/pentos/printer_data/run/klipper.sock \
  -l /home/evank/code/rphys/pentos/printer_data/logs/klippy.log \
  -o /tmp/pentos-klippy-out/fake.serial \
  -d out/klipper.dict
```

Important flags:

- `-a .../printer_data/run/klipper.sock`: exposes Klippy's API socket for
  Moonraker.
- `-o /tmp/pentos-klippy-out/fake.serial`: writes MCU traffic to a file instead
  of opening a real serial device.
- `-d out/klipper.dict`: loads the host-simulator MCU protocol dictionary.
- `-I /tmp/pentos_printer`: creates a pseudo terminal for direct G-code access.

Expected log line:

```text
Configured MCU 'mcu'
```

### Terminal 2: Moonraker

```bash
cd /home/evank/code/rphys/pentos
docker compose -f docker-compose.moonraker.yml up
```

Moonraker reads this from `printer_data/config/moonraker.conf`:

```ini
klippy_uds_address: /opt/printer_data/run/klipper.sock
```

That is the container view of the socket Klippy creates on the host at:

```text
/home/evank/code/rphys/pentos/printer_data/run/klipper.sock
```

Moonraker exposes the websocket used by the ROS bridge:

```text
ws://127.0.0.1:7125/websocket
```

Verify Moonraker and Klippy:

```bash
curl -s 'http://127.0.0.1:7125/server/info'
curl -s 'http://127.0.0.1:7125/printer/objects/query?toolhead=position,homed_axes'
```

Expected server fields:

```json
"klippy_connected": true
"klippy_state": "ready"
```

### Terminal 3: Gazebo and the Klipper bridge

Run this inside the ROS container, not on the host:

```bash
cd /home/evank/code/rphys/pentos/sim
docker compose exec ros bash
```

Then, inside that container:

```bash
cd /workspaces/pentos
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
source install/setup.bash
ros2 launch pentos sim.launch.py enable_klipper_bridge:=true
```

If Moonraker is on another machine, run this inside the ROS container:

```bash
ros2 launch pentos sim.launch.py \
  enable_klipper_bridge:=true \
  moonraker_url:=ws://192.168.1.50:7125/websocket
```

The bridge publishes commands to:

```text
/pentos_position_controller/commands
```

The v1 bridge mirrors Klipper XYZ and holds A/B at defaults:

```bash
ros2 launch pentos sim.launch.py \
  enable_klipper_bridge:=true \
  a_default:=0.0 \
  b_default:=0.0
```

## Move the Sim

Because this is fake MCU mode, use `SET_KINEMATIC_POSITION` to mark axes as
homed before sending normal moves:

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"script":"SET_KINEMATIC_POSITION X=0 Y=0 Z=0"}' \
  http://127.0.0.1:7125/printer/gcode/script

curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"script":"G1 X25 Y10 Z5 F1200"}' \
  http://127.0.0.1:7125/printer/gcode/script
```

Check the position:

```bash
curl -s 'http://127.0.0.1:7125/printer/objects/query?toolhead=position,homed_axes&motion_report=live_position'
```

In fake MCU mode, `toolhead.position` updates reliably. `motion_report` may stay
at zero because no real MCU step feedback is occurring. The bridge therefore
prefers `toolhead.position` and falls back to `motion_report.live_position`.

## Detached Start

For a background Klippy process:

```bash
cd /home/evank/code/rphys/pentos/klipper
nohup setsid uv run --no-sync python klippy/klippy.py ../klipper_config/sim-printer.cfg \
  -I /tmp/pentos_printer \
  -a /home/evank/code/rphys/pentos/printer_data/run/klipper.sock \
  -l /home/evank/code/rphys/pentos/printer_data/logs/klippy.log \
  -o /tmp/pentos-klippy-out/fake.serial \
  -d out/klipper.dict \
  >/tmp/pentos-klippy.stdout 2>&1 < /dev/null &
```

For a background Moonraker container:

```bash
cd /home/evank/code/rphys/pentos
docker compose -f docker-compose.moonraker.yml up -d
```

Stop them with:

```bash
pkill -f 'klippy.py ../klipper_config/sim-printer.cfg'
docker compose -f docker-compose.moonraker.yml down
```

## Logs and Health Checks

Useful files:

```text
/home/evank/code/rphys/pentos/printer_data/logs/klippy.log
/home/evank/code/rphys/pentos/printer_data/logs/moonraker.log
/home/evank/code/rphys/pentos/printer_data/run/klipper.sock
/tmp/pentos-klippy.stdout
```

Useful checks:

```bash
pgrep -af 'klippy.py|moonraker'
docker compose -f docker-compose.moonraker.yml ps
curl -s 'http://127.0.0.1:7125/server/info'
curl -s 'http://127.0.0.1:7125/printer/objects/query?toolhead=position,homed_axes'
```

## Troubleshooting

If Moonraker reports `klippy_connected:false`, check:

- Klippy is running.
- `printer_data/run/klipper.sock` exists.
- `printer_data/config/moonraker.conf` points at
  `/opt/printer_data/run/klipper.sock`.
- Klippy was started with
  `-a /home/evank/code/rphys/pentos/printer_data/run/klipper.sock`.

If Moonraker returns `401 Unauthorized` for local curl requests, check that
`printer_data/config/moonraker.conf` has loopback in
`[authorization] trusted_clients`.

If Klippy exits immediately, check:

- `klipper/out/klipper.dict` exists.
- The command includes both `-o` and `-d`.
- The log contains `Configured MCU 'mcu'`.

If Gazebo does not move, check:

- Moonraker returns `klippy_state: ready`.
- The ROS launch used `enable_klipper_bridge:=true`.
- The bridge can reach `ws://127.0.0.1:7125/websocket`.
- `toolhead.position` changes after G-code moves.
