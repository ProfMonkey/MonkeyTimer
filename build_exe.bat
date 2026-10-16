@echo off
setlocal

py -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    py -m pip install pyinstaller
)

py -m PyInstaller --onefile --windowed --name MonkeyTimer monkey_timer.py
if errorlevel 1 (
    echo Packaging failed.
    pause
    exit /b 1
)

echo Created dist\MonkeyTimer.exe
pause
