"""Version simplifiée de l'algorithme Solitaire.

Après lecture de la carte du dessus :
  Tour impair -> placer en dernière position
  Tour pair   -> placer en avant-dernière position
"""

from __future__ import annotations

from core.deck import JOKER_A, JOKER_B, card_value


def simple_step(
    deck: tuple[int, ...], round_number: int,
) -> tuple[tuple[int, ...], int | None]:
    """Un pas du Solitaire simplifié. Renvoie (deck, valeur ou None)."""
    cards = list(deck)
    top_card = cards.pop(0)

    if round_number % 2 == 1:
        cards.append(top_card)
    else:
        cards.insert(len(cards) - 1, top_card)

    if top_card in (JOKER_A, JOKER_B):
        return tuple(cards), None

    value = card_value(top_card)
    return tuple(cards), value


def generate_simple_keystream_value(
    deck: tuple[int, ...], round_number: int,
) -> tuple[tuple[int, ...], int, int]:
    """Génère une valeur en sautant les jokers. Renvoie (deck, val, round)."""
    while True:
        deck, output = simple_step(deck, round_number)
        round_number += 1
        if output is not None:
            return deck, output, round_number


def generate_simple_keystream(
    deck: tuple[int, ...], length: int,
) -> tuple[tuple[int, ...], list[int]]:
    """Génère `length` valeurs simplifiées. Renvoie (deck_final, valeurs)."""
    values: list[int] = []
    round_number = 1
    for _ in range(length):
        deck, value, round_number = generate_simple_keystream_value(deck, round_number)
        values.append(value)
    return deck, values
