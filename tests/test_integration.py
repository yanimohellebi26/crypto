"""Tests d'intégration pour l'algorithme Solitaire (Phase 5.2).

Couvre :
- Chiffrement multi-messages successifs avec persistance d'état
- Keying par mot de passe + chiffrement + déchiffrement complet
- Version simplifiée : chiffrement + déchiffrement
"""

from __future__ import annotations

import pytest

from core.deck import create_deck
from core.encryption import decrypt, encrypt, normalize_text
from core.keystream import generate_keystream, key_deck
from core.solitaire_simple import generate_simple_keystream


# 5.2.1 : Persistance d'état multi-messages


class TestMultiMessageStatePersistence:
    """L'état du paquet persiste entre les messages successifs."""

    def test_two_messages_sequential_roundtrip(self) -> None:
        """Chiffrer deux messages en séquence, déchiffrer en séquence → mêmes clairs."""
        msg1 = "HELLO"
        msg2 = "WORLD"

        # Chiffrement en séquence (même paquet)
        ct1, deck_after_1 = encrypt(msg1)
        ct2, _ = encrypt(msg2, deck=deck_after_1)

        # Déchiffrement en séquence (même paquet de départ)
        pt1, deck_after_dec1 = decrypt(ct1)
        pt2, _ = decrypt(ct2, deck=deck_after_dec1)

        assert pt1 == msg1
        assert pt2 == msg2

    def test_three_messages_sequential_roundtrip(self) -> None:
        """Chaîne de trois messages : chiffrement puis déchiffrement séquentiels."""
        messages = ["ATTACK", "AT", "DAWN"]
        key = "SECRETKEY"

        # Chiffrement séquentiel
        deck = key_deck(key)
        ciphertexts: list[str] = []
        for msg in messages:
            ct, deck = encrypt(msg, deck=deck)
            ciphertexts.append(ct)

        # Déchiffrement séquentiel avec le même paquet de départ
        deck = key_deck(key)
        for msg, ct in zip(messages, ciphertexts):
            pt, deck = decrypt(ct, deck=deck)
            assert pt == msg

    def test_state_differs_from_fresh_deck(self) -> None:
        """Le paquet après msg1 produit un chiffrement différent d'un paquet neuf."""
        _, deck_after_msg1 = encrypt("FIRSTMESSAGE")
        ct_with_state, _ = encrypt("SECOND", deck=deck_after_msg1)
        ct_fresh, _ = encrypt("SECOND")
        assert ct_with_state != ct_fresh

    def test_keyed_deck_sequential(self) -> None:
        """Persistance d'état avec deck initialisé par passphrase."""
        passphrase = "SOLITAIRE"
        msg_a = "ALPHA"
        msg_b = "BRAVO"

        deck_init = key_deck(passphrase)
        ct_a, deck_mid = encrypt(msg_a, deck=deck_init)
        ct_b, _ = encrypt(msg_b, deck=deck_mid)

        deck_init = key_deck(passphrase)
        pt_a, deck_mid = decrypt(ct_a, deck=deck_init)
        pt_b, _ = decrypt(ct_b, deck=deck_mid)

        assert pt_a == msg_a
        assert pt_b == msg_b

    def test_different_starting_states_independent(self) -> None:
        """Deux sessions indépendantes avec la même clé → mêmes résultats."""
        key = "INDEPENDENT"
        msg = "CONSISTENT"

        ct_session1, _ = encrypt(msg, key=key)
        ct_session2, _ = encrypt(msg, key=key)

        assert ct_session1 == ct_session2

    def test_keystream_is_stateful(self) -> None:
        """Le keystream avance : deux appels successifs produisent des valeurs différentes."""
        deck = create_deck()
        deck, ks1 = generate_keystream(deck, 10)
        _, ks2 = generate_keystream(deck, 10)
        assert ks1 != ks2



