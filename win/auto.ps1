<#
.SYNOPSIS
    Sincronizador y generador de guía para The Binding of Isaac Repentance+ en Windows.
.DESCRIPTION
    Copia los respaldos más recientes de Documents/My Games a save_backups,
    analiza el progreso con Python y genera GUIA_PROXIMOS_DESBLOQUEOS.md.
#>

[CmdletBinding()]
param (
    [int]$Limit = 25,
    [switch]$NoAI
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = (Resolve-Path "$ScriptDir\..").Path
$BackupDir = Join-Path $RootDir "save_backups"
$GuideMd = Join-Path $RootDir "GUIA_PROXIMOS_DESBLOQUEOS.md"
$Enricher = Join-Path $RootDir "isaac_enricher.py"
$Generator = Join-Path $RootDir "generate_guide.py"

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host "    🔄 Sincronización de Partida Isaac (Windows)   " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Detectar Python
$PyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py -3" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { $null }
if (-not $PyCmd) {
    Write-Host "[ERROR] Python no está disponible en PATH. Instala Python 3.10+." -ForegroundColor Red
    exit 1
}

# 2. Sincronizar respaldos de Steam
Write-Host "`n[1/4] Buscando carpeta de guardados de Isaac..." -ForegroundColor Yellow
$CandidateDirs = @(
    "$env:USERPROFILE\Documents\My Games\Binding of Isaac Repentance+\save_backups",
    "$env:USERPROFILE\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups",
    "$env:USERPROFILE\Documents\My Games\Binding of Isaac Repentance\save_backups",
    "$env:USERPROFILE\OneDrive\Documents\My Games\Binding of Isaac Repentance\save_backups",
    "$env:USERPROFILE\Documents\My Games\Binding of Isaac Afterbirth+\save_backups",
    "$env:USERPROFILE\OneDrive\Documents\My Games\Binding of Isaac Afterbirth+\save_backups",
    "$env:USERPROFILE\Documents\My Games\Binding of Isaac Repentance+",
    "$env:USERPROFILE\Documents\My Games\Binding of Isaac Repentance"
)

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$FoundSource = $false
foreach ($dir in $CandidateDirs) {
    if (Test-Path $dir) {
        Write-Host "      ✔ Origen detectado: $dir" -ForegroundColor Green
        Copy-Item -Path "$dir\*persistentgamedata*.dat" -Destination $BackupDir -Force -ErrorAction SilentlyContinue
        Write-Host "      ✔ Archivos de guardado copiados a save_backups\" -ForegroundColor Green
        $FoundSource = $true
        break
    }
}
if (-not $FoundSource) {
    Write-Host "      ℹ No se detectó ruta estándar en Documents. Usando respaldos existentes en save_backups\." -ForegroundColor Cyan
}

# 3. Detectar guardados
Write-Host "`n[2/4] Detectando guardados recientes..." -ForegroundColor Yellow
$FindOutput = & ([scriptblock]::Create("$PyCmd `"$Enricher`" --find-saves `"$BackupDir`""))
$Latest = ($FindOutput | Where-Object { $_ -match "^LATEST=(.+)" } | ForEach-Object { $Matches[1] }).Trim()
$Previous = ($FindOutput | Where-Object { $_ -match "^PREVIOUS=(.+)" } | ForEach-Object { $Matches[1] }).Trim()

if (-not $Latest -or -not (Test-Path $Latest)) {
    Write-Host "[ERROR] No se encontraron archivos de guardado en $BackupDir" -ForegroundColor Red
    exit 1
}

Write-Host "      ✔ Guardado actual: $(Split-Path -Leaf $Latest)" -ForegroundColor Green
if ($Previous -and (Test-Path $Previous)) {
    Write-Host "      ℹ Guardado previo: $(Split-Path -Leaf $Previous)" -ForegroundColor Cyan
}

# 4. Generar Guía
Write-Host "`n[3/4] Analizando binario y generando guía..." -ForegroundColor Yellow
$AiFlags = if ($NoAI) { "--no-ai" } else { "" }
$ArgsEnrich = if ($Previous -and (Test-Path $Previous)) { "`"$Latest`" `"$Previous`"" } else { "`"$Latest`"" }

$PipelineCmd = "$PyCmd `"$Enricher`" $ArgsEnrich | $PyCmd `"$Generator`" -n $Limit $AiFlags -o `"$GuideMd`""
& ([scriptblock]::Create($PipelineCmd))

# 5. Verificación
Write-Host "`n[4/4] Verificando resultado..." -ForegroundColor Yellow
if (Test-Path $GuideMd) {
    $Lines = (Get-Content $GuideMd).Count
    Write-Host "      ✔ Guía actualizada exitosamente: $GuideMd ($Lines líneas)." -ForegroundColor Green
} else {
    Write-Host "      ⚠ Advertencia: no se pudo verificar $GuideMd" -ForegroundColor Yellow
}

Write-Host "`n✨ Sincronización completada con éxito.`n" -ForegroundColor Green
