# MonkeyTimer V0.2

一个免费的 Windows PPT 演讲倒计时工具。V0.2 在普通倒计时基础上增加了适合演讲时使用的桌面悬浮窗；不包含 PPT 自动识别、双屏控制或 EXE 打包。

## 功能

- 自定义分钟和秒（秒为 0–59）
- 开始、暂停、继续、重置
- 使用 `time.monotonic()` 计时，避免系统时间调整影响倒计时
- 到达 `00:00` 后自动停止
- 对空值、非整数、秒数超范围和零时长给出提示
- 演讲模式：无边框、始终置顶、仅显示倒计时数字
- Windows 下透明背景，减少对 PPT 和其他窗口的遮挡
- 拖动数字可移动悬浮窗；可调整数字字体大小
- 悬停数字可显示精简控制条（暂停/继续、重置、字体大小、退出）
- 键盘快捷键：`F11` 切换演讲模式、`Esc` 退出、`Space` 暂停/继续、`R` 重置、`+`/`-` 调整字体

## 演讲模式说明

在普通窗口中点击“进入演讲模式”。悬浮窗会保持在最前方，Windows 会将品红色背景作为透明色，只留下带黑色阴影的白色数字。阴影能帮助数字同时适应浅色和深色幻灯片。

透明色窗口依赖 Windows 的 Tk 支持；在非 Windows 系统上会降级为同色不透明背景。若个别 Windows 图形驱动对透明置顶窗口表现异常，可按 `Esc` 返回普通窗口继续使用全部计时功能。

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
