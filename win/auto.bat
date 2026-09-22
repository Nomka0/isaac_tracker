@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
set "ROOT_DIR=%CD%"
popd

set "BACKUP_DIR=%ROOT_DIR%\save_backups"
set "GUIDE_MD=%ROOT_DIR%\GUIA_PROXIMOS_DESBLOQUEOS.md"
set "ENRICHER=%ROOT_DIR%\isaac_enricher.py"
set "GENERATOR=%ROOT_DIR%\generate_guide.py"

echo ====================================================
echo     Iniciando sincronizacion de partida Isaac (Win)
echo ====================================================

:: 1. Detectar comando de Python funcional
set "PY_CMD="
py -3 -c "import sys" >nul 2>&1 && set "PY_CMD=py -3"
if not defined PY_CMD (
    python -c "import sys" >nul 2>&1 && set "PY_CMD=python"
)

if not defined PY_CMD (
    echo [ERROR] Python no esta instalado, no funciona o no se encuentra en el PATH.
    echo.
    echo 1. Descarga Python 3.10+ desde https://www.python.org/downloads/
    echo 2. IMPORTANTE: En el instalador marca la casilla "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

:: Verificar dependencias (instalar automaticamente si faltan)
%PY_CMD% -c "import jinja2" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Instalando dependencias requeridas (jinja2)...
    %PY_CMD% -m pip install -r "%SCRIPT_DIR%requirements.txt" >nul 2>&1
)

:: 2. Sincronizar respaldos desde carpetas de Isaac en Windows
echo.
echo [1/4] Buscando carpeta de guardados de Isaac en Windows...

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

set "STEAM_SAVE_DIR="
set "CANDIDATES="%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\save_backups" "%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups" "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance\save_backups" "%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance\save_backups" "%USERPROFILE%\Documents\My Games\Binding of Isaac Afterbirth+\save_backups" "%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Afterbirth+\save_backups" "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+" "%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance""

for %%D in (%CANDIDATES%) do (
    if not defined STEAM_SAVE_DIR (
        if exist %%D (
            set "STEAM_SAVE_DIR=%%~fD"
        )
    )
)

if defined STEAM_SAVE_DIR (
    echo       [OK] Origen detectado: "!STEAM_SAVE_DIR!"
    copy /y "!STEAM_SAVE_DIR!\*persistentgamedata*.dat" "%BACKUP_DIR%\" >nul 2>&1
    echo       [OK] Archivos de guardado copiados a save_backups\
) else (
    echo       [INFO] No se encontro ruta estandar de guardados. Usando existentes en save_backups\.
)

:: 3. Determinar el guardado mas reciente
echo.
echo [2/4] Identificando guardados mas recientes...
set "LATEST="
set "PREVIOUS="
for /f "tokens=1* delims==" %%A in ('%PY_CMD% "%ENRICHER%" --find-saves "%BACKUP_DIR%" 2^>nul') do (
    set "%%A=%%B"
)

if not defined LATEST (
    echo [ERROR] No se encontraron archivos de guardado validos en: %BACKUP_DIR%
    echo Asegurate de haber jugado al menos una partida en Isaac o copia tu archivo persistentgamedata1.dat a save_backups\
    echo.
    pause
    exit /b 1
)

echo       [OK] Guardado actual: %LATEST%
if defined PREVIOUS echo       [INFO] Guardado previo: %PREVIOUS%

:: 4. Generar guia con analisis IA
echo.
echo [3/4] Generando guia estrategica con Python...
if defined PREVIOUS (
    %PY_CMD% "%ENRICHER%" "%LATEST%" "%PREVIOUS%" | %PY_CMD% "%GENERATOR%" -o "%GUIDE_MD%"
) else (
    %PY_CMD% "%ENRICHER%" "%LATEST%" | %PY_CMD% "%GENERATOR%" -o "%GUIDE_MD%"
)

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Fallo en la ejecucion del generador de guia.
    pause
    exit /b %ERRORLEVEL%
)

:: 5. Verificacion final
echo.
echo [4/4] Verificando resultado...
if exist "%GUIDE_MD%" (
    echo       [OK] Guia actualizada exitosamente en:
    echo            %GUIDE_MD%
) else (
    echo       [WARN] No se detecto el archivo generado.
)

echo.
echo ====================================================
echo   ¡Sincronizacion completada con exito!
echo   Abre GUIA_PROXIMOS_DESBLOQUEOS.md en Obsidian
echo   para ver tus progresos e iconos interactivos.
echo ====================================================
echo.
pause
