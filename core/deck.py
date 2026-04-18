"""Paquet de 54 cartes pour l'algorithme Solitaire.

Convention de numérotation (Bridge standard) :
  1-13  Trèfles    14-26  Carreaux
  27-39 Cœurs      40-52  Piques
  53    Joker A    54     Joker B
"""

from __future__ import annotations

JOKER_A: int = 53
JOKER_B: int = 54
DECK_SIZE: int = 54

SUITS: tuple[str, ...] = ("Trèfle", "Carreau", "Cœur", "Pique")
RANKS: tuple[str, ...] = (
    "As", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Valet", "Dame", "Roi",
)


def create_deck() -> tuple[int, ...]:
    """Paquet neuf dans l'ordre Bridge (1 à 54)."""
    return tuple(range(1, DECK_SIZE + 1))


def card_to_string(n: int) -> str:
    """Nom lisible d'une carte, ex: 'As de Trèfle'."""
    if n == JOKER_A:
        return "Joker Noir (A)"
    if n == JOKER_B:
        return "Joker Rouge (B)"
    if not 1 <= n <= 52:
        raise ValueError(f"Numéro de carte invalide : {n}")
    suit_index = (n - 1) // 13
    rank_index = (n - 1) % 13
    return f"{RANKS[rank_index]} de {SUITS[suit_index]}"


def card_value(n: int) -> int:
    """Valeur de chiffrement (1-26). Les cœurs/piques sont ramenés mod 26."""
    # Trèfle/Carreau : directement 1-26
    # Cœur/Pique : on soustrait 26 pour retomber dans 1-26
    if n in (JOKER_A, JOKER_B):
        return 53
    if not 1 <= n <= 52:
        raise ValueError(f"Numéro de carte invalide : {n}")
    return n if n <= 26 else n - 26


def card_bridge_value(n: int) -> int:
    """Valeur Bridge (1-53), utilisée pour les opérations de coupe."""
    if n in (JOKER_A, JOKER_B):
        return 53
    if not 1 <= n <= 52:
        raise ValueError(f"Numéro de carte invalide : {n}")
    return n


def find_card(deck: tuple[int, ...], card: int) -> int:
    """Position (0-based) d'une carte dans le paquet."""
    return deck.index(card)


def display_deck(deck: tuple[int, ...]) -> str:
    """Représentation texte du paquet, une ligne par carte."""
    lines = []
    for i, card in enumerate(deck):
        lines.append(f"{i + 1:2d}. {card_to_string(card)} ({card})")
    return "\n".join(lines)
