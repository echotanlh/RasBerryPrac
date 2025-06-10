from flask import Flask, Response
from picamera2 import Picamera2
import time
import io

app = Flask(__name__)


def generate_frames():
    # 配置树莓派5专用摄像头（兼容Camera Module 3/4）
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}  # 降低分辨率提升性能
    )
    picam2.configure(config)
    picam2.start()

    while True:
        frame = picam2.capture_array()  # 直接获取RGB图像数组
        # 转换为JPEG字节流（PIL高效处理）
        from PIL import Image
        img = Image.fromarray(frame)
        stream = io.BytesIO()
        img.save(stream, format="JPEG", quality=85)  # 压缩质量调整
        stream.seek(0)
        yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n'
        )
        stream.close()
        time.sleep(0.05)  # 控制帧率约20fps


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)  # 启用多线程[5](@ref)