#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/save_backups"
AUTO_SCRIPT="$SCRIPT_DIR/auto.sh"
ISAAC_PROC="isaac-ng"

mkdir -p "$BACKUP_DIR"

echo "👀 Vigilando proceso de Isaac ($ISAAC_PROC)... Presiona Ctrl+C para salir."

while true; do
    if pgrep -f "$ISAAC_PROC" > /dev/null 2>&1; then
        echo "🎮 Partida en curso detectada. Esperando a que el juego se cierre..."
        while pgrep -f "$ISAAC_PROC" > /dev/null 2>&1; do
            sleep 2
        done

        echo "🛑 El juego se ha cerrado. Esperando a que se guarden los datos en disco..."
        sleep 2

        # Sincronizar respaldos preservando marcas de tiempo (-p)
        ORIG_DIR="$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/250900/pfx/drive_c/users/steamuser/Documents/My Games/Binding of Isaac Repentance+/save_backups"
        if [ ! -d "$ORIG_DIR" ]; then
            ORIG_DIR="$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/250900/pfx/drive_c/users/steamuser/My Documents/My Games/Binding of Isaac Repentance+/save_backups"
        fi

        if [ -d "$ORIG_DIR" ]; then
            cp -pu "$ORIG_DIR"/*.rep+persistentgamedata1.dat "$BACKUP_DIR/" 2>/dev/null || true
        fi

        # Ejecutar sincronización y actualización de guía
        "$AUTO_SCRIPT"
        echo "👀 Reanudando vigilancia de Isaac..."
    fi
    sleep 3
done
