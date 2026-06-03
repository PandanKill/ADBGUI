"""
设备信息页面
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel,
                             QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Optional
from src.core.adb_manager import DeviceInfo


class DeviceInfoPage(QWidget):
    """设备信息页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_device: Optional[DeviceInfo] = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题
        title = QLabel("设备信息")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # 信息展示区域
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #f5f5f5;
                padding: 10px;
            }
        """)
        info_layout = QGridLayout()

        # 创建信息标签
        self.labels = {}
        info_fields = [
            ("设备名称:", "name"),
            ("设备序列号:", "serial"),
            ("设备IP:", "ip"),
            ("MAC地址:", "mac"),
            ("Android版本:", "android_version"),
            ("设备内存:", "memory"),
            ("存储空间:", "storage")
        ]

        for i, (label_text, field) in enumerate(info_fields):
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            value = QLabel("未连接")
            value.setStyleSheet("color: #666;")
            info_layout.addWidget(label, i, 0)
            info_layout.addWidget(value, i, 1)
            self.labels[field] = value

        self.info_frame.setLayout(info_layout)
        layout.addWidget(self.info_frame)
        layout.addStretch()

        self.setLayout(layout)

    def update_device_info(self, device_info: DeviceInfo):
        """更新设备信息"""
        self.current_device = device_info

        self.labels["name"].setText(device_info.name)
        self.labels["serial"].setText(device_info.serial)
        self.labels["ip"].setText(device_info.ip)
        self.labels["mac"].setText(device_info.mac)
        self.labels["android_version"].setText(device_info.android_version)
        self.labels["memory"].setText(device_info.memory)
        self.labels["storage"].setText(device_info.storage)

        # 更新颜色
        for label in self.labels.values():
            label.setStyleSheet("color: #333;")

    def clear_info(self):
        """清空设备信息"""
        self.current_device = None
        for label in self.labels.values():
            label.setText("未连接")
            label.setStyleSheet("color: #666;")