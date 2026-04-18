"""Démonstration de l'attaque par réutilisation de clé sur Solitaire.

Montre que C1 - C2 = M1 - M2 (mod 26) quand on réutilise la même clé.
Inclut l'attaque par crib-dragging.
"""

from __future__ import annotations

from core.encryption import encrypt, normalize_text
from core.keystream import generate_keystream, key_deck


def demo_key_reuse(
    message1: str,
    message2: str,
    key: str | None = None,
) -> dict:
    """Chiffre deux messages avec la même clé et vérifie la fuite d'info."""
    m1_norm = normalize_text(message1)
    m2_norm = normalize_text(message2)
    min_len = min(len(m1_norm), len(m2_norm))
    m1_norm = m1_norm[:min_len]
    m2_norm = m2_norm[:min_len]

    if min_len == 0:
        return {"error": "Les messages doivent contenir au moins une lettre commune"}

    # Chiffrer les deux messages avec la même clé
    c1, _ = encrypt(m1_norm, key=key)
    c2, _ = encrypt(m2_norm, key=key)

    # Différence des chiffrés : C1 - C2 mod 26
    xor_diff = []
    for a, b in zip(c1, c2):
        val_a = ord(a) - ord("A") + 1
        val_b = ord(b) - ord("A") + 1
        diff = (val_a - val_b) % 26
        xor_diff.append(diff)

    # Différence attendue des clairs : M1 - M2 mod 26
    xor_expected = []
    for a, b in zip(m1_norm, m2_norm):
        val_a = ord(a) - ord("A") + 1
        val_b = ord(b) - ord("A") + 1
        diff = (val_a - val_b) % 26
        xor_expected.append(diff)

    # Vérifier la fuite
    leak_ok = xor_diff == xor_expected
    leak_positions = [i for i, (a, b) in enumerate(zip(xor_diff, xor_expected)) if a == b]

    return {
        "m1": m1_norm,
        "m2": m2_norm,
        "c1": c1,
        "c2": c2,
        "xor_diff": xor_diff,
        "xor_expected": xor_expected,
        "leak_ok": leak_ok,
        "leak_positions": leak_positions,
        "length": min_len,
    }


def crib_drag_attack(
    c1: str,
    c2: str,
    crib: str,
    language: str = "fr",
) -> list[dict]:
    """Essaie le mot 'crib' à chaque position pour déduire M2."""
    crib_norm = normalize_text(crib)
    crib_vals = [ord(c) - ord("A") + 1 for c in crib_norm]

    # Calculer la différence des chiffrés
    diff = []
    for a, b in zip(c1, c2):
        val_a = ord(a) - ord("A") + 1
        val_b = ord(b) - ord("A") + 1
        diff.append((val_a - val_b) % 26)

    candidates = []
    crib_len = len(crib_norm)

    for pos in range(len(diff) - crib_len + 1):
        # Si M1[pos:pos+crib_len] = crib, alors M2[pos:pos+crib_len] = crib - diff mod 26
        m2_fragment_vals = [(crib_vals[i] - diff[pos + i]) % 26 for i in range(crib_len)]
        m2_fragment = "".join(
            chr(ord("A") + v - 1) if v > 0 else "Z" for v in m2_fragment_vals
        )

        # Score heuristique : proportion de voyelles + lettres courantes
        score = _french_letter_score(m2_fragment) if language == "fr" else _english_letter_score(m2_fragment)

        candidates.append({
            "position": pos,
            "crib": crib_norm,
            "m2_fragment": m2_fragment,
            "score": score,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


# Heuristiques de fréquence des lettres

_FR_FREQ = {
    "E": 14.7, "A": 7.6, "I": 7.5, "S": 7.9, "N": 7.1,
    "T": 7.2, "R": 6.6, "O": 5.8, "U": 6.3, "L": 5.5,
    "D": 3.7, "C": 3.3, "M": 3.0, "P": 2.9, "V": 1.6,
}
_EN_FREQ = {
    "E": 12.7, "T": 9.1, "A": 8.2, "O": 7.5, "I": 7.0,
    "N": 6.7, "S": 6.3, "H": 6.1, "R": 6.0, "D": 4.3,
    "L": 4.0, "C": 2.8, "U": 2.8, "M": 2.4, "W": 2.4,
}


def _french_letter_score(text: str) -> float:
    return sum(_FR_FREQ.get(c, 0.1) for c in text) / max(len(text), 1)


def _english_letter_score(text: str) -> float:
    return sum(_EN_FREQ.get(c, 0.1) for c in text) / max(len(text), 1)


def compute_security_metrics() -> dict:
    """Métriques de sécurité théoriques de Solitaire (espace de clés, entropie, etc.)."""
    import math

    n = 54  # nombre de cartes
    factorial_54 = math.factorial(n)
    entropy_bits = math.log2(factorial_54)
    aes128_bits = 128
    aes256_bits = 256

    return {
        "key_space": factorial_54,
        "key_space_str": f"54! ≈ 2.31 × 10^71",
        "entropy_bits": entropy_bits,
        "aes128_bits": aes128_bits,
        "aes256_bits": aes256_bits,
        "vs_aes128": entropy_bits - aes128_bits,
        "vs_aes256": entropy_bits - aes256_bits,
        "brute_force_years": _brute_force_years(factorial_54),
        "crowley_bias": 1 / 22.5,
        "uniform_expected": 1 / 26,
    }


def _brute_force_years(key_space: int) -> str:
    """Estime le temps de brute force en années (à 10^15 essais/seconde)."""
    # Ordinateur quantique hypothétique : sqrt(key_space) essais (Grover)
    import math

    seconds_per_year = 365.25 * 24 * 3600
    trials_per_second = 10**15  # Très optimiste (superordinateur)
    years = key_space / (trials_per_second * seconds_per_year)

    exp = int(math.log10(float(years)))
    return f"~10^{exp} années"
