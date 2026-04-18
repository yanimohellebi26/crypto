"""Onglet Analyse : vecteurs de test, distribution, avalanche, sécurité."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.deck import create_deck
from core.encryption import encrypt
from core.keystream import generate_keystream, key_deck
from visuals.card_loader import HIGHLIGHT_COLORS, SUIT_COLORS


def render() -> None:
    """Point d'entrée du tab Analyse."""
    st.subheader("Analyse statistique et vecteurs de test")
    _render_test_vectors()
    st.divider()
    _render_keystream_distribution()
    st.divider()
    _render_security_metrics()
    st.divider()
    _render_key_reuse_demo()



def _render_test_vectors() -> None:
    st.markdown("#### Vecteurs de test Schneier")
    test_vectors = [
        ("AAAAAAAAAA", None, "EXKYIZSGEH"),
        ("AAAAAAAAAAAAAAA", "FOO", "ITHZUJIWGRFARMW"),
        ("SOLITAIREX", "CRYPTONOMICON", "KIRAKSFJAN"),
    ]
    tests_passed = 0
    table_rows = ""
    for plain, key, expected in test_vectors:
        result, _ = encrypt(plain, key=key)
        ok = result == expected
        if ok:
            tests_passed += 1
        status = "&#10003;" if ok else "&#10007;"
        table_rows += (
            f"<tr>"
            f'<td style="color:#8a8f9a">{plain}</td>'
            f'<td style="color:#7a72a8">{key or "—"}</td>'
            f'<td style="color:#b85040;font-family:monospace">{expected}</td>'
            f'<td style="color:#5a9a6a;font-family:monospace">{result}</td>'
            f'<td style="font-size:1.2em">{status}</td>'
            f"</tr>"
        )
    table_html = (
        '<table class="letter-table">'
        "<thead><tr>"
        '<th style="color:#828894">Message</th>'
        '<th style="color:#828894">Clé</th>'
        '<th style="color:#b85040">Attendu</th>'
        '<th style="color:#5a9a6a">Obtenu</th>'
        '<th style="color:#828894">OK</th>'
        "</tr></thead>"
        f"<tbody>{table_rows}</tbody>"
        "</table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)
    st.success(f"{tests_passed}/3 vecteurs officiels validés")



def _render_keystream_distribution() -> None:
    st.markdown("#### Distribution du flux de clés")
    slider_col, key_col = st.columns([2, 1])
    with slider_col:
        n_samples = st.slider(
            "Nombre de valeurs générées", 100, 5000, 1000, step=100,
        )
    with key_col:
        an_key = st.text_input("Clé (optionnel)", placeholder="FOO", key="an_key")

    if not st.button("Analyser  →", key="btn_analyze"):
        return

    init_dk = key_deck(an_key.upper()) if an_key.strip() else create_deck()
    _, ks_vals = generate_keystream(init_dk, n_samples)
    ks_arr = np.array(ks_vals)

    _render_histogram(ks_arr, n_samples)
    _render_stats(ks_arr)
    _render_avalanche(an_key)


def _render_histogram(ks_arr: np.ndarray, n_samples: int) -> None:
    counts = np.bincount(ks_arr, minlength=27)[1:]
    expected_count = n_samples / 26.0

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(1, 27)),
        y=counts,
        marker_color=[
            HIGHLIGHT_COLORS["output"] if abs(c - expected_count) > 2 * np.sqrt(expected_count)
            else SUIT_COLORS["clubs"]
            for c in counts
        ],
        name="Observé",
    ))
    fig.add_hline(
        y=expected_count,
        line_dash="dash",
        line_color="#b85040",
        annotation_text=f"Attendu ({expected_count:.1f})",
        annotation_font_color="#b85040",
    )
    fig.update_layout(
        title=dict(
            text=f"Distribution du keystream ({n_samples} valeurs)",
            font=dict(family="JetBrains Mono, monospace", color="#c9d1d9", size=13),
        ),
        xaxis_title="Valeur (1–26)",
        yaxis_title="Fréquence",
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e", family="JetBrains Mono, monospace", size=11),
        xaxis=dict(gridcolor="#30363d", tickmode="linear", tick0=1, dtick=1),
        yaxis=dict(gridcolor="#30363d"),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_stats(ks_arr: np.ndarray) -> None:
    n_samples = len(ks_arr)
    counts = np.bincount(ks_arr, minlength=27)[1:]
    expected_count = n_samples / 26.0
    chi2_stat, p_value = stats.chisquare(counts, f_exp=[expected_count] * 26)

    mean_col, std_col, chi2_col, pval_col = st.columns(4)
    mean_col.metric("Moyenne", f"{ks_arr.mean():.2f}", delta="vs 13.5")
    std_col.metric("Écart-type", f"{ks_arr.std():.2f}", delta="vs 7.50")
    chi2_col.metric("χ² stat", f"{chi2_stat:.2f}")
    pval_col.metric(
        "p-valeur",
        f"{p_value:.3f}",
        delta="Uniforme" if p_value > 0.05 else "Non-uniforme",
    )


def _render_avalanche(an_key: str) -> None:
    st.markdown("#### Effet avalanche — sensibilité à la clé")
    if not an_key.strip():
        st.info("Entrez une clé pour voir l'effet avalanche.")
        return

    base_key = an_key.strip().upper()
    _, ks_base = generate_keystream(key_deck(base_key), 100)
    diff_counts: list[int] = []
    for i, ch in enumerate(base_key):
        new_ch = chr((ord(ch) - ord("A") + 1) % 26 + ord("A"))
        mod_key = base_key[:i] + new_ch + base_key[i + 1:]
        _, ks_mod = generate_keystream(key_deck(mod_key), 100)
        diffs = sum(a != b for a, b in zip(ks_base, ks_mod))
        diff_counts.append(diffs)

    fig = go.Figure(go.Bar(
        x=[
            f"pos {i+1}: {c}→{chr((ord(c)-ord('A')+1)%26+ord('A'))}"
            for i, c in enumerate(base_key)
        ],
        y=diff_counts,
        marker_color=SUIT_COLORS["hearts"],
    ))
    fig.update_layout(
        title=dict(
            text="Valeurs différentes (sur 100) par position modifiée",
            font=dict(family="JetBrains Mono, monospace", color="#c9d1d9", size=13),
        ),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e", family="JetBrains Mono, monospace", size=11),
        yaxis=dict(gridcolor="#30363d"),
        margin=dict(l=40, r=20, t=50, b=60),
    )
    st.plotly_chart(fig, use_container_width=True)



def _render_security_metrics() -> None:
    st.markdown("#### Analyse de sécurité théorique")
    from security.key_reuse_demo import compute_security_metrics

    metrics = compute_security_metrics()

    sec_cols = st.columns(4)
    sec_cols[0].metric("Espace de clés", metrics["key_space_str"])
    sec_cols[1].metric("Entropie", f"{metrics['entropy_bits']:.1f} bits")
    sec_cols[2].metric("vs AES-128", f"+{metrics['vs_aes128']:.0f} bits")
    sec_cols[3].metric("Brute force", metrics["brute_force_years"])

    bias_col, _ = st.columns([2, 1])
    with bias_col:
        st.markdown(
            '<div style="background:#0d1626;padding:12px;border-radius:2px;'
            'border-left:3px solid #5f82a6;color:#d8dbe2;font-size:0.9em;'
            "font-family:'JetBrains Mono',monospace;\">"
            '<b style="color:#79c0ff;font-family:\'JetBrains Mono\',monospace;font-size:0.82em;'
            'letter-spacing:0.08em;text-transform:uppercase;">△ Biais de Crowley (1999)</b><br>'
            "La probabilité que la 2ème sortie soit identique à la 1ère est "
            "<b>1/22.5</b> au lieu de <b>1/26</b> attendu."
            " Cela révèle une faiblesse statistique mesurable."
            "</div>",
            unsafe_allow_html=True,
        )



def _render_key_reuse_demo() -> None:
    st.markdown("#### Démonstration — danger de réutilisation de clé")
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.9em;">'
        "Chiffrer deux messages avec la même clé permet de calculer leur différence "
        "sans connaître la clé. C1 − C2 = M1 − M2 (mod 26)."
        "</p>",
        unsafe_allow_html=True,
    )

    kr_col1, kr_col2 = st.columns(2)
    with kr_col1:
        kr_msg1 = st.text_input("Message 1", value="ATTAQUONS DEMAIN", key="kr_msg1")
    with kr_col2:
        kr_msg2 = st.text_input("Message 2", value="RETRAITE URGENT", key="kr_msg2")
    kr_key = st.text_input(
        "Clé partagée (laissez vide pour deck standard)",
        value="SECRET",
        key="kr_key",
    )

    if not st.button("Lancer la démonstration de réutilisation", key="kr_btn"):
        return

    from security.key_reuse_demo import crib_drag_attack, demo_key_reuse

    kr_result = demo_key_reuse(
        kr_msg1,
        kr_msg2,
        key=kr_key.strip() if kr_key.strip() else None,
    )

    if "error" in kr_result:
        st.error(kr_result["error"])
        return

    _display_key_reuse_result(kr_result)
    _display_crib_drag(kr_result)


