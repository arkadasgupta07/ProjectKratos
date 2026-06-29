# colcon --> used to create nodes
# to source the terminal u r using everytime ... code:- source ~/.bashrc
# in environment, added a line:- source ~/ros2_ws/install/setup.bash
# creating a package inside a node ... code:- ros2 pkg create my_robot_controller



#!/usr/bin/env python3
import rclpy # imports the ROS 2 Client Library for Python.
from rclpy.node import Node # Specifically imports the Node class, which is the foundation of every process in ROS 2.

# rclpy is the huge toolbox for ROS 2 in Python;
# node is the specific drawer in that toolbox containing everything related to creating a ROS process.
# import Node: This pulls out the Node class. A "class" in Python is like a blueprint.
# in ROS 2, the Node class contains all the complex background code required to talk to other robots, handle timing, and manage hardware.
# The Node class is the "DNA" of a robot process.
# Your class (MyNode) is a specific "person" you are building using that DNA.


class MyNode(Node): # You are creating a new class (Node Class) named MyNode that INHERITS all the powers of a ROS 2 Node, so that our Class can have all the functionalities of ROS2.
    
    def __init__(self): # constructor (responsible for building) of the node class MyNode.
        super().__init__("first_node") # CREATING A NODE ==> super() allows you to reach out to the parent class and use its DNA ... Here, Node (the ROS2 LIbrary imported on Line3) is the parent and MyNode is the child.
        # "Hey Parent (Node), please run your setup routine and name me 'first_node' so I can use all the official ROS 2 tools."
        
        # self.get_logger().info("ROS2") # Prints a formatted log message to your terminal. It will look like: [INFO] [first_node]: Hello from ROS2.
        # self is the identity of your specific robot node. It is how the node accesses its own memory and its own skills.
        self.counter_ = 0
        self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("Hellobubu " + str(self.counter_))
        self.counter_ +=1
    # ROS2 - Tutorial 5 - 00:21:00 for Recap


# "first_node" (passed in super().init()) is the name ROS2 identifies your node with.

# When you call super().__init__, you are telling Python:
# "Go to the parent class (Node)."
# "Run its setup function (__init__)."
# "Prepare the background tasks (like networking, internal clocks, and logging) so I can use them."

# The "Building a House" Analogy
# Imagine you are building a Smart Home.
# Node is the standard blueprint for a house (it has plumbing, electricity, and walls).
# MyNode is your specific design (you want to add a robot arm in the kitchen).
# If you don't call super().__init__, you are trying to install a robot arm in a house that doesn't have walls or electricity yet.
# By calling super(), you ensure the "foundation" (the standard ROS 2 Node features) is built first.


# IMPORANT CONCEPT:-

# Whenever you edit/change any code here, say you wanna print "Hello" instead of "Hello from ROS2",
# if you just change it in this python file and run its ros2_executable in cmd, it will still print the previous version ("Hello from ROS2")
# (syntax for running:- ros2 run my_robot_controller test_node)

# To overcome this, we need to build (colcon build) after every edit.
# cmd codes:-
# colcon build --symlink-install
# source ~/.bashrc
# ros2 run my_robot_controller test_node)

# # source ~/.bashrc
# When you change your code or build a new package with colcon build, your already open terminals don't know about those changes yet. They are still using the "memory" they had when you first opened them.
# By typing source ~/.bashrc, you force that specific terminal tab to re-read the file without having to close the window and open a new one.



# SOME IMPORANT CMD COMMANDS FOR ROS2:-

# rqt_graph --> creates a live map of all those connections made by the collection of nodes which make up your robot --- helps us to visualize what is actually happening in your robot's brain.
# ros2 node list
# ros2 node info /first_node 
# ros2 node info /<name_of_node>


# HOW DOES ONE NODE COMMUNICATE WITH OTHER NODE?
# THROUGH TOPICS
# CLOSED LOOP CONTROL BTWN. NODES:- NODE1-->TOPIC-->NODE2

# ros2 topic list
# Output:-
# /chatter
# /parameter_events
# /rosout

# ros2 topic info /chatter
# Output:-
# Type: std_msgs/msg/String
# Publisher count: 1    ... talker is the publisher to chatter
# Subscription count: 1 ... listener is the subscriber of chatter
# ... visualize as /talker --> /chatter --> /listener map (generate by rqt_graph)
# /talker is node1 (publisher), /chatter is topic, /listner is node2 (subscriber)

# ros2 interface show std_msgs/msg/String

# ros2 topic echo /chatter (in 3rd terminal) (1st & 2nd terminals are for ros2 run demo_nodes_cpp talker AND ros2 run demo_nodes_cpp listener)
# now by ros2 topic info /chatter (in 4th terminal)
# we get output:-
# Type: std_msgs/msg/String
# Publisher count: 1 ... /talker is publisher to /chatter
# Subscription count: 2 ... two subscribers of /chatter now, viz. listener and echo
# (visualize using rqt_graph)

