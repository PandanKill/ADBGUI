"""
主窗口 - 应用主界面
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QMessageBox, QFrame, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.ui.connect_dialog import ConnectDialog
from src.ui.device_list import DeviceListWidget
from src.ui.pages.device_info_page import DeviceInfoPage
from src.ui.pages.logcat_page import LogcatPage
from src.ui.pages.file_manager_page import FileManagerPage
from src.core.device_manager import DeviceManager


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.device_manager = DeviceManager()
        self.init_ui()
        self.check_devices()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("ADB可视化工具")
        self.setMinimumSize(1200, 700)

        # 主窗口部件
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 顶部栏
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)

        # 内容区域
        content_layout = QHBoxLayout()

        # 左侧设备列表
        self.device_list = DeviceListWidget()
        self.device_list.device_selected.connect(self._on_device_selected)
        device_container = self._create_container("设备列表", self.device_list)
        content_layout.addWidget(device_container, stretch=1)

        # 右侧功能区域
        right_container = self._create_right_content()
        content_layout.addWidget(right_container, stretch=4)

        main_layout.addLayout(content_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _create_top_bar(self) -> QFrame:
        """创建顶部栏"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-bottom: 1px solid #ccc;
            }
        """)
        layout = QHBoxLayout()

        title = QLabel("ADB可视化工具")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addStretch()

        # 连接按钮
        self.connect_btn = QPushButton("📡 连接设备")
        self.connect_btn.clicked.connect(self._show_connect_dialog)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(self.connect_btn)

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self._refresh_devices)
        layout.addWidget(self.refresh_btn)

        frame.setLayout(layout)
        return frame

    def _create_container(self, title: str, widget) -> QFrame:
        """创建容器框架"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        layout = QVBoxLayout()

        # 容器标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("padding: 8px;")
        layout.addWidget(title_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 内容
        layout.addWidget(widget)

        frame.setLayout(layout)
        return frame

    def _create_right_content(self) -> QFrame:
        """创建右侧内容区域"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        layout = QVBoxLayout()

        # 标签页导航
        tab_layout = QHBoxLayout()
        self.tab_buttons = []

        tab_names = ["设备信息", "Logcat日志", "文件管理"]
        for i, name in enumerate(tab_names):
            btn = QPushButton(name)
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 10px 20px;
                    font-size: 14px;
                    background-color: transparent;
                }
                QPushButton:checked {
                    border-bottom: 3px solid #0078d4;
                    color: #0078d4;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, index=i: self._switch_tab(index))
            tab_layout.addWidget(btn)
            self.tab_buttons.append(btn)

        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 页面堆栈
        self.stack_widget = QStackedWidget()

        # 设备信息页面
        self.device_info_page = DeviceInfoPage()
        self.stack_widget.addWidget(self.device_info_page)

        # Logcat页面
        self.logcat_page = LogcatPage()
        self.stack_widget.addWidget(self.logcat_page)

        # 文件管理页面
        self.file_manager_page = FileManagerPage()
        self.stack_widget.addWidget(self.file_manager_page)

        layout.addWidget(self.stack_widget)
        frame.setLayout(layout)
        return frame

    def _switch_tab(self, index: int):
        """切换标签页"""
        # 更新按钮状态
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)

        # 停止当前页面
        current_index = self.stack_widget.currentIndex()
        if current_index == 1:  # Logcat页面
            self.logcat_page.on_page_hide()

        # 切换页面
        self.stack_widget.setCurrentIndex(index)

        # 启动新页面
        if index == 1:  # Logcat页面
            self.logcat_page.on_page_show()

    def _show_connect_dialog(self):
        """显示连接对话框"""
        dialog = ConnectDialog(self)
        if dialog.exec():
            ip, port = dialog.get_connection_info()
            success, message = self.device_manager.connect(ip, port)

            if success:
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "失败", message)

    def _refresh_devices(self):
        """刷新设备列表"""
        self.device_manager.refresh_devices()
        self.check_devices()

    def _on_device_selected(self, serial: str):
        """设备被选中"""
        device = self.device_manager.get_device(serial)
        if device and device.info:
            # 更新设备信息页面
            self.device_info_page.update_device_info(device.info)
            # 更新logcat页面
            self.logcat_page.set_device(serial)
            # 更新文件管理页面
            self.file_manager_page.set_device(serial)

    def check_devices(self):
        """检查设备连接状态"""
        self.device_manager.refresh_devices()

        devices = self.device_manager.get_devices()
        self.device_list.update_devices(devices)

        if devices:
            # 自动选择第一个设备
            first_device = devices[0]
            if first_device.info:
                self._on_device_selected(first_device.serial)
        else:
            self.device_info_page.clear_info()

    def closeEvent(self, event):
        """关闭事件"""
        # 停止logcat
        self.logcat_page.cleanup()
        event.accept()