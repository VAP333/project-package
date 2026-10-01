@echo off
setlocal EnableExtensions EnableDelayedExpansion
title AksharSetu Backend (FastAPI :8000)
cd /d "%~dp0"
color 0A

echo ==============================================================
echo       AksharSetu Backend Engine (FastAPI on Port 8000)
echo       Master Subject: Class 8 History
echo ==============================================================
echo.

set "PY="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY=%~dp0.venv\Scripts\python.exe"
    goto :py_found
)
if exist "%~dp0venv\Scripts\python.exe" (
    set "PY=%~dp0venv\Scripts\python.exe"
    goto :py_found
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY=python"
    goto :py_found
)

for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Python312\python.exe"
) do (
    if exist %%P (
        set "PY=%%~P"
        goto :py_found
    )
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY=py -3"
    goto :py_found
)

:py_found
if "%PY%"=="" (
    echo [ERROR] Python 3.9+ was not found on your system!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Using Python: %PY%
set PYTHONPATH=%~dp0;%PYTHONPATH%
echo Running: %PY% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
echo.

"%PY%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Backend exited with error code %errorlevel%.
    pause
)
