@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "REQ_FILE=%SCRIPT_DIR%requirements.txt"

echo ====================================================
echo   Instalador de Dependencias - Isaac Guide (Win)
echo ====================================================
echo.

:: 1. Detectar comando de Python
set "PY_CMD="
where py >nul 2>&1 && set "PY_CMD=py -3"
if not defined PY_CMD (
    where python >nul 2>&1 && set "PY_CMD=python"
)

if not defined PY_CMD (
    echo [ERROR] No se encontro Python en el sistema.
    echo.
    echo Por favor instala Python 3.10+ desde https://www.python.org/
    echo IMPORTANTE: Marca la casilla "Add python.exe to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado:
%PY_CMD% --version
echo.

:: 2. Actualizar pip e instalar dependencias
echo [1/2] Actualizando pip...
%PY_CMD% -m pip install --upgrade pip >nul 2>&1

echo [2/2] Instalando paquetes desde requirements.txt...
if exist "%REQ_FILE%" (
    %PY_CMD% -m pip install -r "%REQ_FILE%"
) else (
    %PY_CMD% -m pip install "jinja2>=3.0.0"
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Ocurrio un error al instalar las dependencias con pip.
    pause
    exit /b %ERRORLEVEL%
)

:: 3. Verificar importacion de jinja2
echo.
echo Verificando instalacion...
%PY_CMD% -c "import jinja2; print('✔ Jinja2 importado correctamente (v' + jinja2.__version__ + ')')" 2>nul

if %ERRORLEVEL% equ 0 (
    echo.
    echo ====================================================
    echo   ¡Todas las dependencias se instalaron con exito!
    echo ====================================================
    echo Ya puedes ejecutar auto.bat para sincronizar tu partida.
) else (
    echo [ERROR] No se pudo verificar la libreria Jinja2.
)

echo.
pause
