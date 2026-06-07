from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    
    # 1. Khai báo ép chạy Node Web bằng đúng Python của môi trường ảo tennis_env
    web_stream_node = ExecuteProcess(
        cmd=[
            '/home/honvo/ros2_new/tennis_env/bin/python3', 
            '/home/honvo/ros2_new/src/tennis_display_ui/tennis_display_ui/web_node.py'
        ],
        output='screen'
    )

    # 2. Trả về danh sách khởi chạy đồng bộ cả 5 nút hệ thống
    return LaunchDescription([
        # Kích hoạt Node Camera (Package 1)
        Node(
            package='tennis_cam_preprocessing',
            executable='run_cam',
            name='cam_node',
            output='screen'
        ),
        # Kích hoạt Node AI Detection (Package 2)
        Node(
            package='tennis_ai_detection',
            executable='run_ai',
            name='ai_node',
            output='screen'
        ),
        # Kích hoạt Node Không gian (Package 3)
        Node(
            package='tennis_spatial_localization',
            executable='run_local',
            name='local_node',
            output='screen'
        ),
        # Kích hoạt Node Giao diện (Package 4)
        Node(
            package='tennis_display_ui',
            executable='run_ui',
            name='ui_node',
            output='screen'
        ),
        # Kích hoạt Node Stream Web (Package 5 - Gọi từ biến ExecuteProcess phía trên)
        web_stream_node
    ])
