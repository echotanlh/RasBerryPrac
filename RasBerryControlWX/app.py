from wxpy import *
import picamera

bot = Bot(cache_path=True)  # 扫码登录微信
my_friend = bot.friends().search('接收者微信备注名')[0]  # 指定消息接收人

@bot.register(msg_types=TEXT)
def handle_message(msg):
    if msg.text == '拍照':  # 接收拍照指令
        with picamera.PiCamera() as camera:
            camera.resolution = (800, 600)
            camera.capture('/tmp/image.jpg')  # 保存临时文件
            my_friend.send_image('/tmp/image.jpg')  # 发送照片[1,4,7](@ref)
    elif msg.text == '录像':  # 扩展视频功能
        camera.start_recording('video.h264')
        camera.wait_recording(10)  # 录10秒
        camera.stop_recording()
        my_friend.send_video('video.h264')[1](@ref)

bot.join()  # 保持运行