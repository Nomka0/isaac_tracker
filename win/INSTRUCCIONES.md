# Guía de Instalación y Uso en Windows

Instrucciones para ejecutar el analizador de guardados y generador de guía estratégica en Windows.

---

## 1. Requisitos Previos

1. **Python 3.10 o superior:**
   - Descargar de [python.org](https://www.python.org/downloads/).
   - **IMPORTANTE:** Durante la instalación, marcar la casilla `Add python.exe to PATH`.

2. **Dependencias de Python:**
   - Haz doble clic en `win\instalar_dependencias.bat` para instalarlas de forma automática.
   - O alternativamente ejecuta en consola:
   ```cmd
   pip install -r win\requirements.txt
   ```
   *(Solo requiere `jinja2`). Además, `win\auto.bat` las instalará automáticamente si detecta que faltan.*

3. **(Opcional) CLI de IA Antigravity:**
   - Si tienes instalado el comando `agy` en el PATH de Windows, generará bitácoras tácticas con IA automáticamente.
   - Si no está instalado, la herramienta usa el motor heurístico determinista sin errores.

---

## 2. Rutas de Guardado en Windows

El juego almacena los respaldos en:
- Ruta estándar: `%USERPROFILE%\Documents\My Games\Binding of Isaac Repentance+\save_backups`
- Con OneDrive activo: `%USERPROFILE%\OneDrive\Documents\My Games\Binding of Isaac Repentance+\save_backups`

Los scripts `auto.bat` y `auto.ps1` detectan automáticamente ambas rutas y copian los archivos más recientes (`*.rep+persistentgamedata1.dat`) a la carpeta local `save_backups\`.

---

## 3. Ejecución

### Opción A: Doble clic (Recomendado)
Haz doble clic sobre:
```
win\auto.bat
```
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
