"""Tests des vecteurs officiels de Bruce Schneier.

Source : https://www.schneier.com/academic/solitaire/
Vecteurs : https://www.schneier.com/wp-content/uploads/2015/12/sol-test.txt
"""

import pytest

from core.deck import create_deck
from core.encryption import decrypt, encrypt
from core.solitaire import generate_keystream_value
from tests.test_vectors import (
    SOLITAIRE_UNKEYED_KEYSTREAM_LETTERS,
    SOLITAIRE_VALIDATION_VECTORS,
)


class TestUnkeyedKeystream:
    """Vérifie le flux de clés du paquet standard non clé."""

    def test_first_ten_keystream_letters(self) -> None:
        """Les 10 premières lettres valides correspondent à D,W,J,X,H,Y,R,F,D,G."""
        deck = create_deck()
        for i, expected_letter in enumerate(SOLITAIRE_UNKEYED_KEYSTREAM_LETTERS):
            deck, value = generate_keystream_value(deck)
            actual_letter = chr(value - 1 + ord("A"))
            assert actual_letter == expected_letter, (
                f"Position {i}: attendu {expected_letter}, obtenu {actual_letter}"
            )


class TestOfficialVectors:
    """Les 3 vecteurs officiels de Schneier."""

    def test_vector_1_unkeyed_deck(self) -> None:
        """'AAAAAAAAAA' → 'EXKYIZSGEH' avec paquet standard."""
        ciphertext, _ = encrypt("AAAAAAAAAA")
        assert ciphertext == "EXKYIZSGEH"

    def test_vector_2_key_foo(self) -> None:
        """Clé 'FOO', 'AAAAAAAAAAAAAAA' → 'ITHZUJIWGRFARMW'."""
        ciphertext, _ = encrypt("AAAAAAAAAAAAAAA", key="FOO")
        assert ciphertext == "ITHZUJIWGRFARMW"

    def test_vector_3_key_cryptonomicon(self) -> None:
        """Clé 'CRYPTONOMICON', 'SOLITAIREX' → 'KIRAKSFJAN'."""
        ciphertext, _ = encrypt("SOLITAIREX", key="CRYPTONOMICON")
        assert ciphertext == "KIRAKSFJAN"

    def test_vector_1_decrypt(self) -> None:
        plaintext, _ = decrypt("EXKYIZSGEH")
        assert plaintext == "AAAAAAAAAA"

    def test_vector_2_decrypt(self) -> None:
        plaintext, _ = decrypt("ITHZUJIWGRFARMW", key="FOO")
        assert plaintext == "AAAAAAAAAAAAAAA"

    def test_vector_3_decrypt(self) -> None:
        plaintext, _ = decrypt("KIRAKSFJAN", key="CRYPTONOMICON")
        assert plaintext == "SOLITAIREX"


class TestValidationVectors:
    """Vecteurs étendus de validation (sol-test.txt)."""

    @pytest.mark.parametrize(
        "vector",
        SOLITAIRE_VALIDATION_VECTORS,
        ids=[v["key"] for v in SOLITAIRE_VALIDATION_VECTORS],
    )
    def test_encrypt(self, vector: dict) -> None:
        ciphertext, _ = encrypt(vector["plaintext"], key=vector["key"])
        assert ciphertext == vector["ciphertext"]

    @pytest.mark.parametrize(
        "vector",
        SOLITAIRE_VALIDATION_VECTORS,
        ids=[v["key"] for v in SOLITAIRE_VALIDATION_VECTORS],
    )
    def test_decrypt(self, vector: dict) -> None:
        plaintext, _ = decrypt(vector["ciphertext"], key=vector["key"])
        assert plaintext == vector["plaintext"]
