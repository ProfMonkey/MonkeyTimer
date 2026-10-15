# MonkeyTimer V0.1

一个免费的 Windows PPT 演讲倒计时工具。本版本仅提供普通窗口倒计时，不包含悬浮窗、透明背景或 PPT 插件功能。

## 功能

- 自定义分钟和秒（秒为 0–59）
- 开始、暂停、继续、重置
- 使用 `time.monotonic()` 计时，避免系统时间调整影响倒计时
- 到达 `00:00` 后自动停止
- 对空值、非整数、秒数超范围和零时长给出提示

## Windows 运行

1. 安装 Python 3（安装时勾选 **Add Python to PATH**）。Tkinter 随官方 Windows Python 一同安装。
2. 在此项目目录打开 PowerShell 或命令提示符。
3. 运行：

   ```powershell
   py monkey_timer.py
   ```

   如系统未提供 `py` 启动器，也可运行：

   ```powershell
   python monkey_timer.py
   ```

## 测试

项目只使用 Python 标准库。运行核心计时逻辑测试：

```powershell
py -m unittest discover -s tests -v
```
