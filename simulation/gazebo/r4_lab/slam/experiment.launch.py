from pathlib import Path
import json
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def simulation_exit(event,context):
    if context.is_shutdown:return []
    return [EmitEvent(event=Shutdown(reason='Gazebo stopped'))]


def generate_launch_description():
    root = Path(__file__).resolve().parent
    cfg=json.loads((root/'generated/resolved.json').read_text())
    renderer_path=root/'generated/rviz_renderer.json'
    renderer=json.loads(renderer_path.read_text()) if renderer_path.exists() else {}
    rviz_env={}
    if renderer.get('workaround_enabled'):
        rviz_env['AMENT_PREFIX_PATH']=renderer['overlay']+os.pathsep+os.environ.get('AMENT_PREFIX_PATH','')
    bridge = [
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        '/motor_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        '/scan_raw@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
        '/ground_truth/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        '/wrist_cam/image@sensor_msgs/msg/Image[gz.msgs.Image',
        '/belly_cam/image@sensor_msgs/msg/Image[gz.msgs.Image']
    bridge += [f'/arm/{name}@std_msgs/msg/Float64]gz.msgs.Double' for name in
               ('shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper')]
    if cfg.get('scenario')=='pick_place':
        bridge += ['/wrist_cam/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
                   '/evaluation/object_odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                   '/grasp/fixed_contacts@ros_gz_interfaces/msg/Contacts[gz.msgs.Contacts',
                   '/grasp/moving_contacts@ros_gz_interfaces/msg/Contacts[gz.msgs.Contacts']
    gui_sim=ExecuteProcess(cmd=['gz','sim','-r','--gui-config',str(root/'research_gui.config'),
        '--seed',str(cfg['seed']),str(root/'generated/world.sdf')],
        condition=IfCondition(LaunchConfiguration('gui')),output='screen')
    headless_sim=ExecuteProcess(cmd=['gz','sim','-r','-s','--headless-rendering',
        '--seed',str(cfg['seed']),str(root/'generated/world.sdf')],
        condition=UnlessCondition(LaunchConfiguration('gui')),output='screen')
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('stress', default_value='false'),
        RegisterEventHandler(OnProcessExit(target_action=gui_sim,
            on_exit=simulation_exit)),
        RegisterEventHandler(OnProcessExit(target_action=headless_sim,
            on_exit=simulation_exit)),
        gui_sim,headless_sim,
        Node(package='ros_gz_bridge', executable='parameter_bridge', arguments=bridge,
             remappings=[('/motor_states', '/joint_states')],
             parameters=[{'use_sim_time': True}], output='screen'),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'use_sim_time': True,
                          'robot_description': (root/'generated/r4.urdf').read_text()}]),
        ExecuteProcess(cmd=['/usr/bin/python3', str(root/'scan_pipeline.py'), '--ros-args',
                            '-p', 'use_sim_time:=true', '-p', ['stress:=', LaunchConfiguration('stress')]], output='screen'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            str(Path(get_package_share_directory('slam_toolbox'))/'launch/online_async_launch.py')),
            launch_arguments={'use_sim_time':'true', 'slam_params_file':str(root/'generated/slam.yaml')}.items()),
        Node(package='rviz2', executable='rviz2', arguments=['-d', str(root/('carry.rviz' if cfg.get('scenario')=='carry' else 'mapping.rviz'))],
             parameters=[{'use_sim_time': True}],additional_env=rviz_env,condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
