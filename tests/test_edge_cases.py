"""Tests des cas limites pour l'algorithme Solitaire."""

import pytest

from core.deck import DECK_SIZE, create_deck
from core.encryption import decrypt, encrypt
from core.solitaire import solitaire_step


class TestEdgeCases:
    def test_empty_message(self) -> None:
        with pytest.raises(ValueError, match="aucune lettre"):
            encrypt("")

    def test_all_spaces(self) -> None:
        with pytest.raises(ValueError, match="aucune lettre"):
            encrypt("     ")

    def test_all_same_letters(self) -> None:
        """100 fois la même lettre → chiffre/déchiffre correctement."""
        message = "A" * 100
        ciphertext, _ = encrypt(message, key="TESTKEY")
        plaintext, _ = decrypt(ciphertext, key="TESTKEY")
        assert plaintext == message

    def test_message_state_persists(self) -> None:
        """Chiffrer msg1 puis msg2 : le paquet évolue entre les deux."""
        _, deck_after_msg1 = encrypt("HELLO")
        ct_with_state, _ = encrypt("WORLD", deck=deck_after_msg1)
        ct_fresh, _ = encrypt("WORLD")
        assert ct_with_state != ct_fresh

    def test_deck_always_54_cards(self) -> None:
        """Après 50 cycles, toujours 54 cartes."""
        deck = create_deck()
        for _ in range(50):
            deck, _ = solitaire_step(deck)
            assert len(deck) == DECK_SIZE

    def test_no_duplicate_cards(self) -> None:
        """Après 50 cycles, aucun doublon dans le paquet."""
        deck = create_deck()
        for _ in range(50):
            deck, _ = solitaire_step(deck)
            assert len(set(deck)) == DECK_SIZE

    def test_very_long_message(self) -> None:
        """Message de 1000+ caractères."""
        message = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 40  # 1040 lettres
        ciphertext, _ = encrypt(message, key="LONGKEY")
        plaintext, _ = decrypt(ciphertext, key="LONGKEY")
        assert plaintext == message

    def test_decrypt_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            decrypt("")

    def test_key_case_insensitive(self) -> None:
        """Le keying est insensible à la casse."""
        ct1, _ = encrypt("HELLO", key="foo")
        ct2, _ = encrypt("HELLO", key="FOO")
        assert ct1 == ct2

    def test_special_characters_only_raises(self) -> None:
        with pytest.raises(ValueError, match="aucune lettre"):
            encrypt("!@#$%^&*()")

    def test_french_sentence_roundtrip(self) -> None:
        """Phrase française avec accents → roundtrip correct."""
        message = "Le héros est allé à l'école"
        ciphertext, _ = encrypt(message, key="CLEF")
        plaintext, _ = decrypt(ciphertext, key="CLEF")
        assert plaintext == "LEHEROSESTALLEALECOLE"
