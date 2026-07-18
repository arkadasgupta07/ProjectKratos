# Nav2 Workflow Summary

When the action client dispatches a `MapsToPose` goal, it is first received by the **BT (Behavior Tree) Navigator** node. The BT Navigator acts as the core orchestrator, ticking a behavior tree to manage execution flow. It first invokes the **Global Planner** server to calculate a collision-free path from the robot's current position to the goal. Once a path is generated, the tree continuously passes it to the **Local Controller** server, which computes dynamic velocity commands (`/cmd_vel`) to execute the trajectory.

Environmental tracking relies on two distinct occupancy grids:
* **Global Costmap:** Represents the entire environment to facilitate long-term route planning. It is used exclusively by the *Global Planner* to map static obstacles.
* **Local Costmap:** A small, rolling window centered directly on the robot used exclusively by the *Local Controller* to detect immediate, dynamic obstacles via sensor updates (e.g., `/turtlebot/scan`).

Two costmaps are required because long-distance path planning needs high-level spatial context without computational overhead, whereas dynamic collision avoidance requires ultra-fast, real-time sensor processing of immediate surroundings.
