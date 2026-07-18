# Week 3 Assignment: Robotic Arm Simulation (arm_humble)

This package contains the setup for visualizing and simulating a robotic arm using ROS 2 Humble. A URDF file defines the connections between the arm joints and links, and a launch file handles the visualization configuration inside RViz.

---

## 🎯 Approach
* **Robot Structure Definition (URDF):** A URDF file was written to connect the various components of the arm sequentially in a single kinematic chain, starting from the world frame up to the final moving finger link.
* **Joints and Links Hierarchy:** The structural links connect in the following order: `world` -> `base_plate_link` -> `base_yaw_column_link` -> `upper_arm_link` -> `forearm_link` -> `wrist_bracket_link` -> `wrist_output_shaft_link` -> `gripper_base_link` -> `moving_finger_link`.
* **State Publishing:** The standard `robot_state_publisher` node is utilized to receive joint data and compute the 3D coordinate transformations dynamically, allowing RViz to render the link states accurately.

---

## 🧠 Assumptions
* **Operating Environment:** It is assumed that the host machine runs Ubuntu 22.04 LTS with a functioning installation of ROS 2 Humble.
* **Graphical Dependencies:** It is assumed that the `rviz2` and `joint_state_publisher_gui` packages are available on the system to enable manual joint adjustments via the graphical slider interface.

---

## 🚧 Challenges and Resolutions
* **Wayland Compositor Warnings:** Launching the node initially produced a terminal warning stating `Ignoring XDG_SESSION_TYPE=wayland`. Troubleshooting confirmed this is a common occurrence with GNOME display configurations on Ubuntu that does not affect RViz functionality, allowing the application to run successfully regardless.
* **Workspace Path Disruptions:** Reorganizing the repository structure into a clean, professional layout caused initial build path discrepancies. This issue was resolved by clearing the outdated `build`, `install`, and `log` directories and executing a clean `colcon build --symlink-install` from the repository root workspace.

---

## 🧪 Testing Methodology
1. Navigate to the repository root directory (`~/ProjectKratos`) and rebuild the workspace:
   ```bash
   colcon build --symlink-install
   source install/setup.bash
