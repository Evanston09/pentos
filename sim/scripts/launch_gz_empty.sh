#!/usr/bin/env bash

set -euo pipefail

WORLD_FILE="${1:-empty.sdf}"
shift $(( $# > 0 ? 1 : 0 ))

exec ros2 launch ros_gz_sim gz_sim.launch.py "gz_args:=${WORLD_FILE}" "$@"
