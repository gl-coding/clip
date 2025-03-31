import sys
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                           QWidget, QHBoxLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

class ClipboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_content = ""
        
        # 设置定时器，每秒检查一次剪贴板
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # 1000ms = 1秒
        
    def initUI(self):
        # 设置窗口基本属性
        self.setWindowTitle('剪贴板监控')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 添加标题文本
        title_label = QLabel("剪贴板监控")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # 添加关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        
        # 创建文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                padding: 10px;
            }
        """)
        self.text_edit.setFont(QFont('Arial', 10))
        content_layout.addWidget(self.text_edit)
        
        # 添加所有部件到主布局
        main_layout.addWidget(title_bar)
        main_layout.addWidget(content_widget)
        
        # 设置窗口大小和位置
        self.setGeometry(100, 100, 300, 200)
        
        # 添加鼠标事件处理
        self.oldPos = None
        title_bar.mousePressEvent = self.on_mouse_press
        title_bar.mouseMoveEvent = self.on_mouse_move
        title_bar.mouseReleaseEvent = self.on_mouse_release
        
    def check_clipboard(self):
        try:
            content = pyperclip.paste()
            if content != self.last_content:
                self.last_content = content
                self.text_edit.setText(content)
        except Exception as e:
            print(f"获取剪贴板内容时出错：{str(e)}")
    
    def on_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
    
    def on_mouse_move(self, event):
        if self.oldPos is not None:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()
    
    def on_mouse_release(self, event):
        self.oldPos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClipboardWindow()
    window.show()
    sys.exit(app.exec_()) 