import sys
# Ép Python quét thẳng vào thư mục site-packages của môi trường ảo để bốc thư viện chuẩn
sys.path.insert(0, '/home/honvo/ros2_new/tennis_env/lib/python3.12/site-packages')

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image  # Hứng ảnh đã vẽ AI từ Gói 2
from std_msgs.msg import String     # Hứng khoảng cách Z từ Gói 3
from cv_bridge import CvBridge     # Cầu nối chuyển đổi ảnh
import cv2
import os

class UiStorageNode(Node):
    def __init__(self):
        super().__init__('ui_node')
        self.bridge = CvBridge()
        
        # 🟢 ĐỒNG BỘ 1: Đăng ký nhận ảnh kết quả AI từ Gói 2
        self.image_sub = self.create_subscription(
            Image, 
            '/tennis/processed_image', 
            self.image_callback, 
            10
        )
        
        # 🟢 ĐỒNG BỘ 2: Đăng ký nhận kết quả tính khoảng cách từ Gói 3
        self.spatial_sub = self.create_subscription(
            String, 
            '/tennis/spatial_data', 
            self.spatial_callback, 
            10
        )
        
        self.latest_distance = "Đang tính..."
        self.video_out_path = '/home/honvo/ros2_new/video_output.mp4'
        self.video_writer = None
        
        self.get_logger().info(f"Gói 4: Bộ ghi video kiểm chứng NCKH đã kích hoạt! Đang chờ dữ liệu...")

    def spatial_callback(self, msg):
        try:
            # Tách chuỗi dữ liệu "Kích_Thước_Pixel,Khoảng_Cách_Z" lấy từ Gói 3
            _, distance_z = msg.data.split(',')
            self.latest_distance = f"{distance_z} mm"
        except:
            pass

    def image_callback(self, msg):
        try:
            # Chuyển ảnh ROS 2 sang OpenCV để chuẩn bị ghi file
            cv_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            h, w = cv_frame.shape[:2]
            
            # 🟢 KHỞI TẠO BỘ GHI VIDEO: Chỉ chạy 1 lần duy nhất khi nhận được khung hình đầu tiên
            if self.video_writer is None:
                # Dùng mã hóa MP4V phổ biến, lưu tốc độ chuẩn 30 FPS theo kích thước ảnh thực tế
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(self.video_out_path, fourcc, 30.0, (w, h))
                self.get_logger().info(f"🎥 Gói 4: Đang tiến hành ghi dữ liệu vào file: {self.video_out_path}")
            
            # 🟢 ÉP CHỮ KIỂM CHỨNG: Ghi số mét khoảng cách trực tiếp xuống góc dưới video
            save_text = f"NCKH - Realtime Distance: {self.latest_distance}"
            cv2.putText(cv_frame, save_text, (20, h - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Đút khung hình vào file MP4
            self.video_writer.write(cv_frame)
            
        except Exception as e:
            self.get_logger().error(f"Gói 4 lỗi ghi video: {str(e)}")

    def destroy_node(self):
        # 🟢 QUAN TRỌNG: Khi bấm Ctrl+C tắt hệ thống, phải giải phóng VideoWriter để video không bị lỗi file (corrupt)
        if self.video_writer is not None:
            self.video_writer.release()
            self.get_logger().info("Gói 4: Đã đóng và lưu file video cứng thành công! File sẵn sàng để báo cáo.")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = UiStorageNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
