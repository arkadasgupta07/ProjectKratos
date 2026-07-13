import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'aruco_search_mission'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # This line ensures your launch files get compiled!
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Induction User',
    maintainer_email='user@todo.todo',
    description='Week 4 Autonomous Waypoint & ArUco Search',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # This links the command 'mission_node' to your main() function
            'mission_node = aruco_search_mission.mission_node:main',
        ],
    },
)