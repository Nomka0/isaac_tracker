import json
import re
import urllib.parse
from bs4 import BeautifulSoup
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_WIKI_PATH = Path("/home/nomka/.gemini/antigravity-cli/brain/4000cd4d-eca5-46a7-86d0-6c83a5370247/.system_generated/steps/84/content.md")

BOSS_MAP = {
    "Mom": "Mom",
    "Mom's Heart": "Mom's Heart",
    "It Lives!": "It Lives!",
    "Isaac": "Isaac",
    "???": "??? (Blue Baby)",
    "Satan": "Satan",
    "The Lamb": "The Lamb",
    "Mega Satan": "Mega Satan",
    "Ultra Greed": "Ultra Greed",
    "Ultra Greedier": "Ultra Greedier",
    "Hush": "Hush",
    "Delirium": "Delirium",
    "Mother": "Mother",
    "The Beast": "The Beast",
    "Boss Rush": "Boss Rush"
}

CHAR_MAP = {
    "Isaac": "Isaac",
    "Magdalene": "Magdalene",
    "Maggy": "Magdalene",
    "Cain": "Cain",
    "Judas": "Judas",
    "???": "??? (Blue Baby)",
    "Blue Baby": "??? (Blue Baby)",
    "Eve": "Eve",
    "Samson": "Samson",
    "Azazel": "Azazel",
    "Lazarus": "Lazarus",
    "Eden": "Eden",
    "The Lost": "The Lost",
    "Lilith": "Lilith",
    "Keeper": "Keeper",
    "The Keeper": "Keeper",
    "Apollyon": "Apollyon",
    "The Forgotten": "The Forgotten",
    "Bethany": "Bethany",
    "Jacob and Esau": "Jacob & Esau",
    "Jacob & Esau": "Jacob & Esau",
    "Tainted Isaac": "Tainted Isaac",
    "Tainted Magdalene": "Tainted Magdalene",
    "Tainted Cain": "Tainted Cain",
    "Tainted Judas": "Tainted Judas",
    "Tainted ???": "Tainted ???",
    "Tainted Eve": "Tainted Eve",
    "Tainted Samson": "Tainted Samson",
    "Tainted Azazel": "Tainted Azazel",
    "Tainted Lazarus": "Tainted Lazarus",
    "Tainted Eden": "Tainted Eden",
    "Tainted Lost": "Tainted Lost",
    "Tainted Lilith": "Tainted Lilith",
    "Tainted Keeper": "Tainted Keeper",
    "Tainted Apollyon": "Tainted Apollyon",
    "Tainted Forgotten": "Tainted Forgotten",
    "Tainted Bethany": "Tainted Bethany",
    "Tainted Jacob": "Tainted Jacob"
}

CHALLENGES = {
    1: "Pitch Black", 2: "High Brow", 3: "Head Trauma", 4: "Darkness Falls", 5: "The Tank",
    6: "Solar System", 7: "Suicide King", 8: "Cat Got Your Tongue", 9: "Demo Man", 10: "Cursed!",
    11: "Glass Cannon", 12: "When Life Gives You Lemons", 13: "Beans!", 14: "It's in the Cards", 15: "Slow Roll",
    16: "Computer Savvy", 17: "Waka Waka", 18: "The Host", 19: "The Family Man", 20: "Purist",
    21: "XXXXXXXXL", 22: "SPEED!", 23: "Blue Bomber", 24: "PAY TO PLAY", 25: "Have a Heart",
    26: "I RULE!", 27: "BRAINS!", 28: "PRIDE DAY!", 29: "Onan's Streak", 30: "The Guardian",
    31: "Backasswards", 32: "Aprils Fool", 33: "Pokey Mans", 34: "Ultra Hard", 35: "Pong",
    36: "Scat Man", 37: "Bloody Mary", 38: "Baptism by Fire", 39: "Isaac's Awakening", 40: "Seeing Double",
    41: "Pica Run", 42: "Hot Potato", 43: "Cantripped!", 44: "Red Redemption", 45: "DELETE_THIS"
}

