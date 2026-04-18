"""Les 5 opérations de mélange de l'algorithme Solitaire (Pontifex).

Référence : https://www.schneier.com/academic/solitaire/
"""

from __future__ import annotations

from core.deck import JOKER_A, JOKER_B, card_bridge_value, card_value


def move_joker_a(deck: tuple[int, ...]) -> tuple[int, ...]:
    """Op 1 : descendre le Joker A d'une position.

    Attention : si le Joker A est dernier, il passe en 2e position (pas en 1re).
    """
    cards = list(deck)
    pos = cards.index(JOKER_A)
    cards.pop(pos)
    new_pos = pos + 1
    if new_pos > len(cards):
        new_pos = 1
    cards.insert(new_pos, JOKER_A)
    return tuple(cards)


def move_joker_b(deck: tuple[int, ...]) -> tuple[int, ...]:
    """Op 2 : descendre le Joker B de deux positions (wrap circulaire)."""
    cards = list(deck)
    pos = cards.index(JOKER_B)
    cards.pop(pos)
    new_pos = pos + 2
    if new_pos > len(cards):
        new_pos -= len(cards)
    cards.insert(new_pos, JOKER_B)
    return tuple(cards)


def triple_cut(deck: tuple[int, ...]) -> tuple[int, ...]:
    """Op 3 : intervertir le segment au-dessus du 1er joker
    avec celui en dessous du 2nd. Le milieu ne bouge pas.
    """
    cards = list(deck)
    pos_a = cards.index(JOKER_A)
    pos_b = cards.index(JOKER_B)
    first = min(pos_a, pos_b)
    second = max(pos_a, pos_b)

    top = cards[:first]
    middle = cards[first : second + 1]
    bottom = cards[second + 1 :]

    return tuple(bottom + middle + top)


def count_cut(deck: tuple[int, ...]) -> tuple[int, ...]:
    """Op 4 : coupe selon la valeur Bridge de la dernière carte.

    La dernière carte ne bouge jamais. Si c'est un joker (val 53),
    le paquet reste inchangé.
    """
    cards = list(deck)
    n = card_bridge_value(cards[-1])

    if n >= len(cards) - 1:
        return tuple(cards)

    top = cards[:n]
    middle = cards[n:-1]
    bottom = [cards[-1]]

    return tuple(middle + top + bottom)


def read_output(deck: tuple[int, ...]) -> int | None:
    """Op 5 : lire la carte de sortie sans modifier le paquet.

    Renvoie la valeur (1-26) ou None si c'est un joker.
    """
    n = card_bridge_value(deck[0])

    if n >= len(deck):
        return None

    output_card = deck[n]

    if output_card in (JOKER_A, JOKER_B):
        return None

    return card_value(output_card)


def solitaire_step(deck: tuple[int, ...]) -> tuple[tuple[int, ...], int | None]:
    """Un cycle complet (op 1 à 4 + lecture). Renvoie (deck, valeur | None)."""
    deck = move_joker_a(deck)
    deck = move_joker_b(deck)
    deck = triple_cut(deck)
    deck = count_cut(deck)
    output = read_output(deck)
    return deck, output


def generate_keystream_value(deck: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    """Génère UNE valeur de keystream (1-26), en sautant les jokers."""
    while True:
        deck, output = solitaire_step(deck)
        if output is not None:
            return deck, output
