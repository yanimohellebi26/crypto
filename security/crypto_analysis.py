"""Fonctions d'analyse cryptographique pour le flux de Solitaire.

Fournit : entropie de Shannon, autocorrélation, test des runs (NIST SP 800-22),
vérification expérimentale du biais de Crowley, indice de coïncidence.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np
from scipy import stats


# ── Entropie de Shannon ──────────────────────────────────────────────────────

def shannon_entropy(values: np.ndarray, alphabet_size: int = 26) -> float:
    """H(X) = -Σ p_i · log₂(p_i), en bits."""
    counts = np.bincount(values, minlength=alphabet_size + 1)[1:alphabet_size + 1]
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -float(np.sum(probs * np.log2(probs)))


def max_entropy(alphabet_size: int = 26) -> float:
    """H_max = log₂(|A|)."""
    return math.log2(alphabet_size)


# ── Indice de coïncidence ────────────────────────────────────────────────────

def index_of_coincidence(values: np.ndarray, alphabet_size: int = 26) -> float:
    """IC = Σ n_i(n_i-1) / (N(N-1)).  Uniforme attendu : 1/|A|."""
    n = len(values)
    if n < 2:
        return 0.0
    counts = np.bincount(values, minlength=alphabet_size + 1)[1:alphabet_size + 1]
    return float(np.sum(counts * (counts - 1))) / (n * (n - 1))


# ── Autocorrélation ──────────────────────────────────────────────────────────

def autocorrelation(values: np.ndarray, max_lag: int = 50) -> np.ndarray:
    """Autocorrélation normalisée C(τ) pour τ = 1..max_lag."""
    x = values.astype(float)
    x = x - x.mean()
    var = np.var(x)
    if var == 0:
        return np.zeros(max_lag)
    n = len(x)
    result = np.zeros(max_lag)
    for lag in range(1, max_lag + 1):
        if lag >= n:
            break
        result[lag - 1] = np.sum(x[:n - lag] * x[lag:]) / ((n - lag) * var)
    return result


# ── Test des runs (NIST SP 800-22) ───────────────────────────────────────────

def runs_test(values: np.ndarray, alphabet_size: int = 26) -> dict:
    """Test des runs : séquences montantes/descendantes.
    
    On binarise le flux en comparant chaque valeur à la médiane théorique.
    """
    median = (alphabet_size + 1) / 2.0
    binary = (values > median).astype(int)
    n = len(binary)
    n1 = int(binary.sum())
    n0 = n - n1
    
    if n0 == 0 or n1 == 0:
        return {"runs": 0, "expected": 0, "z_stat": 0, "p_value": 0}
    
    # Compter les runs
    runs = 1 + int(np.sum(binary[1:] != binary[:-1]))
    
    # Espérance et variance
    expected = 1 + (2 * n0 * n1) / n
    variance = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n * n * (n - 1))
    
    if variance <= 0:
        return {"runs": runs, "expected": expected, "z_stat": 0, "p_value": 1.0}
    
    z = (runs - expected) / math.sqrt(variance)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    
    return {"runs": runs, "expected": round(expected, 2), "z_stat": round(z, 3), "p_value": round(p, 4)}


# ── Biais de Crowley ─────────────────────────────────────────────────────────

def crowley_bias_test(n_trials: int = 10000) -> dict:
    """Mesure expérimentale du biais P(K₂ = K₁).
    
    Crowley (1999) : P(K₂ = K₁) ≈ 1/22.5 au lieu de 1/26.
    """
    from core.deck import create_deck
    from core.keystream import generate_keystream
    
    repeats = 0
    for _ in range(n_trials):
        deck = create_deck()
        _, vals = generate_keystream(deck, 2)
        if vals[0] == vals[1]:
            repeats += 1
    
    p_observed = repeats / n_trials
    p_expected = 1.0 / 26
    p_crowley = 1.0 / 22.5
    
    # Test binomial
    binom_p = stats.binom_test(repeats, n_trials, p_expected) if hasattr(stats, 'binom_test') else \
              stats.binomtest(repeats, n_trials, p_expected).pvalue
    
    return {
        "n_trials": n_trials,
        "repeats": repeats,
        "p_observed": p_observed,
        "p_expected": p_expected,
        "p_crowley": p_crowley,
        "ratio": p_observed / p_expected,
        "p_value": binom_p,
    }


# ── Distribution des écarts (gap test) ──────────────────────────────────────

def gap_distribution(values: np.ndarray, target: int = 1) -> np.ndarray:
    """Calcule la distribution des écarts entre occurrences successives de `target`."""
    positions = np.where(values == target)[0]
    if len(positions) < 2:
        return np.array([])
    return np.diff(positions)


# ── Fréquence des bigrammes ─────────────────────────────────────────────────

def bigram_frequencies(values: np.ndarray) -> np.ndarray:
    """Matrice 26×26 des fréquences de bigrammes consécutifs."""
    matrix = np.zeros((26, 26), dtype=int)
    for i in range(len(values) - 1):
        a, b = values[i] - 1, values[i + 1] - 1
        if 0 <= a < 26 and 0 <= b < 26:
            matrix[a, b] += 1
    return matrix
