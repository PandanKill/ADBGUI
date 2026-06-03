"""
ADBGUI 打包脚本
支持 Windows 和 Mac
"""
import os
import sys
import platform
import subprocess
from pathlib import Path


def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("请运行: pip3 install pyinstaller")
        return False


def build_mac():
    """Mac 打包"""
    print("\n" + "="*50)
    print("开始打包 Mac 版本...")
    print("="*50)

    app_name = "ADBGUI"
    icon = "assets/icon.icns" if os.path.exists("assets/icon.icns") else None

    cmd = [
        "pyinstaller",
        "--name", app_name,
        "--windowed",  # 无控制台
        "--onefile",   # 单文件
        "--clean",     # 清理临时文件
    ]

    if icon:
        cmd.extend(["--icon", icon])

    # 添加隐藏导入
    hidden_imports = [
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtGui",
    ]
    cmd.extend(hidden_imports)

    cmd.append("main.py")

    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"\n✓ Mac 打包成功!")
        print(f"  位置: dist/{app_name}")
    else:
        print(f"\n✗ Mac 打包失败")
        return False

    return True


def build_windows():
    """Windows 打包"""
    print("\n" + "="*50)
    print("开始打包 Windows 版本...")
    print("="*50)

    app_name = "ADBGUI"
    icon = "assets/icon.ico" if os.path.exists("assets/icon.ico") else None

    cmd = [
        "pyinstaller",
        "--name", app_name,
        "--windowed",  # 无控制台
        "--onefile",   # 单文件
        "--clean",     # 清理临时文件
        "--uac-admin", # 请求管理员权限（ADB可能需要）
    ]

    if icon:
        cmd.extend(["--icon", icon])

    # 添加隐藏导入
    hidden_imports = [
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtGui",
    ]
    cmd.extend(hidden_imports)

    cmd.append("main.py")

    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"\n✓ Windows 打包成功!")
        print(f"  位置: dist/{app_name}.exe")
    else:
        print(f"\n✗ Windows 打包失败")
        return False

    return True


def build_current():
    """打包当前平台"""
    system = platform.system()

    if system == "Darwin":
        return build_mac()
    elif system == "Windows":
        return build_windows()
    else:
        print(f"\n✗ 不支持的平台: {system}")
        return False


def main():
    """主函数"""
    print("ADBGUI 打包工具")
    print("="*50)

    if not check_pyinstaller():
        sys.exit(1)

    # 切换到项目目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"工作目录: {os.getcwd()}")

    # 根据参数选择打包平台
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        if target == "mac":
            build_mac()
        elif target == "windows" or target == "win":
            build_windows()
        elif target == "all":
            # 当前平台打包
            build_current()
            print("\n注意: 要打包所有平台，请在对应系统上分别运行")
        else:
            print(f"未知参数: {target}")
            print("用法: python build.py [mac|windows|all]")
    else:
        # 默认打包当前平台
        build_current()


if __name__ == "__main__":
    main()