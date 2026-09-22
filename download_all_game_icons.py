#!/usr/bin/env python3
"""
Descarga iconos organizados para The Binding of Isaac Repentance+:
- rooms/: Salas (Sacrificio, Cursed, Dados, Boss, Angel, Devil, Shop, Treasure, Secret, etc.)
- bosses/: Jefes principales y de marcas (Satan, Mega Satan, Mom, Delirium, Mother, Beast, etc.)
- items/ y pickups/: Consumibles con todas sus variaciones (Corazones, Monedas, Bombas, Llaves, Cofres)
"""

import urllib.request
import urllib.parse
from pathlib import Path
import io
import shutil
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Referer": "https://bindingofisaacrebirth.wiki.gg/wiki/Characters"
}

ROOMS = {
    "sacrifice": "Sacrifice_Room_Icon.png",
    "curse": "Curse_Room_Icon.png",
    "dice": "Dice_Room_Icon.png",
    "boss": "Boss_Room_Icon.png",
    "boss_rush": "Boss_Rush_Icon.png",
    "boss_challenge": "Boss_Challenge_Room_Icon.png",
    "challenge": "Challenge_Room_Icon.png",
    "treasure": "Treasure_Room_Icon.png",
    "shop": "Shop_Icon.png",
    "secret": "Secret_Room_Icon.png",
    "super_secret": "Super_Secret_Room_Icon.png",
    "ultra_secret": "Ultra_Secret_Room_Icon.png",
    "devil": "Devil_Room_Icon.png",
    "angel": "Angel_Room_Icon.png",
    "arcade": "Arcade_Icon.png",
    "library": "Library_Icon.png",
    "planetarium": "Planetarium_Icon.png",
    "vault": "Vault_Icon.png",
    "bedroom": "Bedroom_Icon.png",
    "dirty_bedroom": "Dirty_Bedroom_Icon.png",
    "crawl_space": "Crawl_Space_Icon.png",
    "black_market": "Black_Market_Icon.png",
    "error": "Error_Room_Icon.png",
    "mini_boss": "Mini-Boss_Room_Icon.png"
}

BOSSES = {
    "satan": "Boss_Satan_portrait.png",
    "mega_satan": "Boss_Mega_Satan_portrait.png",
    "mom": "Boss_Mom_portrait.png",
    "moms_heart": "Boss_Mom%27s_Heart_portrait.png",
    "it_lives": "Boss_It_Lives%21_portrait.png",
    "isaac": "Boss_Isaac_portrait.png",
    "blue_baby": "Boss_%3F%3F%3F_portrait.png",
    "the_lamb": "Boss_The_Lamb_portrait.png",
    "hush": "Boss_Hush_portrait.png",
    "delirium": "Boss_Delirium_portrait.png",
    "mother": "Boss_Mother_portrait.png",
    "the_beast": "Boss_The_Beast_portrait.png",
    "ultra_greed": "Boss_Ultra_Greed_portrait.png",
    "ultra_greedier": "Boss_Ultra_Greedier_ingame.png",
    "dogma": "Boss_Dogma_portrait.png",
    "boss_rush": "Boss_Rush_Icon.png",
    "uriel": "Uriel.png",
    "gabriel": "Gabriel.png",
    "krampus": "Boss_Krampus_portrait.png",
    "monstro": "Boss_Monstro_portrait.png",
    "baby_plum": "Boss_Baby_Plum_portrait.png",
    "the_siren": "Boss_The_Siren_portrait.png"
}

