from setuptools import find_packages, setup

package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arka',
    maintainer_email='arka@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # "ros2_executable = package_name . file_name : function_we_want_to_run"
            "test_node = my_robot_controller.my_first_node:main",
            "draw_circle = my_robot_controller.draw_circle:main",
            "pose_subscriber = my_robot_controller.pose_subscriber:main",
            "turtle_controller = my_robot_controller.turtle_controller:main"
        ],
        # Use:- we don't have to run the python file separately; the node will run along with ros2 execution.
        
        # note on variable names here:-
        # my_first_node --> file name (python), where we write the code.
        # my_robot_controller --> package name
        # main --> function we want to execute (node is defined in this function)
        # first_node --> passed in super().init()) is the name ROS2 identifies your node with.
        # test_node --> ros2_executable --- it is installed with colcon build and THIS is run in the cmd.
        # (Hence, we cannot do ./my_robot_controller to run the node in cmd.
        # ... we need to go to ./ros_ws/ and do ros2 run my_robot_controller test_node)
    },
)
