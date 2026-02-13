import sys
import os
import json
import re
import io
import html
import markdown
import shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox, QGroupBox, QTextBrowser, QFrame,
                               QComboBox, QSizePolicy)
from PySide6.QtGui import QFont, QColor, QPalette, QTextCursor, QIcon
from PySide6.QtCore import Qt, QProcess, QProcessEnvironment, QTimer

import importlib.metadata

# ==========================================
#   🛡️ 核心修复：强制使用 UTF-8 编码
#   解决 Windows 下打印 ✅ 🔥 等 Emoji 报错的问题
# ==========================================
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
# ==========================================

# ==========================================
#   🔥 新增：从 model_api 文件夹导入配置
# ==========================================
try:
    from model_api.settings import DEFAULT_MODELS, MODELS_CONFIG
except ImportError as e:
    print(f" 错误: 无法导入模型配置，请检查 model_api 文件夹是否存在。详细信息: {e}")
    DEFAULT_MODELS = {}
    MODELS_CONFIG = {}

# ==========================================
#   🎤 核心修改：导入语音模块 (Vosk)
# ==========================================
try:
    # 动态将 skills 文件夹加入搜索路径，确保能找到 VoiceChat
    current_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.join(current_dir, "skills")
    if skills_dir not in sys.path:
        sys.path.append(skills_dir)

    from skills.VoiceChat import VoiceButton

    print("语音模块加载成功 (Vosk)")
except ImportError as e:
    print(f"无法加载语音模块: {e}")
    print("提示: 请确保 skills/VoiceChat.py 存在且已安装 vosk 库")
    VoiceButton = None

_original_version = importlib.metadata.version


def _fake_version(distribution_name):
    if distribution_name == "nanobot": return "1.0.0"
    return _original_version(distribution_name)


importlib.metadata.version = _fake_version

# ==========================================
#   配置与常量
# ==========================================
CONFIG_DIR = Path.home() / ".easybot"
if not CONFIG_DIR.exists(): CONFIG_DIR.mkdir(parents=True)
PROFILES_FILE = CONFIG_DIR / "profiles.json"
NANOBOT_CONFIG = Path.home() / ".nanobot" / "config.json"
SESSION_FILE = Path.home() / ".nanobot" / "sessions" / "cli_direct.jsonl"
SESSION_BAK = Path.home() / ".nanobot" / "sessions" / "cli_direct.jsonl.bak"
LOGS_DIR = CONFIG_DIR / "logs"
if not LOGS_DIR.exists(): LOGS_DIR.mkdir(parents=True)

STYLESHEET = """
QWidget { background-color: #f5f5f5; font-family: "Microsoft YaHei", sans-serif; color: #333; }
QFrame#LeftPanel { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
QLabel#Title { font-size: 22px; font-weight: bold; color: #333; margin: 20px 0; }
QPushButton.ModelBtn { text-align: left; padding: 12px 16px; border: 1px solid transparent; border-radius: 8px; font-size: 14px; color: #555; margin-bottom: 4px; background-color: transparent; }
QPushButton.ModelBtn:hover { background-color: #f0f0f0; }
QPushButton.ModelBtn:checked { background-color: #e8f4ff; color: #1890ff; font-weight: bold; }
QLineEdit, QComboBox { padding: 8px; border: 1px solid #ddd; border-radius: 6px; background-color: #fff; font-size: 13px; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #1890ff; }
QPushButton#StartBtn { background-color: #07c160; color: white; font-size: 15px; font-weight: bold; padding: 12px; border-radius: 8px; border: none; margin-top: 20px; }
QPushButton#StartBtn:hover { background-color: #06ad56; }
QPushButton#StartBtn:disabled { background-color: #ccc; }
QPushButton#StartBtn[running="true"] { background-color: #fa5151; }
QPushButton#StartBtn[running="true"]:hover { background-color: #e04848; }
QTextBrowser#ChatArea { background-color: #ffffff; border: none; padding: 25px; font-size: 15px; line-height: 1.6; }
"""


class EasyBotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyBot AI v0.3 (Voice Enabled)")
        self.resize(1100, 760)
        self.setup_icon()

        self.process = None
        # 防止配置为空导致报错
        if not MODELS_CONFIG:
            QMessageBox.critical(self, "配置错误", "无法加载模型配置 (model_api/settings.py)。\n请检查文件是否丢失。")
            self.current_model_provider = ""
        else:
            self.current_model_provider = list(MODELS_CONFIG.keys())[0]

        self.profiles = self.load_profiles()
        self.auth_error_detected = False

        self.setup_ui()
        self.setStyleSheet(STYLESHEET)

        if self.current_model_provider:
            self.on_provider_select(self.current_model_provider)

    def setup_icon(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def load_profiles(self):
        if PROFILES_FILE.exists():
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_profiles(self):
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f: json.dump(self.profiles, f, indent=2)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Left Panel ===
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_panel.setFixedWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)

        left_layout.addWidget(QLabel("🤖 EasyBot", objectName="Title"))

        self.provider_btns = []
        for name in MODELS_CONFIG:
            btn = QPushButton(name)
            btn.setProperty("class", "ModelBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda c, n=name: self.on_provider_select(n))
            left_layout.addWidget(btn)
            self.provider_btns.append(btn)

        left_layout.addStretch()

        # === Config Area ===
        self.config_group = QGroupBox("模型配置")
        config_layout = QVBoxLayout()
        config_layout.setSpacing(10)

        self.reg_link = QLabel()
        self.reg_link.setOpenExternalLinks(True)
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("在此粘贴 API Key")
        self.api_input.setEchoMode(QLineEdit.Normal)

        self.model_combo = QComboBox()
        self.model_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        save_btn = QPushButton("保存并应用")
        save_btn.clicked.connect(self.save_current_config)

        config_layout.addWidget(self.reg_link)
        config_layout.addWidget(self.api_input)
        config_layout.addWidget(QLabel("选择模型:", styleSheet="font-size:12px; color:#666; margin-top:5px;"))
        config_layout.addWidget(self.model_combo)
        config_layout.addWidget(save_btn)

        self.config_group.setLayout(config_layout)
        left_layout.addWidget(self.config_group)
        left_layout.addSpacing(10)

        self.start_btn = QPushButton("启动助手")
        self.start_btn.setObjectName("StartBtn")
        self.start_btn.clicked.connect(self.toggle_bot)
        left_layout.addWidget(self.start_btn)

        # === Right Panel ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.chat_view = QTextBrowser()
        self.chat_view.setObjectName("ChatArea")
        self.chat_view.setOpenExternalLinks(True)

        input_container = QFrame()
        input_container.setObjectName("InputContainer")
        input_layout = QHBoxLayout(input_container)

        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("请先配置并启动助手...")
        self.msg_input.setFixedHeight(45)
        self.msg_input.returnPressed.connect(self.send_msg)
        self.msg_input.setEnabled(False)

        self.send_btn = QPushButton("发送")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.clicked.connect(self.send_msg)
        self.send_btn.setEnabled(False)

        input_layout.addWidget(self.msg_input)

        # 🔥🔥🔥 核心修改：插入语音按钮 🔥🔥🔥
        if VoiceButton:
            # 添加一个小竖线分隔符
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("background-color: #ddd; margin: 5px;")
            input_layout.addWidget(line)

            # 实例化语音按钮
            self.voice_btn = VoiceButton()
            # 绑定信号：当语音识别出文字后，调用 on_voice_input
            self.voice_btn.text_captured.connect(self.on_voice_input)
            input_layout.addWidget(self.voice_btn)
        # 🔥🔥🔥 核心修改结束 🔥🔥🔥

        input_layout.addWidget(self.send_btn)

        right_layout.addWidget(self.chat_view)
        right_layout.addWidget(input_container)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def on_provider_select(self, name):
        self.current_model_provider = name
        if name not in MODELS_CONFIG: return

        cfg = MODELS_CONFIG[name]

        for btn in self.provider_btns:
            btn.setChecked(btn.text() == name)

        self.reg_link.setText(
            f"<a href='{cfg['reg_url']}' style='color:#1890ff; text-decoration:none;'>👉 获取 API Key</a>")

        saved_key = self.profiles.get(name, "")
        self.api_input.setText(saved_key)

        self.model_combo.clear()
        defaults = DEFAULT_MODELS.get(name, ["gpt-3.5-turbo"])
        self.model_combo.addItems(defaults)

        self.start_btn.setEnabled(bool(saved_key))

    # 🔥🔥 新增：处理语音识别结果 🔥🔥
    def on_voice_input(self, text):
        """当语音识别成功时触发，将文字填入输入框"""
        if not text: return

        current_text = self.msg_input.text()

        # 如果输入框里已经有字了，加个空格再追加
        if current_text:
            new_text = current_text + " " + text
        else:
            new_text = text

        self.msg_input.setText(new_text)
        self.msg_input.setFocus()

        # 如果您希望说完话自动发送，请取消下面这行的注释：
        # self.send_msg()

    def save_current_config(self):
        key = self.api_input.text().strip()
        if not key: return
        self.profiles[self.current_model_provider] = key
        self.save_profiles()
        self.start_btn.setEnabled(True)
        QMessageBox.information(self, "配置已保存", f"已保存配置！\n当前使用模型: {self.model_combo.currentText()}")

    def apply_config_to_nanobot(self):
        key = self.profiles.get(self.current_model_provider)
        if not key: return False

        selected_model = self.model_combo.currentText()
        if not selected_model: selected_model = "gpt-3.5-turbo"

        final_model_name = selected_model

        cfg_template = MODELS_CONFIG[self.current_model_provider]['template']
        json_str = json.dumps(cfg_template).replace("{KEY}", key).replace("{MODEL}", final_model_name)

        try:
            NANOBOT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
            with open(NANOBOT_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(json.loads(json_str), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.save_to_log(f"Config Error: {e}", "system")
            return False

    def backup_session(self):
        if SESSION_FILE.exists():
            try:
                shutil.copy2(SESSION_FILE, SESSION_BAK)
            except:
                pass

    def restore_session(self):
        if SESSION_BAK.exists():
            try:
                shutil.copy2(SESSION_BAK, SESSION_FILE)
                return True
            except:
                pass
        return False

    def toggle_bot(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished(1000)
            self.process = None
            self.reset_ui_state()
            self.save_to_log("System: Bot stopped.", "system")
        else:
            if self.apply_config_to_nanobot():
                self.start_process()

    def reset_ui_state(self):
        self.start_btn.setText("启动助手")
        self.start_btn.setProperty("running", "false")
        self.start_btn.style().unpolish(self.start_btn);
        self.start_btn.style().polish(self.start_btn)
        self.msg_input.setEnabled(False);
        self.send_btn.setEnabled(False)
        # 如果有语音按钮，停止时禁用
        if hasattr(self, 'voice_btn') and self.voice_btn:
            self.voice_btn.setEnabled(False)
        self.msg_input.setPlaceholderText("请先配置并启动助手...")

    def start_process(self):
        self.chat_view.clear()
        self.backup_session()
        self.auth_error_detected = False

        self.append_system_msg(f"正在启动 {self.current_model_provider} ({self.model_combo.currentText()}) ...")

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.SeparateChannels)
        env = QProcessEnvironment.systemEnvironment()

        env.insert("PYTHONUNBUFFERED", "1")
        env.insert("PYTHONIOENCODING", "utf-8")
        self.process.setProcessEnvironment(env)

        if getattr(sys, 'frozen', False):

            program = sys.executable

            arguments = ["--worker"]
        else:

            program = "python"  #
            arguments = ["-u", "nanobot", "agent"]

        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.on_process_end)
        self.process.start(program, arguments)

        self.start_btn.setText("停止助手")
        self.start_btn.setProperty("running", "true")
        self.start_btn.style().unpolish(self.start_btn);
        self.start_btn.style().polish(self.start_btn)
        self.msg_input.setEnabled(True);
        self.send_btn.setEnabled(True)
        # 启动时启用语音按钮
        if hasattr(self, 'voice_btn') and self.voice_btn:
            self.voice_btn.setEnabled(True)
        self.msg_input.setFocus()
        self.msg_input.setPlaceholderText("请输入您的问题...")

        QTimer.singleShot(1500, lambda: self.append_system_msg("启动成功，请开始对话吧！"))

    def read_stdout(self):
        data = self.process.readAllStandardOutput()
        text = self.decode_bytes(data)
        if "AuthenticationError" in text or "Incorrect API key" in text or "401" in text:
            self.auth_error_detected = True

        clean_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
        clean_text = re.sub(r'🐈', '', clean_text)
        clean_text = re.sub(r'Interactive mode \(Ctrl\+C to exit\)', '', clean_text)
        clean_text = re.sub(r'^You:\s*', '', clean_text, flags=re.MULTILINE)

        if clean_text.strip() and not clean_text.strip().startswith(">") and "Processing message" not in clean_text:
            self.append_ai_msg(clean_text)
            self.save_to_log(f"Bot: {clean_text.strip()}", "chat")

    def read_stderr(self):
        data = self.process.readAllStandardError()
        text = self.decode_bytes(data)
        if "AuthenticationError" in text or "Incorrect API key" in text or "401" in text:
            self.auth_error_detected = True
        self.save_to_log(text, "system")

    def decode_bytes(self, data):
        try:
            return bytes(data).decode('utf-8')
        except:
            return str(data)

    def send_msg(self):
        text = self.msg_input.text().strip()
        if not text: return
        self.append_user_msg(text)
        self.save_to_log(f"You: {text}", "chat")
        self.msg_input.clear()
        if self.process: self.process.write((text + "\n").encode('utf-8'))

    def on_process_end(self):
        self.reset_ui_state()
        self.append_system_msg("助手已断开")
        if self.auth_error_detected:
            if self.restore_session():
                QMessageBox.warning(self, "连接失败", "检测到 API Key 无效或认证失败。\n已自动回滚历史记录。")

    def append_user_msg(self, text):
        self.chat_view.append(
            f"<div style='font-weight:bold;color:#1890ff;margin-bottom:5px;'>You:</div><div style='margin-bottom:20px;'>{html.escape(text)}</div>")
        self.scroll_to_bottom()

    def append_ai_msg(self, text):
        text = re.sub(r'(我是|I am)\s+nanobot', '我是你的个人AI助手', text, flags=re.IGNORECASE)
        html_body = markdown.markdown(text, extensions=['fenced_code', 'tables'])
        self.chat_view.append(
            f"<div style='font-weight:bold;color:#fa8c16;margin-bottom:5px;'>Bot:</div><div style='margin-bottom:20px;'>{html_body}</div>")
        self.scroll_to_bottom()

    def append_system_msg(self, text):
        self.chat_view.append(f"<div style='text-align:center;color:#999;font-size:12px;margin:20px;'>— {text} —</div>")

    def scroll_to_bottom(self):
        self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum())

    def save_to_log(self, content, log_type="chat"):
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H:%M:%S")
        filename = LOGS_DIR / f"{log_type}_{today}.txt"
        line = f"[{timestamp}] {content}\n" if log_type == "chat" else content
        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(line)
        except:
            pass


def worker_entry():
    import sys
    import os

    try:
        import tiktoken_ext.openai_public
    except ImportError:
        pass

    try:
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    sys.argv = ["nanobot", "agent"]
    try:
        from nanobot.cli.commands import app
        app()
    except Exception as e:
        sys.stderr.write(f"FATAL: {e}\n")


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker_entry()
    else:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setFont(QFont("Microsoft YaHei", 10))
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = "icon.ico"
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        window = EasyBotWindow()
        window.show()
        sys.exit(app.exec())
