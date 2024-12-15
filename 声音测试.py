import pygame

# 初始化pygame的音频模块
pygame.mixer.init()

# 加载音频文件
pygame.mixer.music.load('res/rosmontis_frames/sound/start.wav')

# 播放音频
pygame.mixer.music.play()

# 等待音频播放完成
import time
time.sleep(24)  # 根据音频长度调整等待时间