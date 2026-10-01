@echo off
setlocal EnableExtensions EnableDelayedExpansion
title AksharSetu Frontend (Vite Dev Server)
cd /d "%~dp0"
color 0E

echo ==============================================================
echo       AksharSetu Frontend Dev Server
echo ==============================================================
echo.

set "FRONTEND_CMD="

:: 1. Check npm in PATH
where npm >nul 2>&1
if !errorlevel! equ 0 (
    set "FRONTEND_CMD=npm run dev"
    goto :launch_frontend
)

:: 2. Check bun in PATH
where bun >nul 2>&1
if !errorlevel! equ 0 (
    set "FRONTEND_CMD=bun run dev"
    goto :launch_frontend
)

:: 3. Check C:\Program Files\nodejs\npm.cmd
if exist "C:\Program Files\nodejs\npm.cmd" (
    set "FRONTEND_CMD="C:\Program Files\nodejs\npm.cmd" run dev"
    goto :launch_frontend
)

:: 4. Check ProgramFiles environment variable
if exist "%ProgramFiles%\nodejs\npm.cmd" (
    set "FRONTEND_CMD="%ProgramFiles%\nodejs\npm.cmd" run dev"
    goto :launch_frontend
)

:: 5. Check direct node execution of vite
if exist "C:\Program Files\nodejs\node.exe" (
    if exist "%~dp0node_modules\vite\bin\vite.js" (
        set "FRONTEND_CMD="C:\Program Files\nodejs\node.exe" "%~dp0node_modules\vite\bin\vite.js""
        goto :launch_frontend
    )
)

:: 6. Check LocalAppData / AppData
if exist "%LOCALAPPDATA%\Programs\nodejs\npm.cmd" (
    set "FRONTEND_CMD="%LOCALAPPDATA%\Programs\nodejs\npm.cmd" run dev"
    goto :launch_frontend
)
if exist "%APPDATA%\npm\npm.cmd" (
    set "FRONTEND_CMD="%APPDATA%\npm\npm.cmd" run dev"
    goto :launch_frontend
)
if exist "%USERPROFILE%\.bun\bin\bun.exe" (
    set "FRONTEND_CMD="%USERPROFILE%\.bun\bin\bun.exe" run dev"
    goto :launch_frontend
)

:: 7. Check if node is in PATH
where node >nul 2>&1
if !errorlevel! equ 0 (
    if exist "%~dp0node_modules\vite\bin\vite.js" (
        set "FRONTEND_CMD=node "%~dp0node_modules\vite\bin\vite.js""
        goto :launch_frontend
    )
)

:launch_frontend
if "%FRONTEND_CMD%"=="" (
    echo [ERROR] Neither Node.js, npm, nor bun could be located.
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Starting Frontend with: %FRONTEND_CMD%
echo.

call %FRONTEND_CMD%
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Frontend server stopped with code %errorlevel%.
    pause
)
