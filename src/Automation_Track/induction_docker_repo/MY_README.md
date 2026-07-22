# Autonomous 10x10 Maze Solver

An autonomous maze navigation package for ROS 2 Humble. This node utilizes a reactive wall-following algorithm powered by 2D LiDAR telemetry to solve $10 \times 10$ simulation mazes without human intervention or map-based global planners.

---

## 🛠️ System Overview & Architecture

### Environment
* **OS / Container**: Ubuntu 22.04 LTS (Docker / noVNC)
* **ROS Version**: ROS 2 Humble Hawksbill
* **Simulator**: Gazebo Classic / Ignition Gazebo
* **Topic Inputs**: `/scan` (`sensor_msgs/msg/LaserScan`)
* **Topic Outputs**: `/cmd_vel` (`geometry_msgs/msg/Twist`)

### Project Structure
```text
.
├── wall_follower.py       # Main ROS 2 python node containing maze solving logic
├── README.md              # Project documentation and reproduction instructions
└── maze_solution_demo.mp4 # Autonomous run recording

```

## 🚀 Execution Instructions (Terminal Workflow)


#### Prerequisites: Clone the repository and set execution permissions:
```text
git clone <YOUR_GIT_REPOSITORY_URL>cd induction_docker_repo
chmod +x setup.sh kratos-env.sh
./setup.sh
```

#### Terminal 1: Start Container & Environment
Start the container environment and launch the noVNC desktop:
```text
./kratos-env.sh start
```
Open http://localhost:6080/vnc.html in your web browser to view the Linux desktop environment.

#### Terminal 2: Launch Gazebo Simulation
Open a shell inside the container to launch Gazebo with the $10 \times 10$ maze and robot:
```text
./kratos-env.sh shell
ros2 launch kratos_maze maze10x10.launch.py
```

#### Terminal 3: Run Solver Node
Open a second container shell to execute the autonomous wall-following node:
```text
./kratos-env.sh shell
chmod +x wall_follower.py
python3 wall_follower.py
```
The robot will immediately process LiDAR data and navigate out of the top exit.
