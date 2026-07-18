#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist # importing Twist message type from geometry_msgs package

class DrawCircleNode(Node): # this class inherits from Node

    # initializing our node
    def __init__(self):
        super().__init__("draw_circle")
        # now to create a publisher (to send msgs to topic for subscriber) and a timer and print something
        # self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10) # for 2D
        self.cmd_vel_pub_ = self.create_publisher(Twist, "/cmd_vel", 10) # for 3D
        self.timer_ = self.create_timer(0.5, self.send_velocity_command) # the timer is going to call this function every 0.5sec (inside the function we create the msg)
        self.get_logger().info("Draw circle node has been started")

        # hovering over the self.create_publisher(), we get to know that we have to pass 3 parameters:-
        
        # (1) msg_type ==>
        # get this by:- ros2 topic list -->  ros2 topic info /turtle1/cmd_vel
        # output is got as:-
        # Type: geometry_msgs/msg/Twist
        # Publisher count: 0
        # Subscription count: 1
        # Hence, we get to know that to send Twist msg from geometry_msgs package.
        # thus also write at top --> from geometry_msgs.msg import Twist
        # also since we are using geometry_msgs package inside out my_robot_controller package, hence to add a dependency of geometry_msgs in package.xml
        # thus from now any package used in my_robot_controller will have dependency on geometry_msgs too.

        # (2) topic name ==>
        # from ros2 topic list, we got out topic name as /turtle1/cmd_vel

        # (3) queue_size ==>
        # creates a buffer so that all msgs get sent in case of sending big pieces of data or on unreliable network.



    def send_velocity_command(self): # the function which contains the msg, and is called every 0.5sec by the timer

        msg = Twist() # creating msg object from the class Twist
        msg.linear.x = 0.4
        msg.angular.z = 1.0
        # content of msg ... only x (linear) & z (angular) motion reqrd to move tortoise in circle.
        self.cmd_vel_pub_.publish(msg) # publishing/sending the msg object


        # WHAT TO SEND AS MSG??
        # Know this by (in cmd):- ros2 interface show Type
        # --> ros2 interface show geometry_msgs/msg/Twist
        # ... (geonetry_msgs package, interface type is a message, Twist is the specific message name.)
        # 
        # we get output as:-
        # Vector3  linear
        #    	float64 x
        #    	float64 y
        #    	float64 z
        # Vector3  angular
        #    	float64 x
        #    	float64 y
        #    	float64 z



def main(args=None):
    rclpy.init(args=args)
    node = DrawCircleNode() # make the node
    rclpy.spin(node) # keep the node alive
    rclpy.shutdown()

# make sure to go to setup.py and write the ros2 executatle file name.
# "ros2_executable = package . file_name : function_we_want_to_run"

if __name__ == '__main__':
    main()


# IMPORTANT CONCEPTUAL NOTE (--symlink-install) FOR CMD:-

# Normally, when you run colcon build, ROS 2 takes your Python files from your src folder and copies them into the install folder.
# The Problem: If you open draw_circle.py in VS Code and change a speed value, you have only changed the file in src. The "installed" version that ROS 2 actually runs is still the old copy.
# The Result: You have to run colcon build every single time you save a change, which is a massive waste of time.

# The Professional Way (Solution):- --symlink-install
# When you add this flag, colcon does not copy your files. Instead, it creates a Symbolic Link (a shortcut).
# The Link: The file in your install folder becomes a "portal" that points directly back to your source code in src.
# The Result: You can keep your terminal running, stop the node with Ctrl+Shift+C, and immediately run ros2 run again to see your changes. No rebuilding required!

# When do you STILL need to rebuild?
# --> Creating a new file
# --> Edit setup.py: If you change your entry points (the commands you type to run the node).
# --> Edit package.xml: If you add new dependencies (like adding sensor_msgs).
# --> Change C++ code: C++ must always be recompiled; symlinks only work for interpreted languages like Python.


# source ~/.bashrc
# When you change your code or build a new package with colcon build, your already open terminals don't know about those changes yet. They are still using the "memory" they had when you first opened them.
# By typing source ~/.bashrc, you force that specific terminal tab to re-read the file without having to close the window and open a new one.



# In this project, rqt_graph gives map:-
# /draw_circle --> /tutle/cmd_vel --> /turtlesim
# if we kept the /turtlesim terminal on (ros2 run turtlesim turtlesim_node)
# and in another terminal if we kept /draw_circle on (ros2 run my_robot_controller draw_circle), then circle is drawn, if terminal is killed, then turtle stops/pauses and so on.

# More CMD ros2 commands:-
# ros2 topic list
# ros2 topic info /turtle1/cmd_vel
# ros2 topic echo /turtle1/cmd_vel
