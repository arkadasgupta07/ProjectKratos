import os
import yaml
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image
from nav2_msgs.action import NavigateToPose

from aruco_search_mission.image_processor import ArucoTargetDetector

class ArucoSearchMissionNode(Node):
    def __init__(self):
        super().__init__('mission_node')
        
        self.state = 'NAVIGATING'
        self.current_waypoint_idx = 0
        self.waypoints = []
        
        self.current_robot_x = 0.0
        self.current_robot_y = 0.0
        self.detected_id = None
        self.target_distance = None
        self.target_offset_x = 0.0  

        self.detector = ArucoTargetDetector()
        self.load_waypoints()

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.image_sub = self.create_subscription(Image, '/turtlebot/rgb', self.image_callback, 10)
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info("🤖 Autonomous Waypoint Mission Control Initialized!")
        self.send_next_nav2_goal()

    def load_waypoints(self):
        yaml_path = os.path.expanduser('~/dasgu/ros2/kratos_repo/Automation/Inductions/ros2_ws/aruco_waypoints.yaml')
        try:
            with open(yaml_path, 'r') as file:
                data = yaml.safe_load(file)
                self.waypoints = data.get('waypoints', [])
                self.get_logger().info(f"--- Loaded {len(self.waypoints)} Search Zone Waypoints ---")
        except Exception as e:
            self.waypoints = [{'x': 2.0, 'y': 1.0}, {'x': -1.5, 'y': 2.0}, {'x': 1.0, 'y': -1.5}]

    def odom_callback(self, msg):
        self.current_robot_x = msg.pose.pose.position.x
        self.current_robot_y = msg.pose.pose.position.y

    def image_callback(self, msg):
        if self.state in ['SEARCHING', 'APPROACHING']:
            tid, dist, offset = self.detector.process_frame(msg)
            
            if tid is not None:
                self.detected_id = tid
                self.target_distance = dist
                self.target_offset_x = offset
                
                # FIXED: Instant State Transition to avoid the timer race condition
                if self.state == 'SEARCHING':
                    self.get_logger().info(f"🎯 Target Detected! Found ID: {self.detected_id}. Engaging Approach State.")
                    self.state = 'APPROACHING'
            else:
                # Only clear target tracking if we are actively trying to approach it and lose it completely
                if self.state == 'APPROACHING':
                    self.target_distance = None

    def send_next_nav2_goal(self):
        if self.current_waypoint_idx >= len(self.waypoints):
            self.state = 'DONE'
            self.get_logger().info("🎉 ALL WAYPOINTS COMPLETED SUCCESSFULLY!")
            return

        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            return

        wp = self.waypoints[self.current_waypoint_idx]
        self.get_logger().info(f"🚀 Moving to Waypoint [{self.current_waypoint_idx + 1}/{len(self.waypoints)}]: (x: {wp['x']}, y: {wp['y']})")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(wp['x'])
        goal_msg.pose.pose.position.y = float(wp['y'])
        goal_msg.pose.pose.orientation.w = 1.0 

        self.state = 'NAVIGATING'
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.nav2_result_callback)

    def nav2_result_callback(self, future):
        self.get_logger().info("📍 Arrived at rough search zone. Switching to Visual Search Routine.")
        self.state = 'SEARCHING'

    def control_loop(self):
        twist = Twist()

        if self.state == 'NAVIGATING':
            return

        elif self.state == 'SEARCHING':
            # Keep spinning until the image_callback catches a frame and flips the state
            twist.angular.z = 0.25
            self.cmd_vel_pub.publish(twist)

        elif self.state == 'APPROACHING':
            # If the marker is completely cut off or lost due to proximity, assume arrival
            if self.target_distance is None:
                self.get_logger().info("🏁 Marker proximity limit reached. Assuming destination reached.")
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.cmd_vel_pub.publish(twist)
                self.state = 'LOGGING'
                return

            if self.target_distance > 0.25:
                twist.linear.x = 0.08  
                twist.angular.z = -0.003 * self.target_offset_x 
                self.cmd_vel_pub.publish(twist)
            else:
                self.get_logger().info("🏁 Stopped precisely 0.25m from target.")
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.cmd_vel_pub.publish(twist)
                self.state = 'LOGGING'

        elif self.state == 'LOGGING':
            final_id = self.detected_id if self.detected_id is not None else "Unknown"
            self.log_target_data(final_id)
            
            self.detected_id = None
            self.target_distance = None
            self.current_waypoint_idx += 1
            self.send_next_nav2_goal()

        elif self.state == 'DONE':
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_vel_pub.publish(twist)

    def log_target_data(self, target_id):
        log_path = os.path.expanduser('~/dasgu/ros2/kratos_repo/Automation/Inductions/ros2_ws/detected_targets.txt')
        log_string = f"Target found! ID: {target_id}, Rover Position: ({self.current_robot_x:.2f}, {self.current_robot_y:.2f})\n"
        with open(log_path, 'a') as file:
            file.write(log_string)
        self.get_logger().info(f"📝 Logged to file: {log_string.strip()}")

def main(args=None):
    rclpy.init(args=args)
    node = ArucoSearchMissionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()