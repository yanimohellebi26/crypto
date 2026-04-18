"""Tests unitaires pour core/encryption.py."""

import pytest

from core.encryption import (
    decrypt,
    encrypt,
    normalize_text,
    numbers_to_text,
    text_to_numbers,
)


class TestNormalizeText:
    def test_uppercase(self) -> None:
        assert normalize_text("hello") == "HELLO"

    def test_remove_spaces(self) -> None:
        assert normalize_text("hello world") == "HELLOWORLD"

    def test_remove_punctuation(self) -> None:
        assert normalize_text("hello, world!") == "HELLOWORLD"

    def test_remove_digits(self) -> None:
        assert normalize_text("abc123def") == "ABCDEF"

    def test_french_accents(self) -> None:
        assert normalize_text("éàùçî") == "EAUCI"

    def test_mixed_accents_and_punctuation(self) -> None:
        assert normalize_text("L'épée du héros !") == "LEPEEDUHEROS"

    def test_empty_string(self) -> None:
        assert normalize_text("") == ""

    def test_only_non_alpha(self) -> None:
        assert normalize_text("123 !@#") == ""

    def test_ligature_oe(self) -> None:
        assert normalize_text("cœur") == "COEUR"

    def test_ligature_ae(self) -> None:
        assert normalize_text("Ægypte") == "AEGYPTE"

    def test_n_tilde(self) -> None:
        assert normalize_text("señor") == "SENOR"


class TestTextToNumbers:
    def test_single_letter_a(self) -> None:
        assert text_to_numbers("A") == [1]

    def test_single_letter_z(self) -> None:
        assert text_to_numbers("Z") == [26]

    def test_word(self) -> None:
        assert text_to_numbers("ABC") == [1, 2, 3]


class TestNumbersToText:
    def test_single_number(self) -> None:
        assert numbers_to_text([1]) == "A"
        assert numbers_to_text([26]) == "Z"

    def test_multiple_numbers(self) -> None:
        assert numbers_to_text([1, 2, 3]) == "ABC"


class TestEncryptDecrypt:
    def test_encrypt_single_letter(self) -> None:
        ciphertext, _ = encrypt("A")
        assert len(ciphertext) == 1
        assert ciphertext.isalpha()

    def test_decrypt_single_letter(self) -> None:
        ciphertext, _ = encrypt("A")
        plaintext, _ = decrypt(ciphertext)
        assert plaintext == "A"

    def test_roundtrip_short(self) -> None:
        message = "HELLO"
        ciphertext, _ = encrypt(message)
        plaintext, _ = decrypt(ciphertext)
        assert plaintext == message

    def test_roundtrip_with_key(self) -> None:
        message = "SECRETMESSAGE"
        key = "TESTKEY"
        ciphertext, _ = encrypt(message, key=key)
        plaintext, _ = decrypt(ciphertext, key=key)
        assert plaintext == message

    def test_roundtrip_long(self) -> None:
        message = "A" * 200
        ciphertext, _ = encrypt(message, key="LONGKEY")
        plaintext, _ = decrypt(ciphertext, key="LONGKEY")
        assert plaintext == message

    def test_roundtrip_with_accents(self) -> None:
        ciphertext, _ = encrypt("Héllo Wörld", key="KEY")
        plaintext, _ = decrypt(ciphertext, key="KEY")
        assert plaintext == "HELLOWORLD"

    def test_empty_message_raises(self) -> None:
        with pytest.raises(ValueError, match="aucune lettre"):
            encrypt("")

    def test_only_digits_raises(self) -> None:
        with pytest.raises(ValueError, match="aucune lettre"):
            encrypt("12345")

    def test_different_keys_different_output(self) -> None:
        ct1, _ = encrypt("HELLO", key="ALPHA")
        ct2, _ = encrypt("HELLO", key="BRAVO")
        assert ct1 != ct2

    def test_deck_state_returned(self) -> None:
        _, deck = encrypt("HELLO")
        assert len(deck) == 54
        assert len(set(deck)) == 54
