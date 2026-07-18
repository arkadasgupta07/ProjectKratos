#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class DrawCircleNode(Node): # this class inherits from Node

    # initializing our node
    def __init__(self):
        super().__init__("draw_circle")
        # now to create a publisher (to send msgs to topic for subscriber) and a timer and print something
        self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.timer_ = self.create_timer(0.5, self.send_velocity_command) # the timer is going to call this function every 0.5sec (inside the function we create the msg)
        self.get_logger().info("Draw circle node has been started")


    def send_velocity_command(self): # the function which contains the msg, and is called every 0.5sec by the timer

        msg = Twist() # creating msg object from the class Twist
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        # content of msg ... only x (linear) & z (angular) motion reqrd to move tortoise in circle.
        self.cmd_vel_pub_.publish(msg) # publishing/sending the msg object

def main(args=None):
    rclpy.init(args=args)
    node = DrawCircleNode() # make the node
    rclpy.spin(node) # keep the node alive
    rclpy.shutdown()


if __name__ == '__main__':
    main()
