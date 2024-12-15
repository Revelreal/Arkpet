import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import os


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_player('res/rosmontis_frames/start')  # 初始播放进场动画

    def init_player(self, folder_path):
        self.setWindowTitle("Desktop Pet")
        self.setGeometry(1000, 500, 700, 800)  # 调整窗口大小
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.label = QLabel(self)
        self.label.resize(700, 800)  # 调整标签大小以匹配窗口
        self.label.move(100, 100)  # 调整标签位置以居中
        self.frame_files = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.png')])
        self.current_frame = 0
        self.set_frame_rate(30)  # 设置帧率为30fps

    def set_frame_rate(self, fps):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        interval = int(1000 / fps) if fps > 0 else 1000  # 防止除以零
        self.timer.start(interval)  # 设置定时器间隔

    def update_frame(self):
        if self.current_frame >= len(self.frame_files):
            self.current_frame = 0  # 如果到达文件列表末尾，重新开始
        frame_path = self.frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 缩放并保持纵横比
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
