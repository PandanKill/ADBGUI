"""
Logcat日志页面
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                             QHBoxLayout, QComboBox, QLabel)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QTextCursor
from src.core.logcat_manager import LogcatManager


class LogcatPage(QWidget):
    """Logcat日志页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial: str = ""
        self.logcat_manager = LogcatManager()
        self.is_page_active = False
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题和控制栏
        control_layout = QHBoxLayout()

        title = QLabel("Logcat日志")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        control_layout.addWidget(title)

        control_layout.addStretch()

        # 日志级别过滤
        self.level_filter = QComboBox()
        self.level_filter.addItems(["All", "Verbose", "Debug", "Info", "Warn", "Error"])
        self.level_filter.setMinimumWidth(100)
        control_layout.addWidget(QLabel("级别:"))
        control_layout.addWidget(self.level_filter)

        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(self.clear_btn)

        layout.addLayout(control_layout)

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def set_device(self, serial: str):
        """设置当前设备"""
        if self.is_page_active and self.current_serial != serial:
            self.stop_logcat()

        self.current_serial = serial

        if self.is_page_active and self.current_serial:
            self.start_logcat()

    def on_page_show(self):
        """页面显示时调用"""
        self.is_page_active = True
        if self.current_serial:
            self.start_logcat()

    def on_page_hide(self):
        """页面隐藏时调用"""
        self.is_page_active = False
        self.stop_logcat()

    def start_logcat(self):
        """启动logcat"""
        if not self.current_serial:
            return

        self.log_text.clear()
        self.log_text.append("正在启动logcat...\n")

        def append_log(line: str):
            self.log_text.append(line)

        self.logcat_manager.start(self.current_serial, append_log)

    def stop_logcat(self):
        """停止logcat"""
        self.logcat_manager.stop()
        if not self.log_text.toPlainText().endswith("\n\nLogcat已停止"):
            self.log_text.append("\n\nLogcat已停止")

    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()
        self.log_text.append("日志已清空\n")

    def cleanup(self):
        """清理资源"""
        self.stop_logcat()