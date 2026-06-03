"""
应用配置
"""
import platform
from pathlib import Path


class Config:
    """应用配置类"""

    # 应用信息
    APP_NAME = "ADBGUI"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "ADBGUI Team"

    # 系统信息
    SYSTEM = platform.system()
    IS_WINDOWS = SYSTEM == "Windows"
    IS_MAC = SYSTEM == "Darwin"
    IS_LINUX = SYSTEM == "Linux"

    # ADB配置
    ADB_DEFAULT_PORT = 5555
    ADB_PATH = "adb.exe" if IS_WINDOWS else "adb"

    # UI配置
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 700
    WINDOW_DEFAULT_WIDTH = 1400
    WINDOW_DEFAULT_HEIGHT = 800

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_DIR = Path.home() / ".adbgui" / "logs"

    # 主题配置
    THEME = {
        "primary": "#0078d4",
        "success": "#107c10",
        "warning": "#ff8c00",
        "danger": "#d13438",
        "background": "#ffffff",
        "text": "#333333",
        "border": "#cccccc"
    }

    @classmethod
    def init_dirs(cls):
        """初始化应用目录"""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)