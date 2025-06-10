from wxpy import *
from picamera2 import Picamera2
import time

# 初始化picamera2
picam2 = Picamera2()
config = picam2.create_still_configuration()  # 创建静态图片配置
picam2.configure(config)  # 应用配置
picam2.start()  # 启动摄像头（预热）

# 微信登录
bot = Bot(cache_path=True, console_qr=2)  # console_qr=2支持文本设备扫码
my_friend = bot.friends().search('孤烟')[0]  # 替换为实际备注


@bot.register(my_friend, msg_types=TEXT)
def reply_photo(msg):
    if msg.text == '拍照':
        # 拍照并保存
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        file_path = f"/tmp/{timestamp}.jpg"

        picam2.capture_file(file_path)  # 使用picamera2拍照
        msg.reply_image(file_path)  # 直接回复发送图片
        print("照片已发送")
    else:
        # 其他指令处理
        pass


bot.join()  # 阻塞线程（wxpy写法）或 bot.join()