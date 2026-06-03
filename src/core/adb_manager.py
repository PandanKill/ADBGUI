"""
ADB管理器 - 封装ADB操作
"""
import subprocess
import re
import platform
import os
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """设备信息数据类"""
    serial: str
    name: str
    ip: str
    mac: str
    android_version: str
    memory: str
    storage: str
    cpu_info: str = ""


class ADBManager:
    """ADB操作管理器"""

    def __init__(self):
        self.system = platform.system()
        self.adb_path = self._get_adb_path()

    def _get_adb_path(self) -> str:
        """获取ADB路径"""
        if self.system == "Windows":
            return "adb.exe"
        return "adb"

    def _run_command(self, command: str) -> Tuple[bool, str]:
        """执行ADB命令"""
        try:
            full_command = f"{self.adb_path} {command}"
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                timeout=30
            )
            success = result.returncode == 0
            # 优先 UTF-8，失败则用 replace 容错
            output = ''
            for data in [result.stdout, result.stderr]:
                if data:
                    output += data.decode('utf-8', errors='replace').strip()
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)

    def connect_device(self, ip: str, port: int = 5555) -> Tuple[bool, str]:
        """连接设备"""
        command = f"connect {ip}:{port}"
        _, output = self._run_command(command)
        if output and ("connected" in output.lower() or "reconnected" in output.lower()):
            return True, f"成功连接到 {ip}:{port}"
        return False, output or "连接失败"

    def disconnect_device(self, serial: str) -> bool:
        """断开设备连接"""
        command = f"disconnect {serial}"
        success, _ = self._run_command(command)
        return success

    def get_connected_devices(self) -> List[str]:
        """获取已连接的设备列表"""
        success, output = self._run_command("devices")
        if not success:
            return []

        devices = []
        lines = output.split('\n')
        for line in lines[1:]:  # 跳过第一行标题
            if line.strip() and "device" in line:
                serial = line.split('\t')[0].strip()
                if serial:
                    devices.append(serial)
        return devices

    def get_device_info(self, serial: str) -> Optional[DeviceInfo]:
        """获取设备详细信息"""
        device_name = self._get_device_name(serial)
        device_serial = self._get_device_serial_number(serial)
        device_ip = self._get_device_ip(serial)
        device_mac = self._get_device_mac(serial)
        android_version = self._get_android_version(serial)
        memory = self._get_memory_info(serial)
        storage = self._get_storage_info(serial)

        if not device_name:
            return None

        return DeviceInfo(
            serial=device_serial,
            name=device_name,
            ip=device_ip,
            mac=device_mac,
            android_version=android_version,
            memory=memory,
            storage=storage
        )

    def _get_device_name(self, serial: str) -> str:
        """获取设备名称"""
        command = f"-s {serial} shell getprop ro.product.model"
        _, output = self._run_command(command)
        return output or "Unknown"

    def _get_device_serial_number(self, serial: str) -> str:
        """获取设备序列号"""
        command = f"-s {serial} shell getprop ro.serialno"
        _, output = self._run_command(command)
        return output or serial

    def _get_device_ip(self, serial: str) -> str:
        """获取设备IP"""
        command = f"-s {serial} shell ip addr show wlan0 | grep 'inet ' | awk '{{print $2}}' | cut -d/ -f1"
        _, output = self._run_command(command)
        return output or "Unknown"

    def _get_device_mac(self, serial: str) -> str:
        """获取设备MAC地址"""
        command = f"-s {serial} shell cat /sys/class/net/wlan0/address"
        _, output = self._run_command(command)
        return output or "Unknown"

    def _get_android_version(self, serial: str) -> str:
        """获取Android版本"""
        command = f"-s {serial} shell getprop ro.build.version.release"
        _, output = self._run_command(command)
        return output or "Unknown"

    def _get_memory_info(self, serial: str) -> str:
        """获取内存信息"""
        command = f"-s {serial} shell cat /proc/meminfo | grep MemTotal"
        _, output = self._run_command(command)
        match = re.search(r'MemTotal:\s+(\d+)\s+kB', output)
        if match:
            kb = int(match.group(1))
            gb = kb / (1024 * 1024)
            return f"{gb:.1f} GB"
        return "Unknown"

    def _get_storage_info(self, serial: str) -> str:
        """获取存储空间信息"""
        command = f"-s {serial} shell df /data | tail -1"
        _, output = self._run_command(command)
        parts = output.split()
        if len(parts) >= 4:
            total = int(parts[1])
            used = int(parts[2])
            available = int(parts[3])
            total_gb = total / (1024 * 1024)
            used_gb = used / (1024 * 1024)
            available_gb = available / (1024 * 1024)
            return f"{used_gb:.1f}GB / {total_gb:.1f}GB (可用: {available_gb:.1f}GB)"
        return "Unknown"

    def start_logcat(self, serial: str) -> subprocess.Popen:
        """启动logcat"""
        command = f"-s {serial} logcat -v time"
        process = subprocess.Popen(
            f"{self.adb_path} {command}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process

    def list_files(self, serial: str, path: str = "/") -> List[Dict]:
        """列出文件"""
        try:
            command = f"-s {serial} shell ls -1 '{path}'"
            _, output = self._run_command(command)
            if not output or 'not found' in output.lower() or 'error' in output.lower():
                return []

            files = []
            for name in output.strip().split('\n'):
                name = name.strip()
                if not name:
                    continue
                full = f"{path}/{name}" if path != "/" else f"/{name}"
                is_dir_cmd = f"-s {serial} shell test -d '{full}' && echo 1 || echo 0"
                _, is_dir_out = self._run_command(is_dir_cmd)
                is_dir = is_dir_out.strip() == '1'
                size_cmd = f"-s {serial} shell stat -c '%s' '{full}' 2>/dev/null"
                _, size_out = self._run_command(size_cmd)
                size = size_out.strip() if (size_out and size_out.strip().isdigit()) else '0'
                files.append({
                    'name': name,
                    'is_dir': is_dir,
                    'permissions': 'd' if is_dir else '-rw-r--r--',
                    'size': size,
                    'date': ''
                })
            return files
        except Exception:
            return []

    def push_file(self, serial: str, local_path: str, device_path: str, progress_callback: Optional[Callable[[str, int, int], None]] = None) -> Tuple[bool, str]:
        """上传文件到设备 (adb push)"""
        try:
            if not os.path.exists(local_path):
                return False, f"文件不存在: {local_path}"

            file_size = os.path.getsize(local_path)
            file_name = os.path.basename(local_path)

            # 转义路径中的特殊字符
            escaped_device_path = device_path.replace(" ", "\\ ").replace("(", "\\(").replace(")", "\\)")

            command = f"-s {serial} push \"{local_path}\" {escaped_device_path}"

            if progress_callback:
                progress_callback(file_name, 0, file_size)

            process = subprocess.Popen(
                f"{self.adb_path} {command}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )

            output, error = process.communicate()

            if process.returncode == 0:
                if progress_callback:
                    progress_callback(file_name, file_size, file_size)
                return True, f"上传成功: {file_name}"
            else:
                return False, f"上传失败: {error or output}"
        except Exception as e:
            return False, f"上传出错: {str(e)}"

    def pull_file(self, serial: str, device_path: str, local_path: str, progress_callback: Optional[Callable[[str, int, int], None]] = None) -> Tuple[bool, str]:
        """从设备下载文件 (adb pull)"""
        try:
            # 确保本地目录存在
            local_dir = os.path.dirname(local_path)
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)

            # 转义设备路径中的特殊字符
            escaped_device_path = device_path.replace(" ", "\\ ").replace("(", "\\(").replace(")", "\\)")

            command = f"-s {serial} pull \"{escaped_device_path}\" \"{local_path}\""

            file_name = os.path.basename(device_path)

            if progress_callback:
                # 获取远程文件大小
                size_cmd = f"-s {serial} shell \"stat -c '%s' '{escaped_device_path}'\""
                success, size_output = self._run_command(size_cmd)
                remote_size = int(size_output) if success and size_output.strip().isdigit() else 0
                progress_callback(file_name, 0, remote_size)

            process = subprocess.Popen(
                f"{self.adb_path} {command}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )

            output, error = process.communicate()

            if process.returncode == 0:
                if progress_callback:
                    file_size = os.path.getsize(local_path) if os.path.exists(local_path) else 0
                    progress_callback(file_name, file_size, file_size)
                return True, f"下载成功: {file_name}"
            else:
                return False, f"下载失败: {error or output}"
        except Exception as e:
            return False, f"下载出错: {str(e)}"

    def create_directory(self, serial: str, path: str) -> Tuple[bool, str]:
        """创建目录"""
        escaped_path = path.replace(" ", "\\ ").replace("(", "\\(").replace(")", "\\)")
        command = f"-s {serial} shell mkdir -p {escaped_path}"
        success, output = self._run_command(command)
        return success, output

    def list_directory_files(self, serial: str, path: str) -> List[Dict]:
        """列出目录下所有文件（递归），用于统计"""
        try:
            command = f"-s {serial} shell find '{path}' -type f"
            _, output = self._run_command(command)
            if not output:
                return []
            files = []
            for line in output.strip().split('\n'):
                line = line.strip()
                if line:
                    files.append(line)
            return files
        except Exception:
            return []

    def pull_directory(self, serial: str, device_dir: str, local_dir: str,
                       progress_callback: Optional[Callable] = None,
                       downloaded_counter: Optional[list] = None) -> Tuple[bool, str]:
        """递归下载整个目录"""
        try:
            os.makedirs(local_dir, exist_ok=True)
            if downloaded_counter is None:
                downloaded_counter = [0]

            files = self.list_directory_files(serial, device_dir)
            total = len(files)

            for i, device_file in enumerate(files):
                device_file = device_file.strip()
                if not device_file:
                    continue
                rel_path = device_file[len(device_dir):].lstrip('/')
                local_file = os.path.join(local_dir, rel_path)
                local_file_dir = os.path.dirname(local_file)
                if local_file_dir:
                    os.makedirs(local_file_dir, exist_ok=True)

                success, message = self.pull_file(serial, device_file, local_file)
                if not success:
                    return False, f"下载失败: {rel_path} - {message}"
                downloaded_counter[0] += 1
                if progress_callback:
                    progress_callback(rel_path, downloaded_counter[0], total)

            return True, f"文件夹下载完成: {total} 个文件"
        except Exception as e:
            return False, str(e)