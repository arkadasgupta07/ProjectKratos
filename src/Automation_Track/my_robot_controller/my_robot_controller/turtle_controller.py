#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

class TurtleControllerNode(Node):

    def __init__(self):
        super().__init__("turtle_controller") # name of node
        self.cmd_vel_publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pose_subscriber_ = self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 10)
        self.get_logger().info("Turtle controller has been started.")

    def pose_callback(self, pose: Pose):
        cmd = Twist()
        if pose.x > 9.0 or pose.x < 2.0 or pose.y > 9.0 or pose.y < 2.0:
            cmd.linear.x = 1.0
            cmd.angular.z = 0.9
        else:
            cmd.linear.x = 5.0
            cmd.angular.z = 0.0
        self.cmd_vel_publisher_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


# Closed Loop Control System with Publisher and Subscriber

# From rqt_graph ==>
# We have turtlesim and turtle_controller nodes.
# (1) turtle_controller node is listens to (is subscriber of) /turtle1/pose topic
# and sends message to (is publisher to) /turtle1/cmd_vel topic.
# (2) turtlesim node is listens to (is subscriber of) /turtle1/cmd_vel topic
# and sends message to (is publisher to) /turtle1/pose topic.
# Hence, a closed loop control with publisher and subscriber.