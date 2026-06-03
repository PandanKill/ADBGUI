ADBGUI/
├── README.md
├── requirements.txt
├── main.py                 # 应用入口
├── config/
│   └── config.py          # 配置文件
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── adb_manager.py      # ADB操作管理
│   │   ├── device_manager.py   # 设备管理
│   │   └── logcat_manager.py   # Logcat管理
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── connect_dialog.py   # 连接对话框
│   │   ├── device_list.py      # 设备列表组件
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── device_info_page.py    # 设备信息页面
│   │   │   ├── logcat_page.py         # Logcat页面
│   │   │   └── file_manager_page.py   # 文件管理页面
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py          # 日志工具
│   │   └── validators.py      # 验证工具
│   └── components/
│       ├── __init__.py
│       └── device_card.py     # 设备卡片组件
└── assets/
    └── icons/