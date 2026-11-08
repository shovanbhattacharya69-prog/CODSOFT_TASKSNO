@echo off
title Build Standalone Executable - TaskMaster Pro
cd /d "%~dp0"

echo ========================================================
echo  TaskMaster Pro - Standalone Windows Executable Builder
echo  Asset Reference: cf772cd9-6178-4b38-b3a8-ee99efa59dc3
echo ========================================================
echo.

:: Check PyInstaller
py -m pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo PyInstaller is not installed. Installing PyInstaller...
    py -m pip install pyinstaller
)

echo Building single-file executable...
py -m PyInstaller --onefile --windowed --name "TaskMaster_Pro" --clean main.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo  Build Successful!
    echo  Your standalone executable is ready in the \dist folder:
    echo  %~dp0dist\TaskMaster_Pro.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed. Please check output messages above.
)

echo.
pause
