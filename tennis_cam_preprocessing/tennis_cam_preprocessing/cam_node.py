import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CamNode(Node):
    def __init__(self):
        super().__init__('cam_node')
        self.bridge = CvBridge()
        
        # 🟢 SỬA LỖI 1: Đổi tên topic thành /tennis/raw_image để nuôi Gói 2 (AI YOLO)
        self.publisher_ = self.create_publisher(Image, '/tennis/raw_image', 10)
        
        # Đường dẫn luồng Stream từ xa của con Jetson Nano
        self.video_path = 'http://192.168.1.5:5000/video_feed'
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            self.get_logger().error("Gói 1: Không thể kết nối tới luồng ảnh của Jetson!")
            return
            
        self.get_logger().info("Gói 1: Đang chờ 6 giây để các Node AI và UI ổn định hệ thống...")
        
        # 🟢 SỬA LỖI 2: Dùng One-shot Timer chờ 6 giây cực kỳ chuyên nghiệp (Không chặn luồng máy ảo)
        self.startup_timer = self.create_timer(6.0, self.start_publishing_stream)

    def start_publishing_stream(self):
        """ Hàm này tự động kích hoạt sau khi hết 6 giây đếm ngược """
        self.startup_timer.cancel() # Hủy bỏ timer đếm ngược một lần
        
        # Chính thức kích hoạt timer đọc khung hình liên tục (~30 FPS)
        self.timer = self.create_timer(0.03, self.timer_callback)
        self.get_logger().info("Gói 1: Node Cam CHÍNH THỨC phát luồng dữ liệu video thô!")

    def timer_callback(self):
        ret, frame = self.cap.read()
        
        # 🟢 SỬA LỖI 3: Cơ chế chống rớt mạng Wi-Fi nội bộ
        if not ret:
            self.get_logger().warn("Hệ thống: Mất kết nối với Jetson! Đang tự động kết nối lại luồng mạng...")
            self.cap.open(self.video_path) # Ép mở lại cổng kết nối mạng
            return
            
        # Resize giảm 50% kích thước siêu mượt của bro giữ nguyên
        h, w = frame.shape[:2]
        resized_frame = cv2.resize(frame, (w // 2, h // 2))
        
        # Đóng gói ảnh OpenCV thành định dạng ROS 2 và bắn đi cho AI YOLO
        img_msg = self.bridge.cv2_to_imgmsg(resized_frame, encoding="bgr8")
        self.publisher_.publish(img_msg)

def main(args=None):
    rclpy.init(args=args)
    node = CamNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
