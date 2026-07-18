#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, String, Bool

class RoverStatusSubscriber(Node):
    """
    A ROS2 Node that subscribes to multiple telemetry topics to monitor
    and print the current operational telemetry of the rover platform.
    """

    def __init__(self):
        """Initializes the subscriber node and configures topic subscriptions."""
        super().__init__('rover_status_subscriber')
        
        # Variables to cache latest readings
        self.current_battery = None
        self.current_mode = None
        self.current_estop = None

        # Define subscriptions
        self.battery_sub = self.create_subscription(
            Float32, '/battery_level', self.battery_callback, 10)
        self.mode_sub = self.create_subscription(
            String, '/rover_mode', self.mode_callback, 10)
        self.estop_sub = self.create_subscription(
            Bool, '/emergency_stop', self.estop_callback, 10)

    def battery_callback(self, msg):
        """
        Processes updates received from the battery level topic.
        
        Args:
            msg (Float32): The current battery message value.
        """
        self.current_battery = msg.data
        self.print_telemetry_report()

    def mode_callback(self, msg):
        """
        Processes updates received from the operational mode topic.
        
        Args:
            msg (String): The current rover operating mode mode.
        """
        self.current_mode = msg.data
        self.print_telemetry_report()

    def estop_callback(self, msg):
        """
        Processes updates received from the critical emergency stop topic.
        
        Args:
            msg (Bool): The active status of the system level emergency stop.
        """
        self.current_estop = msg.data
        self.print_telemetry_report()

    def print_telemetry_report(self):
        """Outputs a consolidated status report whenever a new message pair arrives."""
        # Print status updates when data has been successfully collected
        battery_str = f"{self.current_battery:.1f}%" if self.current_battery is not None else "N/A"
        mode_str = f"'{self.current_mode}'" if self.current_mode is not None else "N/A"
        estop_str = f"{self.current_estop}" if self.current_estop is not None else "N/A"
        
        self.get_logger().info(
            f"[RECEIVED TELEMETRY] -> Battery: {battery_str} | Mode: {mode_str} | Emergency Stop: {estop_str}"
        )

def main(args=None):
    """Entry point for execution lifecycle management."""
    rclpy.init(args=args)
    node = RoverStatusSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
