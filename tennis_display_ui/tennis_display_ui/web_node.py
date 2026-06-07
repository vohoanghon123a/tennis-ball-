#!/home/honvo/ros2_new/tennis_env/bin/python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
import cv2
import threading
import sys
import time
import os
from flask import Flask, Response, render_template_string

# 1. Khởi tạo Flask Web Server
app = Flask(__name__)

# ⚠️ ĐƯỜNG DẪN FILE VIDEO: Bro hãy đổi tên/đường dẫn này thành file video đã xử lý của bro nhé!
VIDEO_PATH = '/home/honvo/Desktop/NCKH/data_test/output_processed_video.mp4' 

class WebStreamNode(Node):
    def __init__(self):
        super().__init__('web_node')
        self.get_logger().info(f"Gói 5: Web Server đã chuyển sang chế độ phát lặp video: {VIDEO_PATH}")

# 2. Hàm đọc video từ file và ÉP LẶP VÔ TẬN (Infinite Loop)
def generate_mjpeg_stream():
    # Kiểm tra xem file video có tồn tại thực tế không
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ KHÔNG TÌM THẤY FILE VIDEO TẠI: {VIDEO_PATH}")
        print("💡 Bro hãy kiểm tra lại đường dẫn hoặc tên file video của mình nhé!")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)

    while True:
        if not cap.isOpened():
            cap = cv2.VideoCapture(VIDEO_PATH)
            time.sleep(1)
            continue

        ret, frame = cap.read()
        
        # 🟢 CHIẾN THUẬT LẶP VIDEO: Nếu hết video (ret == False), tua ngược về frame số 0 để chạy lại
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # ĐỒNG BỘ TỐC ĐỘ: Đọc FPS gốc của video để phát đúng tốc độ, không bị quá nhanh
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = 1.0 / fps if fps > 0 else 0.03
        time.sleep(delay)

        # Nén ảnh thành JPG để bắn lên trình duyệt
        ret_code, buffer = cv2.imencode('.jpg', frame)
        if ret_code:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()

# 3. Định tuyến giao diện Web hiển thị
@app.route('/')
def index():
    html_code = """
    <html>
        <head>
            <title>ROS 2 AI Tennis Video Playback</title>
            <style>
                body { background: #1e1e1e; color: white; text-align: center; font-family: Arial; padding-top: 20px; }
                h1 { color: #4CAF50; }
                .meta-info { color: #aaa; font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>📡 Chế Độ Phát Lặp Video AI - ROS 2 Jazzy</h1>
            <p class="meta-info">🎬 Đang phát lặp vô tận file video đã xử lý thành công!</p>
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
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

def main(args=None):
    # Thám tử in thông tin kiểm check luồng
    print("\n" + "="*60)
    print(f"🚨 [THÁM TỬ] Bộ thực thi Python đang phát video là: {sys.executable}")
    print(f"🎬 [THÁM TỬ] Đang tải file video từ: {VIDEO_PATH}")
    print("="*60 + "\n")

    rclpy.init(args=args)
    node = WebStreamNode()
    
    # Chạy Flask Server ở luồng riêng
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
