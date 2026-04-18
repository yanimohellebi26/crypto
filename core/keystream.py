"""Génération du flux de clés et keying du paquet.

Le keying utilise la méthode #3 de Schneier : pour chaque lettre du mot
de passe, on effectue les opérations 1-4 puis une coupe supplémentaire.
"""

from __future__ import annotations

from core.deck import create_deck
from core.solitaire import (
    count_cut,
    generate_keystream_value,
    move_joker_a,
    move_joker_b,
    triple_cut,
)


def key_deck(passphrase: str) -> tuple[int, ...]:
    """Initialise le paquet à partir d'un mot de passe (Schneier méthode #3)."""
    deck = create_deck()
    passphrase = passphrase.upper()

    for char in passphrase:
        if not char.isalpha():
            continue

        deck = move_joker_a(deck)
        deck = move_joker_b(deck)
        deck = triple_cut(deck)
        deck = count_cut(deck)

        letter_value = ord(char) - ord("A") + 1
        cards = list(deck)
        top = cards[:letter_value]
        middle = cards[letter_value:-1]
        bottom = [cards[-1]]
        deck = tuple(middle + top + bottom)

    return deck


def generate_keystream(
    deck: tuple[int, ...], length: int,
) -> tuple[tuple[int, ...], list[int]]:
    """Génère `length` valeurs de keystream. Renvoie (deck_final, valeurs)."""
    values: list[int] = []
    for _ in range(length):
        deck, value = generate_keystream_value(deck)
        values.append(value)
    return deck, values