MANUAL_CONDITIONS = {
    1: "Tener 7 o más contenedores de corazón rojo a la vez",
    2: "Tener 55 monedas a la vez",
    3: "Derrotar a Satan por primera vez",
    4: "Derrotar a Mom por primera vez (desbloquea The Womb)",
    5: "Derrotar a Mom por primera vez (desbloquea los Jinetes)",
    6: "Derrotar a Mom por primera vez",
    7: "Derrotar a un Jinete del Apocalipsis por primera vez",
    8: "Derrotar a Mom's Heart 3 veces",
    10: "Derrotar a Mom's Heart 8 veces",
    11: "Derrotar a Mom's Heart 9 veces",
    12: "Destruir 100 rocas marcadas (Tinted Rocks)",
    13: "Completar el Capítulo 1 (Basement / Cellar)",
    14: "Completar el Capítulo 2 (Caves / Catacombs)",
    15: "Derrotar al jefe Lokii",
    16: "Completar Basement 40 veces",
    17: "Completar el Capítulo 2 (Caves) 30 veces",
    18: "Completar el Capítulo 3 (Depths) 20 veces",
    19: "Crear una Super Bandage Girl recogiendo 4 Ball of Bandages en una sola partida",
    22: "Derrotar a los 7 Pecados Capitales",
    23: "Derrotar al jefe Gish",
    24: "Derrotar al jefe Steven",
    25: "Derrotar al jefe C.H.A.D.",
    26: "Visitar 10 salas Arcade",
    27: "Derrotar a Mom, Mom's Heart o It Lives! usando The Bible (o la carta XV - The Devil?)",
    28: "Destruir 10 rocas marcadas (Tinted Rocks)",
    30: "Morir 100 veces",
    31: "Recoger 2 objetos relacionados con la muerte ('dead') en una sola partida",
    32: "Derrotar a Mom's Heart 10 veces",
    33: "Derrotar a Mom's Heart 11 veces (desbloquea It Lives!)",
    35: "Obtener 3 objetos de la transformación Yes Mother? (Mamá) en una sola partida",
    36: "Usar la carta XIII - Death 4 veces",
    37: "Completar el Capítulo 1 sin recibir daño",
    38: "Completar el Capítulo 2 sin recibir daño",
    39: "Completar el Capítulo 3 sin recibir daño",
    40: "Completar el Capítulo 4 sin recibir daño",
    41: "Completar The Chest o Dark Room sin recibir daño",
    42: "No recoger ningún corazón durante 2 pisos consecutivos",
    56: "Derrotar a Satan con Samson",
    57: "Derrotar a Isaac 5 veces (desbloquea The Polaroid)",
    58: "Obtener ambas Key Pieces de los Ángeles en una sola partida",
    59: "Donar 900 monedas en la máquina de donación",
    60: "Completar el Desafío #13 (Beans!)",
    61: "Destruir con bombas a 20 tenderos (Shopkeepers)",
    62: "Completar el Desafío #19 (The Family Man)",
    63: "Completar el Desafío #14 (It's in the Cards)",
    64: "Jugar 100 veces a los juegos Shell Game o Hell Game",
    65: "Transformarse en Guppy (recoger 3 objetos de Guppy)",
    66: "Tomar 10 objetos de salas del Ángel en total",
    67: "Completar 2 pisos consecutivos sin recibir daño",
    68: "Derrotar a ??? (Blue Baby) en The Chest y a The Lamb en Dark Room",
    69: "Recoger todos los objetos no-DLC y desbloquear todos los secretos y finales base (excepto The Lost)",
    79: "Hacer 3 pactos con el Diablo en una sola partida",
    80: "Tener 4 o más corazones de alma a la vez",
    81: "Completar el Capítulo 4 (The Womb) por primera vez",
    82: "Morir en una Sacrifice Room llevando equipado el Missing Poster",
    83: "Completar el Capítulo 6 (The Chest / Dark Room) sin recibir daño",
    84: "Completar el 100% de Rebirth: todos los objetos, secretos y finales no-DLC",
    85: "Destruir 100 rocas comunes",
    86: "Derrotar a todos los jefes de Basement (desbloquea The Cellar)",
    87: "Derrotar a todos los jefes de Caves (desbloquea The Catacombs)",
    88: "Derrotar a todos los jefes de Depths (desbloquea The Necropolis)",
    120: "Completar el Desafío #7 (Suicide King)",
    134: "Donar 10 monedas en la máquina de donación",
    135: "Donar 50 monedas en la máquina de donación",
    136: "Donar 150 monedas en la máquina de donación",
    137: "Donar 400 monedas en la máquina de donación",
    138: "Donar 999 monedas en la máquina de donación",
    142: "Tomar 20 objetos de salas del Diablo en total",
    144: "Crear un Super Meat Boy recogiendo 4 Cube of Meat en una sola partida",
    145: "Destruir 100 cacas",
    146: "Recoger 2 objetos tipo jeringa ('syringe') en una sola partida",
    147: "Usar la máquina de donación de sangre 30 veces",
    148: "Destruir con bombas 30 máquinas tragaperras (Slot Machines)",
    151: "Donar 20 monedas en la máquina de donación (mejora la tienda a nivel 1)",
    152: "Donar 100 monedas en la máquina de donación (mejora la tienda a nivel 2)",
    153: "Donar 200 monedas en la máquina de donación (mejora la tienda a nivel 3)",
    154: "Donar 600 monedas en la máquina de donación (mejora la tienda a nivel 4)",
    155: "Completar el Capítulo 6 (The Chest / Dark Room)",
    156: "Completar todas las marcas en Difícil con The Lost",
    157: "Completar Sheol con Eve (desbloquea Desafío #4)",
    158: "Tener 7 o más contenedores de corazón rojo a la vez (desbloquea Desafío #5)",
    159: "Completar Sheol con Judas (desbloquea Desafío #6)",
    160: "Completar The Chest con Lazarus (desbloquea Desafío #7)",
    161: "Transformarse en Guppy (desbloquea Desafío #8)",
    162: "Completar Caves 30 veces (desbloquea Desafío #9)",
    163: "Tener 7 o más contenedores de corazón rojo a la vez (desbloquea Desafío #10)",
    164: "Completar el Desafío #19, derrotar a Lokii y desbloquear a Judas e It Lives! (desbloquea Desafío #11)",
    165: "Obtener ambas Key Pieces de los Ángeles en una sola partida (desbloquea Desafío #19)",
    166: "Completar The Chest (desbloquea Desafío #20)",
    178: "Transformarse en Beelzebub (recoger 3 objetos de moscas)",
    224: "Completar el Desafío #21 (XXXXXXXXL)",
    225: "Completar el Desafío #22 (SPEED!)",
    226: "Completar el Desafío #23 (Blue Bomber)",
    227: "Completar el Desafío #24 (PAY TO PLAY)",
    228: "Completar el Desafío #25 (Have a Heart)",
    229: "Completar el Desafío #26 (I RULE!)",
    230: "Completar el Desafío #27 (BRAINS!)",
    231: "Completar el Desafío #28 (PRIDE DAY!)",
    232: "Completar el Desafío #29 (Onan's Streak) y #30 (The Guardian)",
    233: "Completar el Desafío #29 (Onan's Streak) y #30 (The Guardian)",
    234: "Derrotar a Mom's Heart en menos de 30 minutos (desbloquea Blue Womb / Hush)",
    235: "Desbloquear todos los secretos de Afterbirth y conseguir todos los objetos de Afterbirth",
    240: "Derrotar a Satan con Keeper",
    242: "Donar 2 monedas en la máquina de Greed",
    243: "Donar 14 monedas en la máquina de Greed",
    244: "Donar 33 monedas en la máquina de Greed",
    245: "Donar 68 monedas en la máquina de Greed",
    246: "Donar 111 monedas en la máquina de Greed",
    247: "Donar 234 monedas en la máquina de Greed",
    248: "Donar 439 monedas en la máquina de Greed",
    249: "Donar 666 monedas en la máquina de Greed",
    250: "Donar 879 monedas en la máquina de Greed",
    251: "Donar 1000 monedas en la máquina de Greed",
    258: "Usar Blank Card mientras sostienes la carta XIX - The Sun",
    265: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #21)",
    266: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #22)",
    267: "Destruir 10 rocas marcadas y derrotar a Mom's Heart 11 veces (desbloquea Desafío #23)",
    268: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #24)",
    269: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #25)",
    270: "Derrotar a Satan con Isaac y desbloquear The Negative (desbloquea Desafío #26)",
    271: "Derrotar a Isaac con ??? (desbloquea Desafío #27)",
    272: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #28)",
    273: "Derrotar a Isaac con Judas (desbloquea Desafío #29)",
    274: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #30)",
    275: "Donar 999 monedas en la máquina de Greed",
    276: "Derrotar a Mega Satan con todos los personajes de Afterbirth",
    277: "Derrotar a ??? o The Lamb y a Mega Satan (desbloquea Desafío #31 Backasswards)",
    278: "Derrotar a Mom (desbloquea Desafío #32 Aprils Fool)",
    279: "Derrotar a Mom's Heart 11 veces (desbloquea Desafío #33 Pokey Mans)",
    280: "Derrotar a Mega Satan y desbloquear The Negative (desbloquea Desafío #34 Ultra Hard)",
    281: "Derrotar a Isaac 5 veces (desbloquea Desafío #35 Pong)",
    320: "Derrotar a Hush por primera vez (desbloquea The Void)",
    321: "Completar una Victory Lap derrotando a The Lamb",
    322: "Conseguir una racha de 3 victorias consecutivas",
    323: "Conseguir una racha de 5 victorias consecutivas usando un personaje diferente cada vez",
    324: "Registrar todas las entradas en el Bestiario",
    325: "Participar en 31 Daily Challenges (no necesitan ser consecutivos ni ganarse)",
    326: "Derrotar a The Lamb en menos de 20 minutos",
    327: "Derrotar a The Lamb sin recoger corazones, monedas ni bombas en toda la partida",
    328: "Reiniciar la partida (R) 7 veces seguidas",
    329: "Completar un capítulo entero tras Basement de principio a fin con solo medio corazón (o con The Lost)",
    330: "Obtener 50 objetos en una sola partida",
    331: "Completar el Desafío #31 (Backasswards)",
    332: "Completar el Desafío #32 (Aprils Fool)",
    333: "Completar el Desafío #33 (Pokey Mans)",
    334: "Completar el Desafío #34 (Ultra Hard)",
    335: "Completar el Desafío #35 (Pong)",
    336: "Conseguir una racha de 5 victorias en Daily Challenges",
    337: "Completar 3 Victory Laps consecutivas derrotando a The Lamb",
    339: "Conseguir el 100% de Afterbirth+: todos los objetos, secretos, finales y bestiario",
    341: "Donar 500 monedas en la máquina de Greed (desbloquea modo Greedier)",
    347: "Derrotar a todos los nuevos jefes de Afterbirth+",
    348: "Derrotar a Hush o a los jefes finales para abrir el portal a The Void",
    350: "Destruir 500 rocas",
    351: "Completar el Capítulo 1 sin recibir daño",
    352: "Transformarse en Beelzebub (recoger 3 objetos de moscas)",
    353: "Destruir 5 cacas arcoíris",
    354: "Completar 7 Daily Challenges con victoria",
    355: "Recoger 5 familiares en una sola partida",
    358: "Recargar objetos usando microbaterías 20 veces",
    359: "Dormir en una cama",
    360: "Completar 2 Victory Laps derrotando a The Lamb",
    361: "Aumentar de tamaño 3 veces por encima del inicial en una sola partida",
    362: "Usar cartas o runas 20 veces",
    363: "Tener Broken Watch y Stop Watch registrados en tu colección",
    364: "Comprar 50 objetos en tiendas, pactos con el Diablo o mercados negros",
    365: "Completar el Capítulo 2 sin recibir daño",
    366: "Usar Pandora's Box en la Dark Room",
    367: "Recoger 2 objetos relacionados con baterías en una sola partida",
    368: "Completar el Capítulo 3 sin recibir daño",
    369: "Recoger 2 objetos de tecnología en una sola partida",
    370: "Adquirir Key Piece 1 y Key Piece 2 en una sola partida",
    371: "Abrir 20 cofres con cerradura",
    374: "Completar el Capítulo 4 sin recibir daño",
    375: "Destruir con bombas 50 puertas y paredes secretas",
    376: "Hacer 25 pactos con el Diablo en total",
    377: "Recoger Blood Clot 10 veces en total",
    378: "Recoger 10 aumentos de lágrimas (Tears Up) en una sola partida",
    379: "Entrar en 6 tiendas en una sola partida",
    380: "Tomar 25 objetos de salas del Ángel en total",
    381: "Tener The Battery, 9 Volt y Car Battery registrados en la colección",
    382: "Recoger Rubber Cement 5 veces en total",
    383: "Hacer 50 pactos con el Diablo en total",
    384: "Morir por tu propia explosión con lágrimas venenosas y explosivas",
    385: "Dormir en 10 camas en total",
    386: "Usar 5 píldoras Gulp! en una sola partida",
    387: "Tener 3 enemigos encantados al mismo tiempo en una sala",
    388: "Tener 20 moscas azules al mismo tiempo",
    389: "Usar The Magician o Telepathy For Dummies teniendo lágrimas teledirigidas",
    390: "Superar la misión secreta de The Forgotten (pala rota y cavar en Dark Room)",
    391: "Desbloquear al personaje The Forgotten",
    404: "Derrotar a Mom's Heart en modo Difícil sin perder vidas adicionales con Lazarus",
    405: "Derrotar a Mother",
    406: "Recoger 3 objetos con la etiqueta 'stars' en una sola partida",
    407: "Derrotar a Hush 3 veces (desbloquea la ruta alternativa: Downpour/Dross)",
    408: "Destruir con una bomba la calavera de The Siren tras derrotarla",
    410: "Dejar escapar a Baby Plum pacíficamente sin hacerle daño",
    411: "Entrar en Corpse por primera vez",
    415: "Abrir el cofre de Mom en Home por primera vez (desbloquea Red Key)",
    508: "Desbloquear a Bethany, Blood Bag e It Lives! (desbloquea Desafío #37)",
    509: "Derrotar a Satan con Bethany, derrotar a Mom's Heart 11 veces y desbloquear Maggy's Faith (desbloquea Desafío #38)",
    510: "Derrotar a Mother (desbloquea Desafío #39)",
    511: "Derrotar a Mother (desbloquea Desafío #40)",
    512: "Derrotar a Mom's Heart 11 veces y desbloquear Marbles (desbloquea Desafío #41)",
    513: "Desbloquear a Tainted Forgotten (desbloquea Desafío #42)",
    514: "Desbloquear a Tainted Cain (desbloquea Desafío #43)",
    515: "Desbloquear a Tainted Jacob (desbloquea Desafío #44)",
    516: "Desbloquear a Tainted Eden (desbloquea Desafío #45)",
    517: "Completar el Desafío #36 (Scat Man)",
    518: "Completar el Desafío #37 (Bloody Mary)",
    519: "Completar el Desafío #38 (Baptism by Fire)",
    520: "Completar el Desafío #39 (Isaac's Awakening)",
    521: "Completar el Desafío #40 (Seeing Double)",
    522: "Completar el Desafío #41 (Pica Run)",
    523: "Donar a Battery Bums hasta que entreguen un objeto 5 veces",
    531: "Completar el Desafío #42 (Hot Potato)",
    532: "Completar el Desafío #43 (Cantripped!)",
    533: "Completar el Desafío #44 (Red Redemption)",
    538: "Completar el Desafío #45 (DELETE_THIS)",
    545: "Matar a 10 Battery Bums",
    546: "Destruir el vagoncito de Hornfel y matarlo antes de que escape",
    547: "Completar todas las marcas en Difícil con todos los personajes no-Tainted",
    582: "Gastar 40 o más monedas en una sola tienda",
    583: "Acumular 99 monedas y gastarlas todas en una misma partida",
    635: "Derrotar a Mother",
    636: "Completar todas las marcas en Difícil con todos los personajes (normales y Tainted)",
    637: "Desbloquear todos los demás logros del juego (incluidos los 4 de Repentance+) y recoger todos los objetos",
    638: "Jugar una partida en modo Online",
    639: "Ganar una partida en modo Online",
    640: "Ganar una partida Daily Run en modo Online",
    641: "Derrotar a Mom (activa descripciones de objetos en Repentance+)",
    642: "Marca interna del motor de guardado de Isaac Repentance+"
}

