#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class TopExitWallFollower(Node):
    def __init__(self):
        super().__init__('top_exit_wall_follower')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.get_logger().info('Top Exit Maze Solver Started!')

    def scan_callback(self, msg):
        ranges = msg.ranges

        # 3 Key Lidar Regions
        front_arc = ranges[0:15] + ranges[345:360]
        fright_arc = ranges[300:330]
        right_arc = ranges[250:290]

        # Distance Filters
        d_front = min([r for r in front_arc if 0.05 < r < 10.0], default=10.0)
        d_fright = min([r for r in fright_arc if 0.05 < r < 10.0], default=10.0)
        d_right = min([r for r in right_arc if 0.05 < r < 10.0], default=10.0)

        move = Twist()

        # --- BALANCED TOP-EXIT NAVIGATION LOGIC ---

        # 1. FRONT WALL DETECTED -> PIVOT LEFT
        if d_front < 0.38:
            move.linear.x = 0.0
            move.angular.z = 0.75
            self.get_logger().info('Wall ahead! Turning Left...')

        # 2. CLEAR RIGHT CORNER -> ARC RIGHT
        elif d_right > 0.48 and d_fright > 0.48:
            move.linear.x = 0.18
            move.angular.z = -0.70
            self.get_logger().info('Following Right Corner...')

        # 3. PROXIMITY CORRECTIONS
        elif d_right < 0.22 or d_fright < 0.25:
            # Too close to right wall -> Nudge left
            move.linear.x = 0.22
            move.angular.z = 0.35
            self.get_logger().info('Adjusting Left...')

        elif d_right > 0.36:
            # Too far from right wall -> Drift right
            move.linear.x = 0.22
            move.angular.z = -0.35
            self.get_logger().info('Adjusting Right...')

        # 4. CRUISING STRAIGHT
        else:
            move.linear.x = 0.40
            move.angular.z = 0.0
            self.get_logger().info('Cruising Straight to Top Exit...')

        self.cmd_pub.publish(move)

def main(args=None):
    rclpy.init(args=args)
    node = TopExitWallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

