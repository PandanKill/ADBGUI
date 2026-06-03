# ADB可视化工具

一款基于PyQt的ADB桌面可视化工具，支持Windows和Mac系统。

## 功能特性

- 设备连接管理（支持IP连接）
- 设备信息查看（设备名、序列号、Android版本、内存、存储等）
- 实时Logcat日志查看（进入页面自动启动，退出自动停止）
- 设备文件管理（支持拖拽上传/下载）

## 项目结构

```
ADBGUI/
├── main.py                 # 应用入口
├── build.py                # 打包脚本
├── requirements.txt        # 依赖列表
├── config/
│   └── config.py          # 配置文件
├── src/
│   ├── core/              # 核心模块
│   │   ├── adb_manager.py      # ADB操作管理
│   │   ├── device_manager.py   # 设备管理
│   │   └── logcat_manager.py   # Logcat管理
│   ├── ui/                # UI模块
│   │   ├── main_window.py      # 主窗口
│   │   ├── connect_dialog.py   # 连接对话框
│   │   ├── device_list.py      # 设备列表组件
│   │   └── pages/              # 功能页面
│   │       ├── device_info_page.py    # 设备信息页面
│   │       ├── logcat_page.py         # Logcat页面
│   │       └── file_manager_page.py   # 文件管理页面
│   └── utils/             # 工具模块
└── assets/                # 资源文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

```bash
# Mac
python3 main.py

# Windows
python main.py
```

## 打包发布

```bash
# Mac 打包
python3 build.py mac

# Windows 打包
python build.py windows
```

详细打包说明请查看 [BUILD.md](BUILD.md)

## 系统要求

- Python 3.7+
- PyQt5
- ADB工具（需要添加到系统PATH）

## 使用说明

1. 启动应用
2. 点击"连接设备"按钮
3. 输入设备IP地址和端口（默认5555）
4. 连接成功后，左侧显示设备列表
5. 右侧可切换查看：
   - 设备信息
   - Logcat日志
   - 文件管理

## 文件拖拽功能

- **上传文件**: 从电脑拖入文件到文件管理页面 → adb push
- **下载文件**: 从文件管理页面拖出文件到桌面 → adb pull

## 注意事项

- 确保设备已开启USB调试
- 确保设备已开启无线调试
- 确保设备和电脑在同一网络
- 打包的应用需要系统已安装 ADB 工具