# HOW DOES ONE NODE COMMUNICATE WITH OTHER NODE?
# THROUGH TOPICS
# CLOSED LOOP CONTROL BTWN. NODES:- /NODE1 --> /TOPIC --> /NODE2 ... (visualize through rqt_graph)
# --> SO, TOPIC IS A WAY TO COMMUNICATE BTWN. DIFFERENT NODES IN YOUR ROS APPLICATION.
# --> NODES DO NOT DIRECTY ALK TO EACH-OTHER. THEY JUST PUBLISH OR SUBSCRIBE TO A TOPIC.
# --> CAN HAVE MULTIPLE NODES PUBLISHING TO / SUBSCRIBING FROM THE SAME TOPIC.
# --> note:- the topic mechanism is anonymous, i.e.- a subscriber node just receives the messages from the topic, does not know which node published it.


def main(args=None): # This defines the starting point of your program. args=None allows the function to accept arguments from the command line
    rclpy.init(args=args) # INITIALIZE ROS2 COMMUNICATIONS --- This is the "Power On" switch. Before you can create a Node, you must initialize the ROS 2 communication system.

    node = MyNode() # This creates the actual instance of your class. Now, a "Node" object exists in your computer's memory, but it isn't "doing" anything yet.

    rclpy.spin(node) # keeps node alive, enables callbacks, so that can continue to communicate with ros2 functionalities until manually killed with Ctrl+Shift+C

    rclpy.shutdown() # This is the "POWER OFF" sequence. # This line only runs after you stop the program (usually by pressing Ctrl+Shift+C in the terminal).

    # rclpy.spin(node) =>
    # The "Infinite Loop": Without this, the script would move to the next line and exit immediately.
    # spin tells the program to "pause here and keep the node alive."
    # While "spinning," the node is constantly checking for events
    # This is the most important line for a running robot.

    # GENERAL STRUCTURE OF MAIN() ==>
    # START WITH => rclpy.init(args=args)
    # BODY INBTWN. (NODE CREATION) ... node is not the file/program itself, node is this part inside the file/program.
    # END WITH ==> rclpy.shutdown()

if __name__ == '__main__':
    main()

# This is a standard Python "guard" that ensures your code only runs when you want it to.
# In the context of ROS 2, it’s the difference between running your robot and just sharing your code.

# 1. What is __name__?
# Every time you run a Python file, Python automatically creates a special hidden variable called __name__.
# If you run the file directly (e.g., typing python3 my_first_node.py in your terminal), Python sets __name__ to the string "__main__".
# If you import the file into another script (e.g., import my_first_node), Python sets __name__ to the filename ( "my_first_node").

# 2. The "If" Logic
# The line if __name__ == '__main__': is basically a security check. It asks:
# "Is this file being run as the main program right now?"
# If YES: It executes the main() function, which starts your ROS 2 node.
# If NO (imported): It does nothing.
#  This allows other scripts to "borrow" your MyNode class without accidentally starting the whole robot process.

# 3. Why is this important for ROS 2?
# In ROS 2 development, you will eventually have many files.
# Sometimes you'll want to use a class you wrote in File_A inside of File_B.
# Without this "if" statement, the moment you typed import File_A inside your new script, the old robot node would start running automatically, likely causing errors or conflicting node names.


# Example:- Car Analogy (Driver vs Mechanic)

# Scenario A: You are the Driver ==>
# Action: You go to your terminal and type python3 my_first_node.py.
# In this case, Python sets a hidden variable: __name__ = "__main__".
# The script reads your Blueprint (class MyNode).
# It reaches the bottom line: if __name__ == '__main__':.
# Since the names match, it calls main().
# Result: The engine starts, the lights turn on, and you are "driving" the robot.

# Scenario B: You are the Mechanic (The "Import")
# Action: You are writing a new, different script (let's call it mega_robot.py), and you type from my_first_node import MyNode.
# In this case, Python sets the hidden variable for that file to: __name__ = "my_first_node".
# The script reads the Blueprint (class MyNode) so the mechanic knows how the engine is built.

# It reaches the bottom line: if __name__ == '__main__':.
# Wait! "my_first_node" does not equal "__main__".
# The if statement fails, and main() is skipped.
# Result: The mechanic gets the blueprint to use in their own project, but the car stays parked and silent in the garage.



# HOW DOES ONE NODE COMMUNICATE WITH OTHER NODE?
# THROUGH TOPICS
# CLOSED LOOP CONTROL BTWN. NODES:- /NODE1 --> /TOPIC --> /NODE2 ... (visualize through rqt_graph)
# --> SO, TOPIC IS A WAY TO COMMUNICATE BTWN. DIFFERENT NODES IN YOUR ROS APPLICATION.
# --> NODES DO NOT DIRECTY ALK TO EACH-OTHER. THEY JUST PUBLISH OR SUBSCRIBE TO A TOPIC.
# --> CAN HAVE MULTIPLE NODES PUBLISHING TO / SUBSCRIBING FROM THE SAME TOPIC.
# --> note:- the topic mechanism is anonymous, i.e.- a subscriber node just receives the messages from the topic, does not know which node published it.




#  IMPORTANT CONCEPTUAL NOTE (--symlink-install) FOR CMD:-

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