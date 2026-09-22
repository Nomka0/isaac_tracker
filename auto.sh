#!/usr/bin/env bash
set -euo pipefail

# Colores para la terminal
C_RESET='\033[0m'
C_CYAN='\033[1;36m'
C_GREEN='\033[1;32m'
C_YELLOW='\033[1;33m'
C_BLUE='\033[1;34m'
C_RED='\033[1;31m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/save_backups"
GUIDE_MD="$SCRIPT_DIR/GUIA_PROXIMOS_DESBLOQUEOS.md"
ENRICHER="$SCRIPT_DIR/isaac_enricher.py"

echo -e "\n${C_CYAN}====================================================${C_RESET}"
echo -e "${C_CYAN}    🔄 Iniciando sincronización de partida Isaac    ${C_RESET}"
echo -e "${C_CYAN}====================================================${C_RESET}"

# 1. Sincronizar desde la carpeta de Steam si existe y buscar el respaldo más reciente
echo -e "\n${C_YELLOW}[1/4]${C_RESET} Buscando el archivo de guardado más reciente..."

STEAM_BACKUP_DIR="$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/250900/pfx/drive_c/users/steamuser/Documents/My Games/Binding of Isaac Repentance+/save_backups"
if [ ! -d "$STEAM_BACKUP_DIR" ]; then
  STEAM_BACKUP_DIR="$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/250900/pfx/drive_c/users/steamuser/My Documents/My Games/Binding of Isaac Repentance+/save_backups"
fi

if [ -d "$STEAM_BACKUP_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
  cp -pu "$STEAM_BACKUP_DIR"/*.rep+persistentgamedata1.dat "$BACKUP_DIR/" 2>/dev/null || true
fi

if [ ! -f "$ENRICHER" ]; then
  echo -e "${C_RED}❌ Error:${C_RESET} No se encuentra el script $ENRICHER"
  exit 1
fi

eval "$(python3 "$ENRICHER" --find-saves "$BACKUP_DIR")"

if [ -z "${LATEST:-}" ] || [ ! -f "$LATEST" ]; then
  echo -e "${C_RED}❌ Error:${C_RESET} No se encontraron archivos de guardado en $BACKUP_DIR"
  exit 1
fi

SAVE_NAME=$(basename "$LATEST")
echo -e "      ${C_GREEN}✔ Guardado más reciente:${C_RESET} $SAVE_NAME"
if [ -n "${PREVIOUS:-}" ] && [ -f "$PREVIOUS" ]; then
  echo -e "      ${C_BLUE}ℹ Guardado previo (referencia):${C_RESET} $(basename "$PREVIOUS")"
fi

# 2. Procesar binario y enriquecer con Python
echo -e "\n${C_YELLOW}[2/4]${C_RESET} Analizando binario y mapeando logros con $ENRICHER..."

if [ -n "${PREVIOUS:-}" ] && [ -f "$PREVIOUS" ]; then
  PROMPT_DATA=$(python3 "$ENRICHER" "$LATEST" "$PREVIOUS")
else
  PROMPT_DATA=$(python3 "$ENRICHER" "$LATEST")
fi

read -r TOTAL_UNLOCKED PCT PENDING_COUNT NEW_COUNT < <(python3 -c "import json, sys; d=json.loads(sys.argv[1]); print(d.get('desbloqueados_total', 'N/A'), d.get('porcentaje_completado', 'N/A'), len(d.get('pendientes_clave', [])), len(d.get('nuevos_esta_sesion', [])))" "$PROMPT_DATA")

echo -e "      ${C_GREEN}✔ Desbloqueados:${C_RESET} $TOTAL_UNLOCKED / 641 (${PCT}%)"
if [ "$NEW_COUNT" -gt 0 ]; then
  echo -e "      ${C_GREEN}🎉 Nuevos esta sesión:${C_RESET} $NEW_COUNT logros"
fi
echo -e "      ${C_BLUE}ℹ Pendientes clave identificados:${C_RESET} $PENDING_COUNT"

# 3. Generar la guía en Markdown (Estructura determinista + Análisis táctico IA con agy)
echo -e "\n${C_YELLOW}[3/4]${C_RESET} Generando guía dinámica y consultando análisis de IA..."
echo -e "      ${C_BLUE}ℹ Destino:${C_RESET} $GUIDE_MD"

# Generar guía dinámica mediante generate_guide.py y guide_template.j2
echo "$PROMPT_DATA" | python3 "$SCRIPT_DIR/generate_guide.py" -o "$GUIDE_MD"

# 4. Finalización
echo -e "\n${C_YELLOW}[4/4]${C_RESET} Verificando resultado..."
if [ -f "$GUIDE_MD" ] && [ -s "$GUIDE_MD" ]; then
  LINES=$(wc -l <"$GUIDE_MD")
  echo -e "      ${C_GREEN}✔ Guía actualizada correctamente${C_RESET} ($LINES líneas generadas)."
else
  echo -e "      ${C_YELLOW}⚠ Advertencia:${C_RESET} No se pudo confirmar la creación de $GUIDE_MD"
fi

echo -e "\n${C_GREEN}✨ Sincronización completada con éxito.${C_RESET}\n"
