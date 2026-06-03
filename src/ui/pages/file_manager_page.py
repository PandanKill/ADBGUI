"""
文件管理页面
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
                             QTreeWidgetItem, QPushButton, QLineEdit, QLabel,
                             QProgressDialog, QMessageBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QUrl, QPoint
from PyQt5.QtGui import QFont, QIcon, QDrag, QCursor
from typing import List, Dict, Optional, Callable
from src.core.adb_manager import ADBManager


class DragDropTreeWidget(QTreeWidget):
    """支持拖拽的文件树组件"""

    drag_started = pyqtSignal(object)  # 拖拽开始信号，传递文件数据
    files_dropped = pyqtSignal(list)  # 文件拖入信号，传递文件路径列表

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.DropOnly)
        self.drag_start_pos = QPoint()
        self.drag_file_data = None

    def dragEnterEvent(self, event):
        """拖入事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        """拖动移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖放事件 - 上传文件到设备"""
        urls = event.mimeData().urls()
        files = []
        for url in urls:
            if url.isLocalFile():
                local_path = url.toLocalFile()
                if os.path.exists(local_path):
                    files.append(local_path)

        if files:
            self.files_dropped.emit(files)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                file_data = item.data(0, Qt.ItemDataRole.UserRole)
                if file_data and not item.text(0).startswith(".."):
                    self.drag_start_pos = event.pos()
                    self.drag_file_data = file_data
                else:
                    self.drag_file_data = None
            else:
                self.drag_file_data = None
        else:
            self.drag_file_data = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if (self.drag_file_data and
            (event.buttons() & Qt.MouseButton.LeftButton) and
            (event.pos() - self.drag_start_pos).manhattanLength() >= 10):
            self.drag_started.emit(self.drag_file_data)
            self.drag_file_data = None

        super().mouseMoveEvent(event)


