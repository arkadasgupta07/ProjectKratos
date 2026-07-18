import sys
import threading
import rclpy
import math
import time
import cv2
import numpy as np

from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, JointState, Image
from cv_bridge import CvBridge

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QLineEdit, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QImage, QPixmap


class GUIBridge(QObject):
    """Thread-safe signal channel to stream data from ROS 2 background worker to PyQt GUI."""
    log_signal = pyqtSignal(str)
    warning_signal = pyqtSignal(str, str)
    
    # Telemetry Signals
    status_signal = pyqtSignal(bool)
    telemetry_signal = pyqtSignal(float, float, float, float, float)
    cmd_vel_signal = pyqtSignal(float, float)
    lidar_signal = pyqtSignal(float)
    wheel_signal = pyqtSignal(float, float)
    
    # Video Signals
    rgb_signal = pyqtSignal(QImage)
    depth_signal = pyqtSignal(QImage)


class MissionControlGUI(QMainWindow):
    def __init__(self, ros_node):
        super().__init__()
        self.ros_node = ros_node
        self.setWindowTitle("Mission Control Dashboard - Project Kratos")
        self.setGeometry(100, 100, 900, 850) # Made wider to fit cameras
        
        # Bridge Communication Wiring
        self.bridge = GUIBridge()
        self.bridge.log_signal.connect(self.append_log)
        self.bridge.warning_signal.connect(self.show_popup_warning)
        
        self.bridge.status_signal.connect(self.update_status)
        self.bridge.telemetry_signal.connect(self.update_telemetry_display)
        self.bridge.cmd_vel_signal.connect(self.update_cmd_vel)
        self.bridge.lidar_signal.connect(self.update_lidar)
        self.bridge.wheel_signal.connect(self.update_wheels)
        
        # Connect Video Signals
        self.bridge.rgb_signal.connect(self.update_rgb_feed)
        self.bridge.depth_signal.connect(self.update_depth_feed)
        
        self.ros_node.bridge = self.bridge

        # Layout Setup
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        layout.addWidget(QLabel("<h2>🚀 Kratos Mission Control</h2>"))
        
        # --- TOP SECTION: TELEMETRY & CONTROLS ---
        top_layout = QHBoxLayout()
        
        # Telemetry Panel
        telemetry_group = QGroupBox("📡 Real-Time Base Station Telemetry")
        telemetry_group.setStyleSheet("QGroupBox { font-weight: bold; color: #007ACC; }")
        tel_layout = QVBoxLayout()
        
        self.status_lbl = QLabel("<b>Status:</b> 🔴 DISCONNECTED")
        self.position_lbl = QLabel("<b>📍 Position:</b> X: 0.00 m | Y: 0.00 m")
        self.heading_lbl = QLabel("<b>🧭 Heading:</b> 0.0°")
        self.velocity_lbl = QLabel("<b>🏎️ Actual Vel:</b> Lin: 0.00 m/s | Ang: 0.00 rad/s")
        self.cmd_vel_lbl = QLabel("<b>🎯 Commanded Vel:</b> Lin: 0.00 m/s | Ang: 0.00 rad/s")
        self.lidar_lbl = QLabel("<b>📡 LiDAR Min Dist:</b> -- m")
        self.wheel_lbl = QLabel("<b>⚙️ Wheel Speeds:</b> L: 0.00 | R: 0.00 rad/s")
        
        for lbl in [self.status_lbl, self.position_lbl, self.heading_lbl, 
                    self.velocity_lbl, self.cmd_vel_lbl, self.lidar_lbl, self.wheel_lbl]:
            tel_layout.addWidget(lbl)
            
        self.estop_btn = QPushButton("🛑 EMERGENCY STOP")
        self.estop_btn.setStyleSheet("background-color: #D9534F; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        self.estop_btn.clicked.connect(self.handle_emergency_stop)
        tel_layout.addWidget(self.estop_btn)
        
        telemetry_group.setLayout(tel_layout)
        top_layout.addWidget(telemetry_group, 1)
        
        # Controls Panel
        controls_group = QGroupBox("🗺️ Mission Dispatcher")
        controls_layout = QVBoxLayout()
        self.inputs = {}
        for i in range(1, 4):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"WP {i} X:"))
            x_input = QLineEdit("0.0")
            row.addWidget(x_input)
            row.addWidget(QLabel("Y:"))
            y_input = QLineEdit("0.0")
            row.addWidget(y_input)
            controls_layout.addLayout(row)
            self.inputs[i] = {'x': x_input, 'y': y_input}
            
        self.dispatch_btn = QPushButton("📡 Dispatch Sequence")
        self.dispatch_btn.setStyleSheet("background-color: #007ACC; color: white; font-weight: bold; padding: 8px;")
        self.dispatch_btn.clicked.connect(self.handle_dispatch)
        controls_layout.addWidget(self.dispatch_btn)
        controls_group.setLayout(controls_layout)
        top_layout.addWidget(controls_group, 1)
        
        layout.addLayout(top_layout)

        # --- MIDDLE SECTION: CAMERA FEEDS (Features 8 & 9) ---
        camera_group = QGroupBox("📷 Live Vision Systems")
        camera_layout = QHBoxLayout()
        
        self.rgb_label = QLabel("Waiting for RGB Feed...")
        self.rgb_label.setAlignment(Qt.AlignCenter)
        self.rgb_label.setStyleSheet("background-color: #000; color: #fff; border: 1px solid #444;")
        self.rgb_label.setMinimumSize(320, 240)
        
        self.depth_label = QLabel("Waiting for Depth Feed...")
        self.depth_label.setAlignment(Qt.AlignCenter)
        self.depth_label.setStyleSheet("background-color: #000; color: #fff; border: 1px solid #444;")
        self.depth_label.setMinimumSize(320, 240)
        
        camera_layout.addWidget(self.rgb_label)
        camera_layout.addWidget(self.depth_label)
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # --- BOTTOM SECTION: LOGS ---
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setStyleSheet("background-color: #1E1E1E; color: #4AF626; font-family: Monospace; font-size: 11px;")
        layout.addWidget(self.log_panel)
        self.append_log("[System] Telemetry and Vision channels linked. Initialization complete.")

    # --- UI UPDATE METHODS ---
    def update_status(self, is_connected):
        if is_connected:
            self.status_lbl.setText("<b>Status:</b> 🟢 CONNECTED & RECEIVING")
            self.status_lbl.setStyleSheet("color: green;")
        else:
            self.status_lbl.setText("<b>Status:</b> 🔴 DISCONNECTED (No Data)")
            self.status_lbl.setStyleSheet("color: red;")

    def update_telemetry_display(self, x, y, yaw, lin_v, ang_v):
        self.position_lbl.setText(f"<b>📍 Position:</b> X: {x:.2f} m | Y: {y:.2f} m")
        self.heading_lbl.setText(f"<b>🧭 Heading:</b> {yaw:.1f}°")
        self.velocity_lbl.setText(f"<b>🏎️ Actual Vel:</b> Lin: {lin_v:.2f} m/s | Ang: {ang_v:.2f} rad/s")

    def update_cmd_vel(self, lin, ang):
        self.cmd_vel_lbl.setText(f"<b>🎯 Commanded Vel:</b> Lin: {lin:.2f} m/s | Ang: {ang:.2f} rad/s")

    def update_lidar(self, min_dist):
        self.lidar_lbl.setText(f"<b>📡 LiDAR Min Dist:</b> {min_dist:.2f} m")

    def update_wheels(self, left, right):
        self.wheel_lbl.setText(f"<b>⚙️ Wheel Speeds:</b> L: {left:.2f} | R: {right:.2f} rad/s")

    def update_rgb_feed(self, q_img):
        self.rgb_label.setPixmap(QPixmap.fromImage(q_img).scaled(320, 240, Qt.KeepAspectRatio))

    def update_depth_feed(self, q_img):
        self.depth_label.setPixmap(QPixmap.fromImage(q_img).scaled(320, 240, Qt.KeepAspectRatio))

    def append_log(self, text):
        self.log_panel.append(text)

    def show_popup_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def handle_emergency_stop(self):
        self.append_log("\n⚠️ [CRITICAL] Emergency Stop triggered!")
        self.ros_node.trigger_emergency_stop()

    def handle_dispatch(self):
        waypoints = []
        for i in range(1, 4):
            try:
                x_val = float(self.inputs[i]['x'].text().strip())
                y_val = float(self.inputs[i]['y'].text().strip())
                waypoints.append((x_val, y_val))
            except ValueError:
                QMessageBox.warning(self, "Error", f"Waypoint {i} invalid!")
                return
        
        self.dispatch_btn.setEnabled(False)
        self.append_log("\n[System] Coordinates dispatched to Nav2...")
        self.ros_node.start_mission(waypoints, finished_callback=self.enable_dispatch)

    def enable_dispatch(self):
        self.dispatch_btn.setEnabled(True)


