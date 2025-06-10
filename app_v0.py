from flask import Flask, Response
import cv2,os

app = Flask(__name__)
def gen_frames():
    print("开始啦")
    os.environ["OPENCV_VIDEOIO_V4L2_ASSUME_MJPEG"] = "1"
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        print("获取数据啦")
        success, frame = camera.read()
        if not success:
            error_code = camera.get(cv2.CAP_PROP_POS_MSEC)  # 或其他属性，但OpenCV没有直接的错误码获取，可以尝试其他方式
            print("错误状态:", error_code)
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/image_data')
def image_data():
    with open('test.jpg', 'rb') as f:  # 二进制模式读取
        image_bytes = f.read()
    # 直接返回二进制数据并设置 Content-Type
    return Response(image_bytes, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)