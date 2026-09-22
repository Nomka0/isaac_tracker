#!/usr/bin/env python3
"""
Descarga iconos de tamaño reducido (32x32) de todos los personajes de The Binding of Isaac Repentance+
(incluyendo personajes normales, Tainted y variantes jugables) organizados en la carpeta characters/.
"""

import urllib.request
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent
CHAR_DIR = BASE_DIR / "images" / "characters"
CHAR_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Referer": "https://bindingofisaacrebirth.wiki.gg/wiki/Characters"
}

CHARACTERS = {
    # Personajes normales
    "isaac": "Character_Isaac_icon.png",
    "magdalene": "Character_Magdalene_icon.png",
    "cain": "Character_Cain_icon.png",
    "judas": "Character_Judas_icon.png",
    "blue_baby": "Character_%3F%3F%3F_icon.png",
    "eve": "Character_Eve_icon.png",
    "samson": "Character_Samson_icon.png",
    "azazel": "Character_Azazel_icon.png",
    "lazarus": "Character_Lazarus_icon.png",
    "eden": "Character_Eden_icon.png",
    "the_lost": "Character_The_Lost_icon.png",
    "lilith": "Character_Lilith_icon.png",
    "keeper": "Character_Keeper_icon.png",
    "apollyon": "Character_Apollyon_icon.png",
    "the_forgotten": "Character_The_Forgotten_icon.png",
    "bethany": "Character_Bethany_icon.png",
    "jacob_and_esau": "Character_Jacob_and_Esau_icon.png",

    # Sub-personajes y variantes normales
    "jacob": "Character_Jacob_icon.png",
    "esau": "Character_Esau_icon.png",
    "the_soul": "Character_The_Soul_icon.png",
    "black_judas": "Character_Black_Judas_icon.png",
    "lazarus_risen": "Character_Lazarus_Risen_icon.png",

    # Personajes Tainted
    "tainted_isaac": "Character_Tainted_Isaac_icon.png",
    "tainted_magdalene": "Character_Tainted_Magdalene_icon.png",
    "tainted_cain": "Character_Tainted_Cain_icon.png",
    "tainted_judas": "Character_Tainted_Judas_icon.png",
    "tainted_blue_baby": "Character_Tainted_%3F%3F%3F_icon.png",
    "tainted_eve": "Character_Tainted_Eve_icon.png",
    "tainted_samson": "Character_Tainted_Samson_icon.png",
    "tainted_azazel": "Character_Tainted_Azazel_icon.png",
    "tainted_lazarus": "Character_Tainted_Lazarus_icon.png",
    "tainted_eden": "Character_Tainted_Eden_icon.png",
    "tainted_lost": "Character_Tainted_Lost_icon.png",
    "tainted_lilith": "Character_Tainted_Lilith_icon.png",
    "tainted_keeper": "Character_Tainted_Keeper_icon.png",
    "tainted_apollyon": "Character_Tainted_Apollyon_icon.png",
    "tainted_forgotten": "Character_Tainted_Forgotten_icon.png",
    "tainted_bethany": "Character_Tainted_Bethany_icon.png",
    "tainted_jacob": "Character_Tainted_Jacob_icon.png",

    # Sub-personajes Tainted
    "dead_tainted_lazarus": "Character_Dead_Tainted_Lazarus_icon.png",
    "tainted_soul": "Character_Tainted_Soul_icon.png"
}

# Alias comunes para comodidad en Markdown
ALIASES = {
    "lost.png": "the_lost.png",
    "forgotten.png": "the_forgotten.png",
    "jacob_esau.png": "jacob_and_esau.png",
    "bluebaby.png": "blue_baby.png",
    "dark_judas.png": "black_judas.png",
    "tainted_the_lost.png": "tainted_lost.png",
    "tainted_the_forgotten.png": "tainted_forgotten.png",
    "tainted_bluebaby.png": "tainted_blue_baby.png"
}

def download_character(name, filename):
    target = CHAR_DIR / f"{name}.png"
    if target.exists() and target.stat().st_size > 100:
        return True
    
    url = f"https://bindingofisaacrebirth.wiki.gg/images/{filename}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 50:
                target.write_bytes(data)
                return True
    except Exception as e:
        print(f"Error descargando {name}: {e}")
        return False
    return False

def main():
    print(f"Iniciando descarga de {len(CHARACTERS)} iconos de personajes a {CHAR_DIR}...")
    success = 0
    for name, filename in CHARACTERS.items():
        if download_character(name, filename):
            success += 1
            print(f"  [OK] {name}.png")
        else:
            print(f"  [FAIL] {name}.png")

    # Crear copias para alias comunes
    for alias, original in ALIASES.items():
        src = CHAR_DIR / original
        dst = CHAR_DIR / alias
        if src.exists():
            shutil.copyfile(src, dst)

    total_files = len(list(CHAR_DIR.glob("*.png")))
    print(f"\nProceso finalizado: {success} iconos base descargados, total {total_files} archivos en {CHAR_DIR}.")

if __name__ == "__main__":
    main()
