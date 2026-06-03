"""
Logcat管理器 - 管理logcat进程
"""
import subprocess
import threading
from threading import Thread
from typing import Optional, Callable


class LogcatManager:
    """Logcat管理器"""

    # Android log level 与 adb 过滤语法的映射
    # 语法: *:LEVEL 表示所有 tag 的最低显示级别为 LEVEL
    LEVEL_FILTER_MAP = {
        "Verbose": "*",       # 不过滤，显示全部
        "Debug": "*:D",
        "Info": "*:I",
        "Warn": "*:W",
        "Error": "*:E",
    }

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.serial: Optional[str] = None
        self.thread: Optional[Thread] = None
        self.adb_path = "adb.exe" if __import__('platform').system() == "Windows" else "adb"

    def start(self, serial: str, callback: Callable[[str], None], level_filter: Optional[str] = None):
        """启动logcat

        Args:
            serial: 设备序列号
            callback: 每行日志的回调
            level_filter: 日志级别过滤，如 "Debug", "Info", "Error" 等
        """
        if self.running:
            self.stop()

        self.serial = serial
        self.running = True

        # 构建 adb logcat 命令，带级别过滤
        cmd = f"{self.adb_path} -s {self.serial} logcat -v time"
        if level_filter and level_filter in self.LEVEL_FILTER_MAP:
            filter_expr = self.LEVEL_FILTER_MAP[level_filter]
            if filter_expr != "*":
                cmd += f" {filter_expr}"

        self.thread = Thread(target=self._read_logcat, args=(callback, cmd), daemon=True)
        self.thread.start()

    def _read_logcat(self, callback: Callable[[str], None], cmd: str):
        """读取logcat输出"""
        try:
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )

            while self.running and self.process:
                line = self.process.stdout.readline()
                if line:
                    callback(line)
                else:
                    break

        except Exception as e:
            callback(f"Error: {str(e)}")
        finally:
            self.stop()

    def stop(self):
        """停止logcat"""
        self.running = False

        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None

        if self.thread and self.thread.is_alive() and self.thread != threading.current_thread():
            self.thread.join(timeout=2)
            self.thread = None

    def is_running(self) -> bool:
        """是否正在运行"""
        return self.running
