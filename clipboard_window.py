import sys
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                           QWidget, QHBoxLayout, QPushButton, QLabel, QMenu)
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtGui import QFont, QColor, QCursor

class ResizableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 5
        self.oldPos = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            if pos.x() <= self.resize_margin:  # 左边缘
                self.resizing = True
                self.resize_edge = 'left'
                self.setCursor(QCursor(Qt.SizeHorCursor))
            elif pos.x() >= self.width() - self.resize_margin:  # 右边缘
                self.resizing = True
                self.resize_edge = 'right'
                self.setCursor(QCursor(Qt.SizeHorCursor))
            elif pos.y() <= self.resize_margin:  # 上边缘
                self.resizing = True
                self.resize_edge = 'top'
                self.setCursor(QCursor(Qt.SizeVerCursor))
            elif pos.y() >= self.height() - self.resize_margin:  # 下边缘
                self.resizing = True
                self.resize_edge = 'bottom'
                self.setCursor(QCursor(Qt.SizeVerCursor))
            else:
                self.oldPos = event.globalPos()
                self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseMoveEvent(self, event):
        if self.resizing:
            if self.resize_edge == 'right':
                width = event.pos().x()
                if width >= self.parent().minimumWidth():
                    self.parent().resize(width, self.parent().height())
            elif self.resize_edge == 'bottom':
                height = event.pos().y()
                if height >= self.parent().minimumHeight():
                    self.parent().resize(self.parent().width(), height)
            elif self.resize_edge == 'left':
                width = self.parent().width() - event.pos().x()
                if width >= self.parent().minimumWidth():
                    self.parent().resize(width, self.parent().height())
                    self.parent().move(self.parent().x() + event.pos().x(), self.parent().y())
            elif self.resize_edge == 'top':
                height = self.parent().height() - event.pos().y()
                if height >= self.parent().minimumHeight():
                    self.parent().resize(self.parent().width(), height)
                    self.parent().move(self.parent().x(), self.parent().y() + event.pos().y())
        elif self.oldPos is not None:
            delta = event.globalPos() - self.oldPos
            self.parent().move(self.parent().pos() + delta)
            self.oldPos = event.globalPos()
        else:
            pos = event.pos()
            if pos.x() <= self.resize_margin or pos.x() >= self.width() - self.resize_margin:
                self.setCursor(QCursor(Qt.SizeHorCursor))
            elif pos.y() <= self.resize_margin or pos.y() >= self.height() - self.resize_margin:
                self.setCursor(QCursor(Qt.SizeVerCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseReleaseEvent(self, event):
        self.oldPos = None
        self.resizing = False
        self.resize_edge = None
        self.setCursor(QCursor(Qt.ArrowCursor))

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
        self.setWindowTitle('重点内容')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(200, 150)  # 设置最小尺寸
        
        # 创建中心部件和布局
        central_widget = ResizableWidget(self)
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
        title_label = QLabel("重点内容")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # 添加设置按钮
        settings_button = QPushButton("⚙")
        settings_button.setFixedSize(20, 20)
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        settings_button.clicked.connect(self.show_size_menu)
        title_layout.addWidget(settings_button)
        
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
                color: red;
            }
        """)
        self.text_edit.setFont(QFont('Arial', 18))
        content_layout.addWidget(self.text_edit)
        
        # 添加所有部件到主布局
        main_layout.addWidget(title_bar)
        main_layout.addWidget(content_widget)
        
        # 设置窗口大小和位置
        self.setGeometry(0, 0, 300, 200)
        
    def show_size_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #34495e;
            }
        """)
        
        small_action = menu.addAction("小窗口 (200x150)")
        medium_action = menu.addAction("中窗口 (400x300)")
        large_action = menu.addAction("大窗口 (600x400)")
        
        action = menu.exec_(self.mapToGlobal(self.rect().topRight() + QPoint(-100, 30)))
        
        if action == small_action:
            self.resize(300, 200)
        elif action == medium_action:
            self.resize(400, 300)
        elif action == large_action:
            self.resize(600, 400)
        
    def check_clipboard(self):
        try:
            content = pyperclip.paste()
            if content != self.last_content:
                self.last_content = content
                self.text_edit.setText(content)
        except Exception as e:
            print(f"获取剪贴板内容时出错：{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClipboardWindow()
    window.show()
    sys.exit(app.exec_()) 