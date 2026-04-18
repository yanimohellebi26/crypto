"""
Vecteurs de test officiels de Bruce Schneier pour l'algorithme Solitaire.

Source : https://www.schneier.com/wp-content/uploads/2015/12/sol-test.txt

Ces vecteurs sont la référence absolue. Si l'implémentation ne les reproduit
pas exactement, il y a un bug.
"""

# Vecteurs de test officiels de Schneier (les 3 du plan de base)

SOLITAIRE_OFFICIAL_VECTORS = [
    # Vecteur 1 : paquet non clé (standard 1..52, JokerA=53, JokerB=54)
    {
        "id": 1,
        "key": None,
        "plaintext": "AAAAAAAAAAAAAAA",
        "keystream_raw": [4, 49, 10, 53, 24, 8, 51, 44, 6, 4, 33, 20, 39, 19, 34, 42],
        "ciphertext": "EXKYIZSGEH",
        "description": "Paquet non clé (standard), 10 premières lettres",
    },
    # Vecteur 2 : clé "FOO"
    {
        "id": 2,
        "key": "FOO",
        "plaintext": "AAAAAAAAAAAAAAA",
        "keystream_raw": [8, 19, 7, 25, 20, 53, 9, 8, 22, 32, 43, 5, 26, 17, 53, 38, 48],
        "ciphertext": "ITHZUJIWGRFARMW",
        "description": "Clé FOO, 15 lettres",
    },
    # Vecteur 3 : clé "CRYPTONOMICON"
    {
        "id": 3,
        "key": "CRYPTONOMICON",
        "plaintext": "SOLITAIREX",
        "ciphertext": "KIRAKSFJAN",
        "description": "Clé CRYPTONOMICON, message SOLITAIRE (+ X padding)",
    },
]
# Vecteurs étendus de validation (issus de sol-test.txt)

SOLITAIRE_VALIDATION_VECTORS = [
    {"key": "f",              "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "XYIUQBMHKKJBEGY"},
    {"key": "fo",             "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "TUJYMBERLGXNDIW"},
    {"key": "foo",            "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "ITHZUJIWGRFARMW"},
    {"key": "a",              "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "XODALGSCULIQNSC"},
    {"key": "aa",             "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "OHGWMXXCAIMCIQP"},
    {"key": "aaa",            "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "DCSQYHBQZNGDRUT"},
    {"key": "b",              "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "XQEEMOITLZVDSQS"},
    {"key": "bc",             "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "QNGRKQIHCLGWSCE"},
    {"key": "bcd",            "plaintext": "AAAAAAAAAAAAAAA", "ciphertext": "FMUBYBMAXHNQXCJ"},
    {
        "key": "cryptonomicon",
        "plaintext": "AAAAAAAAAAAAAAAAAAAAAAAAA",
        "ciphertext": "SUGSRSXSWQRMXOHIPBFPXARYQ",
    },
]
# Flux de clés attendu pour le paquet standard non clé (premier cycle détaillé)

# Les 11 premières sorties brutes (y compris les jokers sautés) du paquet Solitaire standard.
# Le 53 est un joker qu'on doit sauter (opération 5 recommence la boucle).
SOLITAIRE_UNKEYED_KEYSTREAM_RAW = [4, 49, 10, 53, 24, 8, 51, 44, 6, 4, 33]

# Les 10 premières sorties valides (après suppression des jokers réitérés).
SOLITAIRE_UNKEYED_KEYSTREAM_VALID = [4, 49, 10, 24, 8, 51, 44, 6, 4, 33]

# Conversion en lettres (valeur Bridge > 26 → soustraire 26 pour obtenir 1-26).
# 4→D, 49→23→W, 10→J, 24→X, 8→H, 51→25→Y, 44→18→R, 6→F, 4→D, 33→7→G
SOLITAIRE_UNKEYED_KEYSTREAM_LETTERS = ["D", "W", "J", "X", "H", "Y", "R", "F", "D", "G"]
# Constantes de l'algorithme Solitaire

SOLITAIRE_JOKER_A = 53  # Joker noir/petit (valeur)
SOLITAIRE_JOKER_B = 54  # Joker rouge/grand (valeur)
SOLITAIRE_DECK_SIZE = 54  # Taille standard du paquet (52 cartes + 2 jokers)

# Paquet Solitaire dans l'ordre standard Bridge (non clé)
# Trèfle 1-13, Carreau 14-26, Cœur 27-39, Pique 40-52, Joker A (53), Joker B (54)
SOLITAIRE_STANDARD_DECK = tuple(range(1, SOLITAIRE_DECK_SIZE + 1))

# Tables de conversion lettres ↔ nombres

# Conversion lettre → nombre pour le chiffrement (A=1, B=2, ..., Z=26)
SOLITAIRE_LETTER_TO_NUMBER = {chr(64 + i): i for i in range(1, 27)}  # {'A': 1, 'B': 2, ..., 'Z': 26}

# Conversion nombre → lettre pour le chiffrement (1=A, 2=B, ..., 26=Z)
SOLITAIRE_NUMBER_TO_LETTER = {i: chr(64 + i) for i in range(1, 27)}  # {1: 'A', 2: 'B', ..., 26: 'Z'}
# Noms des cartes (pour l'affichage)SUITS = ["Trèfle", "Carreau", "Cœur", "Pique"]
SUIT_SYMBOLS = {"Trèfle": "♣", "Carreau": "♦", "Cœur": "♥", "Pique": "♠"}
RANKS = ["As", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Valet", "Dame", "Roi"]
# Alias rétro-compatibles (anciennes nomenclatures)# Maintenir les anciens noms pour la compatibilité avec les tests hérités
SCHNEIER_VECTORS = SOLITAIRE_OFFICIAL_VECTORS
EXTENDED_VECTORS = SOLITAIRE_VALIDATION_VECTORS
STANDARD_DECK = SOLITAIRE_STANDARD_DECK
JOKER_A = SOLITAIRE_JOKER_A
JOKER_B = SOLITAIRE_JOKER_B
DECK_SIZE = SOLITAIRE_DECK_SIZE
UNKEYED_KEYSTREAM_RAW = SOLITAIRE_UNKEYED_KEYSTREAM_RAW
UNKEYED_KEYSTREAM_VALID = SOLITAIRE_UNKEYED_KEYSTREAM_VALID
UNKEYED_KEYSTREAM_LETTERS = SOLITAIRE_UNKEYED_KEYSTREAM_LETTERS
LETTER_TO_NUMBER = SOLITAIRE_LETTER_TO_NUMBER
NUMBER_TO_LETTER = SOLITAIRE_NUMBER_TO_LETTER
