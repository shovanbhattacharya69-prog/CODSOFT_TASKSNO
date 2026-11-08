@echo off
title Task Master - To-Do List Application
cd /d "%~dp0"

echo Starting Task Master To-Do List Application...

:: 1. Try Python Launcher (py)
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py main.py %*
    goto end
)

:: 2. Try python
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python main.py %*
    goto end
)

:: 3. Try Windows Store Python 3.13 direct binary
set "WIN_STORE_PY=%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
if exist "%WIN_STORE_PY%" (
    "%WIN_STORE_PY%" main.py %*
    goto end
)

:: 4. Fallback: Search common install locations
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" main.py %*
        goto end
    )
)

echo.
echo [ERROR] Python was not found on your system!
echo Please ensure Python 3 is installed and added to your system PATH.
echo.
pause

:end
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with an error code: %ERRORLEVEL%
    pause
)
