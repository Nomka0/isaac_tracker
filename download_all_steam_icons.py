#!/usr/bin/env python3
import re
import urllib.request
from pathlib import Path
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/appcache/stats/UserGameStatsSchema_250900.bin"
IMG_DIR = BASE_DIR / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)
STEAM_CDN = "https://shared.steamstatic.com/community_assets/images/apps/250900"

def extract_all_icons(raw_data):
    # En el esquema binario de Steam, cada logro numérico tiene name\x00<id>\x00 seguido de icon\x00<hash>.jpg
    matches = re.findall(rb'\x01name\x00(\d{1,3})\x00.*?\x01icon\x00([a-f0-9]{40})\.jpg', raw_data, re.DOTALL)
    mapping = {}
    for num_b, hash_b in matches:
        n = num_b.decode('ascii')
        h = hash_b.decode('ascii')
        if 1 <= int(n) <= 641:
            mapping[n] = h
    return mapping

def download_task(item):
    name, icon_hash = item
    target = IMG_DIR / f"{name}.png"
    if target.exists() and target.stat().st_size > 500:
        return
    url = f"{STEAM_CDN}/{icon_hash}.jpg"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read()
            if len(content) > 200:
                target.write_bytes(content)
    except Exception:
        pass

def main():
    if not SCHEMA_FILE.exists():
        print(f"No existe el archivo de esquema de Steam: {SCHEMA_FILE}")
        return
    with open(SCHEMA_FILE, "rb") as f:
        raw_data = f.read()
    icons = extract_all_icons(raw_data)
    print(f"Encontrados {len(icons)} iconos en el esquema. Descargando a {IMG_DIR}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(download_task, icons.items()))
    print(f"Total imágenes en {IMG_DIR}: {len(list(IMG_DIR.glob('*.png')))}")

if __name__ == "__main__":
    main()
