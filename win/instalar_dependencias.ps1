<#
.SYNOPSIS
    Instalador automatizado de dependencias para The Binding of Isaac Tracker en Windows 10/11.
.DESCRIPTION
    - Gestiona permisos solicitando elevación de Administrador (UAC) automáticamente si es necesario.
    - Configura política de ejecución (ExecutionPolicy Bypass) y protocolos TLS.
    - Instala Python 3.12 con PATH activado (vía winget o instalador oficial).
    - Instala Jinja2 y dependencias desde requirements.txt.
    - Instala Antigravity CLI (agy) y lo vincula al PATH del usuario.
#>

[CmdletBinding()]
param()

# 1. Gestión de Permisos: Auto-elevar a Administrador (UAC) si no se tienen permisos
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[INFO] Solicitando permisos de Administrador para gestionar dependencias del sistema (UAC)..." -ForegroundColor Yellow
    $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }
    try {
        Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    } catch {
        Write-Host "[ERROR] Se canceló la elevación de permisos UAC." -ForegroundColor Red
    }
    exit
}

# Configuración de consola y protocolos de red
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = (Resolve-Path "$ScriptDir\..").Path
$ReqFile = Join-Path $ScriptDir "requirements.txt"

function Update-SessionEnvironment {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
    $agyBin = "$env:LOCALAPPDATA\agy\bin"
    if (Test-Path $agyBin) {
        if ($env:Path -notlike "*$agyBin*") {
            $env:Path = "$agyBin;$env:Path"
        }
    }
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   Instalador de Dependencias Isaac (Win 10/11)    " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "[OK] Permisos de Administrador concedidos." -ForegroundColor Green

# -----------------------------------------------------------
# PASO 1: Python 3.10+
# -----------------------------------------------------------
Write-Host "`n[1/3] Comprobando instalacion de Python..." -ForegroundColor Yellow
Update-SessionEnvironment

$pyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { $null }

if (-not $pyCmd) {
    Write-Host "      ℹ Python no detectado. Iniciando instalacion desatendida..." -ForegroundColor Cyan
    $installed = $false

    # Intentar instalación con winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "      ⬇ Descargando e instalando Python 3.12 con winget..." -ForegroundColor Gray
        try {
            Start-Process -FilePath "winget" -ArgumentList "install Python.Python.3.12 --scope machine --silent --accept-source-agreements --accept-package-agreements --override `"/passive InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_launcher=1`"" -Wait -NoNewWindow
            Update-SessionEnvironment
            if (Get-Command py -ErrorAction SilentlyContinue -or Get-Command python -ErrorAction SilentlyContinue) {
                $installed = $true
            }
        } catch { }
    }

    # Fallback: Descarga directa del instalador oficial
    if (-not $installed) {
        Write-Host "      ⬇ Descargando instalador oficial de Python 3.12 desde python.org..." -ForegroundColor Gray
        $pythonUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
        $installerPath = Join-Path $env:TEMP "python_installer.exe"
        try {
            Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
            Write-Host "      ⚙ Ejecutando instalador (agregando al PATH del sistema)..." -ForegroundColor Gray
            Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_launcher=1" -Wait
            Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
            Update-SessionEnvironment
        } catch {
            Write-Host "      ❌ Error al descargar el instalador oficial de Python: $_" -ForegroundColor Red
        }
    }
}

Update-SessionEnvironment
$pyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { $null }
if (-not $pyCmd) {
    $commonPy = "$env:ProgramFiles\Python312\python.exe"
    if (Test-Path $commonPy) {
        $env:Path = "$env:ProgramFiles\Python312;$env:ProgramFiles\Python312\Scripts;$env:Path"
        $pyCmd = "python"
    }
}

if ($pyCmd) {
    $pyVersion = if ($pyCmd -eq "py") { & py -3 --version 2>$null } else { & python --version 2>$null }
    Write-Host "      ✔ Python detectado: $pyVersion" -ForegroundColor Green
} else {
    Write-Host "      ❌ No se pudo detectar Python tras la instalacion. Por favor reinicia o instala manualmente." -ForegroundColor Red
}

# -----------------------------------------------------------
# PASO 2: Jinja2 ("jinju") y paquetes pip
# -----------------------------------------------------------
Write-Host "`n[2/3] Instalando dependencias de Python (Jinja2)..." -ForegroundColor Yellow
if ($pyCmd) {
    $runPy = if ($pyCmd -eq "py") { "py -3" } else { "python" }
    
    Write-Host "      ⬇ Actualizando pip..." -ForegroundColor Gray
    cmd /c "$runPy -m pip install --upgrade pip --quiet" | Out-Null

    Write-Host "      ⬇ Instalando Jinja2..." -ForegroundColor Gray
    if (Test-Path $ReqFile) {
        cmd /c "$runPy -m pip install -r `"$ReqFile`" --quiet" | Out-Null
    } else {
        cmd /c "$runPy -m pip install `"jinja2>=3.0.0`" --quiet" | Out-Null
    }

    $jinjaVer = cmd /c "$runPy -c `"import jinja2; print(jinja2.__version__)`"" 2>$null
    if ($jinjaVer) {
        Write-Host "      ✔ Jinja2 verificado exitosamente (v$jinjaVer)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠ Advertencia: No se pudo verificar la importación de Jinja2." -ForegroundColor Yellow
    }
} else {
    Write-Host "      ⚠ Omitiendo pip por falta de ejecutable de Python." -ForegroundColor Yellow
}

# -----------------------------------------------------------
# PASO 3: Antigravity CLI (agy)
# -----------------------------------------------------------
Write-Host "`n[3/3] Comprobando CLI de Antigravity (agy)..." -ForegroundColor Yellow
Update-SessionEnvironment

$agyCmd = Get-Command agy -ErrorAction SilentlyContinue
$agyExe = "$env:LOCALAPPDATA\agy\bin\agy.exe"

if (-not $agyCmd -and -not (Test-Path $agyExe)) {
    Write-Host "      ⬇ Descargando e instalando Antigravity CLI (agy)..." -ForegroundColor Cyan
    try {
        Invoke-Expression (Invoke-RestMethod -Uri "https://antigravity.google/cli/install.ps1")
    } catch {
        Write-Host "      ℹ Intentando método cmd alternativo..." -ForegroundColor Gray
        $cmdInstaller = Join-Path $env:TEMP "install_agy.cmd"
        try {
            Invoke-WebRequest -Uri "https://antigravity.google/cli/install.cmd" -OutFile $cmdInstaller -UseBasicParsing
            Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$cmdInstaller`"" -Wait
            Remove-Item $cmdInstaller -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "      ⚠ Error al obtener el instalador de agy: $_" -ForegroundColor Yellow
        }
    }
}

# Vincular %LOCALAPPDATA%\agy\bin al PATH de usuario de Windows de forma permanente
$agyBinDir = "$env:LOCALAPPDATA\agy\bin"
if (Test-Path $agyExe) {
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$agyBinDir*") {
        [System.Environment]::SetEnvironmentVariable("Path", "$userPath;$agyBinDir", "User")
    }
    Update-SessionEnvironment
    $agyVer = & "$agyExe" --version 2>$null
    Write-Host "      ✔ Antigravity CLI (agy) instalado y vinculado (v$agyVer)" -ForegroundColor Green
} elseif (Get-Command agy -ErrorAction SilentlyContinue) {
    $agyVer = agy --version
    Write-Host "      ✔ Antigravity CLI (agy) detectado (v$agyVer)" -ForegroundColor Green
} else {
    Write-Host "      ℹ Antigravity CLI opcional no pudo ser instalado automáticamente." -ForegroundColor Yellow
    Write-Host "        (El generador funcionará sin problemas con el motor heurístico local)." -ForegroundColor Gray
}

# -----------------------------------------------------------
# RESUMEN Y FINALIZACIÓN
# -----------------------------------------------------------
Write-Host "`n====================================================" -ForegroundColor Green
Write-Host "   ✔ Configuración e Instalación Completadas        " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host "Puedes iniciar la sincronización de partidas haciendo doble clic en:" -ForegroundColor White
Write-Host "  -> ejecutar_windows.bat (en la raíz del proyecto)" -ForegroundColor Cyan
Write-Host "  -> win\auto.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Gray
[void][System.Console]::ReadKey($true)
