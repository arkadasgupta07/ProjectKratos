#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from kratos_arka_msgs.msg import RoverStatus

class RoverSubscriber(Node):
    def __init__(self):
        super().__init__('rover_status_subscriber')
        # Subscribe to the 'rover_status' topic
        self.subscription = self.create_subscription(
            RoverStatus,
            'rover_status',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        # Print all the fields received from the custom message
        self.get_logger().info('--- Received Rover Status ---')
        self.get_logger().info(f'Battery: {msg.battery_percentage}%')
        self.get_logger().info(f'Velocity: {msg.velocity} m/s')
        self.get_logger().info(f'E-Stop Active: {msg.emergency_stop}')
        self.get_logger().info(f'Mode: {msg.mode}')

def main(args=None):
    rclpy.init(args=args)
    node = RoverSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
