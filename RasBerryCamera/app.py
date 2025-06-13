from flask import Flask, Response, render_template, jsonify
import cv2
import numpy as np
import threading
import time
from picamera2 import Picamera2
from libcamera import controls

app = Flask(__name__)

# 加载鱼目标检测模型 (YOLOv5示例)
net = cv2.dnn.readNet("yolov5s.onnx")  # 替换为您的鱼检测模型
classes = ["fish"]  # 类别列表

# 全局计数和锁
fish_count = 0
lock = threading.Lock()


def detect_fish(frame_bgr):
    """在BGR图像上检测鱼目标并绘制框"""
    global fish_count
    height, width = frame_bgr.shape[:2]

    # 创建输入blob
    blob = cv2.dnn.blobFromImage(
        frame_bgr,
        1 / 255.0,
        (640, 640),
        swapRB=True,
        crop=False
    )

    # 模型推理
    net.setInput(blob)
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    # 解析检测结果
    boxes = []
    confidences = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5 and classes[class_id] == "fish":
                # 获取边界框坐标
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # 转换为矩形坐标
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))

    # 应用非极大值抑制
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # 更新计数并绘制检测框
    with lock:
        fish_count = len(indices) if indices is not None else 0

        if indices is not None:
            for i in indices.flatten():
                box = boxes[i]
                x, y, w, h = box
                cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame_bgr, f"Fish: {confidences[i]:.2f}",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)

    # 显示计数
    cv2.putText(frame_bgr, f"Total Fish: {fish_count}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2)

    return frame_bgr


def generate_frames():
    """使用Picamera2生成视频帧"""
    # 初始化Picamera2并配置参数[1,2](@ref)
    picam2 = Picamera2()

    # 创建预览配置（优化性能）[7](@ref)
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"},
        lores={"size": (320, 240), "format": "YUV420"},
        display="lores",  # 使用低分辨率流预览节省性能
        controls={
            "FrameRate": 20,  # 限制帧率
            "AwbEnable": True,  # 自动白平衡
            "AeEnable": True,  # 自动曝光
        }
    )

    # 应用配置并启动相机
    picam2.configure(config)
    picam2.start()

    try:
        while True:
            # 捕获帧（RGB格式）[1,6](@ref)
            frame_rgb = picam2.capture_array("main")

            # 转换为BGR格式（OpenCV默认）
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # 进行鱼目标检测
            processed_frame = detect_fish(frame_bgr)

            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            # 控制帧率
            time.sleep(0.05)  # 约20fps
    finally:
        # 确保释放资源
        picam2.stop()


@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/fish_count')
def get_fish_count():
    """获取当前鱼数量"""
    with lock:
        return jsonify({"count": fish_count})


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)