import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LocalNode(Node):
    def __init__(self):
        super().__init__('local_node')
        self.subscription = self.create_subscription(String, 'tennis_pixels', self.pixel_callback, 10)
        self.publisher_ = self.create_publisher(String, 'tennis_spatial_data', 10)
        self.get_logger().info("Gói 3: Bộ thuật toán giải hình học không gian đã hoạt động...")

    def pixel_callback(self, msg):
        try:
            # Nhận tọa độ x1, y1, x2, y2 của duy nhất quả bóng chuẩn nhất
            x1, y1, x2, y2 = map(float, msg.data.split(','))
            
            # --- ĐOẠN NÀY LÀ CÔNG THỨC TOÁN HỌC GỐC CỦA BRO ---
            width_px = x2 - x1
            
            # Ví dụ công thức giải tiêu cự tính khoảng cách Z (Bro thay bằng công thức thực tế của bro)
            # Giả sử: Distance = (Dường kính thật * Tiêu cự) / width_px
            focal_length = 500.0  # Tiêu cự giả định
            ball_diameter_mm = 67.0  # Đường kính chuẩn quả bóng tennis
            distance_z = (ball_diameter_mm * focal_length) / width_px if width_px > 0 else 0.0
            
            # Đóng gói chuỗi kết quả: "Kích_Thước_Pixel,Khoảng_Cách_Z" phát sang Gói 4
            spatial_msg = String()
            spatial_msg.data = f"{width_px:.1f},{distance_z:.2f}"
            self.publisher_.publish(spatial_msg)
            
        except Exception as e:
            self.get_logger().error(f"Gói 3 lỗi toán học: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LocalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
