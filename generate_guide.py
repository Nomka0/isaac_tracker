#!/usr/bin/env python3
"""
generate_guide.py - Generador 100% dinámico de GUIA_PROXIMOS_DESBLOQUEOS.md para Obsidian.
Cumple estrictamente con:
- Uso de iconos del repositorio (images/...) sin emojis Unicode.
- Tuberías escapadas (\\|) en wikilinks dentro de tablas Markdown para no romper columnas.
- Representación visual de calidad/tier usando estrellas de pixel art (![[images/pickups/star.png\\|14]]) o insignias de categoría.
- Enriquecimiento automático de requisitos con iconos de jefes, personajes y consumibles.
- Renderizado determinista y robusto a través de guide_template.j2.
"""

import os
import sys
import json
import re
import shutil
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from isaac_enricher import es_logro_factible, get_unlocked_ids, find_latest_saves

# Asegurar codificación UTF-8 en terminales de Windows
for _stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "guide_template.j2"
EFFECTS_PATH = BASE_DIR / "achievement_effects.json"
DEFAULT_OUT = BASE_DIR / "GUIA_PROXIMOS_DESBLOQUEOS.md"
WIKI_URLS_PATH = BASE_DIR / "achievement_wiki_urls.json"
WIKI_ENTITIES_PATH = BASE_DIR / "wiki_entities.json"
AI_CACHE_PATH = BASE_DIR / "ai_protocol_cache.json"

# Mapeo de jefes a iconos en images/bosses/
BOSS_ICONS = {
    "Satan": "images/bosses/satan.png",
    "Satanás": "images/bosses/satan.png",
    "Mega Satan": "images/bosses/mega_satan.png",
    "Mom": "images/bosses/mom.png",
    "Mom's Heart": "images/bosses/moms_heart.png",
    "It Lives!": "images/bosses/it_lives.png",
    "Isaac": "images/bosses/isaac.png",
    "??? (Blue Baby)": "images/bosses/blue_baby.png",
    "Blue Baby": "images/bosses/blue_baby.png",
    "???": "images/bosses/blue_baby.png",
    "The Lamb": "images/bosses/the_lamb.png",
    "Hush": "images/bosses/hush.png",
    "Delirium": "images/bosses/delirium.png",
    "Mother": "images/bosses/mother.png",
    "The Beast": "images/bosses/the_beast.png",
    "Ultra Greedier": "images/bosses/ultra_greedier.png",
    "Ultra Greed": "images/bosses/ultra_greed.png",
    "Dogma": "images/bosses/dogma.png",
    "Boss Rush": "images/bosses/boss_rush.png",
    "Baby Plum": "images/bosses/baby_plum.png",
    "The Siren": "images/bosses/the_siren.png",
}

# Mapeo de personajes a iconos en images/characters/
CHAR_ICONS = {
    "Isaac": "images/characters/isaac.png",
    "Magdalene": "images/characters/magdalene.png",
    "Maggy": "images/characters/magdalene.png",
    "Cain": "images/characters/cain.png",
    "Judas": "images/characters/judas.png",
    "??? (Blue Baby)": "images/characters/blue_baby.png",
    "Blue Baby": "images/characters/blue_baby.png",
    "???": "images/characters/blue_baby.png",
    "Eve": "images/characters/eve.png",
    "Samson": "images/characters/samson.png",
    "Azazel": "images/characters/azazel.png",
    "Lazarus": "images/characters/lazarus.png",
    "Eden": "images/characters/eden.png",
    "The Lost": "images/characters/the_lost.png",
    "Lost": "images/characters/the_lost.png",
    "Lilith": "images/characters/lilith.png",
    "Keeper": "images/characters/keeper.png",
    "Apollyon": "images/characters/apollyon.png",
    "The Forgotten": "images/characters/the_forgotten.png",
    "Forgotten": "images/characters/the_forgotten.png",
    "Bethany": "images/characters/bethany.png",
    "Jacob & Esau": "images/characters/jacob_and_esau.png",
    "Jacob and Esau": "images/characters/jacob_and_esau.png",
    "Tainted Isaac": "images/characters/tainted_isaac.png",
    "Tainted Magdalene": "images/characters/tainted_magdalene.png",
    "Tainted Cain": "images/characters/tainted_cain.png",
    "Tainted Judas": "images/characters/tainted_judas.png",
    "Tainted ???": "images/characters/tainted_blue_baby.png",
    "Tainted Eve": "images/characters/tainted_eve.png",
    "Tainted Samson": "images/characters/tainted_samson.png",
    "Tainted Azazel": "images/characters/tainted_azazel.png",
    "Tainted Lazarus": "images/characters/tainted_lazarus.png",
    "Tainted Eden": "images/characters/tainted_eden.png",
    "Tainted Lost": "images/characters/tainted_lost.png",
    "Tainted Lilith": "images/characters/tainted_lilith.png",
    "Tainted Keeper": "images/characters/tainted_keeper.png",
    "Tainted Apollyon": "images/characters/tainted_apollyon.png",
    "Tainted Forgotten": "images/characters/tainted_forgotten.png",
    "Tainted Bethany": "images/characters/tainted_bethany.png",
    "Tainted Jacob": "images/characters/tainted_jacob.png",
}