ITEMS = {
    # Corazones (Hearts)
    "heart_red": "Red_Heart.png",
    "heart_half": "Half_Red_Heart.png",
    "heart_double": "Double_Heart.png",
    "heart_soul": "Soul_Heart.png",
    "heart_half_soul": "Half_Soul_Heart.png",
    "heart_black": "Black_Heart.png",
    "heart_eternal": "Eternal_Heart.png",
    "heart_gold": "Gold_Heart.png",
    "heart_bone": "Bone_Heart.png",
    "heart_rotten": "Rotten_Heart.png",
    "heart_blended": "Blended_Heart.png",

    # Monedas (Coins)
    "penny": "Penny.png",
    "double_penny": "Double_Penny.png",
    "nickel": "Nickel.png",
    "sticky_nickel": "Achievement_Sticky_Nickels_icon.png",
    "dime": "Dime.png",
    "lucky_penny": "Lucky_Penny.png",
    "golden_penny": "Golden_Penny.png",

    # Bombas (Bombs)
    "bomb": "Bomb.png",
    "double_bomb": "Double_Bomb.png",
    "troll_bomb": "Troll_Bomb.png",
    "mega_troll_bomb": "Mega_Troll_Bomb.png",
    "golden_bomb": "Golden_Bomb.png",
    "golden_troll_bomb": "Golden_Troll_Bomb.png",
    "giga_bomb": "Giga_Bomb.png",

    # Llaves (Keys)
    "key": "Key.png",
    "golden_key": "Golden_Key.png",
    "key_ring": "Key_Ring.png",
    "charged_key": "Charged_Key.gif",
    "cracked_key": "Pickup_Cracked_Key_icon.png",
    "red_key": "Collectible_Red_Key_icon.png",

    # Cofres (Chests)
    "chest": "Chest.png",
    "chest_golden": "Locked_Chest.png",
    "chest_red": "Red_Chest.png",
    "chest_stone": "Bomb_Chest.png",
    "chest_eternal": "Eternal_Chest.png",
    "chest_spiked": "Spiked_Chest.png",
    "chest_mimic": "Mimic_Chest.png",
    "chest_old": "Old_Chest.png",
    "chest_wooden": "Wooden_Chest.png",
    "chest_mega": "Mega_Chest.png",
    "chest_haunted": "Haunted_Chest.png",
    "chest_moms": "Mom%27s_Chest.png"
}

def download_and_save(category_dir, name, wiki_filename, upscale_rooms=False):
    target = category_dir / f"{name}.png"
    if target.exists() and target.stat().st_size > 100:
        return True

    url = f"https://bindingofisaacrebirth.wiki.gg/images/{wiki_filename}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) < 50:
                return False

            # Manejo especial de gif a png (como Charged Key)
            if wiki_filename.endswith(".gif"):
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                im.save(target, "PNG")
                return True

            im = Image.open(io.BytesIO(data))

            # Para salas diminutas del minimap (9x8), escalamos 4x en pixel art para máxima nitidez en markdown
            if upscale_rooms and im.width < 16 and im.height < 16:
                im = im.convert("RGBA").resize((im.width * 4, im.height * 4), Image.Resampling.NEAREST)
                im.save(target, "PNG")
            else:
                target.write_bytes(data)
            return True
    except Exception as e:
        print(f"  [ERROR] {name} ({wiki_filename}): {e}")
        return False

def add_aliases(folder, alias_dict):
    for alias, original in alias_dict.items():
        src = folder / original
        dst = folder / alias
        if src.exists() and not dst.exists():
            shutil.copyfile(src, dst)

def main():
    images_dir = BASE_DIR / "images"
    rooms_dir = images_dir / "rooms"
    bosses_dir = images_dir / "bosses"
    pickups_dir = images_dir / "pickups"

    for d in [rooms_dir, bosses_dir, pickups_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print("--- Descargando iconos de salas (images/rooms/) ---")
    for name, f in ROOMS.items():
        if download_and_save(rooms_dir, name, f, upscale_rooms=True):
            print(f"  [OK] images/rooms/{name}.png")

    print("\n--- Descargando iconos de jefes (images/bosses/) ---")
    for name, f in BOSSES.items():
        if download_and_save(bosses_dir, name, f):
            print(f"  [OK] images/bosses/{name}.png")

    print("\n--- Descargando consumibles e items (images/pickups/) ---")
    for name, f in ITEMS.items():
        if download_and_save(pickups_dir, name, f):
            print(f"  [OK] images/pickups/{name}.png")

    # Alias convenientes para items/pickups
    item_aliases = {
        "coin.png": "penny.png",
        "red_heart.png": "heart_red.png",
        "soul_heart.png": "heart_soul.png",
        "black_heart.png": "heart_black.png",
        "eternal_heart.png": "heart_eternal.png",
        "gold_heart.png": "heart_gold.png",
        "bone_heart.png": "heart_bone.png",
        "rotten_heart.png": "heart_rotten.png",
        "double_heart.png": "heart_double.png",
        "half_heart.png": "heart_half.png",
        "blended_heart.png": "heart_blended.png",
        "chest_normal.png": "chest.png",
        "chest_locked.png": "chest_golden.png",
        "red_chest.png": "chest_red.png",
        "stone_chest.png": "chest_stone.png",
        "double_key.png": "key_ring.png"
    }
    add_aliases(pickups_dir, item_aliases)

    print("\n✓ Proceso completado exitosamente.")
    print(f"  images/rooms/: {len(list(rooms_dir.glob('*.png')))} imágenes")
    print(f"  images/bosses/: {len(list(bosses_dir.glob('*.png')))} imágenes")
    print(f"  images/pickups/: {len(list(pickups_dir.glob('*.png')))} imágenes")

if __name__ == "__main__":
    main()
