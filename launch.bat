@echo on
setlocal EnableExtensions EnableDelayedExpansion

:: ---------------------------------------------------------------------------
:: 0. INITIALIZATION & SCRIPT ROOT
:: ---------------------------------------------------------------------------
echo [Kykloi] Windows Launcher initialized. Assessing environment...

set "SCRIPT_DIR=%~dp0"
if "%REQ_MAJ%"=="" set "REQ_MAJ=3"
if "%REQ_MIN%"=="" set "REQ_MIN=10"
set "KYKLOI_FORCE_FALLBACK=0"
set "PASSTHROUGH_ARGS="
set "USE_HOST=0"
set "HOST_EXEC="

:: ---------------------------------------------------------------------------
:: 1. PARSE CLI FLAGS (e.g. --force-fallback)
:: ---------------------------------------------------------------------------
:parse_args
if "%~1"=="" goto done_parse_args
if /i "%~1"=="--force-fallback" (
    set "KYKLOI_FORCE_FALLBACK=1"
) else (
    set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %1"
)
shift
goto parse_args
:done_parse_args

:: ---------------------------------------------------------------------------
rem 2. EVALUATE HOST PYTHON
:: ---------------------------------------------------------------------------
if "%KYKLOI_FORCE_FALLBACK%"=="1" (
    echo [Kykloi] Host probing bypassed [--force-fallback requested].
    goto hydrate_runtime_start
)

echo [Kykloi] Probing host system for Python ^>= %REQ_MAJ%.%REQ_MIN%...

rem 1. Probe py launcher and standard PATH candidates
call :probe_candidate "py -3"
if "!USE_HOST!"=="1" goto host_python_found

call :probe_candidate "python"
if "!USE_HOST!"=="1" goto host_python_found

call :probe_candidate "python3"
if "!USE_HOST!"=="1" goto host_python_found

rem 2. Probe standard Windows installation directories
call :probe_directory_roots
if "!USE_HOST!"=="1" goto host_python_found

echo [Kykloi] No compatible host Python runtime discovered on system.
goto hydrate_runtime_start

:host_python_found
echo [Kykloi] Using host Python runtime: !HOST_EXEC! (!HOST_MAJOR!.!HOST_MINOR!)
!HOST_EXEC! "%SCRIPT_DIR%system\launch.py" %PASSTHROUGH_ARGS%
exit /b !ERRORLEVEL!

:hydrate_runtime_start

:: ---------------------------------------------------------------------------
:: 3. HYDRATE RUNTIME FROM LOCAL ARCHIVE
:: ---------------------------------------------------------------------------
rem Detect Target Architecture (x86_64 vs ARM64)
set "TARGET=windows-x86_64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "TARGET=windows-arm64"
if /i "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "TARGET=windows-arm64"

set "MANIFEST_PATH=%SCRIPT_DIR%system\tools\tools-manifest.json"

if not "%KYKLOI_RUNTIME_DIR%"=="" (
    set "RUNTIME_ROOT=%KYKLOI_RUNTIME_DIR%\runtime_%TARGET%"
) else (
    set "RUNTIME_ROOT=%TEMP%\kykloi_runtime_%TARGET%"
)

set "LOCAL_PY=%RUNTIME_ROOT%\python.exe"
set "STAMP_FILE=%RUNTIME_ROOT%\.verified_sha256"

if exist "%LOCAL_PY%" if exist "%STAMP_FILE%" goto execute_runtime

if not exist "%MANIFEST_PATH%" (
    echo [FATAL] Tool manifest missing: %MANIFEST_PATH%
    pause
    exit /b 1
)

echo [Kykloi] Querying manifest definitions for %TARGET%...
set "ARCHIVE_NAME="
set "EXPECTED_SHA="

rem Extract archive name and sha256 using PowerShell
for /f "usebackq tokens=1,2 delims=|" %%A in (`powershell -NoProfile -Command "$j = (Get-Content '%MANIFEST_PATH%' -Raw | ConvertFrom-Json).tools.python.targets.'%TARGET%'; Write-Output ($j.archive + '|' + $j.sha256)" 2^>nul`) do (
    set "ARCHIVE_NAME=%%A"
    set "EXPECTED_SHA=%%B"
)

