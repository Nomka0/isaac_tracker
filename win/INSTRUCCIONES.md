# Guía de Instalación y Uso en Windows

Instrucciones para ejecutar el analizador de guardados y generador de guía estratégica en Windows.

---

## 1. Instalación Automática (1 Clic)

Haz doble clic sobre el archivo en la raíz del proyecto:
```
instalar_dependencias_windows.bat
```
*(O ejecuta `win\instalar_dependencias.bat` / `win\instalar_dependencias.ps1`)*

El instalador:
1. **Gestiona permisos:** Solicita elevación de Administrador (UAC) automáticamente.
2. **Instala Python 3.12:** Si no está presente, lo descarga e instala con la casilla `Add to PATH` activada.
3. **Instala Jinja2:** Actualiza pip e instala `jinja2` (motor de plantillas).
4. **Instala Antigravity CLI (`agy`):** Configura el CLI de IA oficial para el análisis táctico automático.

---

## 2. Rutas de Guardado en Windows

El juego almacena los respaldos en:
- Ruta estándar: `%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\save_backups`
- Con OneDrive activo: `%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups`

Los scripts `auto.bat` y `auto.ps1` detectan automáticamente ambas rutas y copian los archivos más recientes (`*.rep+persistentgamedata1.dat`) a la carpeta local `save_backups\`.

---

## 3. Ejecución

### Opción A: Doble clic (Recomendado)
Haz doble clic sobre el archivo en la raíz:
```
ejecutar_windows.bat
```
(O directamente sobre `win\auto.bat`).
Se abrirá una ventana de comandos que copiará los respaldos, procesará el binario y actualizará `GUIA_PROXIMOS_DESBLOQUEOS.md`.

### Opción B: PowerShell
Abre PowerShell en la raíz del repositorio y ejecuta:
```powershell
powershell -ExecutionPolicy Bypass -File win\auto.ps1
```
Parámetros opcionales:
- `-Limit 30`: Cambia la cantidad de logros curados (por defecto 25).
- `-NoAI`: Fuerza la generación puramente heurística sin invocar a `agy`.

---

## 4. Visualización en Obsidian

1. Abre **Obsidian**.
2. Selecciona **Open folder as vault** (Abrir carpeta como bóveda).
3. Selecciona la carpeta raíz del proyecto (`isaac_backup`).
4. Abre el archivo `GUIA_PROXIMOS_DESBLOQUEOS.md`.
   - Todas las imágenes (`images/achievements/`, `images/characters/`, etc.) e iconos cargarán automáticamente sin necesidad de configuración adicional.
