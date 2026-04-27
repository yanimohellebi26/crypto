"""Chargement et rendu HTML des cartes pour Streamlit.

Rendus disponibles :
  - render_deck_chips()           chips textuels colorés (léger)
  - render_card_images()          images PNG en spotlight
  - render_poker_table()          table de poker complète
  - render_immersive_spotlight()  composant 3D immersif
"""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

ASSETS_ROOT = Path(__file__).parent
THEME_DIRS: dict[str, tuple[str, ...]] = {
  "modern": ("output", "assets"),
  "classic": ("real_deck",),
  "academic": ("academic_deck",),  # Pas de fichiers — génération SVG à la volée
}
_CARD_THEME = "modern"

RANK_LABELS: tuple[str, ...] = (
    "ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king",
)
RANK_SHORT: tuple[str, ...] = (
    "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K",
)
SUIT_SYMBOLS: dict[str, str] = {
    "clubs": "\u2663", "diamonds": "\u2666", "hearts": "\u2665", "spades": "\u2660",
}
SUIT_COLORS: dict[str, str] = {
    "clubs": "#5a9a6a", "diamonds": "#c85a4f", "hearts": "#c85a4f", "spades": "#6a7a90",
}
HIGHLIGHT_COLORS: dict[str, str] = {
    "joker-a":    "#5a9a6a",
    "joker-b":    "#c85a4f",
    "seg-top":    "#5a80a8",
    "seg-mid":    "#e0a840",
    "seg-bot":    "#7070a0",
    "cut-top":    "#7a68a0",
    "cut-anchor": "#c08838",
    "output":     "#e0a840",
    "reader":     "#4a8a8a",
}
HIGHLIGHT_LABELS: dict[str, tuple[str, str]] = {
    "joker-a":    ("\u25cf", "Joker A"),
    "joker-b":    ("\u25cf", "Joker B"),
    "seg-top":    ("\u25cf", "Segment haut \u2192 descend"),
    "seg-mid":    ("\u25cf", "Milieu avec jokers"),
    "seg-bot":    ("\u25cf", "Segment bas \u2192 monte"),
    "cut-top":    ("\u25cf", "Cartes deplacees"),
    "cut-anchor": ("\u25cf", "Ancre (derniere carte)"),
    "output":     ("\u25cf", "Valeur de sortie"),
    "reader":     ("\u25cf", "Carte lectrice"),
}


def _suit_folder(n: int) -> str:
    """Nom du dossier d'assets pour la carte n."""
    if n >= 53:
        return "jokers"
    if n <= 13:
        return "clubs"
    if n <= 26:
        return "diamonds"
    if n <= 39:
        return "hearts"
    return "spades"


def _resolve_theme(theme: str | None = None) -> str:
    """Retourne un thème valide, sinon le thème moderne."""
    if theme in THEME_DIRS:
        return theme
    try:
        import streamlit as st

        session_theme = st.session_state.get("card_theme")
        if session_theme in THEME_DIRS:
            return session_theme
    except Exception:
        pass
    if _CARD_THEME in THEME_DIRS:
        return _CARD_THEME
    return "modern"


def _theme_asset_dir(theme: str) -> Path:
    """Retourne le premier dossier d'assets existant pour un thème."""
    for dirname in THEME_DIRS[theme]:
        candidate = ASSETS_ROOT / dirname
        if candidate.exists():
            return candidate
    return ASSETS_ROOT / THEME_DIRS[theme][0]


def classic_theme_available() -> bool:
    """Indique si un dossier de cartes classiques est disponible."""
    return (ASSETS_ROOT / "real_deck").exists()


def set_card_theme(theme: str) -> None:
    """Sélectionne le thème visuel global des cartes.

    Le cache des images est vidé pour éviter de mélanger les decks.
    """
    global _CARD_THEME
    _CARD_THEME = _resolve_theme(theme)
    card_b64.cache_clear()
    card_b64_thumb.cache_clear()
    try:
        import streamlit as st
        st.session_state["card_theme"] = _CARD_THEME
    except Exception:
        pass


