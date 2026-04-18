"""Moteur de pré-calcul pour la démonstration pas-à-pas.

Transforme un texte clair + clé en une liste d'EncryptionStep décrivant
chaque sous-opération du chiffrement, pour l'affichage dans l'UI.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.deck import (
    JOKER_A,
    JOKER_B,
    card_bridge_value,
    card_value,
    create_deck,
)
from core.encryption import normalize_text, text_to_numbers
from core.keystream import key_deck
from core.solitaire import count_cut, move_joker_a, move_joker_b, triple_cut
from visuals.card_loader import card_short_name


# Couleurs associées à chaque opération (entier 1-5 ou étiquette string)
OP_COLORS: dict[int | str, str] = {
    1: "#5a9a6a",
    2: "#b85040",
    3: "#c09840",
    4: "#5f82a6",
    5: "#5a9a6a",
    "retry":   "#b07838",
    "encrypt": "#c09840",
}


@dataclass
class EncryptionStep:
    """Décrit une sous-étape du chiffrement pour la démonstration pas-à-pas."""
    letter_idx:   int
    plain_char:   str
    op_num:       int | str          # 1–5, "retry" ou "encrypt"
    op_name:      str
    op_desc:      str
    op_color:     str
    op_tip:       str
    deck_before:  tuple[int, ...]
    deck_after:   tuple[int, ...]
    center_cards: list[int]
    highlights:   dict[int, str]
    output_val:   int | None = None  # valeur lue (ops 5, retry, encrypt)
    cipher_char:  str = ""           # lettre chiffrée (étape encrypt uniquement)
    cipher_so_far: str = ""          # texte chiffré accumulé (étape encrypt uniquement)


def precompute_encryption_steps(
    plain_text: str, key: str | None
) -> list[EncryptionStep]:
    """Pré-calcule toutes les sous-étapes du chiffrement."""
    normalized = normalize_text(plain_text)
    if not normalized:
        return []

    deck = key_deck(key) if key else create_deck()
    plain_nums = text_to_numbers(normalized)
    steps: list[EncryptionStep] = []
    cipher_so_far = ""

    for letter_idx, (char, p_num) in enumerate(zip(normalized, plain_nums)):
        new_steps = _steps_for_letter(deck, letter_idx, char, p_num, cipher_so_far)
        steps.extend(new_steps)
        deck = new_steps[-1].deck_after
        cipher_so_far = new_steps[-1].cipher_so_far

    return steps


def _steps_for_letter(
    deck: tuple[int, ...],
    letter_idx: int,
    char: str,
    p_num: int,
    cipher_so_far: str,
) -> list[EncryptionStep]:
    """Toutes les sous-étapes pour chiffrer une seule lettre."""
    steps: list[EncryptionStep] = []

    # Op 1 — Déplacement Joker A
    deck, step = _op1_move_joker_a(deck, letter_idx, char)
    steps.append(step)

    # Op 2 — Plongée Joker B
    deck, step = _op2_move_joker_b(deck, letter_idx, char)
    steps.append(step)

    # Op 3 — Triple Coupe
    deck, step = _op3_triple_cut(deck, letter_idx, char)
    steps.append(step)

    # Op 4 — Coupe du Croupier
    deck, step = _op4_count_cut(deck, letter_idx, char)
    steps.append(step)

    # Op 5 — Lecture de la carte de sortie
    output_val, step = _op5_read_output(deck, letter_idx, char)
    steps.append(step)

    # Si un joker sort, on répète le cycle complet jusqu'à avoir une valeur
    if output_val is None:
        deck, output_val, retry_steps = _retry_until_non_joker(deck, letter_idx, char)
        steps.extend(retry_steps)

    # Étape de chiffrement : lettre + flux = lettre chiffrée
    steps.append(_encrypt_step(deck, letter_idx, char, p_num, output_val, cipher_so_far))

    return steps


# ── Helpers internes ──────────────────────────────────────────────────────────

def _read_output_from_deck(
    deck: tuple[int, ...],
) -> tuple[int, int | None, bool, int | None]:
    """Lit la carte de sortie selon l'op 5 de Solitaire (sans modifier le deck).

    Retourne (reader, output_card, is_joker, output_val).
    """
    reader = deck[0]
    n_read = card_bridge_value(reader)
    output_card = deck[n_read] if n_read < len(deck) else None
    is_joker = (output_card in (JOKER_A, JOKER_B)) if output_card is not None else True
    output_val = None if is_joker else card_value(output_card)
    return reader, output_card, is_joker, output_val


# ── Op 1 : Déplacement Joker A ────────────────────────────────────────────────

def _op1_move_joker_a(
    deck: tuple[int, ...], letter_idx: int, char: str
) -> tuple[tuple[int, ...], EncryptionStep]:
    deck_before = deck
    old_pos = list(deck).index(JOKER_A) + 1
    deck = move_joker_a(deck)
    new_pos = list(deck).index(JOKER_A) + 1
    ja_idx = list(deck).index(JOKER_A)

    # Cartes voisines du Joker A pour l'affichage
    center = [JOKER_A]
    if ja_idx > 0:
        center.insert(0, deck[ja_idx - 1])
    if ja_idx < len(deck) - 1:
        center.append(deck[ja_idx + 1])

    step = EncryptionStep(
        letter_idx=letter_idx, plain_char=char,
        op_num=1,
        op_name="Op 1 — Déplacement du Joker Noir",
        op_desc=f"Le Joker A glisse de la position {old_pos} → {new_pos}",
        op_color=OP_COLORS[1],
        op_tip="Le Joker A (♠) descend d'une place. S'il est dernier, il passe en 2ème.",
        deck_before=deck_before, deck_after=deck,
        center_cards=center,
        highlights={JOKER_A: "joker-a"},
    )
    return deck, step


# ── Op 2 : Plongée Joker B ────────────────────────────────────────────────────

def _op2_move_joker_b(
    deck: tuple[int, ...], letter_idx: int, char: str
) -> tuple[tuple[int, ...], EncryptionStep]:
    deck_before = deck
    old_pos = list(deck).index(JOKER_B) + 1
    deck = move_joker_b(deck)
    new_pos = list(deck).index(JOKER_B) + 1
    jb_idx = list(deck).index(JOKER_B)

    center = [JOKER_B]
    if jb_idx > 0:
        center.insert(0, deck[jb_idx - 1])
    if jb_idx < len(deck) - 1:
        center.append(deck[jb_idx + 1])

    step = EncryptionStep(
        letter_idx=letter_idx, plain_char=char,
        op_num=2,
        op_name="Op 2 — Plongée du Joker Rouge",
        op_desc=f"Le Joker B descend de 2 positions : {old_pos} → {new_pos}",
        op_color=OP_COLORS[2],
        op_tip="Le Joker B (♥) descend de 2 places avec wrap circulaire.",
        deck_before=deck_before, deck_after=deck,
        center_cards=center,
        highlights={JOKER_B: "joker-b"},
    )
    return deck, step


# ── Op 3 : Triple Coupe ───────────────────────────────────────────────────────

def _op3_triple_cut(
    deck: tuple[int, ...], letter_idx: int, char: str
) -> tuple[tuple[int, ...], EncryptionStep]:
    deck_before = deck
    deck_l = list(deck)
    pos_a, pos_b = deck_l.index(JOKER_A), deck_l.index(JOKER_B)
    first, second = min(pos_a, pos_b), max(pos_a, pos_b)
    n_top = first
    n_bot = len(deck) - second - 1
    deck = triple_cut(deck)

    highlights: dict[int, str] = {}
    for c in deck_before[:first]:
        highlights[c] = "seg-top"
    for c in deck_before[first:second + 1]:
        highlights[c] = "seg-mid"
    for c in deck_before[second + 1:]:
        highlights[c] = "seg-bot"

    step = EncryptionStep(
        letter_idx=letter_idx, plain_char=char,
        op_num=3,
        op_name="Op 3 — Triple Coupe",
        op_desc=f"{n_top} cartes du dessus ↔ {n_bot} du dessous. Les jokers restent au milieu.",
        op_color=OP_COLORS[3],
        op_tip="On soulève le paquet en 3 tas et on échange le haut et le bas.",
        deck_before=deck_before, deck_after=deck,
        center_cards=[JOKER_A, JOKER_B],
        highlights=highlights,
    )
    return deck, step


# ── Op 4 : Coupe du Croupier ──────────────────────────────────────────────────

def _op4_count_cut(
    deck: tuple[int, ...], letter_idx: int, char: str
) -> tuple[tuple[int, ...], EncryptionStep]:
    deck_before = deck
    anchor = deck[-1]
    n_val = card_bridge_value(anchor)
    deck = count_cut(deck)

    highlights: dict[int, str] = {anchor: "cut-anchor"}
    for c in deck_before[:n_val]:
        highlights[c] = "cut-top"

    step = EncryptionStep(
        letter_idx=letter_idx, plain_char=char,
        op_num=4,
        op_name="Op 4 — Coupe du Croupier",
        op_desc=f"La carte du fond ({card_short_name(anchor)}, val={n_val}) dicte la coupe.",
        op_color=OP_COLORS[4],
        op_tip=f"Les {n_val} premières cartes passent juste au-dessus de la carte ancre.",
        deck_before=deck_before, deck_after=deck,
        center_cards=[anchor],
        highlights=highlights,
    )
    return deck, step


# ── Op 5 : Lecture de la carte de sortie ─────────────────────────────────────

def _op5_read_output(
    deck: tuple[int, ...], letter_idx: int, char: str
) -> tuple[int | None, EncryptionStep]:
    """Lecture de la carte de sortie. Retourne (output_val, step)."""
    reader, output_card, is_joker, output_val = _read_output_from_deck(deck)
    n_read = card_bridge_value(reader)

    highlights: dict[int, str] = {reader: "reader"}
    center = [reader]
    if output_card is not None and not is_joker:
        highlights[output_card] = "output"
        center.append(output_card)

    out_name = card_short_name(output_card) if output_card and not is_joker else "Joker"
    step = EncryptionStep(
        letter_idx=letter_idx, plain_char=char,
        op_num=5,
        op_name="Op 5 — Lecture de la carte de sortie",
        op_desc=(
            f"1ère carte = {card_short_name(reader)} (val {n_read})"
            f" → on compte {n_read} → {out_name}"
            + (f" = {output_val}" if output_val else " = Joker ! On recommence.")
        ),
        op_color=OP_COLORS[5],
        op_tip="On regarde la 1ère carte, on compte sa valeur, et on lit la carte à cette position.",
        deck_before=deck, deck_after=deck,
        center_cards=center,
        highlights=highlights,
        output_val=output_val,
    )
    return output_val, step


# ── Retry : cycle supplémentaire si joker en sortie ──────────────────────────

def _retry_until_non_joker(
    deck: tuple[int, ...], letter_idx: int, char: str
) -> tuple[tuple[int, ...], int, list[EncryptionStep]]:
    """Répète un cycle complet (ops 1-4 + lecture) jusqu'à obtenir une valeur non-joker."""
    retry_steps: list[EncryptionStep] = []
    output_val: int | None = None

    while True:
        deck_before = deck
        deck = move_joker_a(deck)
        deck = move_joker_b(deck)
        deck = triple_cut(deck)
        deck = count_cut(deck)

        reader, output_card, is_joker, output_val = _read_output_from_deck(deck)

        highlights: dict[int, str] = {reader: "reader"}
        center = [reader]
        if output_card is not None and not is_joker:
            highlights[output_card] = "output"
            center.append(output_card)

        out_name = card_short_name(output_card) if output_card and not is_joker else "Joker"
        retry_steps.append(EncryptionStep(
            letter_idx=letter_idx, plain_char=char,
            op_num="retry",
            op_name="Cycle supplémentaire — Joker en sortie",
            op_desc=(
                f"Résultat : {out_name}"
                + (f" = {output_val}" if output_val else " → encore un cycle…")
            ),
            op_color=OP_COLORS["retry"],
            op_tip="Quand un joker sort, on refait un cycle complet automatiquement.",
            deck_before=deck_before, deck_after=deck,
            center_cards=center,
            highlights=highlights,
            output_val=output_val,
        ))

        if not is_joker:
            break

    return deck, output_val, retry_steps  # type: ignore[return-value]


# ── Étape de chiffrement : P + K = C ─────────────────────────────────────────

def _encrypt_step(
    deck: tuple[int, ...],
    letter_idx: int,
    char: str,
    p_num: int,
    ks_val: int,
    cipher_so_far: str,
) -> EncryptionStep:
    """Construit l'étape d'addition lettre + flux (modulo 26)."""
    c_num = (p_num + ks_val - 1) % 26 + 1
    cipher_char = chr(c_num - 1 + ord("A"))
    return EncryptionStep(
        letter_idx=letter_idx, plain_char=char,
        op_num="encrypt",
        op_name=f"Chiffrement de la lettre « {char} »",
        op_desc=f"{char} ({p_num}) + flux ({ks_val}) = {c_num} → {cipher_char}",
        op_color=OP_COLORS["encrypt"],
        op_tip="On additionne la valeur de la lettre et la valeur du flux (modulo 26).",
        deck_before=deck, deck_after=deck,
        center_cards=[],
        highlights={},
        output_val=ks_val,
        cipher_char=cipher_char,
        cipher_so_far=cipher_so_far + cipher_char,
    )
