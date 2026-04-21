#!/usr/bin/env bash

set -euo pipefail

set +u
source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
set -u

cd "$(dirname "$0")/.."

if [[ -f install/setup.bash ]]; then
  set +u
  source install/setup.bash
  set -u
else
  printf 'install/setup.bash not found. Run colcon build --symlink-install first.\n' >&2
  exit 1
fi

exec ros2 launch pentos sim.launch.py
