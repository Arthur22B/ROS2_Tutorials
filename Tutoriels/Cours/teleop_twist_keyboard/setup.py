from setuptools import find_packages, setup

package_name = 'teleop_twist_keyboard'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='insa',
    maintainer_email='arthur.bouille@insa-strasbourg.fr',
    description='Télécommande ROS2 pour TurtleBot3',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_twist_keyboard = teleop_twist_keyboard.teleop_twist_keyboard:main'
        ],
    },
)
