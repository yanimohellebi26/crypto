"""Onglet Analyse — tests statistiques et analyse cryptographique du flux Solitaire."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats

from core.deck import create_deck
from core.encryption import encrypt
from core.keystream import generate_keystream, key_deck

# ── Couleurs cohérentes pour les graphes ─────────────────────────────────────
_ACCENT = "#e0a840"
_BLUE = "#5f82a6"
_RED = "#c85a4f"
_GREEN = "#5a9a6a"
_TEAL = "#4a9a8a"
_PURPLE = "#7a72a8"


def render() -> None:
    """Point d'entrée du tab Analyse."""
    st.subheader("Analyse cryptographique")
    st.markdown(
        '<p style="opacity: 0.85; font-size: 0.92em; margin-top: -8px;">'
        "Tests statistiques appliqués au flux de clés produit par l'algorithme Solitaire."
        "</p>",
        unsafe_allow_html=True,
    )

    _render_test_vectors()
    st.divider()
    _render_keystream_analysis()
    st.divider()
    _render_security_metrics()
    st.divider()
    _render_key_reuse_demo()


# §1  VECTEURS DE TEST

def _render_test_vectors() -> None:
    st.markdown("#### 1. Vecteurs de test de Schneier")
    st.latex(r"C_i = (P_i + K_i) \bmod 26, \quad P_i = (C_i - K_i) \bmod 26")
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
            f'<td style="opacity:0.8">{plain}</td>'
            f'<td style="color:{_PURPLE}">{key or "—"}</td>'
            f'<td style="color:{_RED};font-family:monospace">{expected}</td>'
            f'<td style="color:{_GREEN};font-family:monospace">{result}</td>'
            f'<td style="font-size:1.2em">{status}</td>'
            f"</tr>"
        )
    st.markdown(
        '<table class="letter-table"><thead><tr>'
        '<th style="opacity:0.8">Message</th>'
        '<th style="opacity:0.8">Clé</th>'
        f'<th style="color:{_RED}">Attendu</th>'
        f'<th style="color:{_GREEN}">Obtenu</th>'
        '<th style="opacity:0.8">OK</th>'
        f"</tr></thead><tbody>{table_rows}</tbody></table>",
        unsafe_allow_html=True,
    )
    st.success(f"{tests_passed}/3 vecteurs officiels validés")


# §2  ANALYSE DU FLUX DE CLÉS

def _render_keystream_analysis() -> None:
    st.markdown("#### 2. Analyse du flux de clés")

    st.latex(
        r"H(X) = -\sum_{i=1}^{26} p_i \cdot \log_2(p_i), \qquad"
        r"\text{IC}(X) = \frac{\sum n_i(n_i - 1)}{N(N-1)}"
    )

    slider_col, key_col = st.columns([2, 1])
    with slider_col:
        n_samples = st.slider("Nombre de valeurs générées", 500, 10000, 2000, step=500)
    with key_col:
        an_key = st.text_input("Clé (optionnel)", placeholder="FOO", key="an_key")

    if st.button("Lancer l'analyse", key="btn_analyze"):
        init_dk = key_deck(an_key.upper()) if an_key.strip() else create_deck()
        _, ks_vals = generate_keystream(init_dk, n_samples)
        st.session_state["an_ks_arr"] = np.array(ks_vals)
        st.session_state["an_n_samples"] = n_samples
        # Réinitialiser l'interprétation IA lors d'une nouvelle analyse
        st.session_state.pop("ai_interpretation_text", None)

    if "an_ks_arr" not in st.session_state:
        return

    ks_arr = st.session_state["an_ks_arr"]
    n_samples = st.session_state["an_n_samples"]

    # ── Graphiques principaux (2×2) ──
    _render_distribution_and_autocorr(ks_arr, n_samples)

    # ── Métriques numériques ──
    metrics = _render_statistical_tests(ks_arr)

    # ── Interprétation IA ──
    _render_ai_interpretation(metrics)

    # ── Effet avalanche ──
    if an_key.strip():
        _render_avalanche(an_key, ks_arr)