class FileManagerPage(QWidget):
    """文件管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial: str = ""
        self.current_path: str = "/"
        self.adb_manager = ADBManager()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题和路径栏
        header_layout = QHBoxLayout()

        title = QLabel("文件管理")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)

        # 路径显示
        header_layout.addWidget(QLabel("路径:"))
        self.path_display = QLabel("/")
        self.path_display.setStyleSheet("color: #666;")
        header_layout.addWidget(self.path_display)

        header_layout.addStretch()

        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_files)
        header_layout.addWidget(self.refresh_btn)

        # 返回按钮
        self.back_btn = QPushButton("返回上级")
        self.back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_btn)

        layout.addLayout(header_layout)

        # 文件树
        self.file_tree = DragDropTreeWidget()
        self.file_tree.setHeaderLabels(["名称", "大小", "日期"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.file_tree.drag_started.connect(self._on_drag_started)
        self.file_tree.files_dropped.connect(self._on_files_dropped)

        self.file_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        layout.addWidget(self.file_tree)

        # 状态栏
        self.status_label = QLabel("就绪 | 支持拖拽: 拖入文件上传，拖出文件下载")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def set_device(self, serial: str):
        """设置当前设备"""
        self.current_serial = serial
        self.current_path = "/"
        self.refresh_files()

    def refresh_files(self):
        """刷新文件列表"""
        if not self.current_serial:
            self.file_tree.clear()
            self.status_label.setText("未连接设备")
            return

        self.status_label.setText(f"正在加载 {self.current_path} ...")
        self.file_tree.clear()

        files = self.adb_manager.list_files(self.current_serial, self.current_path)

        # 添加父目录
        if self.current_path != "/":
            parent_item = QTreeWidgetItem(["..", "", ""])
            parent_item.setForeground(0, Qt.GlobalColor.blue)
            self.file_tree.addTopLevelItem(parent_item)

        for file_info in files:
            name = file_info['name']
            is_dir = file_info.get('is_dir', False)

            item = QTreeWidgetItem([
                name,
                self._format_size(file_info['size']),
                file_info.get('date', '')
            ])

            if is_dir:
                item.setText(0, f"📁 {name}")
                item.setForeground(0, Qt.GlobalColor.blue)
            else:
                item.setText(0, f"📄 {name}")

            # 存储文件信息用于拖拽
            item.setData(0, Qt.ItemDataRole.UserRole, {
                'name': name,
                'is_dir': is_dir,
                'full_path': f"{self.current_path}/{name}" if self.current_path != "/" else f"/{name}"
            })

            self.file_tree.addTopLevelItem(item)

        self.path_display.setText(self.current_path)
        self.status_label.setText(f"共 {len(files)} 项")

    def _format_size(self, size: str) -> str:
        """格式化文件大小"""
        try:
            bytes_size = int(size)
            if bytes_size == 0:
                return "-"
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f}{unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f}TB"
        except:
            return "-"

    def go_back(self):
        """返回上级目录"""
        if self.current_path == "/":
            return

        path_parts = self.current_path.rstrip('/').split('/')
        if len(path_parts) > 1:
            new_path = '/' + '/'.join(path_parts[:-1])
        else:
            new_path = "/"

        self.current_path = new_path
        self.refresh_files()

    def _on_item_double_clicked(self, item: QTreeWidgetItem):
        """双击项目"""
        # 返回上级目录
        if item.text(0) == "..":
            self.go_back()
            return

        file_data = item.data(0, Qt.ItemDataRole.UserRole)
        if file_data and file_data.get('is_dir'):
            self.current_path = file_data['full_path']
            self.refresh_files()

    def _on_drag_started(self, file_data: Dict):
        """拖拽开始 - 下载文件/文件夹"""
        if not self.current_serial:
            QMessageBox.warning(self, "警告", "请先连接设备")
            return

        file_name = file_data['name']
        device_path = file_data['full_path']

        if file_data.get('is_dir'):
            # 文件夹：选择保存目录
            save_path = QFileDialog.getExistingDirectory(
                self,
                "保存文件夹",
                os.path.join(os.path.expanduser("~"), file_name)
            )
            if not save_path:
                return
            # 将文件夹内容保存到本地目录
            local_dir = os.path.join(save_path, file_name)
            self._download_directory(device_path, local_dir, file_name)
        else:
            # 文件：选择保存位置
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "下载文件",
                os.path.join(os.path.expanduser("~"), file_name),
                "所有文件 (*.*)"
            )
            if not save_path:
                return
            self._download_file(device_path, save_path, file_name)

    def _download_file(self, device_path: str, save_path: str, file_name: str):
        """下载文件"""
        self.status_label.setText(f"正在下载: {file_name}...")

        progress = QProgressDialog(f"下载文件: {file_name}", "取消", 0, 100, self)
        progress.setWindowTitle("下载文件")
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        def progress_callback(name: str, current: int, total: int):
            if total > 0:
                percent = int((current / total) * 100)
                progress.setValue(percent)
                progress.setLabelText(f"下载文件: {name} ({self._format_size(str(current))}/{self._format_size(str(total))})")

        success, message = self.adb_manager.pull_file(
            self.current_serial,
            device_path,
            save_path,
            progress_callback=progress_callback
        )

        progress.close()

        if success:
            self.status_label.setText(message)
            QMessageBox.information(self, "下载成功", f"文件已保存到:\n{save_path}")
        else:
            self.status_label.setText(message)
            QMessageBox.warning(self, "下载失败", message)

    def _download_directory(self, device_dir: str, local_dir: str, dir_name: str):
        """下载文件夹（递归）"""
        self.status_label.setText(f"正在下载文件夹: {dir_name}...")

        progress = QProgressDialog(f"下载文件夹: {dir_name}", "取消", 0, 100, self)
        progress.setWindowTitle("下载文件夹")
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        # 先统计文件总数
        file_list = self.adb_manager.list_directory_files(self.current_serial, device_dir)
        total_files = len(file_list)
        downloaded = [0]

        def progress_callback(name: str, current: int, total: int):
            if total_files > 0:
                percent = int((downloaded[0] / total_files) * 100)
                progress.setValue(percent)
                progress.setLabelText(f"下载文件夹: {dir_name} ({downloaded[0]}/{total_files})")

        try:
            success, message = self.adb_manager.pull_directory(
                self.current_serial,
                device_dir,
                local_dir,
                progress_callback,
                downloaded
            )
        except Exception as e:
            success = False
            message = str(e)

        progress.close()

        if success:
            self.status_label.setText(message)
            QMessageBox.information(self, "下载成功", f"文件夹已保存到:\n{local_dir}")
        else:
            self.status_label.setText(message)
            QMessageBox.warning(self, "下载失败", message)

    def _on_files_dropped(self, files: List[str]):
        """文件拖入 - 上传文件到设备"""
        if not self.current_serial:
            QMessageBox.warning(self, "警告", "请先连接设备")
            return

        self._upload_files(files)

    def _upload_files(self, files: List[str]):
        """上传文件到设备"""
        for i, local_path in enumerate(files):
            if os.path.isdir(local_path):
                continue

            file_name = os.path.basename(local_path)
            device_path = f"{self.current_path}/{file_name}" if self.current_path != "/" else f"/{file_name}"

            progress = QProgressDialog(f"上传文件: {file_name}", "取消", 0, 100, self)
            progress.setWindowTitle("上传文件")
            progress.setWindowModality(Qt.WindowModality.WindowModal)

            def progress_callback(name: str, current: int, total: int):
                if total > 0:
                    percent = int((current / total) * 100)
                    progress.setValue(percent)
                    progress.setLabelText(f"上传文件: {name} ({self._format_size(str(current))}/{self._format_size(str(total))})")

            success, message = self.adb_manager.push_file(
                self.current_serial,
                local_path,
                device_path,
                progress_callback=progress_callback
            )

            progress.close()

            if success:
                self.status_label.setText(message)
            else:
                QMessageBox.warning(self, "上传失败", message)
                return

        # 刷新文件列表
        self.refresh_files()