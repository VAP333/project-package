@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: =====================================================================
:: AksharSetu Production Launcher & Controller
:: Subject: Class 8 History (इतिहास व नागरिकशास्त्र, इतिहास विभाग)
:: Reference Implementation Platform for Marathi Educational Intelligence
:: =====================================================================

title AksharSetu System Controller
cd /d "%~dp0"
color 0B

echo.
echo =====================================================================
echo           AKSHARSETU - MARATHI EDUCATIONAL AI PLATFORM
echo            Master Subject Reference: Class 8 History
echo =====================================================================
echo.

:: ---------------------------------------------------------------------
:: 1. DETECT PYTHON ENVIRONMENT
:: ---------------------------------------------------------------------
echo [1/4] Detecting Python environment...
set "PYTHON_EXEC="

:: Check virtual environment in workspace first
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXEC=%~dp0.venv\Scripts\python.exe"
    goto :python_found
)
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXEC=%~dp0venv\Scripts\python.exe"
    goto :python_found
)

:: Check if python is accessible in current PATH
where python >nul 2>&1
if !errorlevel! equ 0 (
    python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXEC=python"
        goto :python_found
    )
)

:: Check py launcher
where py >nul 2>&1
if !errorlevel! equ 0 (
    py -3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXEC=py -3"
        goto :python_found
    )
)

:: Search known standard Windows install paths
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%P (
        set "PYTHON_EXEC=%%~P"
        goto :python_found
    )
)

:python_found
if "%PYTHON_EXEC%"=="" (
    echo [ERROR] Python 3.9+ was not found on your system!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Ensure "Add Python to PATH" is checked during installation.
    echo.
    pause
    exit /b 1
)
echo       Found Python: %PYTHON_EXEC%

:: ---------------------------------------------------------------------
:: 2. DETECT NODE / NPM ENVIRONMENT
:: ---------------------------------------------------------------------
echo [2/4] Detecting Node / npm environment...
set "NPM_EXEC="

where npm >nul 2>&1
if !errorlevel! equ 0 (
    set "NPM_EXEC=npm"
    goto :npm_found
)

where bun >nul 2>&1
if !errorlevel! equ 0 (
    set "NPM_EXEC=bun"
    goto :npm_found
)

if exist "C:\Program Files\nodejs\npm.cmd" (
    set "NPM_EXEC=C:\Program Files\nodejs\npm.cmd"
    goto :npm_found
)
if exist "%ProgramFiles%\nodejs\npm.cmd" (
    set "NPM_EXEC=%ProgramFiles%\nodejs\npm.cmd"
    goto :npm_found
)
if exist "%LOCALAPPDATA%\Programs\nodejs\npm.cmd" (
    set "NPM_EXEC=%LOCALAPPDATA%\Programs\nodejs\npm.cmd"
    goto :npm_found
)
if exist "%APPDATA%\npm\npm.cmd" (
    set "NPM_EXEC=%APPDATA%\npm\npm.cmd"
    goto :npm_found
)
if exist "%LOCALAPPDATA%\nvm\npm.cmd" (
    set "NPM_EXEC=%LOCALAPPDATA%\nvm\npm.cmd"
    goto :npm_found
)
if exist "%ProgramData%\nvm\npm.cmd" (
    set "NPM_EXEC=%ProgramData%\nvm\npm.cmd"
    goto :npm_found
)
if exist "%USERPROFILE%\.fnm\current\npm.cmd" (
    set "NPM_EXEC=%USERPROFILE%\.fnm\current\npm.cmd"
    goto :npm_found
)
if exist "%USERPROFILE%\.volta\bin\npm.cmd" (
    set "NPM_EXEC=%USERPROFILE%\.volta\bin\npm.cmd"
    goto :npm_found
)
if exist "%USERPROFILE%\.bun\bin\bun.exe" (
    set "NPM_EXEC=%USERPROFILE%\.bun\bin\bun.exe"
    goto :npm_found
)

:: Direct node check
where node >nul 2>&1
if !errorlevel! equ 0 (
    set "NPM_EXEC=node"
    goto :npm_found
)
if exist "C:\Program Files\nodejs\node.exe" (
    set "NPM_EXEC=C:\Program Files\nodejs\node.exe"
    goto :npm_found
)

