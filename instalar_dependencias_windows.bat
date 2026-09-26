@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title Instalador de Dependencias Isaac - Windows 10/11

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%win\instalar_dependencias.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] No se encuentra win\instalar_dependencias.ps1.
    echo Asegurate de DESCOMPRIMIR el archivo ZIP antes de ejecutar.
    echo.
    pause
    exit /b 1
)

echo ====================================================
echo   Instalador de Dependencias Isaac (Win 10/11)
echo ====================================================
echo.
echo Iniciando PowerShell con gestion de permisos (UAC)...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [AVISO] El proceso en PowerShell finalizo o requirio aprobacion de permisos.
    pause
)
