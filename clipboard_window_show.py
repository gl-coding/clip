import sys
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                           QWidget, QHBoxLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QClipboard

class ClipboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_content = ""
        self.last_selection = ""
        
        # 获取系统剪贴板
        self.clipboard = QApplication.clipboard()
        # 连接剪贴板信号
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        
        # 设置定时器检查选中文本
        self.selection_timer = QTimer()
        self.selection_timer.timeout.connect(self.check_selection)
        self.selection_timer.start(50)  # 每50毫秒检查一次
        
    def initUI(self):
        # 设置窗口基本属性
        self.setWindowTitle('文本监控')
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
        title_label = QLabel("文本监控")
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
        
    def on_clipboard_change(self):
        """当剪贴板内容变化时触发"""
        try:
            content = self.clipboard.text()
            if content and content != self.last_content:
                self.last_content = content
                self.text_edit.setText(f"剪贴板内容：\n{content}")
        except Exception as e:
            print(f"获取剪贴板内容时出错：{str(e)}")
    
    def check_selection(self):
        """检查选中文本的变化"""
        try:
            # 保存当前剪贴板内容
            current_clipboard = pyperclip.paste()
            
            # 模拟 Command+C 来获取选中文本
            pyperclip.copy('')  # 清空剪贴板
            import os
            os.system('osascript -e \'tell application "System Events" to keystroke "c" using command down\'')
            
            # 等待一小段时间让系统处理复制操作
            QApplication.processEvents()
            
            # 获取选中文本
            selected_text = pyperclip.paste()
            
            # 恢复原来的剪贴板内容
            pyperclip.copy(current_clipboard)
            
            if selected_text and selected_text != self.last_selection:
                self.last_selection = selected_text
                self.text_edit.setText(f"选中文本：\n{selected_text}")
        except Exception as e:
            print(f"获取选中文本时出错：{str(e)}")
    
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