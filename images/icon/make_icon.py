# make_icon.py - 用代码画一个漂亮的图标
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QLinearGradient, QBrush
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication
import sys


def generate_icon():
    app = QApplication(sys.argv)  # 字体渲染需要 App 实例

    size = 256
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)

    # 1. 画背景 (科技蓝渐变)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor("#40a9ff"))  # 亮蓝
    gradient.setColorAt(1.0, QColor("#096dd9"))  # 深蓝

    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.NoPen)
    # 画一个圆角矩形 (类似 iOS 图标)
    painter.drawRoundedRect(10, 10, size - 20, size - 20, 50, 50)

    # 2. 画文字 "EB"
    painter.setPen(QColor("white"))
    # 尝试使用粗体字
    font = QFont("Arial", 110, QFont.Bold)
    font.setStyleStrategy(QFont.PreferAntialias)
    painter.setFont(font)
    painter.drawText(img.rect(), Qt.AlignCenter, "EB")

    painter.end()

    # 保存为 ico 格式
    img.save("icon.ico")
    print("✅ 图标生成成功！已保存为 icon.ico")


if __name__ == "__main__":
    generate_icon()
