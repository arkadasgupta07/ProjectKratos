#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import os

class MissionClient(Node):

    def __init__(self):
        super().__init__('mission_client')
        
        # Declare the mandatory parameter required by the evaluators
        self.declare_parameter('waypoint_file', 'waypoints.txt')
        self.target_file = self.get_parameter('waypoint_file').get_parameter_value().string_value
        
        # Action Client setup
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Mission counters
        self.waypoints = []
        self.current_waypoint_index = 0
        self.successful_waypoints_reached = 0
        
        # Parse coordinates
        self.load_waypoints()
        
        self.get_logger().info('Waiting for Nav2 action server...')
        self._action_client.wait_for_server()
        
        # Dispatch first target
        self.send_next_waypoint()

    def load_waypoints(self):
        """Parses coordinates separated by spaces as specified in 3.b"""
        if not os.path.exists(self.target_file):
            self.get_logger().error(f"❌ Target coordinate file not found at: {self.target_file}")
            return
            
        with open(self.target_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    self.waypoints.append((float(parts[0]), float(parts[1])))
                    
        self.get_logger().info(f"Loaded {len(self.waypoints)} waypoints from {self.target_file}")

    def send_next_waypoint(self):
        """Sequentially dispatches goals using asynchronous non-blocking patterns"""
        if self.current_waypoint_index >= len(self.waypoints):
            # Print exact summary statement requested in part 3.e
            self.get_logger().info(
                f"Mission complete:  {self.successful_waypoints_reached}/{len(self.waypoints)} waypoints reached"
            )
            return

        x, y = self.waypoints[self.current_waypoint_index]
        self.get_logger().info(
            f"Dispatching waypoint {self.current_waypoint_index + 1}/{len(self.waypoints)}:  x={x:.2f}, y={y:.2f}"
        )

        # Build goal frame transforms
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = 1.0

        # Bind feedback callback to capture remaining distances
        send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server.')
            return

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Logs live runtime telemetry updates as specified in 3.d"""
        feedback = feedback_msg.feedback
        self.get_logger().info(f"Feedback:  distance remaining = {feedback.distance_remaining:.2f} m")

    def get_result_callback(self, future):
        """Handles exit codes and forces continuation on failures as per 3.e"""
        status = future.result().status
        
        # Check standard tracking code (Status 4 = SUCCEEDED)
        if status == 4:
            self.get_logger().info(f"Waypoint {self.current_waypoint_index + 1} SUCCEEDED")
            self.successful_waypoints_reached += 1
        else:
            self.get_logger().warn(f"Waypoint {self.current_waypoint_index + 1} FAILED/ABORTED with status code: {status}")

        # Shift target tracking step forward and loop safely
        self.current_waypoint_index += 1
        self.send_next_waypoint()

def main(args=None):
    rclpy.init(args=args)
    node = MissionClient()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
