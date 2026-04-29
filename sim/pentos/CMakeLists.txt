cmake_minimum_required(VERSION 3.8)
project(pentos)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(pentos_klipper_bridge)

install(
  DIRECTORY config launch meshes urdf
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/klipper_gazebo_bridge
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
