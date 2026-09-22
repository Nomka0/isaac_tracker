@echo off
setlocal

title Isaac Tracker & Guide Generator

if not exist "%~dp0win\auto.bat" (
    echo [ERROR] No se encuentra la carpeta win\ ni el archivo auto.bat.
    echo Asegurate de haber descomprimido el archivo ZIP por completo (Extraer todo).
    echo.
    pause
    exit /b 1
)

call "%~dp0win\auto.bat"
