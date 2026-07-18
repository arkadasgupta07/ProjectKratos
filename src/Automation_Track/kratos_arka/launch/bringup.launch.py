from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Standard Q1 Publisher
        Node(
            package='kratos_arka',
            executable='rover_status_publisher.py',
            name='standard_publisher_node',
            output='screen'
        ),
        # 2. Standard Q1 Subscriber
        Node(
            package='kratos_arka',
            executable='rover_status_subscriber.py',
            name='standard_subscriber_node',
            output='screen'
        ),
        # 3. Dynamic Q2 Rover Publisher
        Node(
            package='kratos_arka',
            executable='rover_status_msg_publisher.py',
            name='rover_status_msg_publisher_node',
            output='screen'
        ),
        # 4. Q2 Rover Subscriber
        Node(
            package='kratos_arka',
            executable='rover_status_msg_subscriber.py',
            name='rover_status_msg_subscriber_node',
            output='screen'
        )
    ])
