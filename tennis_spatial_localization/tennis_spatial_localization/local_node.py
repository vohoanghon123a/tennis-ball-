import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LocalNode(Node):
    def __init__(self):
        super().__init__('local_node')
        
        # 🟢 ĐỒNG BỘ 1: Hứng chính xác tọa độ x1,y1,x2,y2 từ Gói 2 gửi sang
        self.subscription = self.create_subscription(
            String, 
            '/tennis/pixels', 
            self.pixel_callback, 
            10
        )
        
        # 🟢 ĐỒNG BỘ 2: Phát dữ liệu không gian ra hệ thống để các gói khác sử dụng
        self.publisher_ = self.create_publisher(String, '/tennis/spatial_data', 10)
        self.get_logger().info("Gói 3: Bộ thuật toán giải hình học không gian (Pinhole Model) đã hoạt động...")

    def pixel_callback(self, msg):
        try:
            # Nhận tọa độ x1, y1, x2, y2 của duy nhất quả bóng chuẩn nhất
            x1, y1, x2, y2 = map(float, msg.data.split(','))
            
            # --- ĐOẠN NÀY LÀ CÔNG THỨC TOÁN HỌC GỐC ĐỈNH CAO CỦA BRO ---
            width_px = x2 - x1
            
            # Thuật toán tính khoảng cách Z dựa trên độ mở pixel (Tỉ lệ nghịch)
            focal_length = 500.0      # Tiêu cự giả định (Sau này bro có thể hiệu chuẩn - calibrate lại con số này)
            ball_diameter_mm = 67.0   # Đường kính chuẩn quốc tế của quả bóng tennis
            
            distance_z = (ball_diameter_mm * focal_length) / width_px if width_px > 0 else 0.0
            
            # Đóng gói chuỗi kết quả: "Kích_Thước_Pixel,Khoảng_Cách_Z" phát đi
            spatial_msg = String()
            spatial_msg.data = f"{width_px:.1f},{distance_z:.2f}"
            self.publisher_.publish(spatial_msg)
            
            # In thử log ra màn hình máy ảo để bro kiểm tra tọa độ nhảy liên tục
            # self.get_logger().info(f"📐 Ước lượng khoảng cách Z: {distance_z:.2f} mm (Độ rộng: {width_px:.1f} px)")
            
        except Exception as e:
            self.get_logger().error(f"Gói 3 lỗi toán học hoặc phân tách chuỗi: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LocalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
