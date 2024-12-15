import cv2
import os
import numpy as np
from tqdm import tqdm

# 视频文件路径，替换成你实际的webm视频文件名
video_path = "res/阿米娅-默认-基建-Relax-x1.webm"
# 输出图片的文件夹路径
output_folder = "res/amiya_frames/relax"

# 确保输出文件夹存在
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 打开视频文件
cap = cv2.VideoCapture(video_path)
frame_count = 0
frame_skip = 1  # 每隔1帧处理一帧

# 定义纯绿色的HSV范围（这里的范围可能需要根据实际视频微调）
lower_green1 = np.array([35, 100, 100])
upper_green1 = np.array([85, 255, 255])

# 获取视频总帧数
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# 使用tqdm显示进度条
pbar = tqdm(total=total_frames // frame_skip, desc="Processing frames")

# 循环直到视频结束
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 跳过帧
    if frame_count % frame_skip != 0:
        frame_count += 1
        continue

    # 将BGR转换为HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 创建掩码，纯绿色区域为白色，其他为黑色
    mask = cv2.inRange(hsv, lower_green1, upper_green1)

    # 将BGR转换为BGRA
    bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

    # 将掩码应用到BGRA图像的Alpha通道
    bgra[:, :, 3] = np.where(mask == 255, 0, 255)

    # 构建每一帧的文件名
    frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.png")

    # 保存帧为PNG格式，保留透明背景
    cv2.imwrite(frame_filename, bgra, [cv2.IMWRITE_PNG_COMPRESSION, 9])

    # 更新帧计数和进度条
    frame_count += 1
    pbar.update(1)

# 释放视频捕获对象
cap.release()
pbar.close()
