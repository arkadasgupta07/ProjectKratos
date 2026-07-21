#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class DoubleAckermannController(Node):
    def __init__(self):
        super().__init__('double_ackermann_controller')
        
        # Subscribe to teleop/joystick commands
        self.cmd_sub = self.create_subscription(
            Twist, 
            '/cmd_vel', 
            self.cmd_callback, 
            10
        )
        
        # Publisher for the 4 steering hinges (Position in Radians)
        # Order matches YAML: [fl_steer, fr_steer, rl_steer, rr_steer]
        self.steer_pub = self.create_publisher(
            Float64MultiArray, 
            '/steering_controller/commands', 
            10
        )

        # Publisher for the 4 wheel axles (Velocity in Rad/s)
        # Order matches YAML: [fl_drive, fr_drive, rl_drive, rr_drive]
        self.drive_pub = self.create_publisher(
            Float64MultiArray, 
            '/drive_controller/commands', 
            10
        )

        # Rover Physical Constants
        self.wheelbase = 0.5 
        self.track_width = 0.3
        self.wheel_radius = 0.12

        self.get_logger().info("Double Ackermann Controller Node Started. Waiting for /cmd_vel...")

    def cmd_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        # =======================================================
        # APPLICANT TASK: Implement Double Ackermann Kinematics 
        # Calculate the 4 steering angles and 4 wheel velocities
        # =======================================================
        
        # 1. Calculate angles (radians)
        fl_angle, fr_angle, rl_angle, rr_angle = 0.0, 0.0, 0.0, 0.0
        
        # 2. Calculate velocities (rad/s)
        fl_vel, fr_vel, rl_vel, rr_vel = 0.0, 0.0, 0.0, 0.0

        # Handle Straight Line vs Turning Motion
        if abs(angular_z) < 1e-4:
            # Straight Line: No steering angle, equal wheel spin speeds
            fl_angle = fr_angle = rl_angle = rr_angle = 0.0
            
            wheel_spin_vel = linear_x / self.wheel_radius
            fl_vel = fr_vel = rl_vel = rr_vel = wheel_spin_vel
            
        else:
            # Turning: Calculate Instantaneous Center of Rotation (ICR)
            R = linear_x / angular_z  # Turning radius ... using v=wR --> R(o) = v(wheel)/w(o)
            half_L = self.wheelbase / 2.0
            half_W = self.track_width / 2.0

            # Steering Angles (radians)
            fl_angle = math.atan2(half_L, R - half_W)
            fr_angle = math.atan2(half_L, R + half_W)
            rl_angle = -fl_angle  # Rear wheels steer in equal and opposite direction
            rr_angle = -fr_angle

            # Distance from ICR to each wheel center
            r_fl = math.hypot(R - half_W, half_L)
            r_fr = math.hypot(R + half_W, half_L)
            r_rl = r_fl
            r_rr = r_fr

            # Wheel Spin Angular Velocities (rad/s)
            # ... using w(wheel) = v(wheel)/r(wheel) ... where v(wheel) = w(o)*R(o)
            fl_vel = (angular_z * r_fl) / self.wheel_radius 
            fr_vel = (angular_z * r_fr) / self.wheel_radius
            rl_vel = (angular_z * r_rl) / self.wheel_radius
            rr_vel = (angular_z * r_rr) / self.wheel_radius

        # =======================================================
        
        # Publish Steering Commands
        steer_msg = Float64MultiArray()
        steer_msg.data = [fl_angle, fr_angle, rl_angle, rr_angle]
        self.steer_pub.publish(steer_msg)

        # Publish Drive Commands
        drive_msg = Float64MultiArray()
        drive_msg.data = [fl_vel, fr_vel, rl_vel, rr_vel]
        self.drive_pub.publish(drive_msg)

def main(args=None):
    rclpy.init(args=args)
    node = DoubleAckermannController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