CRITICAL_IDS = {
    29, 43, 82, 121, 156, 190, 240, 247, 250, 251, 282, 341, 419, 431, 432, 433, 436,
    440, 460, 463, 474, 477, 485, 486, 491, 504, 547, 584, 587, 607, 616, 618, 629, 636, 637
}

HIGH_IDS = {
    1, 2, 3, 7, 8, 9, 10, 11, 20, 27, 33, 35, 44, 49, 50, 56, 57, 58, 59, 62, 65, 67, 79, 80, 81,
    86, 87, 88, 90, 92, 94, 96, 97, 98, 103, 104, 113, 120, 136, 137, 138, 144, 154, 178, 199,
    203, 204, 216, 218, 220, 225, 234, 235, 236, 239, 244, 245, 248, 270, 276, 277, 278, 280,
    320, 323, 325, 326, 327, 336, 344, 345, 386, 389, 390, 396, 404, 405, 406, 407, 415, 422,
    424, 429, 430, 434, 435, 437, 438, 441, 442, 446, 448, 450, 451, 452, 455, 457, 458, 459,
    461, 462, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 475, 476, 478, 479, 480, 481,
    482, 483, 484, 487, 488, 489, 490, 503, 508, 517, 518, 520, 524, 529, 530, 541, 542, 572,
    596, 601, 603, 606, 609, 611, 613, 615, 620, 627, 628, 630, 633, 635, 639, 641
}

