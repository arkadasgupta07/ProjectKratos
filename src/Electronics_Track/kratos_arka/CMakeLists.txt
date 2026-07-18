cmake_minimum_required(VERSION 3.8)
project(kratos_arka)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find the standard ROS 2 CMake build tool
find_package(ament_cmake REQUIRED)

# Install your 4 exact Python scripts to the execution directory
install(PROGRAMS
  src/rover_status_publisher.py
  src/rover_status_subscriber.py
  src/rover_status_msg_publisher.py
  src/rover_status_msg_subscriber.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install the launch directory to the share directory
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
