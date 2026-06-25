#!/home/honvo/ros2_new/tennis_env/bin/python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image # Hứng ảnh từ hệ thống ROS 2
from cv_bridge import CvBridge    # Cầu nối chuyển ảnh ROS 2 sang OpenCV
import cv2
import threading
import sys
import time
from flask import Flask, Response, render_template_string

# 1. Khởi tạo Flask Web Server
app = Flask(__name__)

# 🟢 BIẾN TOÀN CỤC VÀ KHÓA CHỐNG DEADLOCK (Xung đột luồng giữa ROS và Flask)
global_frame = None
frame_lock = threading.Lock()

class WebStreamNode(Node):
    def __init__(self):
        super().__init__('web_node')
        # Hứng ảnh đã vẽ khung YOLO từ Node AI gửi sang
        self.subscription = self.create_subscription(
            Image, 
            '/tennis/processed_image', 
            self.listener_callback, 
            10
        )
        self.bridge = CvBridge()
        self.get_logger().info("Gói 5: Web Server đã chuyển sang chế độ PHÁT TRỰC TIẾP luồng ảnh từ Jetson + AI!")

    def listener_callback(self, msg):
        global global_frame
        try:
            # Chuyển ảnh từ mạng ROS 2 sang OpenCV để Flask xử lý
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Nén ảnh thành định dạng JPG
            ret_code, buffer = cv2.imencode('.jpg', cv_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            if ret_code:
                # Cập nhật frame mới nhất vào vùng nhớ chung (Có khóa bảo vệ)
                with frame_lock:
                    global_frame = buffer.tobytes()
        except Exception as e:
            self.get_logger().error(f"Lỗi chuyển đổi ảnh CvBridge: {e}")

# 2. Hàm lấy ảnh từ Topic ROS 2 và bắn lên trình duyệt (Thời gian thực)
def generate_mjpeg_stream():
    global global_frame
    while True:
        # Vào vùng nhớ lấy ảnh ra thật nhanh rồi nhả khóa ngay cho ROS nạp ảnh tiếp
        with frame_lock:
            frame = global_frame
        
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # Nếu hệ thống vừa bật, chưa có ảnh từ Jetson truyền qua, ngủ 0.1s chờ dữ liệu
            time.sleep(0.1)
            continue
            
        # Đồng bộ tốc độ phát ~30 FPS phù hợp với Wi-Fi
        time.sleep(0.03)

# 3. Giao diện Web hiển thị (Đã sửa từ Phát lặp sang Phát trực tiếp)
@app.route('/')
def index():
    html_code = """
    <html>
        <head>
            <title>ROS 2 AI Tennis Live Stream</title>
            <style>
                body { background: #1e1e1e; color: white; text-align: center; font-family: Arial; padding-top: 20px; }
                h1 { color: #4CAF50; }
                .meta-info { color: #aaa; font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>📡 Chế Độ Phát Trực Tiếp AI - ROS 2 Jazzy</h1>
            <p class="meta-info">🎬 Đang tiếp sóng trực tiếp từ Jetson Cam và xử lý YOLO AI trên Máy ảo!</p>
            <hr style="width: 60%; border: 1px solid #444;">
            <br>
            <img src="{{ url_for('video_feed') }}" width="75%" style="border: 3px solid #4CAF50; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.6);">
        </body>
    </html>
    """
    return render_template_string(html_code)

@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask_server():
    # Mở cổng 5000 phát ra toàn mạng nội bộ
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

def main(args=None):
    print("\n" + "="*60)
    print(f"🚨 [THÁM TỬ] Bộ thực thi Python hệ Jazzy: {sys.executable}")
    print("🎬 [THÁM TỬ] Hệ thống Live Stream đóng vòng lặp ĐÃ KÍCH HOẠT!")
    print("="*60 + "\n")

    rclpy.init(args=args)
    node = WebStreamNode()
    
    # Kích hoạt Flask Server chạy song song trên một luồng riêng
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