CATEGORIA_METADATA = {
    "Greed Machine": {
        "titulo": "Máquina de Donación de Greed & Fundación de Personajes",
        "icono": "images/pickups/greed_machine.png",
        "icono_size": 30,
        "orden": 1,
        "descripcion": "La máquina de Greed es la mayor inversión estructural de la partida. Desbloquear el Holy Mantle para The Lost y al propio Keeper sienta los cimientos obligatorios antes de intentar cualquier marca seria en modo Difícil.",
        "tip": "No juegues con un solo personaje porque el porcentaje de atasco de la máquina aumenta drásticamente con cada moneda donada por el mismo héroe. Rota entre ![[images/characters/lilith.png|24]] **Lilith** (reina indiscutible de Greed con Box of Friends), ![[images/characters/judas.png|24]] **Judas** (daño base con Book of Belial) y ![[images/characters/azazel.png|24]] **Azazel** para transferir 60-90 ![[images/pickups/penny.png|24]] monedas por run sin atascos prematuros."
    },
    "Jacob & Esau": {
        "titulo": "Jacob & Esau: Los Multiplicadores de Victoria",
        "icono": "images/characters/jacob_and_esau.png",
        "icono_size": 36,
        "orden": 2,
        "descripcion": "Aunque su control dual exige microgestión estricta de posicionamiento, contienen los tres desbloqueos más determinantes para alterar el curso de cualquier partida en Repentance (Birthright, Damocles y Rock Bottom).",
        "tip": "Toma siempre la ruta alternativa (Downpour/Dross, Mines/Ashpit) para entrar en salas del tesoro dobles y recolectar dos pedestales en lugar de uno alineando a ambos hermanos simultáneamente."
    },
    "Tainted Isaac": {
        "titulo": "Tainted Isaac: Manipulación Absoluta de Pedestales",
        "icono": "images/characters/tainted_isaac.png",
        "icono_size": 36,
        "orden": 3,
        "descripcion": "Sus desbloqueos alteran permanentemente los pedestales de la partida (Glitched Crown, Mega Mush, The Stars?). Priorizar sus marcas garantiza convertir cualquier partida mediocre en una victoria garantizada.",
        "tip": "Su límite de 8 ítems pasivos no es una debilidad, sino un filtro de calidad. Aprovecha pedestales que alternan entre dos opciones para maximizar stats antes de cambiar ítems situacionales por Tier 4 definitivos."
    },
    "Isaac": {
        "titulo": "Isaac Clásico: Consolidación Inmediata de Marcas",
        "icono": "images/characters/isaac.png",
        "icono_size": 36,
        "orden": 4,
        "descripcion": "Con Mom's Knife y D6 en el arsenal básico de Isaac, completar el cofre y la ruta alternativa es el camino de menor resistencia mecánica para obtener un generador de partidas infinitas en Greed y una herramienta de control de masas.",
        "tip": "En la ruta hacia The Chest (vía Cathedral con The Polaroid), maximiza las ![[images/rooms/angel.png|24]] **Salas del Ángel** evitando pactos en ![[images/rooms/devil.png|24]] **Salas del Diablo** para conseguir baterías o pasivos de daño sin sacrificar contenedores de ![[images/pickups/heart_red.png|24]]. Guarda el D6 para los 4 cofres iniciales de The Chest."
    },
    "Desafíos": {
        "titulo": "Desafíos Clave: Limpieza de Pools y Mitigación de Maldiciones",
        "icono": "images/pickups/swords.png",
        "icono_size": 26,
        "orden": 5,
        "descripcion": "Desafíos rápidos que eliminan fricción en runs normales, asegurando protección contra maldiciones y generadores de recursos masivos para emergencias.",
        "tip": "En *Darkness Falls* comienzas con ![[images/characters/eve.png|24]] **Eve**, Dead Bird y Whore of Babylon activado. Mantén la vida roja vacía a base de pactos o fuegos para conservar el multiplicador de velocidad y daño; prioriza tiendas buscando cartas de Emperor para saltar directo a la sala del jefe."
    },
    "Apertura Vía Tainted": {
        "titulo": "Apertura de la Vía Tainted: Acceso a Home",
        "icono": "images/pickups/home_key.png",
        "icono_size": 28,
        "orden": 6,
        "descripcion": "Alcanzar la zona de Home con una llave roja (![[images/pickups/red_key.png|24]]) o fragmento (![[images/pickups/cracked_key.png|24]]) abre la puerta a los 17 personajes Tainted, desbloqueando el 50% restante del contenido de Repentance.",
        "tip": "Durante el descenso normal, suelta cualquier baratija (Trinket) en una Boss Room o Treasure Room. Al ascender de regreso durante la secuencia de The Ascent, esa baratija se habrá transformado en un ![[images/pickups/cracked_key.png|24]] Cracked Key garantizado."
    },
    "Personajes Tainted": {
        "titulo": "Personajes Tainted: Los Game-Breakers Absolutos",
        "icono": "images/pickups/crown.png",
        "icono_size": 28,
        "orden": 7,
        "descripcion": "El escalón más alto de poder en el juego. Sus recompensas reescriben las reglas de generación de objetos, tiendas y generación de almas.",
        "tip": "Enfoca primero las rutas cortas (Boss Rush / Hush con cartas de Mama Mega) antes de embarcarte en maratones hacia The Beast o Delirium."
    },
    "The Lost & Keeper": {
        "titulo": "Especialistas Avanzados: The Lost & Keeper",
        "icono": "images/characters/the_lost.png",
        "icono_size": 36,
        "orden": 8,
        "descripcion": "Estas marcas demandan una ejecución táctica impecable, libre de impactos imprudentes, pero sus recompensas (Godhead, Deep Pockets, Crooked Penny) están en la cúspide del tier list.",
        "tip": "Aprovecha el botón de pausa de las ![[images/rooms/devil.png|24]] Devil Rooms: The Lost puede tomar tratos diabólicos gratis. Con Keeper, deja siempre monedas en el suelo sin recoger en salas ya limpiadas para curarte ante emergencias."
    },
    "Personajes Clásicos": {
        "titulo": "Personajes Clásicos: Familiares Ofensivos y Utilidad",
        "icono": "images/characters/isaac.png",
        "icono_size": 28,
        "orden": 9,
        "descripcion": "Desbloqueos de transición accesibles en dificultad Difícil para engrosar el pool de familiares con DPS consistente y utilidades pasivas indispensables.",
        "tip": "Guarda baterías o cargas activas para Box of Friends durante batallas prolongadas de jefes finales (Hush, Mega Satan)."
    },
    "Endgame": {
        "titulo": "Cúspide del Completismo: Endgame Máximo",
        "icono": "images/pickups/dead_god.png",
        "icono_size": 30,
        "orden": 10,
        "descripcion": "Los objetivos que cierran el 100% de The Binding of Isaac Repentance+. Representan maestría absoluta de todas las mecánicas y otorgan control absoluto sobre cualquier partida futura.",
        "tip": "Para encontrar los últimos ítems raros que no hayan aparecido en partida (como Death Certificate), recurre a Spindown Dice o rota pedestales en Secret Rooms mediante D6 / perthro."
    }
}

def cargar_efectos_existentes():
    if EFFECTS_PATH.exists():
        try:
            with open(EFFECTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

BOSS_WIKI_MAP = {
    "Satan": "https://bindingofisaacrebirth.wiki.gg/wiki/Satan",
    "Satanás": "https://bindingofisaacrebirth.wiki.gg/wiki/Satan",
    "Mega Satan": "https://bindingofisaacrebirth.wiki.gg/wiki/Mega_Satan",
    "Mom": "https://bindingofisaacrebirth.wiki.gg/wiki/Mom",
    "Mom's Heart": "https://bindingofisaacrebirth.wiki.gg/wiki/Mom%27s_Heart",
    "Corazón de Mom": "https://bindingofisaacrebirth.wiki.gg/wiki/Mom%27s_Heart",
    "It Lives!": "https://bindingofisaacrebirth.wiki.gg/wiki/It_Lives!",
    "It Lives": "https://bindingofisaacrebirth.wiki.gg/wiki/It_Lives!",
    "Isaac": "https://bindingofisaacrebirth.wiki.gg/wiki/Isaac_(Boss)",
    "??? (Blue Baby)": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Boss)",
    "Blue Baby": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Boss)",
    "???": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Boss)",
    "The Lamb": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Lamb",
    "Hush": "https://bindingofisaacrebirth.wiki.gg/wiki/Hush",
    "Delirium": "https://bindingofisaacrebirth.wiki.gg/wiki/Delirium",
    "Mother": "https://bindingofisaacrebirth.wiki.gg/wiki/Mother",
    "The Beast": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Beast",
    "Ultra Greedier": "https://bindingofisaacrebirth.wiki.gg/wiki/Ultra_Greedier",
    "Ultra Greed": "https://bindingofisaacrebirth.wiki.gg/wiki/Ultra_Greed",
    "Dogma": "https://bindingofisaacrebirth.wiki.gg/wiki/Dogma",
    "Boss Rush": "https://bindingofisaacrebirth.wiki.gg/wiki/Boss_Rush",
    "Baby Plum": "https://bindingofisaacrebirth.wiki.gg/wiki/Baby_Plum",
    "The Siren": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Siren",
}

