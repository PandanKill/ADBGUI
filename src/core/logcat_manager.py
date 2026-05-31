"""
Logcat管理器 - 管理logcat进程
"""
import subprocess
from typing import Optional, Callable
from threading import Thread
from queue import Queue, Empty


class LogcatManager:
    """Logcat管理器"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.serial: Optional[str] = None
        self.thread: Optional[Thread] = None
        self.queue: Queue = Queue()
        self.adb_path = "adb.exe" if __import__('platform').system() == "Windows" else "adb"

    def start(self, serial: str, callback: Callable[[str], None]):
        """启动logcat"""
        if self.running:
            self.stop()

        self.serial = serial
        self.running = True
        self.thread = Thread(target=self._read_logcat, args=(callback,), daemon=True)
        self.thread.start()

    def _read_logcat(self, callback: Callable[[str], None]):
        """读取logcat输出"""
        try:
            self.process = subprocess.Popen(
                f"{self.adb_path} -s {self.serial} logcat -v time",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
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

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
            self.thread = None

    def is_running(self) -> bool:
        """是否正在运行"""
        return self.running