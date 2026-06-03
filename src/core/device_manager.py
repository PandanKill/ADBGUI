"""
设备管理器 - 管理已连接的设备
"""
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass, field
from src.core.adb_manager import ADBManager, DeviceInfo


@dataclass
class ConnectedDevice:
    """已连接设备"""
    serial: str
    info: Optional[DeviceInfo] = None
    is_connected: bool = True


class DeviceManager:
    """设备管理器"""

    def __init__(self):
        self.adb_manager = ADBManager()
        self.devices: Dict[str, ConnectedDevice] = {}
        self.listeners: List[Callable] = []

    def add_listener(self, callback: Callable):
        """添加设备变化监听器"""
        self.listeners.append(callback)

    def notify_listeners(self):
        """通知所有监听器"""
        for listener in self.listeners:
            listener()

    def connect(self, ip: str, port: int = 5555) -> Tuple[bool, str]:
        """连接设备"""
        success, message = self.adb_manager.connect_device(ip, port)

        if success:
            # 刷新设备列表
            self.refresh_devices()
            # 查找刚连接的设备
            serial = f"{ip}:{port}"
            if serial in self.devices:
                # 获取设备信息
                self.devices[serial].info = self.adb_manager.get_device_info(serial)
            self.notify_listeners()

        return success, message

    def disconnect(self, serial: str) -> bool:
        """断开设备"""
        success = self.adb_manager.disconnect_device(serial)

        if success and serial in self.devices:
            del self.devices[serial]
            self.notify_listeners()

        return success

    def refresh_devices(self):
        """刷新设备列表"""
        serials = self.adb_manager.get_connected_devices()

        # 添加新设备
        for serial in serials:
            if serial not in self.devices:
                self.devices[serial] = ConnectedDevice(
                    serial=serial,
                    info=self.adb_manager.get_device_info(serial)
                )

        # 移除断开的设备
        to_remove = [s for s in self.devices if s not in serials]
        for serial in to_remove:
            del self.devices[serial]

        if to_remove:
            self.notify_listeners()

    def get_devices(self) -> List[ConnectedDevice]:
        """获取所有设备"""
        return list(self.devices.values())

    def get_device(self, serial: str) -> Optional[ConnectedDevice]:
        """获取指定设备"""
        return self.devices.get(serial)

    def get_active_device(self) -> Optional[ConnectedDevice]:
        """获取当前活跃设备（第一个设备）"""
        if self.devices:
            return list(self.devices.values())[0]
        return None

    def has_devices(self) -> bool:
        """是否有连接的设备"""
        return len(self.devices) > 0