def card_path(n: int, theme: str | None = None) -> Path:
    """Chemin absolu vers l'image PNG de la carte n (1-54)."""
    resolved_theme = _resolve_theme(theme)
    assets_dir = _theme_asset_dir(resolved_theme)
    modern_assets_dir = _theme_asset_dir("modern")
    folder = _suit_folder(n)
    if n == 53:
        candidate = assets_dir / folder / "53_joker_a.png"
        if candidate.exists() or resolved_theme in ("modern", "classic"):
            return candidate
        return modern_assets_dir / folder / "53_joker_a.png"
    if n == 54:
        candidate = assets_dir / folder / "54_joker_b.png"
        if candidate.exists() or resolved_theme in ("modern", "classic"):
            return candidate
        return modern_assets_dir / folder / "54_joker_b.png"
    rank_idx = (n - 1) % 13
    filename = f"{n:02d}_{RANK_LABELS[rank_idx]}.png"
    candidate = assets_dir / folder / filename
    if candidate.exists() or resolved_theme in ("modern", "classic"):
        return candidate
    return modern_assets_dir / folder / filename


@lru_cache(maxsize=112)
def card_b64(n: int, theme: str | None = None) -> str:
    """Image de la carte n encodée en base64 (mis en cache LRU)."""
    path = card_path(n, theme=theme)
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