class TestKeyingEncryptDecryptRoundtrip:
    """Vecteurs officiels et roundtrips complets avec mot de passe."""

    def test_schneier_vector_1_unkeyed(self) -> None:
        """Vecteur 1 : paquet standard, AAAAAAAAAA → EXKYIZSGEH."""
        ciphertext, _ = encrypt("AAAAAAAAAA")
        assert ciphertext == "EXKYIZSGEH"

    def test_schneier_vector_2_foo(self) -> None:
        """Vecteur 2 : clé FOO, AAAAAAAAAAAAAAA → ITHZUJIWGRFARMW."""
        ciphertext, _ = encrypt("AAAAAAAAAAAAAAA", key="FOO")
        assert ciphertext == "ITHZUJIWGRFARMW"

    def test_schneier_vector_3_cryptonomicon(self) -> None:
        """Vecteur 3 : clé CRYPTONOMICON, SOLITAIREX → KIRAKSFJAN."""
        ciphertext, _ = encrypt("SOLITAIREX", key="CRYPTONOMICON")
        assert ciphertext == "KIRAKSFJAN"

    def test_roundtrip_with_passphrase(self) -> None:
        """Keying passphrase → chiffrement → déchiffrement → clair identique."""
        message = "THECRYPTONOMICON"
        key = "PONTIFEX"
        ciphertext, _ = encrypt(message, key=key)
        plaintext, _ = decrypt(ciphertext, key=key)
        assert plaintext == message

    def test_roundtrip_with_french_message(self) -> None:
        """Message français normalisé → roundtrip correct."""
        message = "Bonjour le monde !"
        normalized = normalize_text(message)  # "BONJOURLEMONDE"
        key = "CLEF"
        ciphertext, _ = encrypt(message, key=key)
        plaintext, _ = decrypt(ciphertext, key=key)
        assert plaintext == normalized

    def test_keying_deterministic(self) -> None:
        """Même mot de passe → même paquet de départ → même chiffrement."""
        message = "DETERMINISTIC"
        key = "PASSPHRASE"
        ct1, _ = encrypt(message, key=key)
        ct2, _ = encrypt(message, key=key)
        assert ct1 == ct2

    def test_key_affects_output(self) -> None:
        """Deux clés différentes produisent des chiffrés différents."""
        message = "HELLO"
        ct_a, _ = encrypt(message, key="ALPHA")
        ct_b, _ = encrypt(message, key="BETA")
        assert ct_a != ct_b

    def test_keying_skips_non_alpha(self) -> None:
        """Les caractères non-alphabétiques dans la passphrase sont ignorés."""
        message = "TEST"
        ct_clean, _ = encrypt(message, key="MYKEY")
        ct_dirty, _ = encrypt(message, key="MY KEY 123!")
        assert ct_clean == ct_dirty

    def test_key_case_insensitive(self) -> None:
        """La clé est insensible à la casse."""
        message = "CASETEST"
        ct_lower, _ = encrypt(message, key="mypassword")
        ct_upper, _ = encrypt(message, key="MYPASSWORD")
        assert ct_lower == ct_upper

    def test_keyed_deck_not_standard(self) -> None:
        """Le paquet après keying est différent du paquet standard."""
        keyed = key_deck("ANYKEY")
        standard = create_deck()
        assert keyed != standard

    def test_roundtrip_200_chars(self) -> None:
        """Message de 200 caractères : roundtrip sans perte."""
        message = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 8  # 208 → tronqué à 200 pour lisibilité
        message = message[:200]
        key = "LONGPASSPHRASE"
        ct, _ = encrypt(message, key=key)
        pt, _ = decrypt(ct, key=key)
        assert pt == message


class TestSimpleVersionRoundtrip:
    """Chiffrement et déchiffrement avec la version simplifiée."""

    def _simple_encrypt(self, plaintext: str) -> tuple[str, tuple[int, ...]]:
        """Chiffrement simple : utilise generate_simple_keystream."""
        from core.encryption import normalize_text, numbers_to_text, text_to_numbers

        normalized = normalize_text(plaintext)
        if not normalized:
            raise ValueError("Le message ne contient aucune lettre à chiffrer.")

        plain_numbers = text_to_numbers(normalized)
        deck = create_deck()
        deck, keystream = generate_simple_keystream(deck, len(plain_numbers))

        cipher_numbers: list[int] = []
        for p, k in zip(plain_numbers, keystream):
            c = (p + k) % 26
            if c == 0:
                c = 26
            cipher_numbers.append(c)

        return numbers_to_text(cipher_numbers), deck

    def _simple_decrypt(
        self, ciphertext: str, deck: tuple[int, ...] | None = None,
    ) -> str:
        """Déchiffrement simple : utilise generate_simple_keystream."""
        from core.encryption import normalize_text, numbers_to_text, text_to_numbers

        normalized = normalize_text(ciphertext)
        cipher_numbers = text_to_numbers(normalized)
        start_deck = create_deck() if deck is None else deck
        _, keystream = generate_simple_keystream(start_deck, len(cipher_numbers))

        plain_numbers: list[int] = []
        for c, k in zip(cipher_numbers, keystream):
            p = c - k
            if p <= 0:
                p += 26
            plain_numbers.append(p)

        return numbers_to_text(plain_numbers)

    def test_simple_roundtrip_short(self) -> None:
        """Version simplifiée : chiffre et déchiffre un message court."""
        message = "HELLO"
        ciphertext, _ = self._simple_encrypt(message)
        plaintext = self._simple_decrypt(ciphertext)
        assert plaintext == message

    def test_simple_roundtrip_alphabet(self) -> None:
        """Version simplifiée : roundtrip avec l'alphabet complet."""
        message = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ciphertext, _ = self._simple_encrypt(message)
        plaintext = self._simple_decrypt(ciphertext)
        assert plaintext == message

    def test_simple_differs_from_full(self) -> None:
        """La version simplifiée produit un résultat différent du Solitaire complet."""
        message = "HELLO"
        ct_full, _ = encrypt(message)
        ct_simple, _ = self._simple_encrypt(message)
        assert ct_full != ct_simple

    def test_simple_keystream_length(self) -> None:
        """Le keystream simplifié produit exactement n valeurs."""
        deck = create_deck()
        _, keystream = generate_simple_keystream(deck, 10)
        assert len(keystream) == 10

    def test_simple_keystream_range(self) -> None:
        """Toutes les valeurs du keystream simplifié sont entre 1 et 52."""
        deck = create_deck()
        _, keystream = generate_simple_keystream(deck, 100)
        assert all(1 <= v <= 52 for v in keystream)

    def test_simple_deterministic(self) -> None:
        """La version simplifiée est déterministe (même paquet → même keystream)."""
        deck = create_deck()
        _, ks1 = generate_simple_keystream(deck, 20)
        _, ks2 = generate_simple_keystream(deck, 20)
        assert ks1 == ks2
