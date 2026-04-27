#!/usr/bin/env bash

# Source this file from an interactive container shell:
#   source sim/scripts/source_pentos.bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "This script must be sourced so the ROS environment stays active:"
  echo "  source ${BASH_SOURCE[0]}"
  exit 1
fi

_pentos_source() {
  local script_dir
  local sim_dir
  local previous_dir

  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || return
  sim_dir="$(cd -- "${script_dir}/.." && pwd)" || return

  source /opt/ros/jazzy/setup.bash || return

  previous_dir="${PWD}"
  cd "${sim_dir}" || return

  colcon build --symlink-install --base-paths pentos || {
    cd "${previous_dir}" || true
    return 1
  }

  source install/setup.bash || {
    cd "${previous_dir}" || true
    return 1
  }

  cd "${previous_dir}" || return
}

_pentos_source
unset -f _pentos_source