:npm_found
if "%NPM_EXEC%"=="" (
    echo [ERROR] Node.js or npm was not found on your system!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo       Found JS Runtime: %NPM_EXEC%

:: ---------------------------------------------------------------------
:: 3. VERIFY AND ENSURE DEPENDENCIES
:: ---------------------------------------------------------------------
echo [3/4] Verifying dependencies...

:: Verify Python required libraries
"%PYTHON_EXEC%" -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if !errorlevel! neq 0 (
    echo       [INSTALL] Installing missing backend packages: fastapi, uvicorn, pydantic
    "%PYTHON_EXEC%" -m pip install --quiet fastapi uvicorn pydantic python-multipart httpx pytest
)

:: Verify frontend node_modules
if not exist "%~dp0node_modules" (
    echo       [INSTALL] node_modules missing. Running npm install
    call "%NPM_EXEC%" install
)
echo       Dependencies verified.

:: ---------------------------------------------------------------------
:: 4. FREE OCCUPIED PORTS IF ANY (PORT 8000, 8080 & 3000)
:: ---------------------------------------------------------------------
echo [4/4] Checking ports 8000, 8080, and 3000...
for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":8000 .*LISTENING"') do (
    echo       Releasing stale process on port 8000 PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":8080 .*LISTENING"') do (
    echo       Releasing stale process on port 8080 PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":3000 .*LISTENING"') do (
    echo       Releasing stale process on port 3000 PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: ---------------------------------------------------------------------
:: 5. LAUNCH BACKEND & FRONTEND
:: ---------------------------------------------------------------------
echo.
echo =====================================================================
echo Starting AksharSetu Services...
echo =====================================================================

start "AksharSetu Backend" "%~dp0run_backend.bat"
start "AksharSetu Frontend" "%~dp0run_frontend.bat"

echo Waiting 6 seconds for services to initialize...
timeout /t 6 /nobreak >nul 2>&1 || ping -n 7 127.0.0.1 >nul 2>&1

:: Launch browser to frontend
start http://localhost:8080

:: ---------------------------------------------------------------------
:: 6. INTERACTIVE MANAGEMENT DASHBOARD
:: ---------------------------------------------------------------------
:menu_loop
cls
echo.
echo =====================================================================
echo                AKSHARSETU SYSTEM CONTROLLER
echo =====================================================================
echo  [STATUS] Both Backend and Frontend services are running!
echo.
echo  ACCESS URLS:
echo   - Frontend Application : http://localhost:8080
echo   - History Reader UI    : http://localhost:8080/read
echo   - Library Hub          : http://localhost:8080/library
echo   - Backend Swagger Docs : http://127.0.0.1:8000/docs
echo   - Health Check API     : http://127.0.0.1:8000/health
echo =====================================================================
echo  AVAILABLE ACTIONS:
echo   [1] Open Frontend in Browser       (http://localhost:8080)
echo   [2] Open Reader UI in Browser      (http://localhost:8080/read)
echo   [3] Open API Docs in Browser       (http://127.0.0.1:8000/docs)
echo   [4] Run History Subject Engine Tests (15-point verification)
echo   [5] Run Science Subject Engine Tests (Class 8 Science verification)
echo   [6] Restart Backend Service (Port 8000)
echo   [7] Restart Frontend Service
echo   [Q] Stop All Services and Exit
echo =====================================================================
echo.
set /p USER_CHOICE="Select an option (1-7 or Q): "

if /i "%USER_CHOICE%"=="1" (
    start http://localhost:8080
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="2" (
    start http://localhost:8080/read
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="3" (
    start http://127.0.0.1:8000/docs
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="4" (
    echo.
    echo Running History Subject Engine test suite...
    set PYTHONPATH=%~dp0;%PYTHONPATH%
    "%PYTHON_EXEC%" -m pytest eval/test_history_subject_engine.py -v
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="5" (
    echo.
    echo Running Science Subject Engine test suite...
    set PYTHONPATH=%~dp0;%PYTHONPATH%
    "%PYTHON_EXEC%" -m pytest eval/test_science_subject_engine.py -v
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="6" (
    echo.
    echo Restarting Backend...
    for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":8000 .*LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
    start "AksharSetu Backend" "%~dp0run_backend.bat"
    echo Backend restarted.
    timeout /t 2 /nobreak >nul
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="7" (
    echo.
    echo Restarting Frontend...
    for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":8080 .*LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":3000 .*LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
    start "AksharSetu Frontend" "%~dp0run_frontend.bat"
    echo Frontend restarted.
    timeout /t 2 /nobreak >nul
    goto :menu_loop
)
if /i "%USER_CHOICE%"=="Q" (
    goto :shutdown
)

goto :menu_loop

:shutdown
echo.
echo Shutting down AksharSetu services...
for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":8000 .*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano -p tcp ^| findstr /R /C:":3000 .*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo All services stopped cleanly. Goodbye!
timeout /t 2 /nobreak >nul
exit /b 0
