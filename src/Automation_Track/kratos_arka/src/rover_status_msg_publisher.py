#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from kratos_arka_msgs.msg import RoverStatus
import math

class RoverPublisher(Node):
    def __init__(self):
        super().__init__('rover_status_publisher')
        self.publisher_ = self.create_publisher(RoverStatus, 'rover_status', 10)
        
        # Initialize internal simulation tracking variables
        self.current_battery = 100.0
        self.step_counter = 0
        
        # 2 Hz means a period of exactly 0.5 seconds
        timer_period = 0.5 
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = RoverStatus()
        
        # 1. DYNAMIC BATTERY: Decreases by 1% every half-second
        if self.current_battery > 0.0:
            self.current_battery -= 1.0
        msg.battery_percentage = max(0.0, self.current_battery)
        
        # Check if battery is completely dead
        is_battery_dead = (msg.battery_percentage == 0.0)
        
        # 2. DYNAMIC VELOCITY WITH DEAD BATTERY OVERRIDE
        if is_battery_dead:
            msg.velocity = 0.0  # Force velocity to zero when battery dies!
        elif 45 <= (self.step_counter % 90) < 60:
            msg.velocity = 0.0  # Periodic stationary test rest
        else:
            msg.velocity = round(abs(1.8 * math.sin(self.step_counter * 0.1)), 2)
        
        # 3. DYNAMIC EMERGENCY STOP
        # If the battery is dead, we trip the E-stop, or if it is critically low (< 10%)
        if msg.battery_percentage < 10.0:
            msg.emergency_stop = True
        else:
            msg.emergency_stop = (self.step_counter % 40 == 0 and self.step_counter > 0)
        
        # 4. DYNAMIC MODE WITH DEAD BATTERY OVERRIDE
        if is_battery_dead:
            msg.mode = "Stationary (Dead Battery)" # Force mode to stationary!
        elif msg.emergency_stop:
            msg.mode = "FAULTS_SAFE_MODE"
        elif msg.velocity == 0.0:
            msg.mode = "Stationary"
        elif self.step_counter % 60 < 30:
            msg.mode = "Autonomous Nav"
        else:
            msg.mode = "Teleoperation"
        
        # Publish the dynamic packet
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing Live Telemetry Stream [Message #{self.step_counter}]')
        
        # Increment step tracking
        self.step_counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = RoverPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