CHAR_WIKI_MAP = {
    "Isaac": "https://bindingofisaacrebirth.wiki.gg/wiki/Isaac",
    "Magdalene": "https://bindingofisaacrebirth.wiki.gg/wiki/Magdalene",
    "Maggy": "https://bindingofisaacrebirth.wiki.gg/wiki/Magdalene",
    "Cain": "https://bindingofisaacrebirth.wiki.gg/wiki/Cain",
    "Judas": "https://bindingofisaacrebirth.wiki.gg/wiki/Judas",
    "??? (Blue Baby)": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Character)",
    "Blue Baby": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Character)",
    "???": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Character)",
    "Eve": "https://bindingofisaacrebirth.wiki.gg/wiki/Eve",
    "Samson": "https://bindingofisaacrebirth.wiki.gg/wiki/Samson",
    "Azazel": "https://bindingofisaacrebirth.wiki.gg/wiki/Azazel",
    "Lazarus": "https://bindingofisaacrebirth.wiki.gg/wiki/Lazarus",
    "Eden": "https://bindingofisaacrebirth.wiki.gg/wiki/Eden",
    "The Lost": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Lost",
    "Lost": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Lost",
    "Lilith": "https://bindingofisaacrebirth.wiki.gg/wiki/Lilith",
    "Keeper": "https://bindingofisaacrebirth.wiki.gg/wiki/Keeper",
    "Apollyon": "https://bindingofisaacrebirth.wiki.gg/wiki/Apollyon",
    "The Forgotten": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Forgotten",
    "Forgotten": "https://bindingofisaacrebirth.wiki.gg/wiki/The_Forgotten",
    "Bethany": "https://bindingofisaacrebirth.wiki.gg/wiki/Bethany",
    "Jacob & Esau": "https://bindingofisaacrebirth.wiki.gg/wiki/Jacob_%26_Esau",
    "Jacob and Esau": "https://bindingofisaacrebirth.wiki.gg/wiki/Jacob_%26_Esau",
    "Jacob": "https://bindingofisaacrebirth.wiki.gg/wiki/Jacob_%26_Esau",
    "Esau": "https://bindingofisaacrebirth.wiki.gg/wiki/Jacob_%26_Esau",
    "Tainted Isaac": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Isaac",
    "Tainted Magdalene": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Magdalene",
    "Tainted Cain": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Cain",
    "Tainted Judas": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Judas",
    "Tainted ???": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_%3F%3F%3F",
    "Tainted Blue Baby": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_%3F%3F%3F",
    "Tainted Eve": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Eve",
    "Tainted Samson": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Samson",
    "Tainted Azazel": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Azazel",
    "Tainted Lazarus": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Lazarus",
    "Tainted Eden": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Eden",
    "Tainted Lost": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Lost",
    "Tainted Lilith": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Lilith",
    "Tainted Keeper": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Keeper",
    "Tainted Apollyon": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Apollyon",
    "Tainted Forgotten": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Forgotten",
    "Tainted Bethany": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Bethany",
    "Tainted Jacob": "https://bindingofisaacrebirth.wiki.gg/wiki/Tainted_Jacob",
}

def cargar_wiki_urls():
    if WIKI_URLS_PATH.exists():
        try:
            with open(WIKI_URLS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def cargar_wiki_entities():
    if WIKI_ENTITIES_PATH.exists():
        try:
            with open(WIKI_ENTITIES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

WIKI_ACH_MAP = cargar_wiki_urls()
WIKI_ENTITIES_MAP = cargar_wiki_entities()
SORTED_WIKI_TERMS = sorted(WIKI_ENTITIES_MAP.keys(), key=lambda x: -len(x))

def enlazar_terminos_wiki(texto):
    """Enlaza automáticamente personajes, ítems, jefes y logros a wiki.gg sin alterar links existentes."""
    if not texto:
        return ""
    placeholders = []
    def hide(m):
        placeholders.append(m.group(0))
        return f"\x00PH_{len(placeholders)-1}\x00"

    # Proteger links existentes, wikilinks de imagen y tags HTML
    t = re.sub(r"!\[\[[^\]]+\]\]|\[[^\]]+\]\([^\)]+\)|<[^>]+>", hide, str(texto))

    # Desambiguación de jefes precedidos por 'vs' o 'contra'
    boss_vs = {
        "??? (Blue Baby)": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Boss)",
        "Blue Baby": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Boss)",
        "???": "https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F_(Boss)",
        "Isaac": "https://bindingofisaacrebirth.wiki.gg/wiki/Isaac_(Boss)",
    }
    for b_name, b_url in sorted(boss_vs.items(), key=lambda x: -len(x[0])):
        pat = re.compile(rf"(\b(?:vs|contra)\s+(?:\x00PH_\d+\x00\s+)?){re.escape(b_name)}(?=$|[^\w&?])", re.IGNORECASE)
        def repl_boss(m, name=b_name, url=b_url):
            prefix = m.group(1)
            placeholders.append(f"[{name}]({url})")
            return f"{prefix}\x00PH_{len(placeholders)-1}\x00"
        t = pat.sub(repl_boss, t)

    for term in SORTED_WIKI_TERMS:
        if len(term) < 2:
            continue
        url = WIKI_ENTITIES_MAP[term]
        escaped = re.escape(term)
        pattern = re.compile(rf"(?<![\w/]){escaped}(?![\w/])")
        if pattern.search(t):
            def repl(m):
                matched = m.group(0)
                placeholders.append(f"[{matched}]({url})")
                return f"\x00PH_{len(placeholders)-1}\x00"
            t = pattern.sub(repl, t)

    for i, orig in enumerate(placeholders):
        t = t.replace(f"\x00PH_{i}\x00", orig)
    return t

def enriquecer_requisito(texto):
    """Inserta iconos con pipe escapado y enlaces a wiki.gg en textos de requisitos para tablas."""
    if not texto:
        return "Condición no especificada"

    res = texto

    # Caso especial: Boss Rush
    if "Boss Rush" in res and "images/bosses/boss_rush.png" not in res:
        url = BOSS_WIKI_MAP.get("Boss Rush", "https://bindingofisaacrebirth.wiki.gg/wiki/Boss_Rush")
        res = re.sub(r"\bBoss Rush\b", rf"![[images/bosses/boss_rush.png\|26]] [Boss Rush]({url})", res)

    # Jefes ordenados por longitud descendente para evitar colisiones
    for boss in sorted(BOSS_ICONS.keys(), key=lambda x: -len(x)):
        if boss == "Boss Rush":
            continue
        icon = BOSS_ICONS[boss]
        url = BOSS_WIKI_MAP.get(boss, f"https://bindingofisaacrebirth.wiki.gg/wiki/{boss}")
        pattern = re.compile(rf"(derrotar a|vencer a|dejar escapar a)\s+{re.escape(boss)}", re.IGNORECASE)
        res = pattern.sub(rf"\1 ![[{icon}\|26]] [{boss}]({url})", res)
        pattern2 = re.compile(rf"\bo\s+{re.escape(boss)}", re.IGNORECASE)
        res = pattern2.sub(rf"o ![[{icon}\|26]] [{boss}]({url})", res)

    # Personajes: "con <Personaje>"
    for char in sorted(CHAR_ICONS.keys(), key=lambda x: -len(x)):
        icon = CHAR_ICONS[char]
        url = CHAR_WIKI_MAP.get(char, f"https://bindingofisaacrebirth.wiki.gg/wiki/{char}")
        pattern = re.compile(rf"\bcon\s+{re.escape(char)}(?=$|[^\w&?])", re.IGNORECASE)
        res = pattern.sub(rf"con ![[{icon}\|24]] [{char}]({url})", res)

    # Desafíos
    def chal_repl(m):
        num = m.group(1)
        name = m.group(2)
        full = m.group(0)
        url = WIKI_ENTITIES_MAP.get(f"Desafío #{num} ({name})") or WIKI_ENTITIES_MAP.get(name) or "https://bindingofisaacrebirth.wiki.gg/wiki/Challenges"
        return f"[{full}]({url})"
    res = re.sub(r"Desafío #(\d+)\s*\(([^)]+)\)", chal_repl, res)

    # Salas
    if "Sacrifice Room" in res:
        url = WIKI_ENTITIES_MAP.get("Sacrifice Room", "https://bindingofisaacrebirth.wiki.gg/wiki/Sacrifice_Room")
        res = res.replace("Sacrifice Room", f"![[images/rooms/sacrifice.png\\|24]] [Sacrifice Room]({url})")
    if "Curse Room" in res:
        url = WIKI_ENTITIES_MAP.get("Curse Room", "https://bindingofisaacrebirth.wiki.gg/wiki/Curse_Room")
        res = res.replace("Curse Room", f"![[images/rooms/curse.png\\|24]] [Curse Room]({url})")
    if "Devil Room" in res or "Sala del Diablo" in res:
        url = WIKI_ENTITIES_MAP.get("Devil Room", "https://bindingofisaacrebirth.wiki.gg/wiki/Devil_Room")
        res = re.sub(r"(Devil Room|Sala del Diablo)", rf"![[images/rooms/devil.png\|24]] [\1]({url})", res)
    if "Angel Room" in res or "Sala del Ángel" in res:
        url = WIKI_ENTITIES_MAP.get("Angel Room", "https://bindingofisaacrebirth.wiki.gg/wiki/Angel_Room")
        res = re.sub(r"(Angel Room|Sala del Ángel)", rf"![[images/rooms/angel.png\|24]] [\1]({url})", res)

    # Monedas / Máquina Greed
    gm_url = WIKI_ENTITIES_MAP.get("máquina de Greed", "https://bindingofisaacrebirth.wiki.gg/wiki/Greed_Donation_Machine")
    res = re.sub(r"(\d+)\s+monedas\s+en\s+la\s+máquina(\s+de\s+greed)?",
                 rf"\1 ![[images/pickups/penny.png\|24]] monedas en la [máquina de Greed]({gm_url})",
                 res, flags=re.IGNORECASE)

    # Enlazar cualquier otro término remanente (ej. Red Key, Cracked Key)
    res = enlazar_terminos_wiki(res)
    return res