class Nav2ActionClientNode(Node):
    def __init__(self):
        super().__init__('mission_control_action_client')
        
        self.bridge = None
        self.last_msg_time = 0.0
        self.cv_bridge = CvBridge()
        
        self.client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Check if your topics actually have the /turtlebot/ prefix!
        # Change from /turtlebot/joint_states to /turtlebot/joint_commands
        self.scan_sub = self.create_subscription(LaserScan, '/turtlebot/scan', self.scan_callback, 10)
        self.wheel_sub = self.create_subscription(JointState, '/turtlebot/joint_commands', self.wheel_callback, 10)
        
        # Video Subscribers
        self.rgb_sub = self.create_subscription(Image, '/turtlebot/rgb', self.rgb_callback, 10)
        self.depth_sub = self.create_subscription(Image, '/turtlebot/depth', self.depth_callback, 10)
        
        self.status_timer = self.create_timer(1.0, self.check_connection_status)

        self.waypoint_queue = []
        self.current_index = 0
        self.finished_cb = None
        self.goal_handle = None

    # --- VIDEO CALLBACKS ---
    def rgb_callback(self, msg):
        if self.bridge:
            try:
                cv_img = self.cv_bridge.imgmsg_to_cv2(msg, "rgb8")
                h, w, ch = cv_img.shape
                q_img = QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888)
                self.bridge.rgb_signal.emit(q_img)
            except Exception as e:
                self.get_logger().error(f"RGB Error: {e}")

    def depth_callback(self, msg):
        if self.bridge:
            try:
                # Convert depth to a normalized 8-bit image for colormapping
                cv_img = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
                
                # Replace NaNs/Infs with 0 to prevent OpenCV crashes
                cv_img = np.nan_to_num(cv_img, nan=0.0, posinf=0.0, neginf=0.0)
                
                cv_img_norm = cv2.normalize(cv_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                depth_color = cv2.applyColorMap(cv_img_norm, cv2.COLORMAP_JET)
                depth_rgb = cv2.cvtColor(depth_color, cv2.COLOR_BGR2RGB)
                
                h, w, ch = depth_rgb.shape
                q_img = QImage(depth_rgb.data, w, h, ch * w, QImage.Format_RGB888)
                self.bridge.depth_signal.emit(q_img)
            except Exception as e:
                self.get_logger().error(f"Depth Error: {e}")

    # --- TELEMETRY CALLBACKS ---
    def check_connection_status(self):
        if self.bridge:
            is_connected = (time.time() - self.last_msg_time) < 2.0
            self.bridge.status_signal.emit(is_connected)

    def odom_callback(self, msg):
        self.last_msg_time = time.time()
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        lin_v = msg.twist.twist.linear.x
        ang_v = msg.twist.twist.angular.z
        
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.degrees(math.atan2(siny_cosp, cosy_cosp))
        
        if self.bridge:
            self.bridge.telemetry_signal.emit(x, y, yaw, lin_v, ang_v)

    def cmd_vel_callback(self, msg):
        if self.bridge:
            self.bridge.cmd_vel_signal.emit(msg.linear.x, msg.angular.z)

    def scan_callback(self, msg):
        import math  # Local defensive import to guarantee math functions are available
        try:
            # 1. Terminal alert to verify data is actively reaching this loop
            print(f"[LiDAR Debug] Raw data arriving! Processing {len(msg.ranges)} points...")
            
            # 2. Resilient boundary checks
            rmin = msg.range_min if msg.range_min > 0 else 0.05
            rmax = msg.range_max if msg.range_max > 0 else 50.0
            
            # 3. Clean filtering of infinite noise, nan values, and zeroed ground hits
            valid_ranges = [
                r for r in msg.ranges 
                if not math.isnan(r) and not math.isinf(r) and rmin <= r <= rmax and r > 0.05
            ]
            
            if valid_ranges and self.bridge:
                nearest_obstacle = min(valid_ranges)
                # Force float cast to match the Qt Signal slot perfectly
                self.bridge.lidar_signal.emit(float(nearest_obstacle))
                
        except Exception as e:
            # Catch and expose any hidden string formatting or logic errors in Terminal 3
            print(f"❌ [LiDAR Thread Error]: {e}")

    def wheel_callback(self, msg):
        if self.bridge:
            # Fallback Layer 1: Check standard velocity array per guidelines
            if hasattr(msg, 'velocity') and len(msg.velocity) >= 2:
                self.bridge.wheel_signal.emit(msg.velocity[0], msg.velocity[1])
            # Fallback Layer 2: Check position array if velocity is left unpopulated
            elif hasattr(msg, 'position') and len(msg.position) >= 2:
                self.bridge.wheel_signal.emit(msg.position[0], msg.position[1])
            # Fallback Layer 3: Check data array if wrapped as a Float64MultiArray
            elif hasattr(msg, 'data') and len(msg.data) >= 2:
                self.bridge.wheel_signal.emit(msg.data[0], msg.data[1])

    # --- CONTROLS & NAVIGATION LOGIC ---
    def trigger_emergency_stop(self):
        if self.goal_handle is not None:
            self.goal_handle.cancel_goal_async()
            self.goal_handle = None
        stop_msg = Twist()
        self.cmd_vel_pub.publish(stop_msg)
        if self.finished_cb:
            self.finished_cb()

    def log_to_gui(self, message):
        if self.bridge:
            self.bridge.log_signal.emit(f"[mission_control] {message}")

    def warn_to_gui(self, title, message):
        if self.bridge:
            self.bridge.warning_signal.emit(title, message)

    def start_mission(self, waypoints, finished_callback):
        self.waypoint_queue = waypoints
        self.current_index = 0
        self.finished_cb = finished_callback
        self.send_next_waypoint()

    def send_next_waypoint(self):
        if self.current_index >= len(self.waypoint_queue):
            self.log_to_gui("✨ All coordinates executed successfully!")
            if self.finished_cb:
                self.finished_cb()
            return
        if not self.client.wait_for_server(timeout_sec=2.0):
            self.warn_to_gui("Error", "Nav2 Server Offline!")
            if self.finished_cb:
                self.finished_cb()
            return

        x, y = self.waypoint_queue[self.current_index]
        self.log_to_gui(f"Dispatching WP {self.current_index + 1}: x={x:.2f}, y={y:.2f}")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = 1.0

        send_goal_future = self.client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.log_to_gui(f"❌ WP {self.current_index + 1} REJECTED!")
            if self.finished_cb:
                self.finished_cb()
            return
        self.goal_handle.get_result_async().add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        self.log_to_gui(f"Distance remaining = {feedback_msg.feedback.distance_remaining:.2f} m")

    def get_result_callback(self, future):
        if future.result().status == 4:
            self.log_to_gui(f"✅ WP {self.current_index + 1} SUCCEEDED")
            self.current_index += 1
            self.send_next_waypoint()
        else:
            self.log_to_gui(f"❌ WP {self.current_index + 1} aborted.")
            if self.finished_cb:
                self.finished_cb()


def main(args=None):
    rclpy.init(args=args)
    ros_node = Nav2ActionClientNode()
    
    ros_thread = threading.Thread(target=lambda: rclpy.spin(ros_node), daemon=True)
    ros_thread.start()
    
    app = QApplication(sys.argv)
    gui = MissionControlGUI(ros_node)
    gui.show()
    
    exit_code = app.exec_()
    ros_node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()