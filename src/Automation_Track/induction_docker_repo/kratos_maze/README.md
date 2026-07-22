# Kratos Maze — Map Assets

This package contains the **maze map files** for the Project Kratos Bonus Maze Challenge.

> **This is a resource-only package.** No launch files, no solver scripts, no simulator setup is included. You must do all of that yourself.

## What's Included

### Models (`models/`)

Gazebo-compatible SDF model directories:

| Model | Description |
|-------|-------------|
| `maze5x5/` | 5×5 orthogonal maze (no loops, no obstacles) |
| `maze10x10/` | 10×10 orthogonal maze (no loops, no obstacles) — **this is the challenge maze** |
| `sample/` | Simple sample walls for testing |

Each model directory contains:
- `model.config` — Gazebo model metadata
- `model.sdf` — SDF model description (references the `.obj` mesh)
- `.obj` / `.mtl` — 3D mesh files

### Worlds (`worlds/`)

Pre-made Gazebo Classic `.world` files that load the maze models:
- `maze5x5.world`
- `maze10x10.world`
- `sample.world`

> These world files are designed for **Gazebo Classic** (the version that ships with ROS 2 Humble). If you're using a different simulator, use the model `.obj` mesh files directly.

### Assets (`assets/`)

SVG and PNG images of the mazes for reference:

<p align="center">
  <img src="assets/10x10white.svg" width="200">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/5x5white.svg" width="200"><br>
  <em>10×10 Maze &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 5×5 Maze</em>
</p>

## Building this Package

Inside the Docker container:

```bash
cd /workspace
mkdir -p src

# Copy or symlink the kratos_maze package into src/
cp -r /path/to/kratos_maze src/

# Build
colcon build --packages-select kratos_maze
source install/setup.bash
```

After building, the maze models and world files are available at:

```bash
# Find the installed share directory
ros2 pkg prefix kratos_maze
# → /workspace/install/kratos_maze

# Models are at:
# <prefix>/share/kratos_maze/models/maze10x10/
# <prefix>/share/kratos_maze/models/maze5x5/

# World files are at:
# <prefix>/share/kratos_maze/worlds/maze10x10.world
# <prefix>/share/kratos_maze/worlds/maze5x5.world
```

## What You Need to Do

1. **Install a simulator** (e.g., `sudo apt install ros-humble-gazebo-ros-pkgs`)
2. **Set up a robot** (e.g., TurtleBot3, custom URDF, etc.)
3. **Write your own launch file** to load the maze world and spawn your robot
4. **Write your own solver algorithm** — no Nav2 allowed!
5. **Record a video** of your bot solving the 10×10 maze

### Hint: Setting the Gazebo Model Path

If using Gazebo Classic, you may need to tell Gazebo where to find the maze models:

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(ros2 pkg prefix kratos_maze)/share/kratos_maze/models
```

## ⚠️ Rules Reminder

- **Nav2 is BANNED.** Do not use `ros-humble-navigation2` or any Nav2 packages.
- Write your **own** maze-solving logic.
- The robot must navigate **autonomously** from start to finish.

---

See the [main README](../README.md) for Docker setup instructions and submission details.