def clean_character(name):
    name = name.strip()
    return CHAR_MAP.get(name, name)

def clean_boss(name):
    name = name.strip()
    return BOSS_MAP.get(name, name)

def translate_condition(aid, unlock_raw):
    if aid in MANUAL_CONDITIONS:
        return MANUAL_CONDITIONS[aid]
    
    u = unlock_raw.strip()
    u = re.sub(r"\s+", " ", u).replace(" ,", ",").strip()

    # Pattern: Use Red Key (etc.) to open the hidden closet in Home as <char>
    m = re.match(r"^Use Red Key.*?as (.+)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Usar Red Key (o Cracked Key) para abrir el armario oculto en Home con {c}"

    # Pattern: Defeat Mom's Heart or It Lives! on Hard mode as <char>
    m = re.match(r"^Defeat Mom\'?s Heart (?:or|/) It Lives!? (?:on|in) Hard mode as (.+)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Derrotar a Mom's Heart o It Lives! en Difícil con {c}"

    # Pattern: Defeat Hush and Boss Rush as <char>
    m = re.match(r"^Defeat Hush and Boss Rush as (.+)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Derrotar a Hush y completar Boss Rush con {c}"

    # Pattern: Defeat Isaac , ??? , Satan , and The Lamb as <char>
    m = re.match(r"^Defeat Isaac\s*,\s*\?\?\?\s*,\s*Satan\s*,\s*and The Lamb as (.+)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Derrotar a Isaac, ???, Satan y The Lamb con {c}"

    # Pattern: Defeat <boss> as <char> on/in Hard mode
    m = re.match(r"^Defeat\s+(.+?)\s+as\s+(.+?)(?:\s+(?:on|in)\s+Hard\s+mode)$", u, re.I)
    if m:
        b = clean_boss(m.group(1))
        c = clean_character(m.group(2))
        return f"Derrotar a {b} en Difícil con {c}"

    # Pattern: Defeat <boss> as <char>
    m = re.match(r"^Defeat\s+(.+?)\s+as\s+(.+?)$", u, re.I)
    if m:
        b = clean_boss(m.group(1))
        c = clean_character(m.group(2))
        return f"Derrotar a {b} con {c}"

    # Pattern: Complete (the )?Boss Rush as <char>
    m = re.match(r"^Complete\s+(?:the\s+)?Boss\s+Rush\s+as\s+(.+?)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Completar Boss Rush con {c}"

    # Pattern: Complete <Challenge Name> (challenge #N)
    m = re.match(r"^Complete\s+(.+?)\s*\(challenge\s*#(\d+)\)$", u, re.I)
    if m:
        cname = m.group(1).strip()
        cnum = int(m.group(2))
        return f"Completar el Desafío #{cnum} ({cname})"

    # Pattern: Complete Challenge #N
    m = re.match(r"^(?:Complete|Beat)\s+Challenge\s+(?:#\s*)?(\d+)", u, re.I)
    if m:
        num = int(m.group(1))
        cname = CHALLENGES.get(num, "")
        return f"Completar el Desafío #{num} ({cname})" if cname else f"Completar el Desafío #{num}"

    # Pattern: Earn all Hard mode Completion Marks as <char>
    m = re.match(r"^Earn all Hard mode Completion Marks (?:on Hard mode )?as (.+)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Completar todas las marcas en Difícil con {c}"

    # Pattern: Earn all Completion Marks as <char>
    m = re.match(r"^Earn all Completion Marks as (.+)$", u, re.I)
    if m:
        c = clean_character(m.group(1))
        return f"Completar todas las marcas con {c}"

    # Pattern: Defeat <boss> N times
    m = re.match(r"^Defeat\s+(.+?)\s+(\d+)\s+times$", u, re.I)
    if m:
        b = clean_boss(m.group(1))
        n = m.group(2)
        return f"Derrotar a {b} {n} veces"

    # Pattern: Defeat <boss>
    m = re.match(r"^Defeat\s+(.+?)$", u, re.I)
    if m:
        b = clean_boss(m.group(1))
        return f"Derrotar a {b}"

    return u

def get_clean_name(aid, raw_name, target):
    tainted_chars = {
        474: "Tainted Isaac (The Broken)",
        475: "Tainted Magdalene (The Dauntless)",
        476: "Tainted Cain (The Hoarder)",
        477: "Tainted Judas (The Deceiver)",
        478: "Tainted ??? (The Soiled)",
        479: "Tainted Eve (The Curdled)",
        480: "Tainted Samson (The Savage)",
        481: "Tainted Azazel (The Benighted)",
        482: "Tainted Lazarus (The Enigma)",
        483: "Tainted Eden (The Capricious)",
        484: "Tainted Lost (The Baleful)",
        485: "Tainted Lilith (The Harlot)",
        486: "Tainted Keeper (The Miser)",
        487: "Tainted Apollyon (The Empty)",
        488: "Tainted Forgotten (The Fettered)",
        489: "Tainted Bethany (The Zealot)",
        490: "Tainted Jacob (The Deserter)"
    }
    if aid in tainted_chars:
        return tainted_chars[aid]

    item_aliases = {
        8: "Transcendence (A Noose)",
        11: "Dr. Fetus (A Fetus in a Jar)",
        16: "Steven (Something From The Future)",
        17: "C.H.A.D. (Something Cute)",
        18: "Gish (Something Sticky)",
        19: "Super Bandage (A Bandage)",
        20: "The Relic (A Cross)",
        21: "Sack of Pennies (A Bag of Pennies)",
        44: "Razor Blade (The Razor)",
        46: "Bomb Bag (A Bag of Bombs)",
        49: "D20 (The D20)",
        55: "Bloody Penny (Blood Penny)",
        59: "The Candle (Blue Candle)",
        64: "Counterfeit Penny (Counterfeit Coin)",
        66: "Conquest (A Forgotten Horseman)",
        227: "2 New Pills (Percs! & Addicted!)",
        228: "2 New Pills (Re-Lax & ???)",
        234: "Blue Womb (Hush)",
        250: "Lost holds Holy Mantle",
        276: "Mega Blast (Mega)",
        321: "Gulp! (Once More with Feeling!)",
        322: "Ace of Clubs (Hat trick!)",
        323: "Super Special Rocks (5 Nights at Mom's)",
        324: "Feels like I'm walking on sunshine! (Sin collector)",
        325: "Horf! (Dedication)",
        326: "Ace of Diamonds (ZIP!)",
        327: "Ace of Spades (It's the Key)",
        328: "Scared Heart (Mr. Resetter!)",
        329: "Ace of Hearts (Living on the edge)",
        330: "Vurp! (U Broke It!)",
        331: "Lazarus holds Anemic (Laz Bleeds More!)",
        332: "Magdalene holds Pill (Maggy Now Holds a Pill!)",
        334: "Samson holds Child's Heart (Samson Feels Healthy!)",
        336: "Cracked Crown (The Marathon)",
        341: "Greedier Mode (Greedier!)",
        347: "Something wicked this way comes+! (Alt Bosses)",
        348: "The Void Portal (The gate is open!)",
        407: "A Secret Exit (Downpour / Alt Path)",
        524: "0 - The Fool? (Reversed)",
        525: "I - The Magician? (Reversed)",
        526: "II - The High Priestess? (Reversed)",
        527: "III - The Empress? (Reversed)",
        528: "IV - The Emperor? (Reversed)",
        529: "V - The Hierophant? (Reversed)",
        530: "VI - The Lovers? (Reversed)",
        531: "VII - The Chariot? (Reversed)",
        532: "VIII - Justice? (Reversed)",
        533: "IX - The Hermit? (Reversed)",
        534: "X - Wheel of Fortune? (Reversed)",
        535: "XI - Strength? (Reversed)",
        536: "XII - The Hanged Man? (Reversed)",
        537: "XIII - Death? (Reversed)",
        538: "XIV - Temperance? (Reversed)",
        539: "XV - The Devil? (Reversed)",
        540: "XVI - The Tower? (Reversed)",
        541: "XVII - The Stars? (Reversed)",
        542: "XVIII - The Moon? / XIX - The Sun? (Reversed)",
        543: "XX - Judgement? (Reversed)",
        544: "XXI - The World? (Reversed)"
    }
    if aid in item_aliases:
        return item_aliases[aid]

    return raw_name

def get_priority(aid, name):
    if aid in CRITICAL_IDS:
        return "Crítica"
    if aid in HIGH_IDS:
        return "Alta"
    if "baby" in name.lower() and aid not in [32, 258]:
        return "Baja"
    return "Media"

def main():
    wiki_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WIKI_PATH
    if not wiki_path.exists():
        print(f"Error: No se encontró el archivo wiki en: {wiki_path}", file=sys.stderr)
        sys.exit(1)

    with open(wiki_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    tables = soup.find_all("table")
    if not tables:
        print("Error: No se encontraron tablas en el archivo wiki.", file=sys.stderr)
        sys.exit(1)

    rows = tables[0].find_all("tr")[1:]

    achievements = {}
    for r in rows:
        tds = r.find_all(["td", "th"])
        if len(tds) < 5:
            continue
        try:
            aid = int(tds[1].get_text(strip=True))
        except ValueError:
            continue
        raw_name = tds[0].get_text(separator=" ", strip=True)
        links = tds[0].find_all("a")
        target = ""
        if links:
            href = links[0].get("href", "")
            target = urllib.parse.unquote(href.replace("/wiki/", "").replace("_", " "))
        unlock_raw = tds[4].get_text(separator=" ", strip=True)
        
        clean_name = get_clean_name(aid, raw_name, target)
        condition = translate_condition(aid, unlock_raw)
        priority = get_priority(aid, clean_name)
        
        achievements[str(aid)] = {
            "name": clean_name,
            "condition": condition,
            "priority": priority
        }

    achievements["642"] = {
        "name": "Save File Check",
        "condition": "Marca interna del motor de guardado de Isaac Repentance+",
        "priority": "Baja"
    }

    out_file = BASE_DIR / "achievements.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(achievements, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {out_file} with {len(achievements)} entries.")

if __name__ == "__main__":
    main()