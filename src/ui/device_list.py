"""
设备列表组件
"""
from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QLabel,
                             QHBoxLayout, QVBoxLayout, QWidget, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import List
from src.core.device_manager import ConnectedDevice


class DeviceListWidget(QWidget):
    """设备列表组件"""

    device_selected = pyqtSignal(str)  # 设备被选中信号
    device_disconnected = pyqtSignal(str)  # 设备断开信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_devices: List[ConnectedDevice] = []
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题
        title = QLabel("已连接设备")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # 设备列表
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def update_devices(self, devices: List[ConnectedDevice]):
        """更新设备列表"""
        self.current_devices = devices
        self.list_widget.clear()

        for device in devices:
            name = device.info.name if device.info else device.serial
            item = QListWidgetItem(f"📱 {name}")
            item.setData(Qt.ItemDataRole.UserRole, device.serial)
            self.list_widget.addItem(item)

        if devices:
            self.list_widget.setCurrentRow(0)

    def _on_item_clicked(self, item: QListWidgetItem):
        """设备被点击"""
        serial = item.data(Qt.ItemDataRole.UserRole)
        self.device_selected.emit(serial)

    def _on_context_menu(self, position):
        """右键菜单"""
        item = self.list_widget.itemAt(position)
        if not item:
            return

        serial = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)

        disconnect_action = menu.addAction("断开连接")
        action = menu.exec_(self.list_widget.mapToGlobal(position))

        if action == disconnect_action:
            self.device_disconnected.emit(serial)

    def get_selected_device(self) -> str:
        """获取选中的设备"""
        current = self.list_widget.currentItem()
        if current:
            return current.data(Qt.ItemDataRole.UserRole)
        return ""