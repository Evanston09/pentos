ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-ros-gz \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/pentos
