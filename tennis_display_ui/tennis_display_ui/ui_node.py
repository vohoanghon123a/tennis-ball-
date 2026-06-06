import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import time

class UiNode(Node):
    def __init__(self):
        super().__init__('ui_node')
        self.bridge = CvBridge()
        
        # Đăng ký nhận ảnh từ Gói 2 (Ảnh đã có khung YOLO và Tọa độ từng quả bóng)
        self.img_sub = self.create_subscription(Image, 'tennis_ai_image', self.image_callback, 10)
        self.data_sub = self.create_subscription(String, 'tennis_spatial_data', self.data_callback, 10)
        
        self.latest_distance = "Calculating..."
        self.latest_width = "0"
        
        # --- CẤU HÌNH LƯU VIDEO VÀO FOLDER DATA KIỂM CHỨNG ---
        self.output_path = '/home/honvo/Desktop/NCKH/data_test/output_processed_video.mp4'
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.frames_buffer = []  # Mảng lưu tạm frame vào RAM để tăng tối đa tốc độ Stress Test
        self.start_time = None
        self.end_time = None
        
        self.get_logger().info(f"Gói 4: Hệ thống Giám sát Hiệu năng đang chờ luồng dữ liệu tại: {self.output_path}")

    def data_callback(self, msg):
        try:
            data_str = msg.data
            if "," in data_str:
                self.latest_width, self.latest_distance = data_str.split(",")
        except Exception:
            pass

    def image_callback(self, msg):
        if self.start_time is None:
            self.start_time = time.time()
            
        cv_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        
        # --- TRỘN THÔNG SỐ TOÁN HỌC KHHOẢNG CÁCH CỦA BÓNG TỐT NHẤT LÊN GÓC TRÁI ---
        cv2.rectangle(cv_frame, (10, 10), (380, 110), (0, 0, 0), -1)  # Khung nền đen mờ
        
        text_width = f"Width Ball: {self.latest_width} px"
        cv2.putText(cv_frame, text_width, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        text_dist = f"Distance Z: {self.latest_distance} mm"
        color = (0, 255, 0) if "Calculating" not in self.latest_distance else (0, 0, 255)
        cv2.putText(cv_frame, text_dist, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Đẩy frame vào bộ đệm RAM
        self.frames_buffer.append(cv_frame)
        self.end_time = time.time()

    def destroy_node(self):
        """ Khi bấm Ctrl+C, tiến hành tính toán tốc độ tối đa và xuất video khớp thời gian thực """
        total_frames = len(self.frames_buffer)
        
        if total_frames > 0 and self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            calculated_fps = total_frames / total_time
            
            # In bảng hiệu năng đanh thép lên Terminal để bro lấy số liệu báo cáo
            self.get_logger().info("\n" + "="*50)
            self.get_logger().info(f"📊 KẾT QUẢ SƠ KẾT HIỆU NĂNG PHẦN CỨNG THỰC TẾ:")
            self.get_logger().info(f"⏱️ Tổng thời gian xử lý toàn bộ dự án: {total_time:.2f} giây")
            self.get_logger().info(f"🎞️ Tổng số lượng Frame bảo toàn: {total_frames} frames")
            self.get_logger().info(f"🚀 TỐC ĐỘ XỬ LÝ TỐI ĐA ĐẠT ĐƯỢC: {calculated_fps:.2f} FPS")
            self.get_logger().info("="*50 + "\n")
            
            # Khởi tạo VideoWriter chạy bằng ĐÚNG số FPS thực tế vừa đo được của máy bro
            h, w, _ = self.frames_buffer[0].shape
            video_writer = cv2.VideoWriter(self.output_path, self.fourcc, calculated_fps, (w, h))
            
            self.get_logger().info("💾 Đang tiến hành ghi dữ liệu nhị phân vào file video.mp4...")
            for frame in self.frames_buffer:
                video_writer.write(frame)
            video_writer.release()
            
            self.get_logger().info("✅ Đã đóng gói và xuất file thành công!")
        else:
            self.get_logger().error("Hệ thống chưa nhận được frame nào.")
            
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = UiNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