def formatear_tier(item, custom_tier=None):
    """Formatea la columna Calidad / Tier con estrellas e iconos pixel art."""
    if custom_tier and "![" in custom_tier:
        return custom_tier

    star = "![[images/pickups/star.png\\|14]]"
    prio = item.get("prioridad", "Media").lower()
    nombre = item.get("nombre", "").lower()
    req = item.get("desbloqueo", "").lower()
    aid = item.get("id", 0)

    if "personaje" in prio or "personaje" in nombre or aid in [82, 251]:
        return "![[images/characters/isaac.png\\|18]] Personaje"
    if "runa" in nombre or "rune" in nombre:
        return "![[images/pickups/rune.png\\|18]] Runa / S"
    if any(k in nombre for k in ["carta", "card", "reversed", "inverted", "the stars", "the moon"]):
        return "![[images/pickups/card.png\\|18]] Carta / A"
    if "trinket" in nombre or "baratija" in req:
        return "![[images/pickups/trinket.png\\|18]] Trinket / A"
    if aid in [249, 250, 251, 341] or "máquina de greed" in req:
        return "![[images/pickups/greed_machine.png\\|18]] Máquina"
    if aid in [636, 637] or "dead god" in nombre:
        return "![[images/pickups/dead_god.png\\|18]] Medalla Final"

    tiers = {"crítica": 4, "critica": 4, "god": 4, "alta": 3, "media": 2}
    t = tiers.get(prio, 1)
    return f"{star * t} Tier {t}"

def generar_efecto_tactico(item, effects_db):
    """Obtiene el efecto enriquecido de la base de datos o genera uno contextual."""
    aid_str = str(item.get("id"))
    if aid_str in effects_db:
        return effects_db[aid_str].get("efecto", item.get("desbloqueo", ""))

    nombre = item.get("nombre", "")
    req = item.get("desbloqueo", "")
    prio = item.get("prioridad", "")

    if "personaje" in req.lower() or item.get("id") in [82, 251]:
        return f"Desbloquea a {nombre} como personaje jugable con mecánicas únicas y acceso a sus desbloqueos avanzados."
    if "runa" in nombre.lower() or "rune" in nombre.lower():
        return f"Poderosa runa consumible que altera el piso o multiplica recursos críticos para situaciones de emergencia."
    if "carta" in nombre.lower() or "card" in nombre.lower():
        return f"Carta consumible de alto impacto estratégico para acelerar la partida o sortear obstáculos clave."

    return f"Objeto pasivo/activo de prioridad {prio} que optimiza de forma sustancial la consistencia de victoria y el escalado de daño."

def detectar_categoria_item(item):
    """Clasifica un ítem pendiente en una categoría temática precisa."""
    req = item.get("desbloqueo", "")
    nombre = item.get("nombre", "")
    aid = item.get("id", 0)

    # 1. Modo Greed / Máquina
    if ("máquina" in req.lower() and "greed" in req.lower()) or aid in [249, 250, 251, 341]:
        return "Greed Machine"

    # 2. Desafíos
    if "desafío #" in req.lower() or "challenge #" in req.lower() or aid in [92, 120, 224, 225, 226, 227, 228, 229, 230]:
        return "Desafíos"

    # 3. Acceso a Home / Vía Tainted
    if any(k in req.lower() for k in ["home", "red key", "cracked key", "the beast"]) or aid in [415, 477, 493]:
        return "Apertura Vía Tainted"

    # 4. Jacob & Esau
    if "jacob & esau" in req.lower() or "jacob" in req.lower() or aid in [429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 472]:
        return "Jacob & Esau"

    # 5. Tainted Isaac
    if "tainted isaac" in req.lower() or aid in [485, 486, 491, 541, 584, 601]:
        return "Tainted Isaac"

    # 6. Otros Personajes Tainted
    if "tainted" in req.lower() or aid in [501, 502, 504, 542, 587, 594, 607, 616, 629]:
        return "Personajes Tainted"

    # 7. Isaac clásico
    if re.search(r"con\s+isaac\b", req, re.IGNORECASE) or aid in [49, 440]:
        return "Isaac"

    # 8. The Lost o Keeper
    if "the lost" in req.lower() or "keeper" in req.lower() or aid in [82, 156, 460]:
        return "The Lost & Keeper"

    # 9. Endgame
    if aid in [547, 636, 637] or "dead god" in nombre.lower():
        return "Endgame"

    # 10. Personajes Clásicos
    for char in ["Lilith", "Judas", "Azazel", "Eve", "Samson", "Lazarus", "Forgotten", "Bethany", "Cain", "Magdalene"]:
        if re.search(rf"con\s+{char}\b", req, re.IGNORECASE):
            return "Personajes Clásicos"

    return "Personajes Clásicos"

