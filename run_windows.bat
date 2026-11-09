@echo off
rem ===========================================================================
rem run_windows.bat - Project Kykloi Portable USB Launcher (Windows)
rem ===========================================================================
setlocal EnableDelayedExpansion

cd /d "%~dp0"
title Project Kykloi

echo === Initializing Kykloi Local Appliance ===

rem 1. Identify Python executable
set PYTHON_BIN=
where py.exe >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_BIN=py -3
) else (
    where python.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_BIN=python
    ) else (
        echo [ERROR] Python 3 was not found on your system PATH.
        echo Please install Python 3.12+ from python.org to run Kykloi.
        pause
        exit /b 1
    )
)

rem 2. Check if artifacts exist; build if missing
if not exist "dist\index.html" (
    echo [INFO] Artifacts missing in dist\. Running initial build...
    %PYTHON_BIN% build\build_site.py
    if !errorlevel! neq 0 (
        echo [ERROR] Build step failed.
        pause
        exit /b 1
    )
)

rem 3. Launch HTTP daemon with automatic browser opening
echo [INFO] Starting local daemon and opening browser...
%PYTHON_BIN% serve.py --browser

pause
