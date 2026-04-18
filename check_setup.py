"""Smoke test: vérifie que le module test_vectors s'importe correctement."""
from tests.test_vectors import (
    SOLITAIRE_OFFICIAL_VECTORS,
    SOLITAIRE_VALIDATION_VECTORS,
    SOLITAIRE_STANDARD_DECK,
    SOLITAIRE_JOKER_A,
    SOLITAIRE_JOKER_B,
    SOLITAIRE_LETTER_TO_NUMBER,
    SOLITAIRE_NUMBER_TO_LETTER,
    SOLITAIRE_UNKEYED_KEYSTREAM_RAW,
    SOLITAIRE_UNKEYED_KEYSTREAM_VALID,
)

print("=== Module Test Vectors Solitaire OK ===")
print(f"Vecteurs officiels Schneier : {len(SOLITAIRE_OFFICIAL_VECTORS)}")
print(f"Vecteurs de validation      : {len(SOLITAIRE_VALIDATION_VECTORS)}")
print(f"Paquet standard Solitaire   : {len(SOLITAIRE_STANDARD_DECK)} cartes, de {SOLITAIRE_STANDARD_DECK[0]} à {SOLITAIRE_STANDARD_DECK[-1]}")
print(f"Joker A (noir) = {SOLITAIRE_JOKER_A}, Joker B (rouge) = {SOLITAIRE_JOKER_B}")
print(f"A={SOLITAIRE_LETTER_TO_NUMBER['A']}, Z={SOLITAIRE_LETTER_TO_NUMBER['Z']}")
print(f"1={SOLITAIRE_NUMBER_TO_LETTER[1]}, 26={SOLITAIRE_NUMBER_TO_LETTER[26]}")
print()

for test_vector in SOLITAIRE_OFFICIAL_VECTORS:
    print(f"  V{test_vector['id']}: clé={test_vector['key']}, clair={test_vector['plaintext'][:10]}..., chiffré={test_vector['ciphertext']}")

print()
print(f"Flux de clés brut Solitaire (paquet standard) : {SOLITAIRE_UNKEYED_KEYSTREAM_RAW}")
print(f"Flux de clés valide (jokers exclus)          : {SOLITAIRE_UNKEYED_KEYSTREAM_VALID}")
print()
print("=== Toutes les vérifications Solitaire OK ===")