def _display_key_reuse_result(kr_result: dict) -> None:
    st.markdown(
        f'<div style="background:#1e293b;padding:12px;border-radius:8px;'
        f'border:1px solid #334155;font-family:monospace;font-size:0.85em;">'
        f'<table style="width:100%;color:#e2e8f0;">'
        f'<tr><td style="color:#94a3b8;width:140px">M1 (clair) :</td>'
        f'<td style="color:#5a9a6a">{kr_result["m1"]}</td></tr>'
        f'<tr><td style="color:#94a3b8">M2 (clair) :</td>'
        f'<td style="color:#5a9a6a">{kr_result["m2"]}</td></tr>'
        f'<tr><td style="color:#94a3b8">C1 (chiffré) :</td>'
        f'<td style="color:#b85040">{kr_result["c1"]}</td></tr>'
        f'<tr><td style="color:#94a3b8">C2 (chiffré) :</td>'
        f'<td style="color:#b85040">{kr_result["c2"]}</td></tr>'
        f'<tr><td style="color:#94a3b8">C1−C2 mod26 :</td>'
        f'<td style="color:#b07838">{kr_result["xor_diff"]}</td></tr>'
        f'<tr><td style="color:#94a3b8">M1−M2 mod26 :</td>'
        f'<td style="color:#b07838">{kr_result["xor_expected"]}</td></tr>'
        f'</table></div>',
        unsafe_allow_html=True,
    )
    if kr_result["leak_ok"]:
        st.success(
            "Fuite confirmée : C1−C2 = M1−M2 à chaque position. "
            "Un attaquant connaissant M1 peut retrouver M2 intégralement.",
        )


def _display_crib_drag(kr_result: dict) -> None:
    st.markdown("**Attaque crib-dragging** — si l'attaquant devine un mot de M1 :")
    crib_word = st.text_input("Mot à essayer (crib)", value="ATTAQUE", key="kr_crib")
    if not crib_word.strip():
        return

    from security.key_reuse_demo import crib_drag_attack

    candidates = crib_drag_attack(kr_result["c1"], kr_result["c2"], crib_word)[:5]
    crib_rows = "".join(
        f"<tr>"
        f'<td style="color:#94a3b8">pos {c["position"]}</td>'
        f'<td style="color:#5f82a6;font-family:monospace">{c["crib"]}</td>'
        f'<td style="color:#5a9a6a;font-family:monospace">{c["m2_fragment"]}</td>'
        f'<td style="color:#b07838">{c["score"]:.2f}</td>'
        f"</tr>"
        for c in candidates
    )
    st.markdown(
        f'<table class="letter-table"><thead><tr>'
        f'<th>Position</th><th>Crib (M1)</th><th>M2 déduit</th><th>Score</th>'
        f'</tr></thead><tbody>{crib_rows}</tbody></table>',
        unsafe_allow_html=True,
    )
