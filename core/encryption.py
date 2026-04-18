"""Chiffrement et déchiffrement Solitaire.

Prétraitement du texte :
  - Suppression des accents, ponctuation, espaces
  - Conversion en majuscules (A=1, B=2, ..., Z=26)

Chiffrement : (clair + flux) mod 26, où 0 vaut Z
Déchiffrement : (chiffré - flux) mod 26, avec ajustement si <= 0
"""

from __future__ import annotations

import unicodedata

from core.deck import create_deck
from core.keystream import generate_keystream, key_deck


def normalize_text(text: str) -> str:
    """Enlève les accents et caractères non-alpha, passe en majuscules."""
    text = text.replace("œ", "oe").replace("Œ", "OE")
    text = text.replace("æ", "ae").replace("Æ", "AE")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = "".join(c for c in text if c.isalpha())
    return text.upper()


def text_to_numbers(text: str) -> list[int]:
    """'ABC' -> [1, 2, 3]"""
    return [ord(c) - ord("A") + 1 for c in text]


def numbers_to_text(numbers: list[int]) -> str:
    """[1, 2, 3] -> 'ABC'"""
    return "".join(chr(n - 1 + ord("A")) for n in numbers)


def encrypt(
    plaintext: str,
    key: str | None = None,
    deck: tuple[int, ...] | None = None,
) -> tuple[str, tuple[int, ...]]:
    """Chiffre un message. Renvoie (texte_chiffré, paquet_final).

    On peut fournir soit une clé (passphrase), soit un deck déjà initialisé.
    Sans rien, le paquet standard est utilisé.
    """
    normalized = normalize_text(plaintext)
    if not normalized:
        raise ValueError("Le message ne contient aucune lettre à chiffrer.")

    plain_numbers = text_to_numbers(normalized)

    if key is not None:
        current_deck = key_deck(key)
    elif deck is not None:
        current_deck = deck
    else:
        current_deck = create_deck()

    current_deck, keystream = generate_keystream(current_deck, len(plain_numbers))

    cipher_numbers: list[int] = []
    for p, k in zip(plain_numbers, keystream):
        c = (p + k) % 26
        if c == 0:
            c = 26
        cipher_numbers.append(c)

    return numbers_to_text(cipher_numbers), current_deck


def decrypt(
    ciphertext: str,
    key: str | None = None,
    deck: tuple[int, ...] | None = None,
) -> tuple[str, tuple[int, ...]]:
    """Déchiffre un message. Renvoie (texte_clair, paquet_final)."""
    normalized = normalize_text(ciphertext)
    if not normalized:
        raise ValueError("Le message chiffré ne contient aucune lettre.")

    cipher_numbers = text_to_numbers(normalized)

    if key is not None:
        current_deck = key_deck(key)
    elif deck is not None:
        current_deck = deck
    else:
        current_deck = create_deck()

    current_deck, keystream = generate_keystream(current_deck, len(cipher_numbers))

    plain_numbers: list[int] = []
    for c, k in zip(cipher_numbers, keystream):
        p = c - k
        if p <= 0:
            p += 26
        plain_numbers.append(p)

    return numbers_to_text(plain_numbers), current_deck