def _render_distribution_and_autocorr(ks_arr: np.ndarray, n_samples: int) -> None:
    """Graphe 1×2 : distribution + autocorrélation."""
    from security.crypto_analysis import autocorrelation, shannon_entropy, max_entropy

    counts = np.bincount(ks_arr, minlength=27)[1:]
    expected = n_samples / 26.0

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Distribution empirique (n = {n_samples})",
            "Autocorrélation C(τ)",
        ],
        horizontal_spacing=0.12,
    )

    # ── Histogramme ──
    colors = [
        _RED if abs(c - expected) > 2 * np.sqrt(expected) else _BLUE
        for c in counts
    ]
    fig.add_trace(go.Bar(
        x=list(range(1, 27)), y=counts,
        marker_color=colors, name="Observé",
        showlegend=False,
    ), row=1, col=1)
    fig.add_hline(
        y=expected, line_dash="dash", line_color=_ACCENT,
        annotation_text=f"E[n] = {expected:.1f}",
        annotation_font_color=_ACCENT,
        row=1, col=1,
    )

    # ── Autocorrélation ──
    max_lag = min(60, n_samples // 10)
    acorr = autocorrelation(ks_arr, max_lag)
    ci_95 = 1.96 / np.sqrt(n_samples)  # intervalle de confiance 95%

    fig.add_trace(go.Scatter(
        x=list(range(1, max_lag + 1)), y=acorr,
        mode="lines+markers", marker=dict(size=3, color=_TEAL),
        line=dict(color=_TEAL, width=1.5), name="C(τ)",
        showlegend=False,
    ), row=1, col=2)
    fig.add_hline(y=ci_95, line_dash="dot", line_color=_RED,
                  annotation_text=f"+1.96/√n", annotation_font_color=_RED,
                  row=1, col=2)
    fig.add_hline(y=-ci_95, line_dash="dot", line_color=_RED, row=1, col=2)
    fig.add_hline(y=0, line_color="#888", line_width=0.5, row=1, col=2)

    fig.update_layout(
        height=380,
        margin=dict(l=50, r=20, t=50, b=40),
    )
    fig.update_xaxes(title_text="Valeur (1–26)", row=1, col=1)
    fig.update_yaxes(title_text="Fréquence", row=1, col=1)
    fig.update_xaxes(title_text="Décalage τ", row=1, col=2)
    fig.update_yaxes(title_text="C(τ)", row=1, col=2)

    st.plotly_chart(fig, use_container_width=True)


def _render_statistical_tests(ks_arr: np.ndarray) -> dict:
    """Affiche les résultats des tests statistiques avec formules LaTeX et retourne les métriques."""
    from security.crypto_analysis import (
        shannon_entropy, max_entropy, index_of_coincidence, runs_test,
    )

    n = len(ks_arr)
    counts = np.bincount(ks_arr, minlength=27)[1:]
    expected = n / 26.0

    # ── Calculs ──
    chi2_stat, p_chi2 = stats.chisquare(counts, f_exp=[expected] * 26)
    h = shannon_entropy(ks_arr)
    h_max = max_entropy()
    ic = index_of_coincidence(ks_arr)
    ic_uniform = 1.0 / 26
    rt = runs_test(ks_arr)

    # ── Affichage en colonnes ──
    st.markdown("##### Résultats des tests statistiques")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Test du χ² d'uniformité**")
        st.latex(r"\chi^2 = \sum_{i=1}^{26} \frac{(O_i - E_i)^2}{E_i}")
        st.metric("χ²", f"{chi2_stat:.2f}", delta=f"ddl = 25")
        st.metric("p-valeur", f"{p_chi2:.4f}",
                  delta="Uniforme" if p_chi2 > 0.05 else "Non-uniforme")

    with c2:
        st.markdown("**Entropie de Shannon**")
        st.latex(r"H(X) = -\sum p_i \log_2 p_i")
        st.metric("H(X)", f"{h:.4f} bits")
        st.metric("H_max", f"{h_max:.4f} bits",
                  delta=f"ratio = {h/h_max:.4f}")

    with c3:
        st.markdown("**Indice de coïncidence**")
        st.latex(r"\text{IC} = \frac{\sum n_i(n_i-1)}{N(N-1)}")
        st.metric("IC observé", f"{ic:.6f}")
        st.metric("IC uniforme", f"{ic_uniform:.6f}",
                  delta=f"écart = {(ic - ic_uniform)*1000:.3f}‰")

    # ── Test des runs ──
    st.markdown("##### Test des runs (NIST SP 800-22)")
    st.latex(
        r"\text{Runs}(X): \text{on binarise } b_i = \mathbb{1}_{X_i > \tilde{\mu}}, "
        r"\; Z = \frac{R - E[R]}{\sqrt{\text{Var}(R)}}"
    )
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Runs observés", rt["runs"])
    r2.metric("Runs attendus", f'{rt["expected"]:.1f}')
    r3.metric("Z-stat", f'{rt["z_stat"]:.3f}')
    r4.metric("p-valeur", f'{rt["p_value"]:.4f}',
              delta="OK" if rt["p_value"] > 0.01 else "Suspect")

    return {
        "n_samples": n,
        "chi2_stat": chi2_stat,
        "p_chi2": p_chi2,
        "h": h,
        "h_max": h_max,
        "ic": ic,
        "ic_uniform": ic_uniform,
        "runs": rt["runs"],
        "expected_runs": rt["expected"],
        "runs_z_stat": rt["z_stat"],
        "runs_p_value": rt["p_value"],
    }


def _render_ai_interpretation(metrics: dict) -> None:
    """Interprétation des résultats statistiques par l'IA Gemini."""
    st.markdown("##### Interprétation par l'IA (Cryptanalyste)")
    
    if st.button("Interpréter ces résultats avec l'IA", key="btn_ai_interpret"):
        with st.spinner("Analyse cryptographique par Gemini en cours..."):
            try:
                import os
                import google.generativeai as genai
                from dotenv import load_dotenv
                
                load_dotenv()
                api_key = os.getenv("GEMINI_API_KEY")
                
                if not api_key:
                    st.error("Clé API Gemini introuvable. Configurez `GEMINI_API_KEY` dans le fichier `.env`.")
                else:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("models/gemini-2.5-pro")
                    
                    prompt = f"""Tu es un cryptanalyste mathématicien expert.
On te fournit les résultats statistiques suivants issus de l'analyse d'un flux de clés généré par l'algorithme Solitaire (sur un alphabet de 26 lettres) :
- Nombre d'échantillons (N) : {metrics['n_samples']}
- Test d'uniformité du χ² : Statistique = {metrics['chi2_stat']:.2f}, p-valeur = {metrics['p_chi2']:.4f}
- Entropie de Shannon : {metrics['h']:.4f} bits (Max théorique : {metrics['h_max']:.4f} bits)
- Indice de coïncidence (IC) : {metrics['ic']:.6f} (Uniforme attendu : {metrics['ic_uniform']:.6f})
- Test des runs (NIST) : Runs observés = {metrics['runs']}, Attendus = {metrics['expected_runs']:.1f}, p-valeur = {metrics['runs_p_value']:.4f}

Agis comme un mathématicien qui observe ces résultats cryptographiques.
1. Interprète brièvement ce que signifient ces chiffres concrets pour la sécurité de ce flux pseudo-aléatoire.
2. Détermine si le flux présente des biais notables (par exemple, p-valeur < 0.05, ou un IC s'éloignant significativement de l'uniforme) ou s'il s'approche d'un flux réellement aléatoire acceptable.
3. Sois précis, professionnel, avec une touche d'analyse académique. Pas de phrases bateau, concentre-toi sur la signification profonde de ces valeurs dans le contexte de l'algorithme Solitaire.

Rédige une réponse incisive (max 3-4 paragraphes). Utilise le markdown pour mettre en valeur les points clés (gras, listes).
IMPORTANT : N'utilise AUCUN emoji dans ta réponse. Rédige en prose académique sobre.
"""
                    response = model.generate_content(prompt)
                    st.session_state["ai_interpretation_text"] = response.text
            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'API Gemini : {e}")

    if "ai_interpretation_text" in st.session_state:
        _display_ai_box(st.session_state["ai_interpretation_text"])


def _display_ai_box(text: str) -> None:
    """Affiche le texte d'interprétation dans un encadré stylisé."""
    st.markdown(
        f'<div style="background:var(--secondary-background-color, rgba(128,128,128,0.1));'
        f'padding:20px;border-radius:8px;border-left:4px solid {_PURPLE};'
        f'margin-top:10px;font-size:0.95em;line-height:1.5;">'
        f'<strong style="color:{_PURPLE};font-size:1.1em;display:block;margin-bottom:10px;">'
        f'Interprétation Mathématique (Gemini)</strong>'
        f'{text}'
        f'</div>',
        unsafe_allow_html=True
    )


def _render_avalanche(an_key: str, ks_base: np.ndarray) -> None:
    """Effet avalanche : distance de Hamming entre flux pour clés voisines."""
    st.markdown("##### Effet avalanche — sensibilité à la clé")
    st.latex(
        r"d_H(K, K') = \frac{1}{n}\sum_{i=1}^{n} \mathbb{1}_{K_i \neq K'_i}"
    )

    base_key = an_key.strip().upper()
    _, ks_base_vals = generate_keystream(key_deck(base_key), 100)
    diff_ratios: list[float] = []
    labels: list[str] = []

    for i, ch in enumerate(base_key):
        new_ch = chr((ord(ch) - ord("A") + 1) % 26 + ord("A"))
        mod_key = base_key[:i] + new_ch + base_key[i + 1:]
        _, ks_mod = generate_keystream(key_deck(mod_key), 100)
        d = sum(a != b for a, b in zip(ks_base_vals, ks_mod)) / 100.0
        diff_ratios.append(d)
        labels.append(f"{ch}→{new_ch} (pos {i+1})")

    fig = go.Figure(go.Bar(
        x=labels, y=diff_ratios,
        marker_color=[_TEAL if d > 0.4 else _RED for d in diff_ratios],
        text=[f"{d:.0%}" for d in diff_ratios],
        textposition="outside",
    ))
    fig.add_hline(y=0.5, line_dash="dash", line_color=_ACCENT,
                  annotation_text="Idéal : 50 %", annotation_font_color=_ACCENT)
    fig.update_layout(
        title=dict(text="Distance de Hamming normalisée d_H(K, K')", font=dict(size=13)),
        yaxis_title="d_H", yaxis_range=[0, 1],
        height=340,
        margin=dict(l=50, r=20, t=50, b=60),
    )
    st.plotly_chart(fig, use_container_width=True)


# §3  MÉTRIQUES DE SÉCURITÉ THÉORIQUES

def _render_security_metrics() -> None:
    st.markdown("#### 3. Analyse de sécurité théorique")

    # Espace de clés
    st.latex(
        r"|\mathcal{K}| = 54! \approx 2{,}31 \times 10^{71} \approx 2^{237}"
    )
    st.latex(
        r"H(\mathcal{K}) = \log_2(54!) \approx 237{,}5 \;\text{bits}"
    )

    from security.key_reuse_demo import compute_security_metrics
    metrics = compute_security_metrics()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Espace de clés", metrics["key_space_str"])
    s2.metric("Entropie théorique", f'{metrics["entropy_bits"]:.1f} bits')
    s3.metric("Avantage vs AES-128", f'+{metrics["vs_aes128"]:.0f} bits')
    s4.metric("Force brute", metrics["brute_force_years"])

    # Biais de Crowley
    st.markdown("##### Biais de Crowley (1999)")
    st.latex(
        r"\Pr[K_2 = K_1] \approx \frac{1}{22{,}5} \neq \frac{1}{26} "
        r"= \Pr[\text{uniforme}]"
    )
    st.markdown(
        '<div style="background:var(--secondary-background-color, rgba(128,128,128,0.1));padding:14px;border-radius:4px;'
        f'border-left:4px solid {_BLUE};font-size:0.9em;">'
        "Crowley (1999) a montré que la probabilité que la seconde valeur "
        "du flux soit identique à la première est de <b>1/22,5</b> au lieu "
        "de <b>1/26</b>. Cet écart, supérieur à 15 %, provient de la structure "
        "des opérations de coupe. Il devient statistiquement mesurable dès "
        "quelques milliers d'échantillons avec un test χ²."
        "</div>",
        unsafe_allow_html=True,
    )


# §4  RÉUTILISATION DE CLÉ

def _render_key_reuse_demo() -> None:
    st.markdown("#### 4. Réutilisation de clé — vulnérabilité fondamentale")
    st.latex(
        r"C_i = M_i + K_i \pmod{26} \implies "
        r"C_1 - C_2 \equiv M_1 - M_2 \pmod{26}"
    )
    st.markdown(
        '<p style="opacity:0.85;font-size:0.9em;">'
        "Lorsque deux messages M₁ et M₂ sont chiffrés avec le même flux K, "
        "la différence des chiffrés C₁ − C₂ révèle la différence des clairs. "
        "Un adversaire peut alors exploiter cette relation par glissement "
        "de crib (<em>crib-dragging</em>)."
        "</p>",
        unsafe_allow_html=True,
    )

    kr_col1, kr_col2 = st.columns(2)
    with kr_col1:
        kr_msg1 = st.text_input("Message M₁", value="ATTAQUONS DEMAIN", key="kr_msg1")
    with kr_col2:
        kr_msg2 = st.text_input("Message M₂", value="RETRAITE URGENT", key="kr_msg2")
    kr_key = st.text_input(
        "Clé partagée (vide = paquet standard)",
        value="SECRET", key="kr_key",
    )

    if not st.button("Lancer l'analyse de réutilisation", key="kr_btn"):
        return

    from security.key_reuse_demo import crib_drag_attack, demo_key_reuse

    kr_result = demo_key_reuse(
        kr_msg1, kr_msg2,
        key=kr_key.strip() if kr_key.strip() else None,
    )
    if "error" in kr_result:
        st.error(kr_result["error"])
        return

    _display_key_reuse_result(kr_result)
    _display_crib_drag(kr_result)


def _display_key_reuse_result(kr_result: dict) -> None:
    st.markdown(
        f'<div style="background:var(--secondary-background-color, rgba(128,128,128,0.1));padding:12px;border-radius:8px;'
        f'font-family:monospace;font-size:0.85em;">'
        f'<table style="width:100%;">'
        f'<tr><td style="opacity:0.7;width:140px">M₁ (clair) :</td>'
        f'<td style="color:{_GREEN}">{kr_result["m1"]}</td></tr>'
        f'<tr><td style="opacity:0.7">M₂ (clair) :</td>'
        f'<td style="color:{_GREEN}">{kr_result["m2"]}</td></tr>'
        f'<tr><td style="opacity:0.7">C₁ (chiffré) :</td>'
        f'<td style="color:{_RED}">{kr_result["c1"]}</td></tr>'
        f'<tr><td style="opacity:0.7">C₂ (chiffré) :</td>'
        f'<td style="color:{_RED}">{kr_result["c2"]}</td></tr>'
        f'<tr><td style="opacity:0.7">C₁−C₂ mod 26 :</td>'
        f'<td style="color:{_ACCENT}">{kr_result["xor_diff"]}</td></tr>'
        f'<tr><td style="opacity:0.7">M₁−M₂ mod 26 :</td>'
        f'<td style="color:{_ACCENT}">{kr_result["xor_expected"]}</td></tr>'
        f'</table></div>',
        unsafe_allow_html=True,
    )
    if kr_result["leak_ok"]:
        st.success(
            "Fuite confirmée : C₁−C₂ = M₁−M₂ à chaque position. "
            "Un adversaire disposant de M₁ peut reconstituer M₂ intégralement.",
        )


def _display_crib_drag(kr_result: dict) -> None:
    st.markdown("**Attaque par glissement de crib** — exploitation de la relation :")
    st.latex(
        r"\text{Si } M_1[j\!:\!j\!+\!k] = w, \;\text{alors } "
        r"M_2[j\!:\!j\!+\!k] = w - (C_1 - C_2)[j\!:\!j\!+\!k] \pmod{26}"
    )
    crib_word = st.text_input("Fragment supposé (crib)", value="ATTAQUE", key="kr_crib")
    if not crib_word.strip():
        return

    from security.key_reuse_demo import crib_drag_attack

    candidates = crib_drag_attack(kr_result["c1"], kr_result["c2"], crib_word)[:5]
    crib_rows = "".join(
        f"<tr>"
        f'<td style="opacity:0.8">pos {c["position"]}</td>'
        f'<td style="color:{_BLUE};font-family:monospace">{c["crib"]}</td>'
        f'<td style="color:{_GREEN};font-family:monospace">{c["m2_fragment"]}</td>'
        f'<td style="color:{_ACCENT}">{c["score"]:.2f}</td>'
        f"</tr>"
        for c in candidates
    )
    st.markdown(
        f'<table class="letter-table"><thead><tr>'
        f'<th>Position</th><th>Crib (M₁)</th><th>M₂ déduit</th><th>Score</th>'
        f'</tr></thead><tbody>{crib_rows}</tbody></table>',
        unsafe_allow_html=True,
    )
    st.latex(
        r"\text{score}(w) = \frac{1}{|w|}\sum_{c \in w} f_{\text{FR}}(c)"
    )
    st.markdown(
        '<p style="opacity:0.7;font-size:0.82em;">'
        "Le score utilise les fréquences des lettres françaises (Beker & Piper, 1982) "
        "pour évaluer la plausibilité linguistique du fragment M₂ déduit."
        "</p>",
        unsafe_allow_html=True,
    )
