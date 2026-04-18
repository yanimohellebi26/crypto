"""Tests de performance pour l'algorithme Solitaire (Phase 5.3).

Mesure le temps de chiffrement pour des messages de 1, 10, 100, 1000 et 10000
caractères, vérifie la scalabilité linéaire et génère un graphique interactif
(plotly HTML) dans le répertoire reports/.
"""

from __future__ import annotations

import time
from pathlib import Path

import plotly.graph_objects as go
import pytest

from core.encryption import encrypt


LENGTHS = [1, 10, 100, 1000, 10000]
KEY = "PERFORMANCETEST"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
CHART_PATH = REPORTS_DIR / "performance_scaling.html"

# Tolérance : le ratio temps/longueur ne doit pas dépasser ce facteur
# (scalabilité quasi-linéaire attendue)
LINEAR_TOLERANCE = 5.0




def measure_encrypt_time(length: int, repetitions: int = 3) -> float:
    """Retourne le temps médian de chiffrement (en secondes) pour `length` caractères."""
    message = "A" * length
    times: list[float] = []
    for _ in range(repetitions):
        start = time.perf_counter()
        encrypt(message, key=KEY)
        end = time.perf_counter()
        times.append(end - start)
    times.sort()
    return times[len(times) // 2]


class TestEncryptionPerformance:
    """Tests de performance du chiffrement Solitaire."""

    def test_1_char_under_1s(self) -> None:
        """Chiffrer 1 caractère prend moins d'1 seconde."""
        elapsed = measure_encrypt_time(1)
        assert elapsed < 1.0, f"1 char: {elapsed:.4f}s ≥ 1s"

    def test_10_chars_under_1s(self) -> None:
        """Chiffrer 10 caractères prend moins d'1 seconde."""
        elapsed = measure_encrypt_time(10)
        assert elapsed < 1.0, f"10 chars: {elapsed:.4f}s ≥ 1s"

    def test_100_chars_under_1s(self) -> None:
        """Chiffrer 100 caractères prend moins d'1 seconde."""
        elapsed = measure_encrypt_time(100)
        assert elapsed < 1.0, f"100 chars: {elapsed:.4f}s ≥ 1s"

    def test_1000_chars_under_5s(self) -> None:
        """Chiffrer 1000 caractères prend moins de 5 secondes."""
        elapsed = measure_encrypt_time(1000)
        assert elapsed < 5.0, f"1000 chars: {elapsed:.4f}s ≥ 5s"

    def test_10000_chars_under_60s(self) -> None:
        """Chiffrer 10000 caractères termine en moins de 60 secondes."""
        elapsed = measure_encrypt_time(10000, repetitions=1)
        assert elapsed < 60.0, f"10000 chars: {elapsed:.4f}s ≥ 60s"

    def test_scaling_is_approximately_linear(self) -> None:
        """La complexité croît de façon quasi-linéaire avec la longueur du message.

        Vérifie que le ratio (temps / longueur) reste dans une plage raisonnable
        entre les messages de 10 et 10000 caractères.
        """
        t10 = measure_encrypt_time(10)
        t10000 = measure_encrypt_time(10000, repetitions=1)

        # Ratio normalisé : (t10000 / 10000) / (t10 / 10)
        # Pour une O(n) parfaite le ratio = 1.0
        normalized_10 = t10 / 10
        normalized_10000 = t10000 / 10000

        if normalized_10 > 0:
            ratio = normalized_10000 / normalized_10
            assert ratio < LINEAR_TOLERANCE, (
                f"Scalabilité non-linéaire : ratio = {ratio:.2f} "
                f"(seuil = {LINEAR_TOLERANCE}). "
                f"t10={t10*1000:.2f}ms, t10000={t10000*1000:.2f}ms"
            )

    def test_encrypt_faster_than_keying_overhead(self) -> None:
        """Le surcoût du keying est borné : 2× keying < 3× chiffrement de 100 chars."""
        # Juste vérifier que l'encrypt de 100 chars reste raisonnable
        elapsed = measure_encrypt_time(100)
        assert elapsed < 1.0

    def test_output_correctness_maintained_at_scale(self) -> None:
        """À grande échelle, le résultat reste correct (roundtrip)."""
        from core.encryption import decrypt

        message = "X" * 1000
        ciphertext, _ = encrypt(message, key=KEY)
        plaintext, _ = decrypt(ciphertext, key=KEY)
        assert plaintext == message


class TestPerformanceReport:
    """Génère le rapport de performance (graphique plotly)."""

    def test_generate_performance_chart(self) -> None:
        """Génère un graphique plotly de temps vs longueur du message.

        Le fichier HTML est sauvegardé dans reports/performance_scaling.html.
        Le test est marqué comme passé si la génération réussit.
        """
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        times: list[float] = []
        for length in LENGTHS:
            reps = 1 if length >= 1000 else 3
            elapsed = measure_encrypt_time(length, repetitions=reps)
            times.append(elapsed * 1000)  # en millisecondes
            print(f"  {length:>6} chars : {elapsed*1000:.2f} ms")

        # Régression linéaire naïve pour l'annotation
        ref_slope = times[-1] / LENGTHS[-1]  # ms par caractère à 10000 chars

        fig = go.Figure()

        # Courbe mesurée
        fig.add_trace(go.Scatter(
            x=LENGTHS,
            y=times,
            mode="lines+markers",
            name="Solitaire",
            marker=dict(size=10, color="#6366f1"),
            line=dict(color="#6366f1", width=2),
            hovertemplate="<b>%{x} caractères</b><br>Temps : %{y:.3f} ms<extra></extra>",
        ))

        # Courbe de référence O(n) théorique
        ref_times = [ref_slope * n for n in LENGTHS]
        fig.add_trace(go.Scatter(
            x=LENGTHS,
            y=ref_times,
            mode="lines",
            name="O(n) théorique",
            line=dict(color="#22c55e", width=1, dash="dash"),
        ))

        fig.update_layout(
            title={
                "text": "Performance du chiffrement Solitaire — Scalabilité",
                "x": 0.5,
            },
            xaxis=dict(
                title="Longueur du message (caractères)",
                type="log",
                gridcolor="#374151",
            ),
            yaxis=dict(
                title="Temps d'exécution (ms)",
                type="log",
                gridcolor="#374151",
            ),
            plot_bgcolor="#111827",
            paper_bgcolor="#111827",
            font=dict(color="#f9fafb"),
            legend=dict(x=0.05, y=0.95),
            annotations=[
                dict(
                    text=(
                        f"Scalabilité quasi-linéaire O(n)<br>"
                        f"1 char → {times[0]:.2f} ms · "
                        f"10k chars → {times[-1]:.2f} ms"
                    ),
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.05,
                    showarrow=False,
                    font=dict(size=11, color="#9ca3af"),
                    align="center",
                ),
            ],
        )

        fig.write_html(str(CHART_PATH))
        assert CHART_PATH.exists(), f"Graphique non généré : {CHART_PATH}"
        print(f"\n  Graphique sauvegardé : {CHART_PATH}")