@lru_cache(maxsize=336)  # 56 cartes × 3 tailles × 2 thèmes
def card_b64_thumb(n: int, width: int = 120, theme: str | None = None) -> str:
    """Miniature PNG de la carte n avec alpha préservé.

    Args:
        n: Numéro de carte (1-54).
        width: Largeur cible en pixels (hauteur proportionnelle).

    Returns:
        Chaîne base64 du PNG redimensionné.
    """
    path = card_path(n, theme=theme)
    if not path.exists():
        return ""
    try:
        from PIL import Image
        import io
        img = Image.open(path).convert("RGBA")
        ratio = width / img.width
        new_h = int(img.height * ratio)
        img = img.resize((width, new_h), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except (ImportError, OSError, ValueError):
        # PIL absent ou image corrompue → retourner l'image originale non redimensionnée
        return card_b64(n, theme=theme)


def _classic_svg_data_uri(n: int, width: int) -> str:
    """Génère une carte classique SVG en secours (sans assets externes)."""
    height = int(width * 1.4)
    corner_size = max(16, int(width * 0.14))
    symbol_size = max(34, int(width * 0.28))

    if n == 53:
      rank_text = "JOKER"
      suit_symbol = "★"
      suit_color = "#222222"
    elif n == 54:
      rank_text = "JOKER"
      suit_symbol = "☆"
      suit_color = "#b02020"
    else:
      folder = _suit_folder(n)
      rank_idx = (n - 1) % 13
      rank_text = RANK_SHORT[rank_idx]
      suit_symbol = SUIT_SYMBOLS[folder]
      suit_color = "#b02020" if folder in ("hearts", "diamonds") else "#222222"

    svg = (
      f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
      f'<rect x="2" y="2" width="{width - 4}" height="{height - 4}" rx="10" fill="#ffffff" stroke="#222222" stroke-width="3"/>'
      f'<text x="12" y="{corner_size}" font-family="Georgia, serif" font-size="{corner_size}" fill="{suit_color}" font-weight="700">{rank_text}</text>'
      f'<text x="12" y="{corner_size + 18}" font-family="Georgia, serif" font-size="18" fill="{suit_color}">{suit_symbol}</text>'
      f'<text x="{width / 2}" y="{height / 2 + 8}" text-anchor="middle" font-family="Georgia, serif" font-size="{symbol_size}" fill="{suit_color}">{suit_symbol}</text>'
      f'<g transform="rotate(180 {width / 2} {height / 2})">'
      f'<text x="12" y="{corner_size}" font-family="Georgia, serif" font-size="{corner_size}" fill="{suit_color}" font-weight="700">{rank_text}</text>'
      f'<text x="12" y="{corner_size + 18}" font-family="Georgia, serif" font-size="18" fill="{suit_color}">{suit_symbol}</text>'
      '</g>'
      '</svg>'
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _academic_svg_data_uri(n: int, width: int) -> str:
    """Carte SVG style académique — fond blanc, typographie propre, bordeaux/encre."""
    height = int(width * 1.4)
    pad = max(3, int(width * 0.08))
    rank_size = max(8, int(width * 0.26))
    suit_top = max(7, int(width * 0.22))
    center_size = max(14, int(width * 0.40))
    pos_size = max(5, int(width * 0.16))

    if n == 53:
        rank_text, suit_sym = "JKR", "★"
        ink = "#8a1538"
        bg1, bg2 = "#ffffff", "#faf4e5"
    elif n == 54:
        rank_text, suit_sym = "JKR", "☆"
        ink = "#1a1a1a"
        bg1, bg2 = "#ffffff", "#faf4e5"
    else:
        folder = _suit_folder(n)
        rank_idx = (n - 1) % 13
        rank_text = RANK_SHORT[rank_idx]
        suit_sym = {"clubs": "♣", "diamonds": "♦",
                    "hearts": "♥", "spades": "♠"}[folder]
        ink = "#8a1538" if folder in ("hearts", "diamonds") else "#1a1a1a"
        bg1, bg2 = "#ffffff", "#ffffff"

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"'
        f' viewBox="0 0 {width} {height}">'
        f'<defs><linearGradient id="bg{n}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{bg1}"/>'
        f'<stop offset="100%" stop-color="{bg2}"/>'
        f'</linearGradient></defs>'
        f'<rect width="{width}" height="{height}" rx="4" fill="url(#bg{n})"'
        f' stroke="#bab3a0" stroke-width="1"/>'
        # Rang coin haut-gauche
        f'<text x="{pad}" y="{pad + rank_size}" font-family="Inter Tight,Inter,sans-serif"'
        f' font-size="{rank_size}" font-weight="600" fill="{ink}">{rank_text}</text>'
        # Symbole sous le rang
        f'<text x="{pad}" y="{pad + rank_size + suit_top + 1}"'
        f' font-family="serif" font-size="{suit_top}" fill="{ink}">{suit_sym}</text>'
        # Grand symbole central
        f'<text x="{width // 2}" y="{height // 2 + center_size // 3}"'
        f' text-anchor="middle" font-family="serif" font-size="{center_size}"'
        f' fill="{ink}" opacity="0.45">{suit_sym}</text>'
        # Numéro position bas-droite
        f'<text x="{width - pad}" y="{height - pad}" text-anchor="end"'
        f' font-family="JetBrains Mono,monospace" font-size="{pos_size}"'
        f' fill="#a8a39a">{n}</text>'
        f'</svg>'
    )
    enc = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{enc}"


def card_img_src(n: int, width: int = 120, theme: str | None = None) -> str:
    """Retourne une source image prête à l'emploi pour la carte n."""
    resolved_theme = _resolve_theme(theme)
    if resolved_theme == "academic":
        return _academic_svg_data_uri(n, width)
    b64 = card_b64_thumb(n, width=width, theme=resolved_theme)
    if b64:
        return f"data:image/png;base64,{b64}"
    if resolved_theme == "classic":
        return _classic_svg_data_uri(n, width)
    return ""


def card_short_name(n: int) -> str:
    """Nom court d'une carte : 'A♣', '10♦', 'JA', 'JB'."""
    if n == 53:
        return "JA"
    if n == 54:
        return "JB"
    folder = _suit_folder(n)
    rank_idx = (n - 1) % 13
    return f"{RANK_SHORT[rank_idx]}{SUIT_SYMBOLS[folder]}"


def render_deck_chips(
    deck: tuple[int, ...],
    highlights: dict[int, str] | None = None,
    chip_width: int = 46,
) -> str:
    """HTML : paquet de 54 cartes comme chips textuels colorés.

    Très léger (pas d'images). Highlights colorés par opération.
    À utiliser avec st.components.v1.html(html, height=130).
    """
    h = highlights or {}
    chips: list[str] = []

    for pos, card in enumerate(deck):
        name = card_short_name(card)
        hl = h.get(card, "")
        if hl:
            bg = HIGHLIGHT_COLORS[hl]
            tc = "#000" if hl in ("output", "seg-mid", "cut-anchor") else "#fff"
            border = f"2px solid {bg}"
        else:
            suit_sym = name[-1] if name not in ("JA", "JB") else ""
            bg = "#1e293b"
            tc = SUIT_COLORS.get(suit_sym, "#94a3b8")
            border = "1px solid #334155"

        chips.append(
            f'<div title="{name} — pos {pos + 1}" '
            f'style="display:inline-block;width:{chip_width}px;margin:2px 1px;'
            f'padding:4px 2px;border-radius:4px;background:{bg};'
            f'border:{border};color:{tc};font-family:monospace;font-size:11px;'
            f'text-align:center;cursor:default;vertical-align:top;">'
            f'<b>{name}</b>'
            f'<br><span style="font-size:8px;opacity:0.55">{pos + 1}</span>'
            f'</div>'
        )

    seen = set(h.values())
    legend_items = [
        f'<span style="margin-right:10px;font-size:11px;color:#94a3b8;">'
        f'{icon} {label}</span>'
        for cls, (icon, label) in HIGHLIGHT_LABELS.items() if cls in seen
    ]
    legend = (
        f'<div style="margin-top:6px;padding-top:4px;border-top:1px solid #334155;">'
        f'{"".join(legend_items)}</div>'
    ) if legend_items else ""

    return (
        f'<div style="background:#0f172a;padding:8px;border-radius:8px;'
        f'border:1px solid #334155;overflow-x:auto;">'
        f'<div style="white-space:nowrap;">{"".join(chips)}</div>'
        f'{legend}'
        f'</div>'
    )


def render_deck_grid(
    deck: tuple[int, ...],
    highlights: dict[int, str] | None = None,
    cols: int = 9,
    card_width: int = 64,
) -> str:
    """HTML : grille de cartes avec images miniatures et highlights visuels.

    Affiche les 54 cartes en grille (cols colonnes), chaque carte avec son image
    JPEG miniature. Les cartes surlignées brillent avec une couleur spécifique.
    Compatible avec st.markdown(unsafe_allow_html=True).
    """
    h = highlights or {}
    theme = _resolve_theme()
    card_h = int(card_width * 1.4)
    rows_html: list[str] = []

    for row_start in range(0, len(deck), cols):
        row_cards = deck[row_start : row_start + cols]
        cells: list[str] = []
        for pos_in_row, card in enumerate(row_cards):
            global_pos = row_start + pos_in_row
            src = card_img_src(card, width=card_width, theme=theme)
            hl = h.get(card, "")
            bc = HIGHLIGHT_COLORS.get(hl, "transparent")
            border = f"3px solid {bc}" if hl else "2px solid #0f172a"
            glow = f"box-shadow:0 2px 8px rgba(0,0,0,0.4);" if hl else ""
            name = card_short_name(card)
            pos_color = bc if hl else "#334155"

            cells.append(
                f'<td style="padding:3px;text-align:center;vertical-align:top;">'
            f'<img src="{src}" '
                f'title="{name} — pos {global_pos + 1}" '
                f'style="width:{card_width}px;height:{card_h}px;object-fit:cover;'
                f'border-radius:5px;display:block;border:{border};{glow}"/>'
                f'<div style="font-family:monospace;font-size:9px;color:{pos_color};'
                f'text-align:center;margin-top:1px;font-weight:{"bold" if hl else "normal"};">'
                f'{name}</div>'
                f'</td>'
            )

        rows_html.append(f'<tr>{"".join(cells)}</tr>')

    seen = set(h.values())
    legend_items = [
        f'<span style="display:inline-block;margin:3px 8px;font-size:11px;color:#e2e8f0;">'
        f'<span style="display:inline-block;width:12px;height:12px;border-radius:2px;'
        f'background:{HIGHLIGHT_COLORS[cls]};margin-right:4px;vertical-align:middle;"></span>'
        f'{label}</span>'
        for cls, (icon, label) in HIGHLIGHT_LABELS.items() if cls in seen
    ]
    legend = (
        f'<div style="margin-top:8px;padding-top:6px;border-top:1px solid #334155;'
        f'text-align:center;">{"".join(legend_items)}</div>'
    ) if legend_items else ""

    return (
        f'<div style="background:#0f172a;padding:10px;border-radius:10px;'
        f'border:1px solid #334155;">'
        f'<table style="border-collapse:collapse;margin:0 auto;">'
        f'{"".join(rows_html)}'
        f'</table>'
        f'{legend}'
        f'</div>'
    )


def render_card_images(
    cards: list[int],
    labels: dict[int, str] | None = None,
    card_width: int = 100,
    highlight_class: dict[int, str] | None = None,
) -> str:
    """HTML : miniatures des cartes pour un spotlight (cartes clés de l'étape).

    Utilise des JPEG redimensionnés (~10KB chacun) pour des performances optimales.
    À utiliser avec st.components.v1.html(html, height=190).
    """
    lbl = labels or {}
    hl = highlight_class or {}
    theme = _resolve_theme()
    parts: list[str] = []

    for card in cards:
        # Utilise la miniature JPEG (réduit ~100× la taille)
        src = card_img_src(card, width=card_width, theme=theme)
        if not src:
            continue
        label = lbl.get(card, card_short_name(card))
        border_color = HIGHLIGHT_COLORS.get(hl.get(card, ""), "#334155")
        parts.append(
            f'<div style="display:inline-block;margin:6px;text-align:center;">'
        f'<img src="{src}" '
            f'style="width:{card_width}px;border-radius:6px;display:block;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.4);border:2px solid {border_color};"/>'
            f'<div style="font-size:11px;color:#94a3b8;margin-top:4px;">{label}</div>'
            f'</div>'
        )

    if not parts:
        return ""

    return (
        f'<div style="background:#0f172a;padding:8px;border-radius:8px;'
        f'border:1px solid #334155;text-align:center;">'
        f'{"".join(parts)}'
        f'</div>'
    )


def render_poker_table(
    deck: tuple[int, ...],
    dealt_cards: list[int] | None = None,
    highlights: dict[int, str] | None = None,
    center_cards: list[int] | None = None,
    card_width: int = 58,
) -> str:
    """Render the full deck as a realistic poker table with oval felt, wooden rail,
    and card positions with glow highlights.

    - deck: the full 54-card deck in current order
    - dealt_cards: cards currently dealt out (shown as empty slots)
    - highlights: card→highlight_class mapping for glow effects
    - center_cards: cards shown larger in the center spotlight area
    """
    h = highlights or {}
    dealt = set(dealt_cards or [])
    center = center_cards or []
    theme = _resolve_theme()
    card_h = int(card_width * 1.4)

    # ── Build shoe (draw pile) cards ──
    shoe_cards: list[str] = []
    for pos, card in enumerate(deck):
        src = card_img_src(card, width=card_width, theme=theme)
        hl_key = h.get(card, "")
        bc = HIGHLIGHT_COLORS.get(hl_key, "transparent")
        is_dealt = card in dealt
        name = card_short_name(card)

        if is_dealt:
            shoe_cards.append(
                f'<div style="display:inline-block;width:{card_width}px;height:{card_h}px;'
                f'margin:2px;border-radius:6px;background:#1a3a20;border:1px dashed #2d5a34;'
                f'opacity:0.3;vertical-align:top;" title="{name} — distribué"></div>'
            )
        else:
            border = f"2px solid {bc}" if hl_key else "1px solid #2d5a34"
            glow = f"box-shadow:0 2px 8px rgba(0,0,0,0.4);" if hl_key else ""
            # Dim non-highlighted cards strongly so active ones pop
            opacity = "1" if hl_key else "0.3"
            scale = "transform:scale(1.08);" if hl_key else ""
            shoe_cards.append(
                f'<div style="display:inline-block;margin:2px;vertical-align:top;'
                f'position:relative;{scale}" title="{name} — pos {pos + 1}">'
              f'<img src="{src}" '
                f'style="width:{card_width}px;height:{card_h}px;object-fit:cover;'
                f'border-radius:6px;border:{border};{glow}'
                f'opacity:{opacity};transition:all 0.3s ease;"/>'
                f'<div style="position:absolute;bottom:2px;left:0;right:0;'
                f'font-family:monospace;font-size:8px;text-align:center;'
                f'color:{"#fff" if hl_key else "#6b8a70"};text-shadow:0 1px 2px rgba(0,0,0,0.8);'
                f'font-weight:{"700" if hl_key else "400"};">'
                f'{pos + 1}</div>'
                f'</div>'
            )

    # ── Build center spotlight cards ──
    center_html = ""
    if center:
        cw = max(card_width + 30, 90)
        ch = int(cw * 1.4)
        center_parts: list[str] = []
        for card in center:
            src = card_img_src(card, width=cw, theme=theme)
            hl_cls = h.get(card, "")
            bc = HIGHLIGHT_COLORS.get(hl_cls, "#e0a840")
            name = card_short_name(card)
            center_parts.append(
                f'<div style="display:inline-block;margin:0 10px;text-align:center;">'
            f'<img src="{src}" '
                f'style="width:{cw}px;height:{ch}px;object-fit:cover;border-radius:8px;'
                f'border:2px solid {bc};box-shadow:0 0 20px 6px {bc},0 4px 15px rgba(0,0,0,0.5);"/>'
                f'<div style="color:{bc};font-family:\'JetBrains Mono\',monospace;font-size:12px;'
                f'margin-top:6px;font-weight:600;">{name}</div>'
                f'</div>'
            )
        center_html = (
            f'<div style="text-align:center;padding:16px 0;min-height:160px;'
            f'display:flex;align-items:center;justify-content:center;gap:8px;">'
            f'{"".join(center_parts)}'
            f'</div>'
        )

    # ── Legend ──
    seen = set(h.values())
    legend_items = [
        f'<span style="display:inline-block;margin:2px 8px;font-size:11px;color:#b0c4a8;">'
        f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
        f'background:{HIGHLIGHT_COLORS[cls]};margin-right:4px;vertical-align:middle;'
        f'box-shadow:0 0 6px {HIGHLIGHT_COLORS[cls]};"></span>'
        f'{label}</span>'
        for cls, (_, label) in HIGHLIGHT_LABELS.items() if cls in seen
    ]
    legend = (
        f'<div style="text-align:center;padding:8px 0;border-top:1px solid #2d5a34;">'
        f'{"".join(legend_items)}</div>'
    ) if legend_items else ""

    # ── Full poker table ──
    return (
        # Outer wood frame
        f'<div style="'
        f'background:linear-gradient(145deg, #2a1a0a 0%, #1a0f05 50%, #0d0800 100%);'
        f'border-radius:50% / 20%;'
        f'padding:10px;'
        f'box-shadow:0 10px 40px rgba(0,0,0,0.7),inset 0 2px 4px rgba(255,255,255,0.05);">'
        # Rail
        f'<div style="'
        f'background:linear-gradient(180deg, #5a3a1a 0%, #3a2510 40%, #2a1a08 100%);'
        f'border-radius:50% / 20%;'
        f'padding:6px;'
        f'box-shadow:inset 0 4px 12px rgba(0,0,0,0.5),inset 0 -2px 6px rgba(212,175,55,0.1);'
        f'position:relative;">'
        # Gold trim on rail
        f'<div style="position:absolute;top:3px;left:3px;right:3px;bottom:3px;'
        f'border:1px solid rgba(212,175,55,0.18);border-radius:50% / 20%;'
        f'pointer-events:none;"></div>'
        # Felt surface
        f'<div style="'
        f'background:radial-gradient(ellipse at 50% 40%, #1f7a3a 0%, #196b30 25%, #135a28 50%, #0d4a1e 75%, #083814 100%);'
        f'border-radius:50% / 20%;'
        f'position:relative;overflow:hidden;'
        f'padding:20px 16px;'
        f'box-shadow:inset 0 0 60px rgba(0,0,0,0.3),inset 0 0 15px rgba(0,0,0,0.2);">'
        # Felt texture
        f'<div style="position:absolute;top:0;left:0;right:0;bottom:0;'
        f'background:url(\'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%226%22 height=%226%22>'
        f'<rect width=%226%22 height=%226%22 fill=%22transparent%22/>'
        f'<circle cx=%223%22 cy=%223%22 r=%220.6%22 fill=%22rgba(255,255,255,0.015)%22/></svg>\');'
        f'pointer-events:none;z-index:0;"></div>'
        # Inner gold border
        f'<div style="position:absolute;top:10px;left:10px;right:10px;bottom:10px;'
        f'border:1.5px solid rgba(212,175,55,0.1);border-radius:50% / 20%;'
        f'pointer-events:none;z-index:0;"></div>'
        # Content
        f'<div style="position:relative;z-index:1;">'
        f'{center_html}'
        # Card grid
        f'<div style="background:rgba(0,0,0,0.15);border-radius:12px;padding:10px;'
        f'border:1px solid rgba(45,90,52,0.4);margin-top:8px;'
        f'max-height:550px;overflow-y:auto;overflow-x:hidden;">'
        f'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:1px;">'
        f'{"".join(shoe_cards)}'
        f'</div>'
        f'</div>'
        f'{legend}'
        f'</div>'
        f'</div></div></div>'
    )


def render_immersive_spotlight(
    center_cards: list[int],
    highlights: dict[int, str],
    op_name: str = "",
    op_color: str = "#e0a840",
    op_num: int | str = 1,
    card_width: int = 180,
) -> str:
    """Immersive HTML component with 3D poker table, animated cards,
    interactive mouse-tracking tilt, and subtle highlight effects.

    Returns a complete HTML document string for st.components.v1.html().
    """
    card_parts: list[str] = []
    theme = _resolve_theme()
    for i, card in enumerate(center_cards):
        src = card_img_src(card, width=card_width, theme=theme)
        if not src:
            continue
        hl_key = highlights.get(card, "")
        bc = HIGHLIGHT_COLORS.get(hl_key, "#e0a840")
        name = card_short_name(card)
        ch = int(card_width * 1.4)
        card_parts.append(
            f'<div class="card-slot" data-idx="{i}" data-color="{bc}">'
        f'<img class="card-img" src="{src}" '
            f'style="width:{card_width}px;height:{ch}px;border-color:{bc};" />'
            f'<div class="card-label" style="color:{bc};">{name}</div>'
            f'</div>'
        )
    cards_html = "\n".join(card_parts)
    n_cards = len(card_parts)

    op_display = str(op_num) if isinstance(op_num, int) else "#"

    return f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;overflow:hidden;font-family:'Segoe UI',system-ui,sans-serif;}}

