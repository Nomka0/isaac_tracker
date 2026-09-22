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

:: 1. Detectar comando de Python
set "PY_CMD="
where py >nul 2>&1 && set "PY_CMD=py -3"
if not defined PY_CMD (
    where python >nul 2>&1 && set "PY_CMD=python"
)

if not defined PY_CMD (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    echo Instala Python 3.10+ desde python.org o Microsoft Store.
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

set "STEAM_SAVE_DIR=%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\save_backups"
if not exist "!STEAM_SAVE_DIR!" (
    set "STEAM_SAVE_DIR=%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups"
)

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

if exist "!STEAM_SAVE_DIR!" (
    echo       [OK] Origen detectado: "!STEAM_SAVE_DIR!"
    copy /y "!STEAM_SAVE_DIR!\*.rep+persistentgamedata1.dat" "%BACKUP_DIR%\" >nul 2>&1
    echo       [OK] Archivos de guardado copiados a save_backups\
) else (
    echo       [INFO] No se encontro la ruta estandar de Steam Documents. Usando respaldos existentes en save_backups\.
)

:: 3. Determinar el guardado mas reciente
echo.
echo [2/4] Identificando guardados mas recientes...
set "TEMP_VARS=%TEMP%\isaac_saves_%RANDOM%.bat"
%PY_CMD% "%ENRICHER%" --find-saves "%BACKUP_DIR%" > "%TEMP_VARS%"
call "%TEMP_VARS%"
del "%TEMP_VARS%" >nul 2>&1

if not defined LATEST (
    echo [ERROR] No se encontraron archivos de guardado validos en: %BACKUP_DIR%
    pause
    exit /b 1
)

echo       [OK] Guardado actual: %LATEST%
if defined PREVIOUS echo       [INFO] Guardado previo: %PREVIOUS%

:: 4. Generar guia con analisis IA
echo.
echo [3/4] Generando guia estrategica con Python y IA...
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
echo Sincronizacion completada con exito.
timeout /t 5 >nul