def evaluar_facilidad_logro(item):
    """Evalúa la facilidad de obtención de un logro en base a sus requisitos."""
    cond = str(item.get("desbloqueo", "")).lower()
    score = 0

    # Penalización máxima: Endgame total / Completismo 100%
    if any(k in cond for k in ["todas las marcas en difícil con todos los personajes", "todos los demás logros", "recoger todos los objetos", "dead god", "death certificate", "mega mush", "platinum god"]):
        return -2500
    if "todas las marcas" in cond:
        return -1200

    # Jefes finales extremos / Rutas pesadas
    if "delirium" in cond or "void" in cond:
        score -= 600
    elif "mother" in cond or "corpse" in cond:
        score -= 500
    elif "the beast" in cond or "dogma" in cond:
        score -= 400
    elif "ultra greedier" in cond:
        score -= 350
    elif "hush" in cond:
        score -= 300
    elif "mega satan" in cond:
        score -= 250
    elif "boss rush" in cond:
        score -= 200
    # Jefes asequibles / Rutas intermedias
    elif any(b in cond for b in ["??? (blue baby)", "blue baby", "the lamb"]):
        score += 200
    elif any(b in cond for b in ["satan", "isaac", "catedral", "sheol"]):
        score += 350
    elif any(b in cond for b in ["mom's heart", "it lives", "corazón de mom", "mom por primera vez"]):
        score += 500

    # Desafíos
    if "desbloquea desafío" in cond:
        score -= 100
    elif "completar el desafío" in cond or "completar desafío" in cond or "challenge #" in cond:
        score += 450

    # Desbloqueos en Home (armario oculto / Tainted)
    if "armario oculto en home" in cond or "red key" in cond or "cracked key" in cond:
        score += 400

    # Máquina de Greed
    if "máquina de greed" in cond or "modo greed" in cond:
        m = re.search(r"(\d+)\s+monedas", cond)
        if m:
            coins = int(m.group(1))
            if coins <= 500:
                score += 450
            elif coins <= 879:
                score += 300
            else:
                score += 150
        else:
            score += 250

    # Tareas simples en partida
    if any(k in cond for k in ["monedas a la vez", "contenedores de corazón", "morir en una sacrifice room"]):
        score += 400

    # Dificultad del personaje
    if "the lost" in cond:
        score -= 350
    elif "keeper" in cond:
        score -= 200
    elif "jacob & esau" in cond or "jacob" in cond:
        score -= 200
    elif any(f"tainted {c}" in cond for c in ["lost", "jacob", "lazarus", "cain", "eden"]):
        score -= 350
    elif any(f"tainted {c}" in cond for c in ["isaac", "lilith", "judas", "keeper", "bethany"]):
        score -= 50
    elif any(f"con {c}" in cond for c in ["azazel", "judas", "lilith", "samson", "cain", "isaac"]):
        score += 150

    return score

def evaluar_utilidad_logro(item, custom_tier=None):
    """Evalúa la utilidad estratégica intrínseca de un logro."""
    prio = str(item.get("prioridad", "")).lower()
    tier = str(custom_tier or "").lower()
    nombre = str(item.get("nombre", "")).lower()

    score = 0
    if "tier 4" in tier or any(k in prio for k in ["critica", "crítica", "god", "nucleo", "núcleo"]):
        score += 1000
    elif "tier 3" in tier or "alta" in prio:
        score += 600
    elif "tier 2" in tier or "media" in prio:
        score += 350
    else:
        score += 150

    # Bonificaciones por utilidad mecánica especial
    if any(k in nombre for k in ["d20", "d6", "spindown", "rock bottom", "birthright", "damocles", "glitched crown", "holy mantle"]):
        score += 300
    elif any(k in nombre for k in ["curved horn", "swallowed penny", "sigil of baphomet", "rune", "runa", "perthro", "jera", "dagaz"]):
        score += 200
    elif any(k in nombre for k in ["tainted lilith", "tainted judas", "keeper", "the lost"]):
        score += 250

    return score

