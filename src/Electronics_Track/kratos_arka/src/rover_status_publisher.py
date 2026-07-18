#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, String, Bool

class RoverStatusPublisher(Node):
    """
    A ROS2 Node that periodically publishes simulated rover status parameters
    including battery level, operating mode, and emergency stop condition.
    """

    def __init__(self):
        """Initializes the node, creates publishers, and sets up a timer loop."""
        super().__init__('rover_status_publisher')
        
        # Initialize publishers for each status parameter
        self.battery_pub = self.create_publisher(Float32, '/battery_level', 10)
        self.mode_pub = self.create_publisher(String, '/rover_mode', 10)
        self.estop_pub = self.create_publisher(Bool, '/emergency_stop', 10)
        
        # Publish rate set to 1 Hz (once per second)
        timer_period = 1.0  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # Simulated states
        self.simulated_battery = 100.0

    def timer_callback(self):
        """
        Callback function executed at a fixed interval to update state variables
        and publish status updates to active topics.
        """
        # Simulate a progressive battery drain
        if self.simulated_battery > 0.0:
            self.simulated_battery -= 0.5
        else:
            self.simulated_battery = 100.0

        # Construct Float32 message
        battery_msg = Float32()
        battery_msg.data = self.simulated_battery
        
        # Construct String message
        mode_msg = String()
        mode_msg.data = "AUTONOMOUS" if self.simulated_battery > 20.0 else "LOW_BATTERY_MANUAL"
        
        # Construct Bool message
        estop_msg = Bool()
        estop_msg.data = False if self.simulated_battery > 5.0 else True

        # Publish the messages
        self.battery_pub.publish(battery_msg)
        self.mode_pub.publish(mode_msg)
        self.estop_pub.publish(estop_msg)

        self.get_logger().info(
            f"Published -> Battery: {battery_msg.data:.1f}%, Mode: '{mode_msg.data}', E-Stop: {estop_msg.data}"
        )

def main(args=None):
    """Entry point for execution lifecycle management."""
    rclpy.init(args=args)
    node = RoverStatusPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
