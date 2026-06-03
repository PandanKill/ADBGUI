"""
ADB可视化工具 - 主入口
"""
import sys
import signal
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MainWindow
from config.config import Config
from src.utils.logger import setup_logger


def main():
    """主函数"""
    # 初始化配置
    Config.init_dirs()

    # 高DPI支持 - 必须在创建QApplication之前设置
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 设置日志
    logger = setup_logger("adbgui")
    logger.info(f"启动 {Config.APP_NAME} v{Config.APP_VERSION}")
    logger.info(f"系统: {Config.SYSTEM}")

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.APP_VERSION)

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 处理Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logger.info("应用启动成功")

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()