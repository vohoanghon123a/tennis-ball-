from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Kích hoạt Node Camera (Package 1)
        Node(
            package='tennis_cam_preprocessing',
            executable='run_cam',
            name='cam_node',
            output='screen'
        ),
        # 2. Kích hoạt Node AI Detection (Package 2)
        Node(
            package='tennis_ai_detection',
            executable='run_ai',
            name='ai_node',
            output='screen'
        ),
        # 3. Kích hoạt Node Không gian (Package 3)
        Node(
            package='tennis_spatial_localization',
            executable='run_local',
            name='local_node',
            output='screen'
        ),
        # 4. Kích hoạt Node Giao diện (Package 4)
        Node(
            package='tennis_display_ui',
            executable='run_ui',
            name='ui_node',
            output='screen'
        )
    ])
