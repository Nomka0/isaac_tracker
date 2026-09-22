#!/usr/bin/env python3
import sys
import json
import struct
import re
import datetime
from pathlib import Path

# Asegurar codificación UTF-8 en Windows
for _stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

BASE_DIR = Path(__file__).resolve().parent
MAP_FILE = BASE_DIR / "achievements.json"
DEFAULT_BACKUP_DIR = BASE_DIR / "save_backups"

def load_achievement_map():
    if not MAP_FILE.exists():
        return {}
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}

def get_unlocked_ids(dat_path):
    p = Path(dat_path)
    if not p.exists() or p.stat().st_size < 32:
        return set()

    with open(p, "rb") as f:
        data = f.read()

    if len(data) < 32:
        return set()

    # Offset 24: tamaño de la tabla (642 en Repentance+)
    num_achievements = struct.unpack("<I", data[24:28])[0]
    # Offset 32: array de bytes (byte 32 = índice 0 no utilizado; logros van de 1 a 641)
    raw_achievements = data[32 : 32 + num_achievements]
    return {i for i, status in enumerate(raw_achievements) if status != 0 and 0 < i <= 641}

def find_latest_saves(backup_dir=DEFAULT_BACKUP_DIR):
    p = Path(backup_dir)
    if not p.exists():
        return None, None

    # Coincidir con archivos de guardado (slot 1 o cualquier slot de Repentance+)
    files = list(p.glob("*persistentgamedata1.dat"))
    if not files:
        files = list(p.glob("*persistentgamedata*.dat"))
    if not files:
        return None, None

    def sort_key(f):
        # 1. Extraer prefijo de fecha si existe (formato YYYYMMDD)
        m = re.match(r"^(\d{8})", f.name)
        if m:
            date_str = m.group(1)
        else:
            # Si no tiene fecha en el nombre, deducirla de su fecha de modificación
            date_str = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y%m%d")
        # Tupla: (fecha_str, fecha_modificacion, nombre_archivo)
        return (date_str, f.stat().st_mtime, f.name)

    files.sort(key=sort_key)
    latest = files[-1]
    previous = files[-2] if len(files) > 1 else None
    return latest, previous

def enrich_progress(current_save, prev_save=None, achievement_map=None):
    if achievement_map is None:
        achievement_map = load_achievement_map()

    current_path = Path(current_save)
    current_unlocked = get_unlocked_ids(current_path)

    output = {
        "archivo_actual": current_path.name,
        "archivo_previo": Path(prev_save).name if prev_save else None,
        "total_logros_juego": 641,
        "desbloqueados_total": len(current_unlocked),
        "porcentaje_completado": round((len(current_unlocked) / 641) * 100, 2),
        "nuevos_esta_sesion": [],
        "pendientes_clave": [],
        "todos_bloqueados": []
    }

    if prev_save:
        prev_path = Path(prev_save)
        prev_unlocked = get_unlocked_ids(prev_path)

        # Si el guardado anterior tiene más logros que el actual, advertir
        if len(prev_unlocked) > len(current_unlocked):
            print(f"Advertencia: {prev_path.name} tiene más logros ({len(prev_unlocked)}) que {current_path.name} ({len(current_unlocked)}).", file=sys.stderr)

        diff_ids = sorted(list(current_unlocked - prev_unlocked))
        for aid in diff_ids:
            info = achievement_map.get(aid, {"name": f"Logro #{aid}", "condition": "Desconocido", "priority": "N/A"})
            output["nuevos_esta_sesion"].append({
                "id": aid,
                "nombre": info.get("name"),
                "como_se_obtuvo": info.get("condition"),
                "prioridad": info.get("priority", "Media")
            })

    # Recopilar todos los logros bloqueados y los pendientes clave
    for aid, data in achievement_map.items():
        if aid not in current_unlocked:
            entry = {
                "id": aid,
                "nombre": data.get("name"),
                "desbloqueo": data.get("condition"),
                "prioridad": data.get("priority", "Media")
            }
            output["todos_bloqueados"].append(entry)
            if data.get("priority") in ["Crítica", "Alta"]:
                output["pendientes_clave"].append(entry)

    # Ordenar pendientes: Crítica primero, luego Alta, y por ID
    priority_order = {"Crítica": 0, "Alta": 1, "Media": 2, "Baja": 3}
    output["pendientes_clave"].sort(key=lambda x: (priority_order.get(x["prioridad"], 99), x["id"]))
    output["todos_bloqueados"].sort(key=lambda x: x["id"])

    return output

