@echo off
setlocal EnableDelayedExpansion

title Isaac Tracker & Guide Generator

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
set "ROOT_DIR=%CD%"
popd

set "BACKUP_DIR=%ROOT_DIR%\save_backups"
set "GUIDE_MD=%ROOT_DIR%\GUIA_PROXIMOS_DESBLOQUEOS.md"
set "GENERATOR=%ROOT_DIR%\generate_guide.py"

echo ====================================================
echo     Isaac Tracker - Sincronizacion de Partida
echo ====================================================
echo.

:: 1. Detectar Python
echo [1/4] Buscando Python...
set "PY_CMD="

py -3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py -3"
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=python"
    )
)

if not defined PY_CMD (
    echo.
    echo ====================================================
    echo [ERROR] Python 3 no esta instalado o no esta en el PATH.
    echo.
    echo 1. Descarga Python 3 desde: https://www.python.org/downloads/
    echo 2. IMPORTANTE: En el instalador marca la casilla:
    echo    "Add python.exe to PATH"
    echo 3. Tras instalar, vuelve a ejecutar este archivo.
    echo ====================================================
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('%PY_CMD% --version 2^>^&1') do echo       [OK] %%V detectado.

:: 2. Dependencias
echo.
echo [2/4] Verificando dependencias (jinja2)...
%PY_CMD% -c "import jinja2" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo       Instalando jinja2...
    %PY_CMD% -m pip install jinja2
    if %ERRORLEVEL% neq 0 (
        echo.
        echo [ERROR] No se pudo instalar jinja2. Verifica tu conexion a internet.
        pause
        exit /b 1
    )
)
echo       [OK] Dependencias listas.

:: 3. Copiar partidas
echo.
echo [3/4] Buscando partidas de The Binding of Isaac...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

set "SRC_DIR="
if exist "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\save_backups" set "SRC_DIR=%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\save_backups"
if not defined SRC_DIR if exist "%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups" set "SRC_DIR=%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups"
if not defined SRC_DIR if exist "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance\save_backups" set "SRC_DIR=%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance\save_backups"
if not defined SRC_DIR if exist "%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance\save_backups" set "SRC_DIR=%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance\save_backups"
if not defined SRC_DIR if exist "%USERPROFILE%\Documents\My Games\Binding of Isaac Afterbirth+\save_backups" set "SRC_DIR=%USERPROFILE%\Documents\My Games\Binding of Isaac Afterbirth+\save_backups"
if not defined SRC_DIR if exist "%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Afterbirth+\save_backups" set "SRC_DIR=%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Afterbirth+\save_backups"
if not defined SRC_DIR if exist "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+" set "SRC_DIR=%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+"
if not defined SRC_DIR if exist "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance" set "SRC_DIR=%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance"

if defined SRC_DIR (
    echo       [OK] Origen detectado: "!SRC_DIR!"
    copy /y "!SRC_DIR!\*persistentgamedata*.dat" "%BACKUP_DIR%\" >nul 2>&1
    echo       [OK] Guardados actualizados en save_backups\
) else (
    echo       [INFO] No se encontro ruta estandar en Documentos. Usando respaldos en save_backups\.
)

:: 4. Generar guia
echo.
echo [4/4] Analizando progreso y generando guia...
%PY_CMD% "%GENERATOR%" --no-ai -o "%GUIDE_MD%"
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Ocurrio un fallo al procesar las partidas.
    echo Verifica que tengas al menos un archivo *.dat en la carpeta save_backups\
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================
echo   [EXITO] Guia actualizada correctamente:
echo   %GUIDE_MD%
echo.
echo   Abrela en Obsidian o tu visor Markdown preferido.
echo ====================================================
echo.
pause
