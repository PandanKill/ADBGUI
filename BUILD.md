# 打包说明

## 当前打包结果

### Mac 版本 ✓

```
dist/ADBGUI          # 单文件可执行程序 (25MB)
dist/ADBGUI.app      # Mac 应用包
```

## 打包命令

### 安装依赖

```bash
pip install -r requirements.txt
```

### 打包当前平台

```bash
# Mac
python build.py mac

# Windows
python build.py windows

# 自动检测当前平台
python build.py
```

## Windows 打包

在 Windows 系统上执行：

```bash
python build.py windows
```

生成的文件：
```
dist/ADBGUI.exe  # Windows 可执行文件
```

## 打包选项

| 选项 | 说明 |
|------|------|
| `--windowed` | 无控制台窗口（GUI应用） |
| `--onefile` | 打包成单个可执行文件 |
| `--clean` | 清理临时文件 |

## 注意事项

1. **ADB 依赖**: 打包的应用不包含 ADB，使用前需确保系统已安装 ADB 并添加到 PATH

2. **Mac 证书**: 首次运行可能需要右键点击 → "打开" 绕过安全限制

3. **Windows 权限**: ADB 操作可能需要管理员权限

4. **Python 版本**: 使用 Python 3.7+ 打包，运行环境无需 Python

## 发布准备

```bash
# 创建发布目录
mkdir -p releases/mac releases/windows

# 复制文件
cp dist/ADBGUI releases/mac/
# Windows 上
cp dist/ADBGUI.exe releases/windows/

# 压缩
cd releases
zip -r ADBGUI-Mac.zip mac/
# Windows 上
powershell Compress-Archive -Path windows\* -DestinationPath ADBGUI-Windows.zip
```

## 常见问题

### 打包后运行报错
检查 `build/ADBGUI/warn-ADBGUI.txt` 查看警告信息

### 文件过大
可移除 `--onefile` 选项使用目录模式，减少重复依赖

### Mac 运行时无法打开
```bash
# 移除隔离属性
xattr -cr dist/ADBGUI
```