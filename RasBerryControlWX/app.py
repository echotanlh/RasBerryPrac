from wxpy import Bot
from picamera2 import Picamera2
import time
import os

# 初始化微信机器人（扫码登录）
bot = Bot()
friend = bot.friends().search('孤烟')[0]  # 替换为实际好友备注

# 初始化摄像头
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1024, 768)})
picam2.configure(config)

@bot.register(friend, msg_types='Text')
def handle_message(msg):
    if msg.text == '拍照':
        try:
            picam2.start()
            time.sleep(1)  # 等待摄像头稳定
            img_path = f"/home/pi/images/{int(time.time())}.jpg"
            picam2.capture_file(img_path)
            msg.reply_image(img_path)  # 发送照片到微信
            os.remove(img_path)  # 清理临时文件
        except Exception as e:
            msg.reply(f"拍照失败: {str(e)}")
        finally:
            picam2.stop()

# 保持运行
bot.join()