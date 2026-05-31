"""
连接对话框 - 连接设备
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from typing import Tuple


class ConnectDialog(QDialog):
    """连接设备对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ip_address = ""
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("连接设备")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()

        # 标题
        title = QLabel("请输入设备IP地址")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # IP输入框
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP地址:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("例如: 192.168.1.100")
        ip_layout.addWidget(self.ip_input)
        layout.addLayout(ip_layout)

        # 端口输入框
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self.port_input = QLineEdit("5555")
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        # 提示
        hint = QLabel("提示: 请确保设备已开启USB调试和无线调试")
        hint.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(hint)

        layout.addStretch()

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.connect_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_connection_info(self) -> Tuple[str, int]:
        """获取连接信息"""
        return self.ip_input.text(), int(self.port_input.text())

    def validate(self) -> bool:
        """验证输入"""
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "警告", "请输入IP地址")
            return False

        # 简单的IP格式验证
        parts = ip.split('.')
        if len(parts) != 4:
            QMessageBox.warning(self, "警告", "IP地址格式不正确")
            return False

        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                QMessageBox.warning(self, "警告", "IP地址格式不正确")
                return False

        try:
            port = int(self.port_input.text())
            if not 1 <= port <= 65535:
                QMessageBox.warning(self, "警告", "端口号必须在1-65535之间")
                return False
        except ValueError:
            QMessageBox.warning(self, "警告", "端口号必须是数字")
            return False

        return True

    def accept(self):
        """确认连接"""
        if self.validate():
            super().accept()