def consultar_ia_bitacora_y_curacion(data, limit=25, timeout=45):
    """
    Pasa los logros bloqueados prioritarios a la IA para que:
    1. Determine qué N objetos son genuinamente buenos y valiosos (independientemente del tier) para este punto de la partida.
    2. Redacte la bitácora estratégica con 2 sugerencias de run.
    """
    if not shutil.which("agy"):
        return None, None, {}, []

    unlocked_set = set(data.get("desbloqueados_ids", []))
    if not unlocked_set:
        latest, _ = find_latest_saves(BASE_DIR / "save_backups")
        if latest:
            unlocked_set = get_unlocked_ids(latest)

    # Obtener lista completa de bloqueados factibles
    bloqueados = [
        b for b in data.get("todos_bloqueados", [])
        if es_logro_factible(b, unlocked_set)
    ]
    if not bloqueados:
        ach_map = {}
        if ACH_MAP_PATH.exists():
            try:
                with open(ACH_MAP_PATH, "r", encoding="utf-8") as f:
                    ach_map = json.load(f)
            except Exception:
                pass
        for aid, info in ach_map.items():
            entry = {
                "id": int(aid),
                "nombre": info.get("name", ""),
                "desbloqueo": info.get("condition", ""),
                "prioridad": info.get("priority", "Media")
            }
            if int(aid) not in unlocked_set and es_logro_factible(entry, unlocked_set):
                bloqueados.append(entry)

    bloqueados_dict = {b["id"]: b for b in bloqueados}
    # Seleccionar los mejores candidatos para la IA (ordenados por utilidad + facilidad)
    candidatos_ia = sorted(
        bloqueados,
        key=lambda b: -(evaluar_utilidad_logro(b) + evaluar_facilidad_logro(b))
    )[:50]
    locked_lines = "\n".join([f"{item['id']}: {item['nombre']} | {item['desbloqueo']}" for item in candidatos_ia])

    nuevos = [
        f"{n.get('nombre', '')} ({n.get('como_se_obtuvo', '')})"
        for n in data.get("nuevos_esta_sesion", [])
    ]
    progreso_str = f"{data.get('desbloqueados_total', 0)}/{data.get('total_logros_juego', 641)} ({data.get('porcentaje_completado', 0)}%)"

    prompt = f"""Eres un analista de élite de The Binding of Isaac Repentance+.
El jugador tiene {progreso_str} logros completados ({len(bloqueados)} logros bloqueados restantes).
Logros conseguidos en la última sesión: {nuevos if nuevos else 'Ninguno en esta sesión'}

Lista completa de los {len(bloqueados)} logros que aún tiene BLOQUEADOS:
{locked_lines}

TAREA 1: RANKING POR RELACIÓN UTILIDAD / FACILIDAD DE OBTENCIÓN (EXACTAMENTE {limit} LOGROS)
Evalúa los {len(bloqueados)} logros bloqueados y selecciona exactamente {limit} logros ordenados ESTRICTAMENTE de mayor a menor prioridad según su relación UTILIDAD / FACILIDAD DE OBTENCIÓN (los objetos más útiles, rotos o prácticos que a la vez sean los MÁS FÁCILES, rápidos o viables de desbloquear primero).

CRITERIOS DE CLASIFICACIÓN (DE ARRIBA A ABAJO):
1. PUESTOS SUPERIORES (1 al 10 - MÁXIMA UTILIDAD + MÁXIMA FACILIDAD):
   - Objetos con impacto masivo que se consiguen con poco esfuerzo o rutas sencillas.
   - Desafíos asequibles con recompensas clave (Swallowed Penny, Rune of Dagaz, Rune of Jera, Perthro, Sigil of Baphomet, Spirit Sword).
   - Jefes estándar (Satan, Isaac, Blue Baby, The Lamb) con personajes poderosos/consistentes (Isaac con D6, Azazel, Judas, Lilith) -> ej. D20, Curved Horn, Rune Bag.
   - Desbloqueos de personajes o mecánicas inmediatas (Tainted Lilith/Judas en Home, Holy Mantle en máquina de Greed).
   - Desbloqueos claves de Jacob & Esau que NO requieran jefes extremos (Birthright en Blue Baby, Damocles en The Lamb).
2. PUESTOS MEDIOS (11 al 18 - ALTA UTILIDAD + DIFICULTAD MODERADA):
   - Objetos excelentes pero que exigen más habilidad o tiempo (Boss Rush, Hush con personajes fuertes, Greedier normal, metas intermedias de Greed Machine).
3. PUESTOS INFERIORES (19 al 25 - ALTA UTILIDAD PERO DIFICULTAD EXTREMA):
   - Desbloqueos que exigen jefes finales brutales o personajes frustrantes (Mother, Delirium, The Beast, marcas duras de Jacob & Esau, The Lost). Solo inclúyelos si su recompensa es trascendental (ej. Spindown Dice, Glitched Crown).
4. EXCLUSIONES TOTALES:
   - PROHIBIDO incluir logros de completismo masivo o inalcanzables a corto plazo como Mega Mush, Death Certificate, Dead God o Platinum God.
   - PROHIBIDO recomendar logros de personajes que el jugador NO tenga desbloqueados (la lista ya fue filtrada estrictamente para contener únicamente objetivos viables con los personajes que el jugador posee; no inventes logros de otros personajes).
Para cada logro seleccionado incluye su 'id' y un 'motivo' táctico conciso (1-2 líneas) destacando su efecto y por qué es rentable sacarlo por su facilidad/impacto.

TAREA 2: PROTOCOLO COMPACTO PARA LA PRÓXIMA RUN
Presenta exactamente 2 sugerencias tácticas viables y de rápida consecución (enfocadas en la mejor relación utilidad/facilidad de la lista y EXCLUSIVAMENTE con personajes ya desbloqueados):
- **Plan A (Principal - Mejor balance Utilidad/Facilidad):** ![[images/achievements/<id>.png|20]] **[Nombre Ítem]** con ![[images/characters/<char>.png|20]] [Personaje] vs ![[images/bosses/<boss>.png|20]] [Jefe / Meta]. Directiva: [Estrategia clave en 1 línea].
- **Plan B (Alternativo):** ![[images/achievements/<id>.png|20]] **[Nombre Ítem]** con ![[images/characters/<char>.png|20]] [Personaje] vs ![[images/bosses/<boss>.png|20]] [Jefe / Meta]. Directiva: [Estrategia clave en 1 línea].

TAREA 3: CONSEJOS TÁCTICOS POR CATEGORÍA
Redacta un consejo táctico específico y práctico (1 o 2 líneas) enfocado en cómo conseguir los ítems que seleccionaste en cada categoría presente, usando exactamente estas claves cuando aplique:
["Greed Machine", "Jacob & Esau", "Tainted Isaac", "Isaac", "Desafíos", "Apertura Vía Tainted", "Personajes Tainted", "The Lost & Keeper", "Personajes Clásicos", "Endgame"]

TAREA 4: PRIORIDAD DE TODAS LAS SECCIONES
Ordena la lista de todas las categorías presentes estrictamente de MAYOR A MENOR PRIORIDAD estratégica según la urgencia y facilidad/valor de sus desbloqueables.
En 'orden_secciones', incluye para cada categoría su nombre y un 'motivo' de 1 línea explicando por qué ocupa ese lugar de prioridad.

REGLAS DE FORMATO (ESTRICTO):
- PROHIBIDO usar emojis Unicode (nada de 💀, 🧠, ⚔️, 🔥). Usa iconos en formato Obsidian: ![[images/characters/<nombre>.png|20]], ![[images/bosses/<jefe>.png|20]], ![[images/pickups/<item>.png|20]].
- Devuelve ÚNICAMENTE un JSON válido con esta estructura:
{{
  "protocolo": "- **Plan A (Principal):** ...\\n- **Plan B (Alternativo):** ...",
  "orden_secciones": [
    {{"categoria": "Nombre Categoria 1", "motivo": "Explicación concisa de 1 línea..."}},
    {{"categoria": "Nombre Categoria 2", "motivo": "Explicación concisa de 1 línea..."}}
  ],
  "seleccionados": [
    {{"id": 431, "motivo": "Duplica slots pasivos y potencia habilidades únicas..."}},
    ...
  ],
  "tips_categorias": {{
    "Greed Machine": "Consejo dinámico para donar eficientemente...",
    "Jacob & Esau": "Consejo dinámico para jugar la doble hitbox..."
  }}
}}"""

    try:
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS="")
        cmd = [
            "agy",
            "--model", "gemini-3.8-flash-low",
            "--effort", "low",
            "--disable-slash-commands",
            "--dangerously-skip-permissions",
            "-p", prompt
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
            stdin=subprocess.DEVNULL
        )
        if res.returncode == 0 and res.stdout.strip():
            raw = res.stdout.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw.rsplit("\n", 1)[0]
            parsed = json.loads(raw)

            raw_proto = (
                parsed.get("protocolo")
                or parsed.get("bitacora")
                or parsed.get("protocolo_run")
                or parsed.get("plan")
                or ""
            )
            if isinstance(raw_proto, list):
                raw_proto = "\n".join(str(x) for x in raw_proto)
            bitacora = sanear_texto_ia(str(raw_proto))

            raw_tips = parsed.get("tips_categorias", {})
            tips_categorias = {k: sanear_texto_ia(str(v)) for k, v in raw_tips.items() if v}

            raw_cats = parsed.get("orden_secciones") or parsed.get("prioridad_secciones") or []
            if isinstance(raw_cats, dict):
                orden_secciones = [str(k).strip() for k in raw_cats.keys() if k]
            else:
                orden_secciones = [
                    str(x.get("categoria", x) if isinstance(x, dict) else x).strip()
                    for x in raw_cats if x
                ]

            # Procesar y validar lista de seleccionados
            seleccionados_raw = parsed.get("seleccionados", [])
            items_seleccionados = []
            seen_ids = set()
            for s in seleccionados_raw:
                aid = int(s.get("id", 0))
                if aid in bloqueados_dict and aid not in seen_ids:
                    info = bloqueados_dict[aid]
                    if not es_logro_factible(info, unlocked_set):
                        continue
                    seen_ids.add(aid)
                    items_seleccionados.append({
                        "id": aid,
                        "nombre": info.get("nombre", f"Logro #{aid}"),
                        "desbloqueo": info.get("desbloqueo", ""),
                        "prioridad": info.get("prioridad", "Alta"),
                        "motivo": s.get("motivo", "")
                    })
                    if len(items_seleccionados) >= limit:
                        break

            # Si faltan para llegar exactamente a limit, rellenar ordenando por utilidad + facilidad
            if len(items_seleccionados) < limit:
                candidatos = [
                    b for b in bloqueados
                    if b["id"] not in seen_ids and b["id"] in bloqueados_dict and es_logro_factible(b, unlocked_set)
                ]
                candidatos.sort(key=lambda b: -(evaluar_utilidad_logro(b) + evaluar_facilidad_logro(b)))
                for p in candidatos:
                    seen_ids.add(p["id"])
                    items_seleccionados.append(p)
            if bitacora:
                try:
                    with open(AI_CACHE_PATH, "w", encoding="utf-8") as f:
                        json.dump({
                            "desbloqueados_total": data.get("desbloqueados_total", 0),
                            "protocolo": bitacora,
                            "tips_categorias": tips_categorias,
                            "orden_secciones": orden_secciones,
                            "seleccionados": items_seleccionados
                        }, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

            return bitacora, items_seleccionados, tips_categorias, orden_secciones
    except Exception as e:
        print(f"      ℹ No se pudo completar curación IA ({e}), usando selección heurística.", file=sys.stderr)

    return None, None, {}, []

ACH_MAP_PATH = BASE_DIR / "achievements.json"
NAME_TO_AID_CACHE = None

def get_name_to_aid_map():
    global NAME_TO_AID_CACHE
    if NAME_TO_AID_CACHE is not None:
        return NAME_TO_AID_CACHE

    m = {}
    if ACH_MAP_PATH.exists():
        try:
            with open(ACH_MAP_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for aid, info in data.items():
                name = info.get("name", "").lower()
                clean = re.sub(r"[^a-z0-9]", "", name)
                m[clean] = str(aid)
                slug = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
                m[slug] = str(aid)
        except Exception:
            pass

    aliases = {
        "holy_mantle": "250",
        "holymantle": "250",
        "the_negative": "78",
        "thenegative": "78",
        "moms_knife": "43",
        "momsknife": "43",
        "d_infinity": "282",
        "dinfinity": "282",
        "godhead": "156",
        "incubus": "190",
        "box_of_friends": "203",
        "birthright": "431",
        "damocles": "432",
        "rock_bottom": "429",
        "boomerang": "270",
        "spindown_dice": "584",
        "glitched_crown": "486",
        "mega_mush": "491",
        "death_certificate": "636",
    }
    m.update(aliases)
    NAME_TO_AID_CACHE = m
    return m

def sanear_texto_ia(texto):
    """Limpia emojis y valida que todas las imágenes enlazadas existan realmente en disco."""
    if not texto:
        return ""

    texto = re.sub(r"💀\s*(?:The Lost\b)?", r"![[images/characters/the_lost.png|20]] The Lost", texto)
    texto = re.sub(r"[\U0001F300-\U0001F9FF]", "", texto)

    name_map = get_name_to_aid_map()

    def resolver_enlace(match):
        full, target, pipe, size = match.group(0), match.group(1).strip(), match.group(2) or "", match.group(3) or ""

        # Si el archivo ya existe directamente en disco, respetarlo
        if (BASE_DIR / target).exists():
            return full

        stem = Path(target).stem.lower()
        clean = re.sub(r"[^a-z0-9]", "", stem)
        aid = name_map.get(clean) or name_map.get(stem)

        if aid and (BASE_DIR / f"images/achievements/{aid}.png").exists():
            return f"![[images/achievements/{aid}.png{pipe}{size}]]"

        for folder in ["characters", "bosses", "rooms", "pickups"]:
            cand = f"images/{folder}/{stem}.png"
            if (BASE_DIR / cand).exists():
                return f"![[{cand}{pipe}{size}]]"

        return ""

    texto = re.sub(r"!\[\[([^\|\]]+)(\\?\|)?([^\]]*)\]\]", resolver_enlace, texto)
    return re.sub(r"[ ]{2,}", " ", texto)

def extraer_ids_protocolo(analisis_ia, unlocked_set=None):
    """Extrae los IDs de logros mencionados como objetivos en Plan A y Plan B, validando su factibilidad."""
    plan_a_ids, plan_b_ids = set(), set()
    if not analisis_ia:
        return plan_a_ids, plan_b_ids

    ach_map = {}
    if unlocked_set is not None and ACH_MAP_PATH.exists():
        try:
            with open(ACH_MAP_PATH, "r", encoding="utf-8") as f:
                ach_map = json.load(f)
        except Exception:
            pass

    for line in analisis_ia.splitlines():
        target_set = plan_a_ids if ("Plan A" in line or "Sugerencia A" in line) else (
            plan_b_ids if ("Plan B" in line or "Sugerencia B" in line) else None
        )
        if target_set is not None:
            for m in re.findall(r"achievements/(\d+)\.png|#(\d+)|ID\s*(\d+)", line):
                val = next((x for x in m if x), None)
                if val:
                    aid = int(val)
                    if unlocked_set is not None and ach_map:
                        item_info = ach_map.get(str(aid), {})
                        if not es_logro_factible(item_info, unlocked_set):
                            continue
                    target_set.add(aid)
    return plan_a_ids, plan_b_ids

def calcular_puntaje_logro(item, rank_idx, total_items, plan_a_ids, plan_b_ids, custom_tier=None):
    """Calcula la prioridad numérica equilibrando utilidad estratégica y facilidad de obtención."""
    aid = item.get("id", 0)
    score = 10000 if aid in plan_a_ids else (5000 if aid in plan_b_ids else 0)
    score += max(0, total_items - rank_idx) * 80

    utilidad = evaluar_utilidad_logro(item, custom_tier)
    facilidad = evaluar_facilidad_logro(item)

    score += (utilidad + facilidad)
    return score

def procesar_guia(data, items, analisis_ia=None, tips_ia=None, orden_secciones_ia=None):
    """Transforma los datos del guardado y los ítems curados en la estructura requerida por guide_template.j2."""
    unlocked_set = set(data.get("desbloqueados_ids", []))
    if not unlocked_set:
        latest, _ = find_latest_saves(BASE_DIR / "save_backups")
        if latest:
            unlocked_set = get_unlocked_ids(latest)
    effects_db = cargar_efectos_existentes()
    plan_a_ids, plan_b_ids = extraer_ids_protocolo(analisis_ia, unlocked_set)
    total_items = len(items)
    grupos = {}

    for idx, item in enumerate(items):
        cat_key = detectar_categoria_item(item)
        if cat_key not in grupos:
            meta = CATEGORIA_METADATA.get(cat_key, {
                "titulo": f"{cat_key}: Desbloqueos Clave",
                "icono": "images/pickups/compass.png",
                "icono_size": 30,
                "descripcion": "Objetivos estratégicos recomendados para la sesión actual.",
                "tip": "Prioriza sinergias de daño y familiarízate con los patrones de las salas."
            })
            tip_final = (tips_ia.get(cat_key) if tips_ia else None) or meta["tip"]
            grupos[cat_key] = {
                "key": cat_key,
                "nombre_corto": cat_key,
                "titulo": meta["titulo"],
                "icono": meta["icono"],
                "icono_size": meta["icono_size"],
                "descripcion": meta["descripcion"],
                "tip": tip_final,
                "logros": []
            }

        custom_tier = effects_db.get(str(item.get("id")), {}).get("tier")
        score = calcular_puntaje_logro(item, idx, total_items, plan_a_ids, plan_b_ids, custom_tier)
        aid_str = str(item.get("id"))
        wiki_url = WIKI_ACH_MAP.get(aid_str, "https://bindingofisaacrebirth.wiki.gg/wiki/Achievements")
        efecto_raw = item.get("motivo") or generar_efecto_tactico(item, effects_db)
        efecto_enlazado = enlazar_terminos_wiki(efecto_raw)

        grupos[cat_key]["logros"].append({
            "id": item.get("id"),
            "nombre": item.get("nombre", f"Logro #{item.get('id')}"),
            "wiki_url": wiki_url,
            "requisito": enriquecer_requisito(item.get("desbloqueo", "")),
            "tier": formatear_tier(item, custom_tier),
            "efecto": efecto_enlazado,
            "score": score
        })

    # Ponderar y ordenar categorías por prioridad
    ai_cat_rank = {name.lower().strip(): len(orden_secciones_ia) - i for i, name in enumerate(orden_secciones_ia or [])}

    for cat in grupos.values():
        cat["logros"].sort(key=lambda l: -l["score"])
        max_score = max((l["score"] for l in cat["logros"]), default=0)
        total_score = sum(l["score"] for l in cat["logros"])
        clean_key = cat["key"].lower().strip()
        ai_bonus = max([weight * 3000 for k, weight in ai_cat_rank.items() if k in clean_key or clean_key in k] or [0])
        cat["prioridad_total"] = (max_score * 5) + total_score + ai_bonus

    categorias_ordenadas = sorted(grupos.values(), key=lambda x: -x["prioridad_total"])

    for cat in categorias_ordenadas:
        cat["titulo"] = enlazar_terminos_wiki(cat["titulo"])
        cat["descripcion"] = enlazar_terminos_wiki(cat["descripcion"])
        cat["tip"] = enlazar_terminos_wiki(cat["tip"])

    # Lista global de logros ordenados estrictamente por prioridad
    items_priorizados = [
        {
            "id": l["id"],
            "nombre": l["nombre"],
            "wiki_url": l["wiki_url"],
            "requisito": l["requisito"],
            "tier": l["tier"],
            "efecto": l["efecto"].replace(r"\|", "|").replace("|", r"\|"),
            "score": l["score"],
            "cat_nombre": enlazar_terminos_wiki(cat["nombre_corto"]),
            "cat_icono": cat["icono"],
        }
        for cat in categorias_ordenadas
        for l in cat["logros"]
    ]
    items_priorizados.sort(key=lambda x: -x["score"])

    # Logros nuevos de la sesión
    nuevos_formateados = [
        {
            "id": n.get("id"),
            "nombre": n.get("nombre", f"Logro #{n.get('id')}"),
            "wiki_url": WIKI_ACH_MAP.get(str(n.get("id")), "https://bindingofisaacrebirth.wiki.gg/wiki/Achievements"),
            "como_se_obtuvo": enriquecer_requisito(n.get("como_se_obtuvo", "")).replace(r"\|", "|")
        }
        for n in data.get("nuevos_esta_sesion", [])
    ]

    analisis_ia_enlazado = enlazar_terminos_wiki(analisis_ia) if analisis_ia else None

    return {
        "progreso_pct": data.get("porcentaje_completado", 0),
        "desbloqueados_total": data.get("desbloqueados_total", 0),
        "total_logros": data.get("total_logros_juego", 641),
        "archivo_actual": data.get("archivo_actual", ""),
        "archivo_previo": data.get("archivo_previo", ""),
        "hitos_recientes": enlazar_terminos_wiki(data.get("hitos_recientes", "")) if data.get("hitos_recientes") else "",
        "nuevos_esta_sesion": nuevos_formateados,
        "analisis_ia": analisis_ia_enlazado,
        "items_priorizados": items_priorizados,
        "categorias": categorias_ordenadas
    }

def generar_protocolo_fallback(items):
    """Genera un Plan A y Plan B determinista a partir de los ítems de mayor prioridad."""
    if not items:
        return None
    p_a = items[0]
    p_b = items[1] if len(items) > 1 else items[0]

    aid_a = p_a.get("id")
    nom_a = p_a.get("nombre")
    req_a = p_a.get("desbloqueo", "")
    efecto_a = p_a.get("motivo") or p_a.get("efecto") or "Maximizar sinergias de daño y supervivencia."

    aid_b = p_b.get("id")
    nom_b = p_b.get("nombre")
    req_b = p_b.get("desbloqueo", "")
    efecto_b = p_b.get("motivo") or p_b.get("efecto") or "Ruta de menor resistencia mecánica y utilidad duradera."

    line_a = f"- **Plan A (Principal - Mejor balance Utilidad/Facilidad):** ![[images/achievements/{aid_a}.png|20]] **{nom_a}** — Requisito: {req_a}. Directiva: {efecto_a}"
    line_b = f"- **Plan B (Alternativo):** ![[images/achievements/{aid_b}.png|20]] **{nom_b}** — Requisito: {req_b}. Directiva: {efecto_b}"
    return f"{line_a}\n{line_b}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generador dinámico de GUIA_PROXIMOS_DESBLOQUEOS.md")
    parser.add_argument("summary_json", nargs="?", help="Ruta al JSON generado por isaac_enricher.py --summary")
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUT), help="Ruta de salida del archivo Markdown")
    parser.add_argument("-n", "--limit", type=int, default=25, help="Número fijo de logros recomendados a incluir en la guía (por defecto 25)")
    parser.add_argument("--no-ai", action="store_true", help="Omitir análisis y curación con IA (agy)")
    parser.add_argument("--force-ai", action="store_true", help="Forzar consulta a la IA incluso si no hay nuevos logros en la sesión")
    args = parser.parse_args()

    if args.summary_json:
        json_path = Path(args.summary_json)
        if not json_path.exists():
            print(f"Error: no existe el archivo {json_path}", file=sys.stderr)
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif not sys.stdin.isatty():
        data = json.load(sys.stdin)
    else:
        from isaac_enricher import find_latest_saves, enrich_progress
        latest, prev = find_latest_saves(BASE_DIR / "save_backups")
        if not latest:
            print("Error: No se encontraron archivos de guardado en save_backups/", file=sys.stderr)
            sys.exit(1)
        data = enrich_progress(latest, prev)

    analisis_ia = None
    items_guia = None
    tips_ia = None
    orden_secciones_ia = None
    if not args.no_ai and shutil.which("agy"):
        usar_cache = (
            not args.force_ai
            and AI_CACHE_PATH.exists()
        )
        if usar_cache:
            try:
                with open(AI_CACHE_PATH, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                cached_total = cached.get("desbloqueados_total")
                current_total = data.get("desbloqueados_total", 0)
                cached_proto = cached.get("protocolo")
                cached_items = cached.get("seleccionados")
                if (
                    cached_proto
                    and cached_items
                    and cached_total is not None
                    and cached_total == current_total
                ):
                    unlocked_set = set(data.get("desbloqueados_ids", []))
                    valid_items = [it for it in cached_items if it.get("id") not in unlocked_set]
                    if len(valid_items) >= args.limit:
                        analisis_ia = cached_proto
                        items_guia = valid_items[:args.limit]
                        tips_ia = cached.get("tips_categorias", {})
                        orden_secciones_ia = cached.get("orden_secciones", [])
                        print("      ⚡ Sin cambios en la partida: Protocolo y curación cargados de caché (0.01s).", flush=True)
            except Exception:
                pass

        if not items_guia:
            print(f"      ✦ Curando los {args.limit} mejores objetivos, bitácora y consejos tácticos con IA (agy)...", flush=True)
            analisis_ia, items_guia, tips_ia, orden_secciones_ia = consultar_ia_bitacora_y_curacion(data, limit=args.limit)
            if items_guia:
                print(f"      ✔ {len(items_guia)} logros seleccionados estratégicamente por la IA.", flush=True)
            if tips_ia:
                print(f"      ✔ {len(tips_ia)} consejos tácticos por categoría generados por la IA.", flush=True)
            if orden_secciones_ia:
                print(f"      ✔ Prioridad de {len(orden_secciones_ia)} secciones determinada por la IA.", flush=True)
            if analisis_ia:
                print("      ✔ Bitácora táctica de la IA generada exitosamente.", flush=True)

    if not items_guia:
        unlocked_set = set(data.get("desbloqueados_ids", []))
        if not unlocked_set:
            latest, _ = find_latest_saves(BASE_DIR / "save_backups")
            if latest:
                unlocked_set = get_unlocked_ids(latest)
        bloqueados = [b for b in data.get("todos_bloqueados", []) if es_logro_factible(b, unlocked_set)]
        bloqueados_ordenados = sorted(
            bloqueados,
            key=lambda b: -(evaluar_utilidad_logro(b) + evaluar_facilidad_logro(b))
        )
        items_guia = bloqueados_ordenados[:args.limit]

    # Recuperación de bitácora táctica (Plan A / Plan B) si no hubo respuesta en vivo de la IA
    if not analisis_ia and AI_CACHE_PATH.exists():
        try:
            with open(AI_CACHE_PATH, "r", encoding="utf-8") as f:
                cached = json.load(f)
            cached_proto = cached.get("protocolo")
            if cached_proto:
                analisis_ia = cached_proto
                if not tips_ia:
                    tips_ia = cached.get("tips_categorias", {})
                if not orden_secciones_ia:
                    orden_secciones_ia = cached.get("orden_secciones", [])
        except Exception:
            pass

    if not analisis_ia:
        analisis_ia = generar_protocolo_fallback(items_guia)

    context = procesar_guia(data, items_guia, analisis_ia=analisis_ia, tips_ia=tips_ia, orden_secciones_ia=orden_secciones_ia)

    env = Environment(loader=FileSystemLoader(str(BASE_DIR)), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("guide_template.j2")
    rendered = template.render(**context)

    out_path = Path(args.output)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"✓ Guía generada exitosamente en: {out_path} ({len(items_guia)} logros en {len(context['categorias'])} categorías)", flush=True)

if __name__ == "__main__":
    main()
