@echo off
chcp 65001 >nul
title Isaac Progress Tracker - Guide

:: Comprobar si se abrió desde un zip sin descomprimir
if not exist "%~dp0win\auto.bat" (
    echo [ERROR] No se encuentra win\auto.bat.
    echo Asegurate de DESCOMPRIMIR [Extraer todo] el archivo ZIP antes de ejecutar.
    echo.
    pause
    exit /b 1
)

call "%~dp0win\auto.bat"
