import json
import subprocess
import sys
import pygame  # 播放声音
from PyQt5.QtCore import QTimer, Qt, QDateTime, pyqtSignal, QProcess
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDesktopWidget, QWidget, QPushButton, QFileDialog, \
    QMessageBox, QLineEdit, qApp
import os
import random


def get_model_path():
    settings_file_path = "settings.json"
    default_path = "res/rosmontis_frames"
    try:
        with open(settings_file_path, 'r') as file:
            settings = json.load(file)
            return settings.get("model_path", default_path)
    except FileNotFoundError:
        print(f"settings.json file not found, using default path: {default_path}")
        return default_path
    except json.JSONDecodeError:
        print("Error decoding settings.json file, using default path")
        return default_path


model_path = get_model_path()


# 设置窗口的类
class SettingsWindow(QWidget):

    closed = pyqtSignal()

    def __init__(self, global_model_path, main_window):
        super().__init__()
        self.global_model_path = global_model_path  # 将全局变量作为属性存储
        self.main_window = main_window  # 添加对主窗口的引用
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                position: relative;
                width: 300px;
                height: 200px;
                background-color: white;
                border-radius: 20px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
            }
            QPushButton {
                padding: 5px;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
                transition: background-color 0.3s;
            }
        """)
        self.close_button = QPushButton("X", self)
        self.close_button.setGeometry(280, 5, 20, 20)
        self.close_button.clicked.connect(self.close)

        self.change_model_button = QPushButton("更改Model", self)
        self.change_model_button.setGeometry(25, 80, 250, 40)

        # 添加一个打开任务管理器的按钮
        self.open_task_manager_button = QPushButton("打开任务管理器", self)
        self.open_task_manager_button.setGeometry(25, 130, 250, 40)  # 根据需要调整位置和大小
        self.open_task_manager_button.clicked.connect(self.open_task_manager)
        self.change_model_button.clicked.connect(self.open_folder_dialog)

        # 添加一个打开桌面文件夹的按钮
        self.open_desktop_button = QPushButton("打开桌面文件夹", self)
        self.open_desktop_button.setGeometry(25, 180, 250, 40)  # 根据需要调整位置和大小
        self.open_desktop_button.clicked.connect(self.open_desktop)

        # 添加自定义启动路径输入框
        self.custom_path_input = QLineEdit(self)
        self.custom_path_input.setGeometry(25, 230, 200, 40)
        self.load_custom_path()  # 加载自定义路径

        # 添加Start按钮
        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(225, 230, 60, 40)
        self.start_button.clicked.connect(self.start_custom_path)

        # 添加静音按钮
        self.mute_button = QPushButton("Mute", self)
        self.mute_button.setGeometry(25, 280, 250, 40)
        self.mute_button.clicked.connect(self.toggle_mute)
        self.load_mute_status()  # 加载静音状态

        # 添加关闭按钮
        self.close_button = QPushButton("关闭", self)
        self.close_button.setGeometry(25, 330, 250, 40)
        self.close_button.clicked.connect(self.close_main_window)

        self.auto_movement_button = QPushButton("自动行走", self)
        self.auto_movement_button.setGeometry(25, 380, 250, 40)
        self.auto_movement_button.clicked.connect(self.toggle_auto_movement)
        self.load_auto_movement_status()

    def open_desktop(self):
        # 使用QProcess.startDetached来启动文件管理器打开桌面文件夹
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        QProcess.startDetached('explorer.exe', [desktop_path])

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", self.global_model_path)
        if folder_path:
            print("选择的文件夹路径：", folder_path)
            self.global_model_path = folder_path  # 更新属性
            self.save_settings()  # 保存设置到JSON文件

    def open_task_manager(self):
        # 使用QProcess.startDetached来启动任务管理器
        QProcess.startDetached("C:/Windows/System32/taskmgr.exe")

    def save_settings(self):
        settings = {"model_path": self.global_model_path}
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        self.show_settings_saved_prompt()

    def show_settings_saved_prompt(self):
        prompt = QMessageBox(self)
        prompt.setWindowTitle("设置已保存")
        prompt.setText("设置已保存，正在重启程序...")
        prompt.setIcon(QMessageBox.Information)
        prompt.setStandardButtons(QMessageBox.Ok)
        prompt.exec_()
        self.restart_app()

    def load_custom_path(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                custom_path = settings.get('custom_path1', '')
                self.custom_path_input.setText(custom_path)
        except FileNotFoundError:
            self.custom_path_input.setText('')

    def start_custom_path(self):
        custom_path = self.custom_path_input.text()
        self.save_custom_path(custom_path)
        # 这里添加启动程序的代码
        # 使用subprocess.Popen执行程序，不阻塞当前线程
        process = subprocess.Popen(custom_path, shell=True)

    def save_custom_path(self, custom_path):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}

        settings['custom_path1'] = custom_path
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_mute_status(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                is_mute = settings.get('is_Mute', True)
                self.mute_button.setText("Mute" if is_mute else "Play Bgm")
        except FileNotFoundError:
            self.mute_button.setText("Default")

    def toggle_mute(self):
        is_mute = not self.mute_button.text() == "Play Bgm"
        self.save_mute_status(is_mute)
        if is_mute:
            pygame.mixer.music.pause()  # 暂停音乐
            self.mute_button.setText("Play Bgm")
        else:
            pygame.mixer.music.unpause()  # 恢复音乐
            self.mute_button.setText("Mute")

    def save_mute_status(self, is_mute):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}

        settings['is_Mute'] = is_mute
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_auto_movement_status(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                enabled_auto_movement = settings.get('enabled_auto_movement', True)
                self.auto_movement_button.setText("已启用自动行走" if enabled_auto_movement else "已禁用自动行走")
        except FileNotFoundError:
            self.auto_movement_button.setText("已默认启用自动行走")

    def toggle_auto_movement(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            settings['enabled_auto_movement'] = not settings.get('enabled_auto_movement', True)
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            self.auto_movement_button.setText(
                "已禁用自动行走" if not settings['enabled_auto_movement'] else "已启用自动行走")
            self.restart_app()
        except FileNotFoundError:
            settings = {'enabled_auto_movement': False}
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            self.auto_movement_button.setText("已启用自动行走")
            self.restart_app()
    def restart_app(self):
        # 获取当前脚本的绝对路径
        script_path = os.path.abspath(__file__)
        # 构造启动参数，包括脚本路径和命令行参数
        arguments = sys.argv[:]
        # 使用QProcess.startDetached来重启当前应用程序
        QProcess.startDetached(sys.executable, [script_path] + arguments)
        # 使用QTimer.singleShot来延迟关闭当前进程，以便新进程有足够的时间启动
        QTimer.singleShot(1000, qApp.quit)

    def close_app(self):
        # 关闭当前窗口
        qApp.quit()  # 使用qApp.quit()来安全地退出应用程序

    def close_main_window(self):
        self.main_window.close_app()  # 调用主窗口的关闭方法

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()


class VideoPlayer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.load_settings()  # 加载设置
        self.interact_count = self.load_interact_count()  # 加载interact事件的计数
        self.init_player(f'{model_path}/start')
        self.idle_folder_path = f'{model_path}/idle'
        self.interact_folder_path = f'{model_path}/interact'
        self.move_folder_path = f'{model_path}/move'
        self.stun_folder_path = f'{model_path}/stun'  # 添加stun动作的文件夹路径
        self.sleep_folder_path = f'{model_path}/sleep'  # 添加sleep动作的文件夹路径
        self.relax_folder_path = f'{model_path}/relax'  # 添加relax动作的文件夹路径
        self.settings_window = None  # 用于存储设置窗口的引用

        # 初始化鼠标拖拽相关变量
        self.drag_position = None

        # 加载静音状态并应用
        self.load_mute_status()

        # 初始化pygame的音频模块
        pygame.mixer.init()

        # 设置背景音乐音量
        bgm_volume = 0.1  # 设置背景音乐音量为10%
        pygame.mixer.music.set_volume(bgm_volume)

        # 加载背景音乐文件
        bgm_path = f'{model_path}/sound/bgm.wav'
        pygame.mixer.music.load(bgm_path)  # 加载背景音乐

        # 播放背景音乐
        pygame.mixer.music.play(-1)  # 循环播放

        # 加载启动音效文件
        start_sound_path = f'{model_path}/sound/start.wav'
        start_sound = pygame.mixer.Sound(start_sound_path)  # 加载启动音效

        # 播放启动音效
        start_sound.play()  # 播放一次启动音效

        # 获取屏幕尺寸
        available_geometry = QDesktopWidget().availableGeometry(self)
        self.screen_width = available_geometry.width()
        self.screen_height = available_geometry.height()

        # 初始化动作状态和位置
        self.current_action = 'start'
        self.is_idle_animation = False
        self.x_position = 100
        self.move_distance = 1  # 减少每次移动的距离
        self.last_move_time = 0  # 记录最后一次进入move状态的时间
        self.last_user_action_time = QDateTime.currentMSecsSinceEpoch()  # 上次用户操作的时间
        self.stun_timer = QTimer(self)  # 用于计时进入stun状态的定时器
        self.stun_timer.timeout.connect(self.check_stun_state)
        self.stun_timer.start(60000)  # 每分钟检查一次

        self.init_player(f'{model_path}/start')
        self.set_frame_rate(60)  # 降低帧率

    def load_mute_status(self):
        try:
            pygame.mixer.init()
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                is_mute = settings.get('is_Mute', False)
                if is_mute:
                    pygame.mixer.music.pause()  # 暂停音乐
                else:
                    pygame.mixer.music.unpause()  # 恢复音乐
        except FileNotFoundError:
            pass  # 如果没有设置文件，不执行任何操作

    def load_interact_count(self):
        try:
            with open('easter_egg.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('interact_count', 0)
        except FileNotFoundError:
            # 如果文件不存在，则创建文件并初始化interact_count
            with open('easter_egg.json', 'w', encoding='utf-8') as f:
                json.dump({'interact_count': 0, 'easter_eggs': []}, f)
            return 0

    def save_interact_count(self):
        try:
            with open('easter_egg.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {'interact_count': 0, 'easter_eggs': []}

        data['interact_count'] = (data.get('interact_count', 0) + 1) % 20  # 累加并取模以循环
        if data['interact_count'] == 0:
            self.send_easter_egg()

        with open('easter_egg.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)

# 彩蛋部分开始
    def send_easter_egg(self):
        try:
            with open('easter_egg.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                egg_texts = data['easter_eggs']
                chosen_egg = random.choice(egg_texts)
                # 保存到桌面
                desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                filename = 'rosmontis【Experiment Files】.txt'
                file_path = os.path.join(desktop_path, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(chosen_egg['title'] + '\n\n' + chosen_egg['content'])

        except FileNotFoundError:
            print("easter_egg.json 文件未找到。")

# 菜单部分截止


    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.model_path = settings['model_path']
                self.enabled_auto_movement = settings.get('enabled_auto_movement', True)
        except FileNotFoundError:
            self.model_path = model_path
            self.enabled_auto_movement = True  # 默认值为True

# TODO: 进入 STUN 状态 和 进入 SLEEP 状态的时间参数
    def check_stun_state(self):
        current_time = QDateTime.currentMSecsSinceEpoch()
        time_diff = current_time - self.last_user_action_time
        if self.current_action != 'stun' and self.current_action != 'sleep':
            if time_diff > 30000:  # 30s转换到stun状态
                self.current_action = 'stun'
                start_sound_path = f'{model_path}/sound/stun.wav'
                start_sound = pygame.mixer.Sound(start_sound_path)
                start_sound.play()
                self.init_stun_player()
        elif self.current_action == 'stun' and time_diff > 60000:  # 1min转换到sleep状态
            self.current_action = 'sleep'
            self.init_sleep_player()

    def init_player(self, folder_path):
        self.setWindowTitle("Desktop Pet")
        self.setGeometry(1000, 500, 700, 800)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.label = QLabel(self)
        self.label.resize(700, 800)
        self.label.move(100, 100)
        self.frame_files = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.png')])
        self.current_frame = 0
        self.set_frame_rate(15)  # 降低帧率

    def mousePressEvent(self, event: QMouseEvent):
        # 用户点击时，首先重置计时器
        self.last_user_action_time = QDateTime.currentMSecsSinceEpoch()

        if event.button() == Qt.RightButton:    # 鼠标触发relax动作
            self.current_action = 'relax'
            # 加载启动音效文件
            start_sound_path = f'{model_path}/sound/settings.wav'
            start_sound = pygame.mixer.Sound(start_sound_path)  # 加载启动音效

            # 播放启动音效
            start_sound.play()  # 播放一次启动音效

            self.init_relax_player()
            self.show_settings_window() # 显示设置窗口

        elif self.current_action == 'stun' or self.current_action == 'sleep':
            # 如果宠物处于 stun 或 sleep 状态，通过点击事件唤醒宠物
            self.current_action = 'idle'

            # 加载启动音效文件
            start_sound_path = f'{model_path}/sound/wakeup.wav'
            start_sound = pygame.mixer.Sound(start_sound_path)  # 加载启动音效

            # 播放启动音效
            start_sound.play()  # 播放一次启动音效

            self.init_idle_player()
        elif event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.x_position = event.globalX() - self.frameGeometry().left()  # 更新x_position
            if self.current_action == 'idle':
                self.current_action = 'interact'
                self.save_interact_count()

                # 加载启动音效文件
                start_sound_path = f'{model_path}/sound/interact.wav'
                start_sound = pygame.mixer.Sound(start_sound_path)  # 加载启动音效

                # 播放启动音效
                start_sound.play()  # 播放一次启动音效

                self.init_interact_player()
        elif event.button() == Qt.MidButton:  # 鼠标中键触发move动作
            if not (self.current_action == 'stun' or self.current_action == 'sleep'):
                self.current_action = 'move'
                self.init_move_player()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            self.x_position = event.globalX() - self.frameGeometry().left()  # 更新x_position
            event.accept()

    def set_frame_rate(self, fps):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        interval = int(1000 / fps) if fps > 0 else 1000
        self.timer.start(interval)

    def update_frame(self):
        if self.current_action == 'idle':
            self.update_idle_frame()
        elif self.current_action == 'start':
            self.update_start_frame()
        elif self.current_action == 'interact':
            self.update_interact_frame()
        elif self.current_action == 'move':
            self.update_move_frame()
        elif self.current_action == 'stun':
            self.update_stun_frame()
        elif self.current_action == 'sleep':
            self.update_sleep_frame()
        elif self.current_action == 'relax':
            self.update_relax_frame()  # 添加relax状态的帧更新

    def update_start_frame(self):
        if self.current_frame >= len(self.frame_files):
            self.current_action = 'idle'
            self.init_idle_player()
            return

        frame_path = self.frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def update_idle_frame(self):
        if self.current_frame >= len(self.idle_frame_files):
            self.current_frame = 0

        frame_path = self.idle_frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

        # 检查是否可以进入move状态
        if self.x_position + 100 < self.screen_width and random.random() < 0.001:
            if not self.enabled_auto_movement:
                self.current_action = 'idle'
                return
            if QDateTime.currentMSecsSinceEpoch() - self.last_move_time > 5000:  # 5秒内只允许进入一次move状态
                self.current_action = 'move'
                self.init_move_player()
                self.last_move_time = QDateTime.currentMSecsSinceEpoch()

    def update_interact_frame(self):
        if self.current_frame >= len(self.interact_frame_files):
            self.current_action = 'idle'
            self.init_idle_player()
            return

        frame_path = self.interact_frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def update_move_frame(self):
        # if not self.enabled_auto_movement:
        #     self.current_action = 'idle'
        #     return
        if self.current_frame >= len(self.move_frame_files):
            self.current_frame = 0
            self.current_action = 'idle'
            self.init_idle_player()
            return

        frame_path = self.move_frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

        # 移动宠物
        target_x = self.x_position + self.move_distance;
        self.x_position = target_x  # 允许桌宠在整个屏幕上移动

        # 移动窗体以跟随宠物
        self.move(self.x_position - self.width() // 2 + self.label.width() // 2, self.y())

    def update_stun_frame(self):
        if self.current_frame >= len(self.stun_frame_files):
            self.current_frame = 0

        frame_path = self.stun_frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def update_sleep_frame(self):
        if self.current_frame >= len(self.sleep_frame_files):
            self.current_frame = 0

        frame_path = self.sleep_frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def update_relax_frame(self):
        if self.current_frame >= len(self.relax_frame_files):
            self.current_frame = 0

        frame_path = self.relax_frame_files[self.current_frame]
        self.current_frame += 1

        image = QImage(frame_path)
        scaled_image = image.scaled(350, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.label.setPixmap(pixmap)

    def show_settings_window(self):
        if not self.settings_window or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(self.model_path, self)  # 传递self作为主窗口的引用
            self.settings_window.closed.connect(self.on_settings_window_closed)  # 连接信号
            self.settings_window.show()

    def on_settings_window_closed(self):
        self.current_action = 'idle'
        self.init_idle_player()

    def init_idle_player(self):
        self.idle_frame_files = sorted([os.path.join(self.idle_folder_path, f) for f in os.listdir(self.idle_folder_path) if f.endswith('.png')])
        self.current_frame = 0

    def init_interact_player(self):
        self.interact_frame_files = sorted([os.path.join(self.interact_folder_path, f) for f in os.listdir(self.interact_folder_path) if f.endswith('.png')])
        self.current_frame = 0

    def init_move_player(self):
        self.move_frame_files = sorted([os.path.join(self.move_folder_path, f) for f in os.listdir(self.move_folder_path) if f.endswith('.png')])
        self.current_frame = 0

    def init_stun_player(self):
        self.stun_frame_files = sorted(
            [os.path.join(self.stun_folder_path, f) for f in os.listdir(self.stun_folder_path) if f.endswith('.png')])
        self.current_frame = 0

    def init_sleep_player(self):
        self.sleep_frame_files = sorted(
            [os.path.join(self.sleep_folder_path, f) for f in os.listdir(self.sleep_folder_path) if f.endswith('.png')])
        self.current_frame = 0

    def init_relax_player(self):
        self.relax_frame_files = sorted(
            [os.path.join(self.relax_folder_path, f) for f in os.listdir(self.relax_folder_path) if f.endswith('.png')])
        self.current_frame = 0

    def closeEvent(self, event):
        super().closeEvent(event)
        pygame.mixer.music.stop()  # 停止音频播放


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())