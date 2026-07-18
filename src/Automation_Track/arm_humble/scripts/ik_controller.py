#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import sys
import threading

class IKController(Node):
    def __init__(self):
        super().__init__('ik_controller')
        
        # Publisher to the joint_states topic
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Robot Link Lengths extracted from URDF
        self.L1 = 0.35  # Upper arm length
        self.L2 = 0.42  # Forearm to wrist output shaft link length
        self.Z_offset = 0.17  # Height from ground to shoulder joint
        
        # Internal configuration tracking (starting home position)
        # Home positions chosen safely within reachable workspace
        self.current_q = [0.0, 0.3, 0.5] # base_yaw, shoulder, elbow
        self.current_pos = self.forward_kinematics(self.current_q[0], self.current_q[1], self.current_q[2])
        
        # Start user interaction thread
        self.running = True
        self.input_thread = threading.Thread(target=self.user_interface_loop)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        # Timer to continuously publish joint states so RViz updates reliably
        self.timer = self.create_timer(0.1, self.publish_joints)
        
        self.get_logger().info("IK Controller Node Started successfully.")
        self.print_current_pose()

    def forward_kinematics(self, q0, q1, q2):
        # Helper to compute current end-effector coordinates from joint angles
        # In the local arm plane, joint angles calculate offsets relative to the vertical Z axis
        r = self.L1 * math.sin(q1) + self.L2 * math.sin(q1 + q2)
        z = self.Z_offset + self.L1 * math.cos(q1) + self.L2 * math.cos(q1 + q2)
        x = r * math.cos(q0)
        y = r * math.sin(q0)
        return [x, y, z]

    def inverse_kinematics(self, x, y, z):
        # Step 1: Compute Base Yaw (q0)
        q0 = math.atan2(y, x)
        
        # Step 2: Project to 2D plane
        r = math.sqrt(x**2 + y**2)
        z_rel = z - self.Z_offset
        
        # Step 3: Solve 2-link planar IK for shoulder (q1) and elbow (q2)
        # Using Cosine Rule formula expressions
        d_sq = r**2 + z_rel**2
        
        cos_q2 = (d_sq - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        if cos_q2 < -1.0 or cos_q2 > 1.0:
            return None # Out of workspace reach bounds
            
        sin_q2 = math.sqrt(1.0 - cos_q2**2) # Choose elbow-up configuration
        q2 = math.atan2(sin_q2, cos_q2)
        
        alpha = math.atan2(r, z_rel)
        beta = math.atan2(self.L2 * sin_q2, self.L1 + self.L2 * cos_q2)
        q1 = alpha - beta
        
        # Check URDF safety limits
        if not (-3.1416 <= q0 <= 3.1416): return None
        if not (-1.5708 <= q1 <= 1.5708): return None
        if not (-2.3562 <= q2 <= 2.3562): return None
        
        return [q0, q1, q2]

    def print_current_pose(self):
        print("\n" + "="*30)
        print("Current End Effector Position:")
        print(f"x = {self.current_pos[0]:.2f}")
        print(f"y = {self.current_pos[1]:.2f}")
        print(f"z = {self.current_pos[2]:.2f}")
        print("="*30)

    def user_interface_loop(self):
        # Loop running inside our companion thread handling terminal interactions
        while rclpy.ok() and self.running:
            try:
                axis = input("Enter axis to move (x/y/z) or 'q' to quit: ").strip().lower()
                if axis == 'q':
                    self.running = False
                    break
                if axis not in ['x', 'y', 'z']:
                    print("Invalid axis selection! Please enter x, y, or z.")
                    continue
                
                disp_str = input("Enter displacement (meters): ").strip()
                try:
                    displacement = float(disp_str)
                except ValueError:
                    print("Invalid displacement entry! Must be a floating number.")
                    continue
                
                # Compute target candidate positions
                target_pos = list(self.current_pos)
                if axis == 'x': target_pos[0] += displacement
                elif axis == 'y': target_pos[1] += displacement
                elif axis == 'z': target_pos[2] += displacement
                
                # Attempt structural calculation check
                ik_sol = self.inverse_kinematics(target_pos[0], target_pos[1], target_pos[2])
                
                if ik_sol is None:
                    print("\n[ERROR] Command Rejected: Target position is outside the robot's reachable workspace or violates joint limits!")
                    self.print_current_pose()
                else:
                    # Commit successful target updates
                    self.current_pos = target_pos
                    self.current_q = ik_sol
                    print("\nCommand successful! Target achieved.")
                    self.print_current_pose()
                    
            except (KeyboardInterrupt, EOFError):
                self.running = False
                break

    def publish_joints(self):
        # Create and broadcast valid sensor_msgs/JointState configuration frame
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['base_yaw_joint', 'shoulder_joint', 'elbow_joint', 'wrist_pitch_joint', 'wrist_roll_joint']
        
        # Match standard structure sequence; holding the wrist pitch/roll steady at zero offset positions
        msg.position = [self.current_q[0], self.current_q[1], self.current_q[2], 0.0, 0.0]
        self.joint_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = IKController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running = False
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