/* ── Scene ── */
.scene{{
  perspective:1200px;
  width:100%;display:flex;justify-content:center;align-items:center;
  padding:8px;
}}

/* ── 3D Table ── */
.table{{
  width:96%;max-width:720px;
  position:relative;
  transform:rotateX(4deg);
  transform-style:preserve-3d;
  transition:transform 0.3s ease;
}}
.table-rail{{
  background:linear-gradient(145deg,#5a3a1a 0%,#3a2510 40%,#2a1a08 100%);
  border-radius:50%/28%;
  padding:10px;
  box-shadow:
    0 25px 80px rgba(0,0,0,0.8),
    0 10px 30px rgba(0,0,0,0.5),
    inset 0 2px 4px rgba(255,255,255,0.06);
  position:relative;
}}
.table-rail::before{{
  content:'';position:absolute;
  top:4px;left:4px;right:4px;bottom:4px;
  border:1.5px solid rgba(212,175,55,0.22);
  border-radius:50%/28%;pointer-events:none;
}}
.table-felt{{
  background:radial-gradient(ellipse at 50% 38%,#1f7a3a 0%,#196b30 20%,#135a28 45%,#0d4a1e 70%,#083814 100%);
  border-radius:50%/28%;
  min-height:280px;
  position:relative;overflow:hidden;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  padding:24px 22px;
  box-shadow:inset 0 0 100px rgba(0,0,0,0.35),inset 0 0 25px rgba(0,0,0,0.2);
}}

/* Felt texture overlay */
.table-felt::before{{
  content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:repeating-conic-gradient(rgba(255,255,255,0.008) 0% 25%,transparent 0% 50%) 0 0/6px 6px;
  pointer-events:none;z-index:0;
}}
/* Inner gold line */
.table-felt::after{{
  content:'';position:absolute;
  top:14px;left:14px;right:14px;bottom:14px;
  border:1.5px solid rgba(212,175,55,0.12);
  border-radius:50%/28%;pointer-events:none;z-index:0;
}}


/* ── Operation banner ── */
.op-banner{{
  text-align:center;position:relative;z-index:3;
  margin-bottom:22px;
  animation:bannerIn 0.5s ease-out;
}}
@keyframes bannerIn{{
  from{{opacity:0;transform:translateY(-15px);}}
  to{{opacity:1;transform:translateY(0);}}
}}
.op-badge{{
  display:inline-flex;align-items:center;justify-content:center;
  width:36px;height:36px;border-radius:50%;
  font-family:'JetBrains Mono',monospace;font-weight:800;font-size:15px;
  margin-right:10px;vertical-align:middle;
  box-shadow:0 2px 8px rgba(0,0,0,0.3);
  position:relative;
}}
.op-text{{
  font-family:'JetBrains Mono',monospace;
  font-size:13px;letter-spacing:0.08em;
  text-transform:uppercase;vertical-align:middle;
}}

/* ── Card zone ── */
.card-zone{{
  display:flex;justify-content:center;align-items:center;
  gap:20px;min-height:200px;flex-wrap:wrap;
  position:relative;z-index:3;
}}

/* ── Card slot ── */
.card-slot{{
  position:relative;text-align:center;
  transform-style:preserve-3d;
  cursor:pointer;
  opacity:0;
}}
.card-slot:hover{{z-index:10;}}
.card-slot:hover .card-img{{
  transform:translateY(-14px) scale(1.06);
}}
.card-slot:hover .card-glow{{
  opacity:1 !important;transform:scale(1.05);
}}

.card-img{{
  border-radius:12px;display:block;
  border:3px solid;
  object-fit:cover;
  transition:transform 0.35s cubic-bezier(0.34,1.56,0.64,1),box-shadow 0.3s ease;
  box-shadow:0 8px 30px rgba(0,0,0,0.6);
  position:relative;z-index:1;
}}

/* ── Neon glow ring ── */
.card-glow{{
  display:none;
}}

.card-label{{
  font-family:'JetBrains Mono',monospace;
  font-weight:700;font-size:15px;
  margin-top:12px;
  letter-spacing:0.1em;
  position:relative;z-index:1;
}}

/* ── Card entrance animations ── */
@keyframes enterFromLeft{{
  0%{{transform:translateX(-60px) scale(0.9);opacity:0;}}
  100%{{transform:translateX(0) scale(1);opacity:1;}}
}}
@keyframes enterFromTop{{
  0%{{transform:translateY(-50px) scale(0.9);opacity:0;}}
  100%{{transform:translateY(0) scale(1);opacity:1;}}
}}
@keyframes enterFromRight{{
  0%{{transform:translateX(60px) scale(0.9);opacity:0;}}
  100%{{transform:translateX(0) scale(1);opacity:1;}}
}}
@keyframes enterFromBottom{{
  0%{{transform:translateY(40px) scale(0.9);opacity:0;}}
  100%{{transform:translateY(0) scale(1);opacity:1;}}
}}

/* Shoe pile indicator */
.shoe{{
  position:absolute;right:28px;bottom:18px;
  display:flex;align-items:flex-end;gap:3px;z-index:3;
  opacity:0.7;
}}
.shoe-card{{
  width:24px;height:34px;
  background:linear-gradient(135deg,#1a3366 0%,#0d1f3d 100%);
  border-radius:3px;border:1px solid #2a4a8a;
}}
.shoe-card:nth-child(2){{margin-left:-18px;transform:translateY(-1px);}}
.shoe-card:nth-child(3){{margin-left:-18px;transform:translateY(-2px);}}
.shoe-label{{
  font-family:'JetBrains Mono',monospace;font-size:10px;
  color:#6b8a70;margin-left:6px;white-space:nowrap;
}}

</style></head><body>
<div class="scene">
  <div class="table" id="pokerTable">
    <div class="table-rail">
      <div class="table-felt" id="felt">

        <div class="op-banner">
          <span class="op-badge" style="background:{op_color};color:#000;border-color:{op_color};">{op_display}</span>
          <span class="op-text" style="color:{op_color};">{op_name}</span>
        </div>

        <div class="card-zone" id="cardZone">
          {cards_html}
        </div>

        <div class="shoe">
          <div class="shoe-card"></div>
          <div class="shoe-card"></div>
          <div class="shoe-card"></div>
          <span class="shoe-label">54 cartes</span>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
(function(){{
  // ── Card entrance animation ──
  const animations = ['enterFromLeft','enterFromTop','enterFromRight','enterFromBottom'];
  const cards = document.querySelectorAll('.card-slot');
  const nCards = {n_cards};

  cards.forEach((card, i) => {{
    const anim = animations[i % animations.length];
    const delay = i * 0.18;
    card.style.animation = anim + ' 0.7s cubic-bezier(0.34,1.56,0.64,1) ' + delay + 's forwards';
  }});

  // ── 3D Mouse tilt on table ──
  const table = document.getElementById('pokerTable');
  const felt = document.getElementById('felt');

  felt.addEventListener('mousemove', (e) => {{
    const rect = felt.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    const rotY = (x - 0.5) * 6;
    const rotX = (y - 0.5) * -3 + 4;
    table.style.transform = 'rotateX(' + rotX + 'deg) rotateY(' + rotY + 'deg)';
  }});

  felt.addEventListener('mouseleave', () => {{
    table.style.transform = 'rotateX(4deg) rotateY(0deg)';
  }});

  // ── Card hover parallax ──
  cards.forEach(card => {{
    card.addEventListener('mousemove', (e) => {{
      const rect = card.getBoundingClientRect();
      const cx = (e.clientX - rect.left) / rect.width - 0.5;
      const cy = (e.clientY - rect.top) / rect.height - 0.5;
      const img = card.querySelector('.card-img');
      if(img) {{
        img.style.transform = 'translateY(-14px) scale(1.06) rotateY(' + (cx*12) + 'deg) rotateX(' + (-cy*8) + 'deg)';
      }}
    }});
    card.addEventListener('mouseleave', (e) => {{
      const img = card.querySelector('.card-img');
      if(img) img.style.transform = '';
    }});
  }});
}})();
</script>
</body></html>'''

