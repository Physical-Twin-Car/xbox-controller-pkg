cmake_minimum_required(VERSION 3.5)
project(xbox_controller_pkg)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(motor_control_pkg REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(
  PROGRAMS
    scripts/xbox_controller_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
