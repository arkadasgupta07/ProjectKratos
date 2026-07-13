from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='aruco_search_mission',
            executable='mission_node',
            name='mission_node',
            output='screen'
        )
    ])