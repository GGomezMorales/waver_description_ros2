import os
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.substitutions import Command
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    pkg_ros_gz_sim = FindPackageShare('ros_gz_sim')

    xacro_file = os.path.join(
        get_package_share_directory('waver_description'),
        'urdf',
        'waver.xacro'
    )
    ros_gz_bridge_config = os.path.join(
        get_package_share_directory('waver_description'),
        'config',
        'ros_gz_bridge.yaml'
    )
    world = os.path.join(
        get_package_share_directory('waver_description'),
        'worlds',
        'room.sdf'
    )
    rviz_config_file = os.path.join(
        get_package_share_directory('waver_description'),
        'rviz',
        'config.rviz'
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'robot_description': Command(['xacro ', xacro_file])}]
    )

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    # Spawn the robot in Gazebo
    spawn_entity_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'waver', '-topic', 'robot_description'],
        output='screen'
    )

    # Start Gazebo Sim Fortress (New Version)
    gz_sim_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])
        ),
        launch_arguments={
            'gz_args': ['-r -v 4 ', world]
        }.items(),
    )

    # Start Gazebo ROS Bridge
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge',
        output='screen',
        parameters=[{
            'config_file': ros_gz_bridge_config
        }]
    )

    # Rviz Node
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false', description='Use simulation (Gazebo) clock'
        ),
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity_robot,
        gz_sim_node,
        gz_bridge,
        rviz
    ])
