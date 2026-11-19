@echo off
setlocal enabledelayedexpansion

:: ---------------------------------------------------------------------------
:: 0. PARSE CLI FLAGS (e.g. --force-fallback)
:: ---------------------------------------------------------------------------
set "PASSTHROUGH_ARGS="

:parse_args
if "%~1"=="" goto :done_parse_args
if /i "%~1"=="--force-fallback" (
    set "KYKLOI_FORCE_FALLBACK=1"
) else (
    set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %1"
)
shift
goto :parse_args
:done_parse_args

:: ---------------------------------------------------------------------------
:: 1. CONFIGURATION & VERSION CONSTRAINTS
:: ---------------------------------------------------------------------------
if "%REQ_MAJ%"=="" set "REQ_MAJ=3"
if "%REQ_MIN%"=="" set "REQ_MIN=10"

set "USE_HOST=0"

:: ---------------------------------------------------------------------------
:: 2. EVALUATE HOST PYTHON (Bypassed if KYKLOI_FORCE_FALLBACK=1)
:: ---------------------------------------------------------------------------
if not "%KYKLOI_FORCE_FALLBACK%"=="1" (
    where python >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "HOST_MAJOR="
        set "HOST_MINOR="
        for /f "tokens=1,2 delims=." %%a in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do (
            set "HOST_MAJOR=%%a"
            set "HOST_MINOR=%%b"
        )
        if defined HOST_MAJOR if defined HOST_MINOR (
            if "!HOST_MAJOR!"=="%REQ_MAJ%" (
                if !HOST_MINOR! geq %REQ_MIN% (
                    set "USE_HOST=1"
                )
            )
        )
    )
)

if "%USE_HOST%"=="1" goto :run_host_python
goto :skip_host_python

:run_host_python
for /f "delims=" %%i in ('where python') do (
    set "HOST_PATH=%%i"
    goto :host_resolved
)
:host_resolved
echo [Kykloi] Using host Python runtime: !HOST_PATH! (!HOST_MAJOR!.!HOST_MINOR!)
python system\launch.py %PASSTHROUGH_ARGS%
exit /b %ERRORLEVEL%

:skip_host_python

:: ---------------------------------------------------------------------------
:: 3. HYDRATE RUNTIME FROM LOCAL ARCHIVE (WITH SHA-256 VERIFICATION)
:: ---------------------------------------------------------------------------
set "SCRIPT_DIR=%~dp0"

:: Architecture Detection (x86_64 vs ARM64)
set "TARGET=windows-x86_64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "TARGET=windows-arm64"
if /i "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "TARGET=windows-arm64"

set "MANIFEST_PATH=%SCRIPT_DIR%system\tools\tools-manifest.json"
set "RUNTIME_ROOT=%TEMP%\kykloi_runtime_%TARGET%"
set "LOCAL_PY=%RUNTIME_ROOT%\python.exe"
set "STAMP_FILE=%RUNTIME_ROOT%\.verified_sha256"

if not exist "%LOCAL_PY%" goto :hydrate_runtime
if not exist "%STAMP_FILE%" goto :hydrate_runtime
goto :execute_runtime

:hydrate_runtime
if not exist "%MANIFEST_PATH%" (
    echo [FATAL] Tool manifest missing: %MANIFEST_PATH%
    pause
    exit /b 1
)

echo [Kykloi] Querying manifest definitions for %TARGET%...
:: Atomic single-process extraction to avoid multi-invocation latency
for /f "usebackq tokens=1,2 delims=|" %%A in (`powershell -NoProfile -Command "$m=(Get-Content -Raw '%MANIFEST_PATH%' | ConvertFrom-Json).tools.python.targets.'%TARGET%'; if($m){Write-Output ($m.archive + '|' + $m.sha256)}" 2^>nul`) do (
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
for /f "skip=1 tokens=*" %%H in ('certutil -hashfile "%ARCHIVE_PY%" SHA256 2^>nul') do (
    set "RAW_HASH=%%H"
    goto :hash_extracted
)
:hash_extracted
set "ACTUAL_SHA=!RAW_HASH: =!"

if /i not "!ACTUAL_SHA!"=="!EXPECTED_SHA!" (
    echo [FATAL] Checksum verification failed for %ARCHIVE_NAME%
    echo         Expected: !EXPECTED_SHA!
    echo         Actual:   !ACTUAL_SHA!
    pause
    exit /b 1
)

echo [Kykloi] Checksum verified. Extracting portable Python runtime to %RUNTIME_ROOT%...
if exist "%RUNTIME_ROOT%" rmdir /s /q "%RUNTIME_ROOT%" >nul 2>&1
mkdir "%RUNTIME_ROOT%" >nul 2>&1
tar -xzf "%ARCHIVE_PY%" -C "%RUNTIME_ROOT%" --strip-components=1
<nul set /p="!ACTUAL_SHA!" > "%STAMP_FILE%"

:execute_runtime

:: ---------------------------------------------------------------------------
:: 4. EXECUTE APPLICATION LAUNCHER
:: ---------------------------------------------------------------------------
echo [Kykloi] Using fallback Python runtime: %LOCAL_PY%
"%LOCAL_PY%" "%SCRIPT_DIR%system\launch.py" %PASSTHROUGH_ARGS%
exit /b %ERRORLEVEL%
