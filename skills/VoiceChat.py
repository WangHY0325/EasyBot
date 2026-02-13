import os
import sys
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
from PySide6.QtWidgets import QPushButton, QMessageBox
from PySide6.QtCore import QThread, Signal, Qt

# 屏蔽 Vosk 底层日志
SetLogLevel(-1)


class VoiceThread(QThread):
    result_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.running = False
        self.q = queue.Queue()

    def run(self):
        try:
            if not os.path.exists(self.model_path):
                self.error_occurred.emit(f"模型路径不存在: {self.model_path}")
                return

            try:
                model = Model(self.model_path)
            except Exception as e:
                self.error_occurred.emit(f"模型加载失败！\n路径: {self.model_path}\n原因: Vosk无法找到conf/am文件。")
                return

            rec = KaldiRecognizer(model, 16000)

            def callback(indata, frames, time, status):
                if status:
                    print(status, file=sys.stderr)
                self.q.put(bytes(indata))

            with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None,
                                   dtype='int16', channels=1, callback=callback):
                self.running = True

                # 循环直到外部调用 stop()
                while self.running:
                    try:
                        # 设置超时，保证 loop 能有机会检查 self.running 状态
                        data = self.q.get(timeout=1.0)

                        if rec.AcceptWaveform(data):
                            # 识别出一句完整的话
                            res = json.loads(rec.Result())
                            text = res.get('text', '').replace(' ', '')
                            if text:
                                self.result_ready.emit(text)
                                # 🔥这里改了：识别完一句不要停，继续听下一句

                    except queue.Empty:
                        pass  # 队列空了继续循环

        except Exception as e:
            self.error_occurred.emit(f"录音异常: {str(e)}")

    def stop(self):
        self.running = False


class VoiceButton(QPushButton):
    """自定义语音按钮组件 - 开关模式"""
    text_captured = Signal(str)

    def __init__(self, parent=None):
        super().__init__("🎤", parent)
        self.setFixedSize(40, 40)

        # 设置为可选中模式 (Toggle)
        self.setCheckable(True)

        # 默认样式
        self.default_style = """
            QPushButton { background-color: #fff; border: 1px solid #ccc; border-radius: 20px; font-size: 18px; }
            QPushButton:hover { border-color: #1890ff; background-color: #f0f5ff; }
        """
        # 录音中样式 (红色闪烁感)
        self.recording_style = """
            QPushButton { background-color: #ff4d4f; border: 2px solid #d9363e; color: white; border-radius: 20px; font-size: 18px;}
        """

        self.setStyleSheet(self.default_style)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("点击开始录音，再次点击停止")

        # 智能查找路径
        self.model_path = self._find_smart_model_path()
        self.thread = None

        # 连接点击事件 (toggled 信号会携带 true/false 状态)
        self.toggled.connect(self.on_toggle)

    def _find_smart_model_path(self):
        """智能查找模型路径"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        root_model_dir = os.path.join(base_dir, "model")

        if not os.path.exists(root_model_dir):
            return root_model_dir

        if os.path.exists(os.path.join(root_model_dir, "conf")):
            return root_model_dir

        try:
            for item in os.listdir(root_model_dir):
                sub_path = os.path.join(root_model_dir, item)
                if os.path.isdir(sub_path):
                    if os.path.exists(os.path.join(sub_path, "conf")):
                        return sub_path
        except:
            pass
        return root_model_dir

    def on_toggle(self, checked):
        """根据按钮状态决定是开始还是停止"""
        if checked:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        if not self.model_path or not os.path.exists(os.path.join(self.model_path, "conf")):
            self.setChecked(False)  # 弹起按钮
            QMessageBox.critical(self, "模型错误", f"无法加载模型！请检查路径:\n{self.model_path}")
            return

        self.setStyleSheet(self.recording_style)
        # 启动线程
        if not self.thread:
            self.thread = VoiceThread(self.model_path)
            self.thread.result_ready.connect(self.on_result)
            self.thread.error_occurred.connect(self.on_error)
            self.thread.start()

    def stop_listening(self):
        self.setStyleSheet(self.default_style)
        # 停止线程
        if self.thread:
            self.thread.stop()
            self.thread.wait()
            self.thread = None

    def on_result(self, text):
        if text:
            # 发送文字，launcher.py 会自动拼接到输入框后面
            self.text_captured.emit(text)

    def on_error(self, err_msg):
        self.setChecked(False)  # 发生错误自动弹起按钮
        self.stop_listening()
        if "Stream closed" not in err_msg:
            QMessageBox.warning(self, "语音出错", err_msg)
