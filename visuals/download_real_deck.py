"""Téléchargement d'un vrai paquet de 54 cartes depuis deckofcardsapi.com.

Usage:
    python visuals/download_real_deck.py

Crée visuals/real_deck/{clubs,diamonds,hearts,spades,jokers}/ avec des PNG nommés
selon la convention du projet : {n:02d}_{rank_label}.png
"""

from __future__ import annotations

import io
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

# ── Constantes ──────────────────────────────────────────────────────────────

BASE_URL = "https://deckofcardsapi.com/static/img/{code}.png"

RANK_CODES   = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "0", "J", "Q", "K"]
RANK_LABELS  = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]

SUITS = [
    ("clubs",    "C",  1),
    ("diamonds", "D", 14),
    ("hearts",   "H", 27),
    ("spades",   "S", 40),
]

REAL_DECK_DIR = Path(__file__).parent / "real_deck"

# ── Téléchargement ───────────────────────────────────────────────────────────

def _download_png(url: str, timeout: int = 15) -> bytes:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def _save_card(data: bytes, dest: Path, target_w: int = 240) -> None:
    """Redimensionne si nécessaire et sauvegarde en PNG."""
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    if img.width != target_w:
        ratio = target_w / img.width
        new_h = int(img.height * ratio)
        img = img.resize((target_w, new_h), Image.LANCZOS)
    img.save(dest, format="PNG", optimize=True)


def download_52_cards(target_w: int = 240) -> None:
    """Télécharge les 52 cartes standard depuis deckofcardsapi.com."""
    total = 52
    done = 0

    for suit_name, suit_code, start_n in SUITS:
        suit_dir = REAL_DECK_DIR / suit_name
        suit_dir.mkdir(parents=True, exist_ok=True)

        for i, (rank_code, rank_label) in enumerate(zip(RANK_CODES, RANK_LABELS)):
            n = start_n + i
            filename = f"{n:02d}_{rank_label}.png"
            dest = suit_dir / filename

            if dest.exists():
                print(f"  ✓ {filename} (déjà présent)", flush=True)
                done += 1
                continue

            url = BASE_URL.format(code=f"{rank_code}{suit_code}")
            try:
                data = _download_png(url)
                _save_card(data, dest, target_w=target_w)
                done += 1
                pct = int(done / total * 100)
                print(f"  [{pct:3d}%] {filename}", flush=True)
                time.sleep(0.05)   # politesse envers l'API
            except Exception as exc:
                print(f"  ERREUR {filename}: {exc}", file=sys.stderr, flush=True)


# ── Génération des Jokers avec Pillow ────────────────────────────────────────

def _make_joker_png(
    letter: str,
    color: str,
    width: int = 240,
) -> Image.Image:
    """Crée un Joker stylisé en pur Pillow (pas de dépendance externe)."""
    height = int(width * 1.4)
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fond blanc avec bordure arrondie simulée
    margin = 4
    draw.rounded_rectangle(
        [margin, margin, width - margin, height - margin],
        radius=14,
        fill=(255, 255, 255, 255),
        outline=(30, 30, 30, 255),
        width=3,
    )

    # Couleur principale
    rgb = (180, 32, 32) if color == "red" else (20, 20, 20)

    # Coin supérieur gauche : "J"
    corner_size = max(18, width // 13)
    try:
        font_big   = ImageFont.truetype("arial.ttf",   corner_size)
        font_mid   = ImageFont.truetype("arial.ttf",   corner_size - 4)
        font_title = ImageFont.truetype("arialbd.ttf", width // 4)
        font_star  = ImageFont.truetype("seguisym.ttf", width // 3)
    except OSError:
        font_big   = ImageFont.load_default()
        font_mid   = font_big
        font_title = font_big
        font_star  = font_big

    # Coin supérieur gauche
    draw.text((12, 10),                   "J",  font=font_big, fill=rgb)
    draw.text((12, 10 + corner_size + 2), "★", font=font_mid, fill=rgb)

    # Texte central "JOKER"
    draw.text(
        (width // 2, height // 2 - width // 8),
        "JOKER",
        font=font_title,
        fill=rgb,
        anchor="mm",
    )

    # Étoile centrale
    star_char = "★" if color == "red" else "☆"
    draw.text(
        (width // 2, height // 2 + width // 5),
        star_char,
        font=font_star,
        fill=rgb,
        anchor="mm",
    )

    # Coin inférieur droit : on mesure les bbox pour placer exactement
    bb_j    = draw.textbbox((0, 0), "J",  font=font_big)
    bb_star = draw.textbbox((0, 0), "★", font=font_mid)
    j_w     = bb_j[2]    - bb_j[0]
    j_h     = bb_j[3]    - bb_j[1]
    star_w  = bb_star[2] - bb_star[0]

    draw.text(
        (width - 12 - j_w,    height - 10 - j_h - (bb_star[3] - bb_star[1]) - 2),
        "J",  font=font_big, fill=rgb,
    )
    draw.text(
        (width - 12 - star_w, height - 10 - (bb_star[3] - bb_star[1])),
        "★", font=font_mid, fill=rgb,
    )

    # Bordure finale
    draw.rounded_rectangle(
        [margin, margin, width - margin, height - margin],
        radius=14,
        fill=None,
        outline=(30, 30, 30, 255),
        width=3,
    )

    return img


def generate_jokers(target_w: int = 240) -> None:
    """Génère les 2 Jokers (A=noir, B=rouge) en PNG."""
    jokers_dir = REAL_DECK_DIR / "jokers"
    jokers_dir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("53_joker_a.png", "black"),
        ("54_joker_b.png", "red"),
    ]
    for filename, color in specs:
        dest = jokers_dir / filename
        if dest.exists():
            print(f"  ✓ {filename} (déjà présent)", flush=True)
            continue
        img = _make_joker_png(letter="J", color=color, width=target_w)
        img.save(dest, format="PNG", optimize=True)
        print(f"  Joker généré : {filename}", flush=True)


# ── Point d'entrée ───────────────────────────────────────────────────────────

def main() -> None:
    print("=== Téléchargement du paquet classique 54 cartes ===")
    print(f"Destination : {REAL_DECK_DIR.resolve()}\n")

    REAL_DECK_DIR.mkdir(parents=True, exist_ok=True)

    print("── 52 cartes standard ──")
    download_52_cards(target_w=240)

    print("\n── 2 Jokers ──")
    generate_jokers(target_w=240)

    # Vérification finale
    pngs = list(REAL_DECK_DIR.rglob("*.png"))
    print(f"\n✓ {len(pngs)}/54 cartes dans {REAL_DECK_DIR.relative_to(Path.cwd())}")
    if len(pngs) < 54:
        print("  Certaines cartes manquent — relancez le script pour réessayer.", file=sys.stderr)
    else:
        print("  Paquet complet ! Choisissez 'Classique (réaliste)' dans la sidebar.")


if __name__ == "__main__":
    main()
