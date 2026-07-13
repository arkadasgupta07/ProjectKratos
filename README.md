# 🚀 Project Kratos: Mission Control Dashboard & Navigation Stack

### 📺 System Verification Video
👉 [**Click Here to Watch the Full System Demo Video**]

 https://drive.google.com/file/d/16pvSpx7VExS1l-PbRo9l8NJkZXNLPmMZ/view?usp=sharing --- GUI Nav2 Control (Week3)

 https://drive.google.com/file/d/1Gb800iGbfB-I2hUB4Bc9amMdk7Ckvq55/view?usp=sharing --- OpenCV ArUCO Search (Week4)
 
 https://drive.google.com/file/d/1qRdI30Lx_w6Fodq4ENaDAhFO8J6IroHU/view?usp=sharing --- OpenCV ArUCO Search (Week4) Backup
 
*Week4 files uploaded as a Branch.
---

## 🛠️ Overview: GUI & Node Functionality
This project implements a comprehensive ground control station and automated navigation stack for a differential drive robot (TurtleBot) operating within a simulated physics environment.

* **Genesis Simulation Node (`turtlebot_sim.py`):** Drives a 3D simulation layer rendering state variables, processing wheel joint telemetry, and handling RGB/Depth perspective cameras.
* **Navigation Stack (`launch_nav2.py`):** Acts as the behavioral layer, spawning lifecycle planners, costmaps, and velocity smoothers to execute closed-loop trajectory targets.
* **Mission Control Dashboard (`mission_control_gui.py`):** A custom, multi-threaded PyQt5 graphical user interface tracking live position coordinates, orientation heading, and real-time linear/angular dynamics. It integrates background camera worker threads and processing logic to compute immediate obstacle proximities.

---

## 📦 Dependencies & System Architecture
* **Operating System & Core Ecosystem:** Linux Ubuntu 22.04 LTS running **ROS 2 Humble Hawksbill**.
* **Python Libraries:** `PyQt5`, `opencv-python (v4.11.0)`, `numpy (v1.26.4)`, and `math`.
* **ROS 2 Message Specifications & Communication Interfaces:**
  * `geometry_msgs/msg/Twist` (Subscribed via `/cmd_vel` to capture navigation control velocities).
  * `nav_msgs/msg/Odometry` (Subscribed via `/odom` to extract ground-truth positioning coordinates and quaternion headings).
  * `sensor_msgs/msg/Image` (Subscribed via camera channels to feed parallel matrix processors).
  * `sensor_msgs/msg/LaserScan` (Subscribed via the namespaced `/turtlebot/scan` channel to compute obstacle clearances).

---

## 🗺️ Coordinate System Input Format
The Mission Dispatcher interface utilizes a strict **`[X Y]` sequential coordinate scheme**:
* Coordinates are provided as floating-point metrics relative to the world origin (`0,0`).
* **Input Example:** `WP 1 X: 1.0, Y: 1.0` targets a position exactly one meter forward and one meter left of the global start frame.

---

## 🛡️ Justification for Selected Telemetry Metrics
1. **Live Wheel Speeds (L / R rad/s):** Vital for slip diagnosis, helping operators spot differences between target commands (`/cmd_vel`) and real joint feedback.
2. **LiDAR Min Dist (meters):** Vital safety fallback metric providing situational awareness even during a network video freeze.
3. **Emergency Stop (E-STOP):** A failsafe safety feature that instantly interrupts running navigation processes and overrides control commands to prevent equipment damage.

---

## 🚀 Step-by-Step Run Instructions

To run this project from a clean system state, open four separate terminal windows and run the following sequences:



### Terminal-Wise Instructions
```

### 🖥️ Terminal 1 - Core Physics Simulator (Turtlebot)
```bash
cd ~/dasgu/ros2/genesis_sim/
source /opt/ros/humble/setup.bash
python3 turtlebot_sim.py

### 🗺️ Terminal 2 - Navigation Stack (Nav2)
```bash
cd ~/dasgu/ros2/genesis_sim/
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch launch_nav2.py

### 📊 Terminal 3 - Mission Control Telemetry Dashboard
```bash
cd ~/dasgu/ros2/kratos_repo/Automation/Inductions/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run mission_control dashboard

### 🛰️ Terminal 4 - Telemetry Echo (Optional Monitoring)
```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /cmd_vel
