import sys
# Ép Python quét thẳng vào thư mục site-packages của môi trường ảo để lấy Ultralytics/Torch chuẩn
sys.path.insert(0, '/home/honvo/ros2_new/tennis_env/lib/python3.12/site-packages')

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

class AiNode(Node):
    def __init__(self):
        super().__init__('ai_node')
        # Nạp model weights từ desktop của bro
        self.model = YOLO('/home/honvo/Desktop/NCKH/data_test/best (1).pt')
        self.bridge = CvBridge()
        
        # 🟢 ĐỒNG BỘ 1: Hứng ảnh thô chuẩn từ Gói 1 truyền từ Jetson về
        self.subscription = self.create_subscription(
            Image, 
            '/tennis/raw_image', 
            self.image_callback, 
            10
        )
        
        # 🟢 ĐỒNG BỘ 2: Phát tọa độ quả bóng tốt nhất sang Gói 3 (Thêm dấu / cho chuẩn quy hoạch)
        self.publisher_ = self.create_publisher(String, '/tennis/pixels', 10)
        
        # 🟢 ĐỒNG BỘ 3: Phát ảnh đã xử lý AI sang Gói 5 để Stream lên Web máy ảo
        self.ai_img_pub = self.create_publisher(Image, '/tennis/processed_image', 10)
        
        self.get_logger().info("Gói 2: Model YOLO đã nạp thành công -> Sẵn sàng detect và xuất tọa độ...")

    def image_callback(self, msg):
        cv_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        
        # 🟢 TỐI ƯU: Thêm verbose=False để màn hình Terminal không bị tràn ngập log fps của YOLO
        results = self.model(cv_frame, verbose=False)
        
        # Lấy ảnh nền đã có khung chữ nhật mặc định của YOLO trước
        annotated_frame = results[0].plot()
        
        best_box = None
        max_conf = -1.0
        
        # Duyệt qua TẤT CẢ các quả bóng phát hiện được để vẽ tọa độ lên video
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                
                # Tính tọa độ tâm (Center) của từng quả bóng
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # --- VẼ TOẠ ĐỘ ĐÈ LÊN TỪNG QUẢ BANH ---
                coord_text = f"({cx},{cy})"
                cv2.circle(annotated_frame, (cx, cy), 4, (0, 0, 255), -1)  # Chấm tâm đỏ
                cv2.putText(annotated_frame, coord_text, (int(x1), int(y1) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # Chữ tọa độ trắng
                
                # Thuật toán lọc tìm quả bóng có độ tin cậy (conf) cao nhất (Giữ nguyên logic đỉnh cao của bro)
                if conf > max_conf:
                    max_conf = conf
                    best_box = box
        
        # 1. Phát ảnh đã chèn tọa độ đa mục tiêu sang Gói 5 để lên Web
        ai_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
        self.ai_img_pub.publish(ai_msg)
        
        # 2. Chỉ gửi duy nhất tọa độ của quả bóng uy tín nhất sang Gói 3 để tính khoảng cách 3D
        if best_box is not None:
            x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()
            pixel_msg = String()
            pixel_msg.data = f"{x1},{y1},{x2},{y2}"
            self.publisher_.publish(pixel_msg)

def main(args=None):
    rclpy.init(args=args)
    node = AiNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
