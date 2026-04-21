#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

ros2 launch ros_gz_sim gz_sim.launch.py gz_args:=empty.sdf &
sleep 5

ros2 run ros_gz_sim create \
  -world empty \
  -name pentos \
  -file "$PWD/pentos/urdf/pentos.urdf" \
  -z 0.05

wait