def generate_markdown(data):
    pct = data.get("porcentaje_completado", 0.0)
    total = data.get("desbloqueados_total", 0)
    max_total = data.get("total_logros_juego", 641)
    current_file = data.get("archivo_actual", "N/A")
    prev_file = data.get("archivo_previo")

    # Barra visual de progreso (20 caracteres)
    filled_len = int(round(20 * pct / 100))
    bar = "█" * filled_len + "░" * (20 - filled_len)

    lines = []
    lines.append("# 🎮 Guía de Próximos Desbloqueos - The Binding of Isaac Repentance+")
    lines.append("")
    lines.append("> [!INFO] **Estado de la Partida**")
    lines.append(f"> - **Progreso:** `{bar}` **{pct}%** ({total} / {max_total} logros)")
    lines.append(f"> - **Guardado actual:** `{current_file}`")
    if prev_file:
        lines.append(f"> - **Guardado previo comparado:** `{prev_file}`")
    lines.append("")

    nuevos = data.get("nuevos_esta_sesion", [])
    if nuevos:
        lines.append("## 🎉 Desbloqueados en la Última Sesión")
        lines.append("")
        lines.append("| Icono | Logro / Ítem | Prioridad | Cómo se obtuvo |")
        lines.append("| :---: | :--- | :---: | :--- |")
        for item in nuevos:
            aid = item["id"]
            name = item["nombre"]
            cond = item["como_se_obtuvo"]
            prio = item.get("prioridad", "N/A")
            lines.append(f'| <img src="images/achievements/{aid}.png" width="45"> | **{name}** | `{prio}` | {cond} |')
        lines.append("")

    pendientes = data.get("pendientes_clave", [])
    criticos = [p for p in pendientes if p["prioridad"] == "Crítica"]
    altos = [p for p in pendientes if p["prioridad"] == "Alta"]

    lines.append(f"## 🔥 Desbloqueos de Prioridad Crítica ({len(criticos)})")
    lines.append("")
    lines.append("Objetos y mecánicas que cambian drásticamente la calidad de las partidas (God Tier / Game Changers):")
    lines.append("")
    lines.append("| Icono | Logro / Ítem | Requisito de desbloqueo | Prioridad |")
    lines.append("| :---: | :--- | :--- | :---: |")
    for item in criticos:
        aid = item["id"]
        name = item["nombre"]
        cond = item["desbloqueo"]
        lines.append(f'| <img src="images/achievements/{aid}.png" width="45"> | **{name}** | {cond} | 🔴 Crítica |')
    lines.append("")

    lines.append(f"## ⭐ Desbloqueos de Prioridad Alta ({len(altos)})")
    lines.append("")
    lines.append("Objetos excelentes, runas, transformaciones y personajes clave:")
    lines.append("")
    lines.append("| Icono | Logro / Ítem | Requisito de desbloqueo | Prioridad |")
    lines.append("| :---: | :--- | :--- | :---: |")
    for item in altos:
        aid = item["id"]
        name = item["nombre"]
        cond = item["desbloqueo"]
        lines.append(f'| <img src="images/achievements/{aid}.png" width="45"> | **{name}** | {cond} | 🟡 Alta |')
    lines.append("")

    lines.append("---")
    lines.append(f"*Guía generada automáticamente a partir del archivo `{current_file}`.*")
    lines.append("")

    return "\n".join(lines)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    output_markdown = "--markdown" in flags
    find_saves_mode = "--find-saves" in flags

    if find_saves_mode:
        target_dir = Path(args[0]) if args else DEFAULT_BACKUP_DIR
        latest, prev = find_latest_saves(target_dir)
        print(f"LATEST={latest or ''}")
        print(f"PREVIOUS={prev or ''}")
        return

    current_save = None
    prev_save = None

    if len(args) >= 2:
        current_save = Path(args[0])
        prev_save = Path(args[1])
    elif len(args) == 1:
        current_save = Path(args[0])
        # Si sólo se pasa un archivo, intentar buscar el anterior en el mismo directorio
        parent_dir = current_save.parent
        latest, prev = find_latest_saves(parent_dir)
        if latest and latest.resolve() == current_save.resolve() and prev:
            prev_save = prev
    else:
        # Sin argumentos: buscar automáticamente los más recientes
        latest, prev = find_latest_saves(DEFAULT_BACKUP_DIR)
        if not latest:
            print(f"Error: No se encontraron archivos de guardado en {DEFAULT_BACKUP_DIR}", file=sys.stderr)
            sys.exit(1)
        current_save = latest
        prev_save = prev

    data = enrich_progress(current_save, prev_save)

    if output_markdown:
        print(generate_markdown(data))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
