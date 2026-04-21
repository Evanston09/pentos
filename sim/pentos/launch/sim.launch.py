from pathlib import Path
import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def _prepend_env_path(value: str, existing: str) -> str:
    if not existing:
        return value
    return f"{value}{os.pathsep}{existing}"


def _render_urdf(urdf_path: Path, config_path: Path) -> tuple[str, str]:
    robot_description = urdf_path.read_text(encoding="utf-8").replace(
        "$(find pentos)/config/pentos_controllers.yaml",
        str(config_path),
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="pentos_",
        suffix=".urdf",
        delete=False,
    ) as rendered_urdf:
        rendered_urdf.write(robot_description)
    return robot_description, rendered_urdf.name


def generate_launch_description() -> LaunchDescription:
    pkg_share = Path(get_package_share_directory("pentos"))
    ros_gz_share = Path(get_package_share_directory("ros_gz_sim"))
    urdf_path = pkg_share / "urdf" / "pentos.urdf"
    config_path = pkg_share / "config" / "pentos_controllers.yaml"
    robot_description, rendered_urdf_path = _render_urdf(urdf_path, config_path)

    resource_path = _prepend_env_path(str(pkg_share), os.environ.get("GZ_SIM_RESOURCE_PATH", ""))
    gz_launch = ros_gz_share / "launch" / "gz_sim.launch.py"

    return LaunchDescription(
        [
            SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", resource_path),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description,
                        "use_sim_time": True,
                    }
                ],
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="clock_bridge",
                output="screen",
                arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
                parameters=[
                    {
                        "qos_overrides./tf_static.publisher.durability": "transient_local",
                    }
                ],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(gz_launch)),
                launch_arguments={"gz_args": "-r empty.sdf"}.items(),
            ),
            TimerAction(
                period=5.0,
                actions=[
                    ExecuteProcess(
                        cmd=[
                            "ros2",
                            "run",
                            "ros_gz_sim",
                            "create",
                            "-world",
                            "empty",
                            "-name",
                            "pentos",
                            "-file",
                            rendered_urdf_path,
                            "-z",
                            "0.05",
                        ],
                        output="screen",
                    )
                ],
            ),
            TimerAction(
                period=7.0,
                actions=[
                    ExecuteProcess(
                        cmd=[
                            "ros2",
                            "control",
                            "load_controller",
                            "--set-state",
                            "active",
                            "joint_state_broadcaster",
                        ],
                        output="screen",
                    ),
                    ExecuteProcess(
                        cmd=[
                            "ros2",
                            "control",
                            "load_controller",
                            "--set-state",
                            "active",
                            "pentos_position_controller",
                        ],
                        output="screen",
                    ),
                ],
            ),
        ]
    )
