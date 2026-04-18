"""
Post-traitement des cartes : transforme les images brutes Gemini
en vraies cartes à jouer avec indices (rang + couleur) dans les coins.

Usage:
    python visuals/post_process_cards.py              # Traite toutes les cartes
    python visuals/post_process_cards.py --suit clubs  # Une couleur
    python visuals/post_process_cards.py --card 11     # Une carte spécifique
    python visuals/post_process_cards.py --preview      # Montre une carte sans sauvegarder
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS_DIR = Path(__file__).parent / "assets"
OUTPUT_DIR = Path(__file__).parent / "output"

# Dimensions finales (format poker standard 2.5" x 3.5" → ratio 5:7)
CARD_W = 750
CARD_H = 1050
CORNER_RADIUS = 30

# Zone d'index (coins)
INDEX_MARGIN_X = 28
INDEX_MARGIN_Y = 24
INDEX_BOX_W = 72
INDEX_BOX_H = 110
INDEX_BOX_RADIUS = 10

# Polices
RANK_FONT_SIZE = 48
SUIT_FONT_SIZE = 40
BRIDGE_FONT_SIZE = 18

# Couleurs des couleurs (ici on utilise les couleurs classiques
# + les couleurs thématiques pour la bordure glow)
SUIT_COLORS = {
    "clubs":    "#10b981",   # vert (thème CPU)
    "diamonds": "#06b6d4",   # cyan (thème DATA)
    "hearts":   "#f43f5e",   # rouge (thème SHIELD)
    "spades":   "#a855f7",   # violet (thème QUBIT)
    "jokers":   "#f59e0b",   # ambre
}

# Couleur du texte d'index (plus sombre, lisible sur fond blanc)
SUIT_TEXT_COLORS = {
    "clubs":    "#047857",   # vert foncé
    "diamonds": "#0891b2",   # cyan foncé
    "hearts":   "#e11d48",   # rouge vif
    "spades":   "#7c3aed",   # violet
    "jokers":   "#d97706",   # ambre foncé
}

# Symboles standard
SUIT_SYMBOLS = {
    "clubs":    "♣",
    "diamonds": "♦",
    "hearts":   "♥",
    "spades":   "♠",
    "jokers":   "★",
}

# Noms de rang
RANK_NAMES = {
    1: "A", 2: "2", 3: "3", 4: "4", 5: "5",
    6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "V", 12: "D", 13: "R",
}


@dataclass(frozen=True)
class CardInfo:
    card_number: int   # 1-54 (valeur Solitaire / Bridge)
    suit: str          # clubs, diamonds, hearts, spades, jokers
    rank: int          # 1-13 pour faces, 0 pour jokers
    file_path: Path


def discover_cards() -> list[CardInfo]:
    """Discover all existing card images."""
    cards: list[CardInfo] = []

    suit_ranges = {
        "clubs": (1, 13, 0),
        "diamonds": (1, 13, 13),
        "hearts": (1, 13, 26),
        "spades": (1, 13, 39),
    }

    for suit, (rank_start, rank_end, offset) in suit_ranges.items():
        suit_dir = ASSETS_DIR / suit
        for rank in range(rank_start, rank_end + 1):
            card_num = rank + offset
            rank_label = {1: "ace", 11: "jack", 12: "queen", 13: "king"}.get(rank, str(rank))
            filename = f"{card_num:02d}_{rank_label}.png"
            filepath = suit_dir / filename
            if filepath.exists():
                cards.append(CardInfo(card_num, suit, rank, filepath))

    # Jokers
    for jnum, jlabel in [(53, "a"), (54, "b")]:
        fp = ASSETS_DIR / "jokers" / f"{jnum}_joker_{jlabel}.png"
        if fp.exists():
            cards.append(CardInfo(jnum, "jokers", 0, fp))

    return cards


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Charge une police avec fallback système."""
    candidates = [
        name,
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _load_fonts():
    """Charge les 3 polices (rang, couleur, bridge)."""
    rank_font = _load_font("C:/Windows/Fonts/arialbd.ttf", RANK_FONT_SIZE)
    suit_font = _load_font("C:/Windows/Fonts/seguisym.ttf", SUIT_FONT_SIZE)
    bridge_font = _load_font("C:/Windows/Fonts/consola.ttf", BRIDGE_FONT_SIZE)
    return rank_font, suit_font, bridge_font


def _round_corners(img: Image.Image, radius: int) -> Image.Image:
    """Ajoute des coins arrondis transparents."""
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
    result = img.copy().convert("RGBA")
    result.putalpha(mask)
    return result


def _crop_to_ratio(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Recadre au centre puis redimensionne au ratio cible."""
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Image too wide → crop sides
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    elif src_ratio < target_ratio:
        # Image too tall → crop top/bottom
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    return img.resize((target_w, target_h), Image.LANCZOS)


def _draw_index_box(draw: ImageDraw.Draw, x: int, y: int,
                    rank_text: str, suit_symbol: str,
                    text_color: str,
                    rank_font: ImageFont.FreeTypeFont,
                    suit_font: ImageFont.FreeTypeFont,
                    rotation: int = 0,
                    img: Image.Image = None):
    """Dessine l'index (rang + couleur) dans un coin."""
    # Create a small overlay for the index box
    box_img = Image.new("RGBA", (INDEX_BOX_W, INDEX_BOX_H), (0, 0, 0, 0))
    box_draw = ImageDraw.Draw(box_img)

    # Semi-transparent white background
    box_draw.rounded_rectangle(
        [0, 0, INDEX_BOX_W - 1, INDEX_BOX_H - 1],
        radius=INDEX_BOX_RADIUS,
        fill=(255, 255, 255, 210),
        outline=(200, 200, 200, 180),
        width=1,
    )

    # Rank text — centered horizontally
    r_bbox = box_draw.textbbox((0, 0), rank_text, font=rank_font)
    r_w = r_bbox[2] - r_bbox[0]
    r_x = (INDEX_BOX_W - r_w) // 2
    box_draw.text((r_x, 8), rank_text, fill=text_color, font=rank_font)

    # Suit symbol — centered horizontally, below rank
    s_bbox = box_draw.textbbox((0, 0), suit_symbol, font=suit_font)
    s_w = s_bbox[2] - s_bbox[0]
    s_x = (INDEX_BOX_W - s_w) // 2
    box_draw.text((s_x, 55), suit_symbol, fill=text_color, font=suit_font)

    if rotation:
        box_img = box_img.rotate(rotation, expand=False)

    img.paste(box_img, (x, y), box_img)


def process_card(card: CardInfo, rank_font, suit_font, bridge_font,
                 output_dir: Path, preview: bool = False) -> bool:
    """Process a single card: crop, add indices, border."""
    try:
        src = Image.open(card.file_path).convert("RGBA")
    except Exception as e:
        print(f"  ❌ {card.file_path.name} — erreur lecture: {e}")
        return False

    # 1. Crop to card ratio and resize
    img = _crop_to_ratio(src, CARD_W, CARD_H)

    # 2. Dark overlay at edges for better index readability
    overlay = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    # Top-left gradient area
    overlay_draw.rectangle([0, 0, INDEX_BOX_W + INDEX_MARGIN_X * 2,
                           INDEX_BOX_H + INDEX_MARGIN_Y * 2],
                          fill=(0, 0, 0, 80))
    # Bottom-right gradient area
    overlay_draw.rectangle([CARD_W - INDEX_BOX_W - INDEX_MARGIN_X * 2,
                           CARD_H - INDEX_BOX_H - INDEX_MARGIN_Y * 2,
                           CARD_W, CARD_H],
                          fill=(0, 0, 0, 80))
    img = Image.alpha_composite(img, overlay)

    # 3. Draw index boxes
    suit_color = SUIT_TEXT_COLORS.get(card.suit, "#333333")
    suit_symbol = SUIT_SYMBOLS.get(card.suit, "?")

    if card.suit == "jokers":
        rank_text = "J"
    else:
        rank_text = RANK_NAMES.get(card.rank, "?")

    # Top-left index
    _draw_index_box(
        draw=None, x=INDEX_MARGIN_X, y=INDEX_MARGIN_Y,
        rank_text=rank_text, suit_symbol=suit_symbol,
        text_color=suit_color,
        rank_font=rank_font, suit_font=suit_font,
        img=img,
    )

    # Bottom-right index (rotated 180°)
    br_x = CARD_W - INDEX_MARGIN_X - INDEX_BOX_W
    br_y = CARD_H - INDEX_MARGIN_Y - INDEX_BOX_H
    _draw_index_box(
        draw=None, x=br_x, y=br_y,
        rank_text=rank_text, suit_symbol=suit_symbol,
        text_color=suit_color,
        rank_font=rank_font, suit_font=suit_font,
        rotation=180,
        img=img,
    )

    # 4. Bridge value (small, bottom-center)
    draw = ImageDraw.Draw(img)
    bridge_text = str(card.card_number)
    b_bbox = draw.textbbox((0, 0), bridge_text, font=bridge_font)
    b_w = b_bbox[2] - b_bbox[0]
    # Small pill background
    pill_x = (CARD_W - b_w) // 2 - 8
    pill_y = CARD_H - 36
    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + b_w + 16, pill_y + 24],
        radius=6,
        fill=(0, 0, 0, 150),
    )
    draw.text(((CARD_W - b_w) // 2, pill_y + 3), bridge_text,
              fill="#94a3b8", font=bridge_font)

    # 5. Glowing border
    glow_color = SUIT_COLORS.get(card.suit, "#ffffff")
    draw.rounded_rectangle(
        [3, 3, CARD_W - 4, CARD_H - 4],
        radius=CORNER_RADIUS,
        outline=glow_color,
        width=3,
    )
    # Inner subtle border
    draw.rounded_rectangle(
        [6, 6, CARD_W - 7, CARD_H - 7],
        radius=CORNER_RADIUS - 3,
        outline=glow_color + "40",  # with alpha
        width=1,
    )

    # 6. Rounded corners
    img = _round_corners(img, CORNER_RADIUS)

    # 7. Save
    if preview:
        img.show()
        return True

    suit_out = output_dir / card.suit
    suit_out.mkdir(parents=True, exist_ok=True)
    out_path = suit_out / card.file_path.name
    img.save(str(out_path), "PNG")
    print(f"  ✅ {card.suit}/{card.file_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Post-traitement des cartes")
    parser.add_argument("--suit", choices=["clubs", "diamonds", "hearts", "spades", "jokers", "all"],
                        default="all", help="Couleur à traiter")
    parser.add_argument("--card", type=int, help="Numéro de carte (1-54)")
    parser.add_argument("--preview", action="store_true", help="Afficher sans sauvegarder")
    parser.add_argument("--output", type=str, default=None,
                        help="Répertoire de sortie (défaut: visuals/output)")
    parser.add_argument("--inplace", action="store_true",
                        help="Écraser les images sources (attention !)")
    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else OUTPUT_DIR
    if args.inplace:
        output_dir = ASSETS_DIR

    print("=" * 60)
    print("🃏 Post-traitement des cartes — Ajout indices & bordures")
    print(f"   Source  : {ASSETS_DIR}")
    print(f"   Sortie  : {output_dir}")
    print("=" * 60)

    # Discover cards
    all_cards = discover_cards()
    print(f"   Cartes trouvées : {len(all_cards)}")

    # Filter
    if args.card:
        cards = [c for c in all_cards if c.card_number == args.card]
    elif args.suit == "all":
        cards = all_cards
    else:
        cards = [c for c in all_cards if c.suit == args.suit]

    if not cards:
        print("Aucune carte à traiter.")
        return

    # Load fonts
    rank_font, suit_font, bridge_font = _load_fonts()

    # Process
    success = 0
    for card in cards:
        if process_card(card, rank_font, suit_font, bridge_font, output_dir, args.preview):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"✅ {success}/{len(cards)} cartes traitées")
    print(f"📁 Sortie : {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