if "%ARCHIVE_NAME%"=="" (
    echo [FATAL] Failed to extract manifest parameters for target %TARGET%
    pause
    exit /b 1
)

set "ARCHIVE_PY=%SCRIPT_DIR%system\tools\archives\%ARCHIVE_NAME%"

if not exist "%ARCHIVE_PY%" (
    echo [FATAL] Pre-packaged archive not found: %ARCHIVE_NAME%
    echo         Expected at: %ARCHIVE_PY%
    pause
    exit /b 1
)

echo [Kykloi] Verifying SHA-256 checksum for %ARCHIVE_NAME%...
set "ACTUAL_SHA="
for /f "skip=1 tokens=*" %%H in ('certutil -hashfile "%ARCHIVE_PY%" SHA256 2^>nul') do (
    if not defined ACTUAL_SHA (
        set "RAW_HASH=%%H"
        set "ACTUAL_SHA=!RAW_HASH: =!"
    )
)

if /i not "!ACTUAL_SHA!"=="!EXPECTED_SHA!" (
    echo [FATAL] Checksum verification failed for %ARCHIVE_NAME%
    echo         Expected: !EXPECTED_SHA!
    echo         Actual:   !ACTUAL_SHA!
    pause
    exit /b 1
)

where tar >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ==================== [FATAL ARCHIVE TOOL ERROR] ====================
    echo Kykloi requires the 'tar' utility to extract its portable Python runtime.
    echo Windows 10 [version 1803+] and Windows 11 include 'tar' natively.
    echo.
    echo Remediation Options:
    echo   1. Install Python 3.10+ directly on the host system.
    echo   2. Run on a modern Windows version with native tar support.
    echo ====================================================================
    pause
    exit /b 1
)

echo [Kykloi] Checksum verified. Extracting portable Python runtime to %RUNTIME_ROOT%...
if exist "%RUNTIME_ROOT%" rmdir /s /q "%RUNTIME_ROOT%" >nul 2>&1
mkdir "%RUNTIME_ROOT%" >nul 2>&1
tar -xzf "%ARCHIVE_PY%" -C "%RUNTIME_ROOT%" --strip-components=1
<nul set /p="!ACTUAL_SHA!" > "%STAMP_FILE%"

:execute_runtime
echo [Kykloi] Using fallback Python runtime: %LOCAL_PY%
"%LOCAL_PY%" "%SCRIPT_DIR%system\launch.py" %PASSTHROUGH_ARGS%
exit /b %ERRORLEVEL%

:: ---------------------------------------------------------------------------
:: 4. SUBROUTINES
:: ---------------------------------------------------------------------------

:probe_candidate
set "CMD_TEST=%~1"
if "%CMD_TEST%"=="" exit /b 0

rem Query version safely using sys.version_info
set "HOST_MAJOR="
set "HOST_MINOR="
for /f "tokens=1,2 delims=." %%a in ('%CMD_TEST% -c "import sys; print(str(sys.version_info[0])+'.'+str(sys.version_info[1]))" 2^>nul') do (
    set "HOST_MAJOR=%%a"
    set "HOST_MINOR=%%b"
)

if not defined HOST_MAJOR exit /b 0
if not defined HOST_MINOR exit /b 0

if "%HOST_MAJOR%"=="%REQ_MAJ%" (
    if %HOST_MINOR% geq %REQ_MIN% (
        set "USE_HOST=1"
        set "HOST_EXEC=%CMD_TEST%"
    )
)
exit /b 0

:probe_directory_roots
for /d %%D in (
    "%LOCALAPPDATA%\Programs\Python\Python3*"
    "%ProgramFiles%\Python3*"
) do (
    if "!USE_HOST!"=="0" (
        if exist "%%~D\python.exe" (
            call :probe_candidate "%%~D\python.exe"
        )
    )
)

if not "%ProgramFiles(x86)%"=="" (
    for /d %%D in ("%ProgramFiles(x86)%\Python3*") do (
        if "!USE_HOST!"=="0" (
            if exist "%%~D\python.exe" (
                call :probe_candidate "%%~D\python.exe"
            )
        )
    )
)
exit /b 0
