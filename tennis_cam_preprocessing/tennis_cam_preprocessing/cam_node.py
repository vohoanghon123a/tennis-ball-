import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time # Đưa import time lên đầu file cho sạch sẽ chuẩn convention

class CamNode(Node):
    def __init__(self):
        super().__init__('cam_node')
        self.bridge = CvBridge()
        self.publisher_ = self.create_publisher(Image, 'tennis_processed_image', 10)
        
        # Đường dẫn video gốc
        self.video_path = '/home/honvo/Desktop/NCKH/data_test/tennis ball.mp4'
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            self.get_logger().error("Gói 1: Không thể mở file video gốc!")
            return
            
        # --- THỜI GIAN DELAY KHỞI ĐỘNG CHUẨN ĐẦU DÒNG ---
        self.get_logger().info("Gói 1: Đang chờ 3.5 giây để các Node AI và UI ổn định hệ thống...")
        time.sleep(6) 
        
        # Sau khi hết thời gian chờ mới bắt đầu kích hoạt timer đọc video
        self.timer = self.create_timer(0.03, self.timer_callback)
        self.get_logger().info("Gói 1: Node Cam CHÍNH THỨC phát luồng dữ liệu video!")

    def timer_callback(self):
        """ Hàm này bắt buộc phải thẳng cột với hàm __init__ ở phía trên """
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().info("Hệ thống: Đã đọc và xử lý hết toàn bộ Video!")
            self.timer.cancel()
            return
            
        # Resize giảm 50% kích thước
        h, w = frame.shape[:2]
        resized_frame = cv2.resize(frame, (w // 2, h // 2))
        
        # Đóng gói và phát đi cho Gói 2
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
