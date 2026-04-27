"""Onglet Rapport — rapport de projet de cryptographie, format éditorial académique."""

from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

_RAPPORT_PATH = Path(__file__).parent.parent / "docs" / "RAPPORT.md"
_RAPPORT_PDF_PATH = Path(__file__).parent.parent / "docs" / "rapport_final.pdf"

# ── CSS du rapport ─────────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Variables ── */
.rp {
  --rp-bg:       #faf8f3;
  --rp-card:     #ffffff;
  --rp-sunken:   #f2efe7;
  --rp-ink:      #000000;
  --rp-ink2:     #000000;
  --rp-mute:     #000000;
  --rp-faint:    #000000;
  --rp-rule:     #d8d3c5;
  --rp-rule-s:   #bab3a0;
  --rp-accent:   #8a1538;
  --rp-navy:     #0a4d68;
  --rp-gold:     #b8860b;
  --rp-ok:       #2a6f3b;
  --rp-warn:     #b35900;
  --rp-err:      #8a1515;
  --rp-serif:    'EB Garamond', Georgia, serif;
  --rp-sans:     'Inter Tight', system-ui, sans-serif;
  --rp-mono:     'JetBrains Mono', ui-monospace, monospace;
}

/* ── Base wrapper ── */
.rp {
  font-family: var(--rp-serif);
  font-size: 17px;
  line-height: 1.55;
  color: var(--rp-ink);
  max-width: 1100px;
  margin: 0 auto;
}

/* ── Topbar ── */
.rp-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--rp-rule);
  margin-bottom: 36px;
}
.rp-brand {
  display: flex; align-items: baseline; gap: 14px;
}
.rp-brand .mark {
  font-family: var(--rp-serif);
  font-style: italic; font-size: 24px; letter-spacing: -0.01em;
}
.rp-brand .mark strong { font-style: normal; font-weight: 600; }
.rp-chip {
  display: inline-flex; align-items: center;
  font-family: var(--rp-sans); font-size: 11.5px; font-weight: 500;
  padding: 3px 8px;
  background: var(--rp-sunken); border: 1px solid var(--rp-rule);
  border-radius: 2px; color: var(--rp-ink2);
}
.rp-meta {
  font-family: var(--rp-sans); font-size: 12px;
  color: var(--rp-mute); text-align: right; line-height: 1.5;
}

/* ── Hero ── */
.rp-hero {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 48px;
  padding: 36px 0 48px;
  border-bottom: 1px solid var(--rp-rule);
  margin-bottom: 40px;
}
.rp-hero h1 {
  font-family: var(--rp-serif);
  font-size: 52px; font-weight: 500; line-height: 1.05;
  letter-spacing: -0.02em; color: var(--rp-ink);
  margin: 0 0 18px;
}
.rp-hero .lead {
  font-size: 18px; color: var(--rp-ink2); line-height: 1.6;
  max-width: 600px;
}
.rp-eyebrow {
  font-family: var(--rp-sans); font-size: 11px; font-weight: 600;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--rp-mute); margin-bottom: 14px;
}
.rp-colophon {
  font-family: var(--rp-sans); font-size: 12px;
  color: var(--rp-mute);
  display: flex; flex-direction: column; gap: 10px;
  padding-top: 4px;
}
.rp-colophon .row { display: flex; gap: 14px; }
.rp-colophon .k {
  width: 86px; color: var(--rp-faint);
  letter-spacing: 0.06em; text-transform: uppercase;
  font-size: 10.5px; padding-top: 2px;
}
.rp-colophon .v { color: var(--rp-ink2); }

/* ── Stats ── */
.rp-stats {
  display: grid; grid-template-columns: repeat(3,1fr);
  gap: 20px; margin-bottom: 48px;
}
.rp-stat .v {
  font-family: var(--rp-serif); font-size: 34px; font-weight: 500;
  line-height: 1; color: var(--rp-ink); letter-spacing: -0.02em;
}
.rp-stat .s {
  font-family: var(--rp-sans); font-size: 12px;
  color: var(--rp-faint); margin-top: 3px; line-height: 1.4;
}
.rp-stat .l {
  font-family: var(--rp-sans); font-size: 10.5px;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--rp-mute); margin-top: 6px;
}

/* ── Section head ── */
.rp-section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 24px;
  padding-bottom: 14px;
  margin: 48px 0 28px;
  border-bottom: 1px solid var(--rp-rule);
}
.rp-section-head .title { display: flex; align-items: baseline; gap: 16px; }
.rp-section-head .num-big {
  font-family: var(--rp-serif); font-size: 52px; font-style: italic;
  color: var(--rp-accent); line-height: 1; font-weight: 400;
  flex-shrink: 0;
}
.rp-section-head h2 {
  font-family: var(--rp-serif); font-size: 26px; font-weight: 500;
  letter-spacing: -0.01em; color: var(--rp-ink); margin: 0;
  line-height: 1.2;
}
.rp-section-head .sub {
  font-family: var(--rp-sans); font-size: 12.5px;
  color: var(--rp-mute); text-align: right; max-width: 320px;
  flex-shrink: 0;
}

/* ── Prose ── */
.rp-prose { font-family: var(--rp-serif); font-size: 17px; line-height: 1.65; }
.rp-prose p { margin: 0 0 14px; color: var(--rp-ink); }
.rp-prose p.dropcap::first-letter {
  font-family: var(--rp-serif); font-size: 58px; line-height: 0.82;
  float: left; padding: 6px 10px 0 0;
  color: var(--rp-accent); font-weight: 500;
}
.rp-prose strong { font-weight: 600; color: var(--rp-ink); }
.rp-prose em { color: var(--rp-ink2); }
.rp-prose code {
  font-family: var(--rp-mono); font-size: 0.88em;
  background: #000000; color: #ffffff; padding: 1px 6px; border-radius: 2px;
}
.rp-prose ul { padding-left: 20px; }
.rp-prose li { margin-bottom: 6px; }
.rp-prose h3 { font-family: var(--rp-serif); font-size: 20px; font-weight: 500; margin: 20px 0 8px; }

/* ── Grid ── */
.rp-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
.rp-grid-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
.rp-grid-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; }

/* ── Panel ── */
.rp-panel {
  background: var(--rp-card); border: 1px solid var(--rp-rule); padding: 20px;
}
.rp-panel.sunken { background: var(--rp-sunken); }
.rp-panel .ph {
  font-family: var(--rp-sans); font-size: 11px; font-weight: 600;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--rp-mute); margin-bottom: 10px;
}

/* ── Callout ── */
.rp-callout {
  border-left: 3px solid var(--rp-accent);
  padding: 14px 18px; background: var(--rp-sunken);
  font-family: var(--rp-sans); font-size: 14px; line-height: 1.55;
  color: var(--rp-ink2); margin: 20px 0;
}
.rp-callout .t {
  font-weight: 600; color: var(--rp-ink); display: block;
  margin-bottom: 4px; font-size: 11.5px;
  letter-spacing: 0.1em; text-transform: uppercase;
}
.rp-callout.warn { border-left-color: var(--rp-warn); }
.rp-callout.info { border-left-color: var(--rp-navy); }

/* ── Mono box ── */
.rp-mono {
  font-family: var(--rp-mono); font-size: 13px; line-height: 1.65;
  padding: 14px 16px; background: #000000;
  border: 1px solid var(--rp-rule); border-radius: 2px;
  white-space: pre-wrap; word-break: break-all; color: #ffffff;
  margin: 12px 0;
}

/* ── Table ── */
.rp table { width:100%; border-collapse:collapse; font-family:var(--rp-sans); font-size:13px; margin:16px 0; }
.rp th {
  text-align:left; padding:9px 14px;
  border-bottom:2px solid var(--rp-ink); font-weight:600;
  font-size:11px; letter-spacing:0.1em; text-transform:uppercase; color:var(--rp-mute);
}
.rp td { padding:9px 14px; border-bottom:1px solid var(--rp-rule); }
.rp td code { font-family:var(--rp-mono); font-size:0.88em; }

/* ── Limits grid ── */
.rp-limit .eyebrow { font-family:var(--rp-sans); font-size:10.5px; font-weight:600;
  letter-spacing:0.12em; text-transform:uppercase; color:var(--rp-err); margin-bottom:6px; }
.rp-limit .desc { font-family:var(--rp-sans); font-size:13.5px; line-height:1.6; color:var(--rp-ink2); }

/* ── Two-col prose ── */
.rp-twocol { column-count:2; column-gap:40px; column-rule:1px solid var(--rp-rule); font-size:16.5px; line-height:1.65; }

/* ── Download bar ── */
.rp-dl-bar {
  display:flex; justify-content:flex-end; gap:10px;
  padding:10px 0 20px; border-bottom:1px solid var(--rp-rule); margin-bottom:28px;
}

/* ── Footer ── */
.rp-footer {
  text-align:center; font-family:var(--rp-serif); font-style:italic;
  color:var(--rp-mute); font-size:14px; margin:48px 0 16px;
  padding-top:24px; border-top:1px solid var(--rp-rule);
}

/* ── Cards académiques ── */
.rp-card-row { display:flex; gap:6px; flex-wrap:wrap; margin-top:12px; }
.rp-card {
  position:relative; width:44px; height:62px; background:#fff;
  border:1px solid var(--rp-rule-s); border-radius:4px;
  display:flex; flex-direction:column; padding:3px 4px;
  font-family:var(--rp-sans); flex-shrink:0;
  box-shadow:0 1px 0 rgba(0,0,0,0.04);
}
.rp-card .rank { font-size:13px; font-weight:600; line-height:1; color:var(--rp-ink); }
.rp-card .suit { font-size:11px; line-height:1; margin-top:1px; }
.rp-card .csuit {
  position:absolute; top:50%; left:50%;
  transform:translate(-50%,-45%); font-size:20px; opacity:0.45;
}
.rp-card.red .rank, .rp-card.red .suit, .rp-card.red .csuit { color:var(--rp-accent); }
.rp-card.joker { background:linear-gradient(135deg,#fff 0%,#faf4e5 100%); }

/* ── Schneier tests table ── */
.rp-test-ok { color:var(--rp-ok); font-weight:600; font-size:11px; font-family:var(--rp-sans); }
.rp-test-code { font-family:var(--rp-mono); font-size:12px; letter-spacing:0.06em; }

/* ── Spacers ── */
.rp .sp-24 { height:24px; } .rp .sp-32 { height:32px; } .rp .sp-48 { height:48px; }
</style>
"""

# ── Helpers HTML ──────────────────────────────────────────────────────────────

def _section_head(num: int, title: str, sub: str = "") -> str:
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return (
        f'<div class="rp-section-head">'
        f'<div class="title">'
        f'<div class="num-big">§{num}</div>'
        f'<div><div class="rp-eyebrow">Section {num}</div>'
        f'<h2>{title}</h2></div>'
        f'</div>{sub_html}</div>'
    )


def _panel(content: str, sunken: bool = False, title: str = "") -> str:
    cls = "rp-panel sunken" if sunken else "rp-panel"
    ph = f'<div class="ph">{title}</div>' if title else ""
    return f'<div class="{cls}">{ph}{content}</div>'


def _callout(content: str, label: str = "", variant: str = "") -> str:
    cls = f"rp-callout {variant}".strip()
    lbl = f'<span class="t">{label}</span>' if label else ""
    return f'<div class="{cls}">{lbl}{content}</div>'


def _academic_card(n: int) -> str:
    suits = {
        range(1,  14): ("♣", False),
        range(14, 27): ("♦", True),
        range(27, 40): ("♥", True),
        range(40, 53): ("♠", False),
    }
    ranks = ("A","2","3","4","5","6","7","8","9","10","J","Q","K")
    if n == 53:
        return '<div class="rp-card joker red"><span class="rank" style="font-size:10px;">JKR</span><span class="csuit">★</span></div>'
    if n == 54:
        return '<div class="rp-card joker"><span class="rank" style="font-size:10px;">JKR</span><span class="csuit">☆</span></div>'
    for r, (sym, red) in suits.items():
        if n in r:
            rank = ranks[(n - 1) % 13]
            cls = "rp-card red" if red else "rp-card"
            return f'<div class="{cls}"><span class="rank">{rank}</span><span class="suit">{sym}</span><span class="csuit">{sym}</span></div>'
    return ""


def _cards_row(ns: list[int]) -> str:
    return '<div class="rp-card-row">' + "".join(_academic_card(n) for n in ns) + "</div>"


# ── Content helpers ───────────────────────────────────────────────────────────

def _load_raw() -> str:
    if not _RAPPORT_PATH.exists():
        return ""
    return _RAPPORT_PATH.read_text(encoding="utf-8")


def _load_pdf() -> bytes | None:
    if not _RAPPORT_PDF_PATH.exists():
        return None
    return _RAPPORT_PDF_PATH.read_bytes()


# ── Section renderers ─────────────────────────────────────────────────────────

def _render_topbar() -> None:
    st.markdown(
        '<div class="rp-topbar">'
        '<div class="rp-brand">'
        '<div class="mark"><strong>Pontifex</strong>&nbsp;·&nbsp;<em>chiffrement Solitaire</em></div>'
        '<span class="rp-chip">Rapport de projet</span>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    cards_html = _cards_row([53, 1, 14, 27, 40, 54])
    st.markdown(
        '<div class="rp-hero">'
        "<div>"
        '<div class="rp-eyebrow">Rapport de projet</div>'
        "<h1>Le chiffrement Solitaire<br/>"
        f'<em style="color:var(--rp-accent)">de Schneier (1999)</em></h1>'
        '<div class="lead">'
        "Étude, implémentation et analyse d'un chiffrement par flux"
        " exécutable à la main avec un jeu de 54 cartes."
        "</div>"
        "</div>"
        '<div class="rp-colophon">'
        '<div class="rp-eyebrow" style="margin-bottom:12px;">Résumé</div>'
        '<div style="font-family:var(--rp-serif);font-size:15px;line-height:1.6;'
        'color:var(--rp-ink2);">'
        "Ce rapport présente l'implémentation complète de l'algorithme Solitaire, "
        "un chiffrement par flux conçu par Bruce Schneier pour le roman "
        "<em>Cryptonomicon</em> (1999). Le projet couvre la formalisation des cinq opérations "
        "de permutation sur un paquet de 54 cartes, leur validation par les vecteurs "
        "officiels de Schneier, l'analyse des faiblesses cryptographiques connues "
        "(biais de Crowley, vulnérabilité à la réutilisation de clé), et l'intégration "
        "d'un assistant de type RAG (ChromaDB + Gemini) pour l'exploration interactive "
        "du corpus de référence."
        "</div>"
        f"<div style='margin-top:16px;'>{cards_html}"
        '<div style="font-family:var(--rp-sans);font-size:11.5px;color:var(--rp-faint);margin-top:6px;">'
        "Les quatre familles et les deux jokers — 54 cartes au total</div></div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_stats() -> None:
    st.markdown(
        '<div class="rp-stats" style="grid-template-columns:repeat(6,1fr);">'
        '<div class="rp-stat"><div class="v">54!</div><div class="s">≈ 2,31 × 10<sup>71</sup></div><div class="l">Espace de clés théorique</div></div>'
        '<div class="rp-stat"><div class="v">5</div><div class="s">opérations sur le paquet par valeur</div><div class="l">Cycle de génération</div></div>'
        '<div class="rp-stat"><div class="v">115/115</div><div class="s">vecteurs Schneier et cas limites vérifiés</div><div class="l">Tests passés</div></div>'
        '<div class="rp-stat"><div class="v">4,693</div><div class="s">bits &mdash; 99,8% de l&#39;entropie id&eacute;ale (H<sub>max</sub>=4,700)</div><div class="l">Entropie Shannon mesur&eacute;e</div></div>'
        '<div class="rp-stat"><div class="v">1/22,5</div><div class="s">au lieu de 1/26 attendu &mdash; biais de Crowley (+15%)</div><div class="l">Biais statistique</div></div>'
        '<div class="rp-stat"><div class="v">3 IA</div><div class="s">RAG, g&eacute;n&eacute;ration d&#39;images, interpr&eacute;tation analytique</div><div class="l">Composantes Gemini</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_s1() -> None:
    st.markdown(
        _section_head(1, "Introduction",
                      "Contexte, problématique et objectifs du projet."),
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown(
            '<div class="rp-prose">'
            "<p class='dropcap'>Le chiffrement <strong>Solitaire</strong> — également désigné sous le nom de"
            " <em>Pontifex</em> — a été conçu par Bruce Schneier en 1999, à la demande de"
            " Neal Stephenson pour son roman <em>Cryptonomicon</em>. L'objectif :"
            " disposer d'un algorithme de chiffrement par flux (<em>stream cipher</em>) pouvant"
            " être exécuté <strong>sans ordinateur</strong>, au moyen d'un jeu"
            " standard de 54 cartes.</p>"
            "<p>Ce qui le distingue des systèmes classiques (César, Vigenère), c'est que son"
            " état interne — l'ordre des 54 cartes — évolue à chaque lettre chiffrée. Ce"
            " mécanisme le rapproche des chiffrements par flux modernes tels que RC4 ou ChaCha20.</p>"
            "<p>Le présent projet poursuit trois objectifs : (i) implémenter l'algorithme complet "
            "avec validation par les vecteurs officiels ; (ii) proposer une démonstration pas-à-pas "
            "et une visualisation du paquet pour en faciliter la compréhension ; (iii) mettre en "
            "évidence les faiblesses connues (biais de Crowley, réutilisation de clé, <em>crib-dragging</em>) "
            "et les replacer dans le contexte de la cryptographie moderne.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            _panel(
                "<div style='display:grid;grid-template-columns:1fr auto;"
                "row-gap:7px;column-gap:18px;font-family:var(--rp-sans);font-size:13px;'>"
                "<div>Trèfles <span style='color:var(--rp-mute)'>(A → Roi)</span></div>"
                "<div style='font-family:var(--rp-mono)'>1 – 13</div>"
                "<div>Carreaux</div><div style='font-family:var(--rp-mono)'>14 – 26</div>"
                "<div>Cœurs</div><div style='font-family:var(--rp-mono)'>27 – 39</div>"
                "<div>Piques</div><div style='font-family:var(--rp-mono)'>40 – 52</div>"
                "<div>Joker A <span style='color:var(--rp-mute)'>(noir)</span></div>"
                "<div style='font-family:var(--rp-mono)'>53</div>"
                "<div>Joker B <span style='color:var(--rp-mute)'>(rouge)</span></div>"
                "<div style='font-family:var(--rp-mono)'>54</div>"
                "</div>",
                sunken=True, title="Le paquet en un coup d'œil",
            ),
            unsafe_allow_html=True,
        )


def _render_s2() -> None:
    st.markdown(
        _section_head(2, "L'algorithme Solitaire",
                      "Cinq opérations sur le paquet, répétées pour chaque valeur du flux."),
        unsafe_allow_html=True,
    )
    ops = [
        ("1", "Joker A descend d'une position",
         "Échange avec la carte en dessous. <strong>Cas limite :</strong> si Joker A est en dernière"
         " position, il passe en deuxième (jamais en première). Source classique d'erreur d'implémentation."),
        ("2", "Joker B descend de deux positions",
         "Retour circulaire. Si en avant-dernière : passe en 2ᵉ. Si en dernière : passe en 3ᵉ."
         " Le Joker B ne peut jamais être en première position."),
        ("3", "Triple coupe",
         "Les deux jokers divisent le paquet en trois segments. Le haut et le bas échangent leurs places."
         " Le segment central (jokers inclus) reste fixe. Segments vides = cas valide."),
        ("4", "Coupe comptée",
         "On lit la valeur Bridge de la <strong>dernière carte</strong> (= <em>n</em>)."
         " On prend les <em>n</em> premières cartes et on les insère juste avant la dernière."
         " La dernière carte <strong>ne bouge jamais</strong>."),
        ("5", "Lecture de la valeur de sortie",
         "On lit la valeur Bridge de la <strong>première carte</strong> (= <em>n</em>)."
         " La carte en position <em>n+1</em> donne la valeur du flux (1–26)."
         " Si c'est un joker → on recommence depuis l'opération 1."),
    ]
    cols = st.columns(5, gap="small")
    op_colors = ["#1e5930", "#0a4d68", "#7d4b10", "#7c3418", "#8a1538"]
    op_bgs    = ["#e7f0e7", "#e7ecf3", "#fde9d1", "#f6e0d7", "#f2dee5"]
    for i, (num, title, desc) in enumerate(ops):
        with cols[i]:
            st.markdown(
                f'<div style="background:{op_bgs[i]};border:1px solid {op_colors[i]}33;'
                f'padding:16px;height:100%;">'
                f'<div style="display:inline-flex;align-items:center;justify-content:center;'
                f'width:26px;height:26px;border-radius:50%;background:{op_colors[i]};'
                f'color:#fff;font-family:var(--rp-mono);font-size:12px;font-weight:700;'
                f'margin-bottom:10px;">{num}</div>'
                f'<div style="font-family:var(--rp-sans);font-size:12px;font-weight:600;'
                f'color:{op_colors[i]};margin-bottom:6px;">{title}</div>'
                f'<div style="font-family:var(--rp-sans);font-size:12.5px;line-height:1.5;'
                f'color:var(--rp-ink2);">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    st.markdown('<div class="sp-32"></div>', unsafe_allow_html=True)

    # Formulas
    col_e, col_d = st.columns(2, gap="large")
    with col_e:
        st.markdown("**Chiffrement lettre par lettre**")
        st.latex(
            r"C = \begin{cases}"
            r"(P + K) \bmod 26 & \text{si } (P + K) \not\equiv 0 \\"
            r"26 & \text{sinon (Z, pas A)}"
            r"\end{cases}"
        )
    with col_d:
        st.markdown("**Déchiffrement**")
        st.latex(
            r"P = \begin{cases}"
            r"(C - K) \bmod 26 & \text{si } (C - K) > 0 \\"
            r"(C - K) + 26 & \text{sinon}"
            r"\end{cases}"
        )


def _render_s3() -> None:
    st.markdown(
        _section_head(3, "Choix techniques",
                      "Python + Streamlit — séparation nette entre logique, interface et IA."),
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown(
            '<div class="rp-prose">'
            "<h3>Pourquoi Python</h3>"
            "<ul>"
            "<li><strong>Lisibilité :</strong> opérations sur le paquet (inversions, coupes)"
            " naturelles avec les slices de listes.</li>"
            "<li><strong>Écosystème IA :</strong> ChromaDB, google-generativeai,"
            " scikit-learn — matures et disponibles.</li>"
            "<li><strong>Visualisation :</strong> Plotly + Streamlit, interface interactive"
            " sans JavaScript côté client.</li>"
            "<li><strong>Tests :</strong> pytest, syntaxe claire, intégration aux outils de couverture.</li>"
            "</ul>"
            "<h3>Principes de conception</h3>"
            "<ul>"
            "<li><strong>Immutabilité :</strong> le paquet est un <code>tuple</code>."
            " Chaque opération retourne un nouveau tuple — aucune mutation en place.</li>"
            "<li><strong>Séparation core/ui :</strong> l'algorithme fonctionne en CLI ou"
            " en tests sans démarrer Streamlit.</li>"
            "<li><strong>Dataclasses typées</strong> pour les étapes de la démo"
            " (vérification statique par mypy/pyright).</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            _panel(
                '<div class="rp-mono" style="font-size:12px;line-height:1.5;">'
                "crypto/\n"
                "├── core/          ← Algorithme pur\n"
                "│   ├── deck.py\n"
                "│   ├── solitaire.py\n"
                "│   ├── keystream.py\n"
                "│   └── encryption.py\n"
                "├── ui/            ← Streamlit\n"
                "│   ├── components.py\n"
                "│   ├── tab_*.py\n"
                "│   └── styles.py\n"
                "├── visuals/\n"
                "├── ai/            ← RAG ChromaDB\n"
                "├── security/\n"
                "└── tests/         ← 115 tests\n"
                "</div>",
                title="Arborescence",
            ),
            unsafe_allow_html=True,
        )


def _render_s4() -> None:
    st.markdown(
        _section_head(4, "Implémentation",
                      "Fonctions pures, tuples immuables et dataclasses typées."),
        unsafe_allow_html=True,
    )
    st.markdown(
        _callout(
            "Le paquet est représenté comme un <strong>tuple immuable</strong> d'entiers."
            " L'immutabilité élimine les bugs d'effets de bord et simplifie le débogage :"
            " chaque opération retourne un nouveau tuple, jamais une mutation en place.",
            label="Invariant fondamental",
        ),
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("**`core/deck.py`** — représentation du paquet")
        st.code("def create_deck() -> tuple[int, ...]:\n    return tuple(range(1, 55))", language="python")
        st.markdown("**`core/solitaire.py`** — les 5 opérations")
        st.markdown(
            '<div class="rp-prose" style="font-size:15px;">'
            "<p>Chaque opération est une fonction pure"
            " <code>(tuple) → tuple</code>. Les 5 sont composées dans"
            " <code>solitaire_step()</code>. <code>generate_keystream_value()</code>"
            " répète le cycle jusqu'à une valeur non-joker.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("**`ui/demo_engine.py`** — dataclass typée")
        st.code(
            "@dataclass\nclass EncryptionStep:\n"
            "    letter_idx:   int\n"
            "    plain_char:   str\n"
            "    op_num:       int | str\n"
            "    op_name:      str\n"
            "    op_color:     str\n"
            "    deck_before:  tuple[int, ...]\n"
            "    deck_after:   tuple[int, ...]\n"
            "    center_cards: list[int]\n"
            "    highlights:   dict[int, str]\n"
            "    output_val:   int | None = None\n"
            "    cipher_char:  str = ''",
            language="python",
        )


def _render_s5() -> None:
    from pathlib import Path
    import base64

    st.markdown(
        _section_head(5, "Visuels — génération des 54 cartes",
                      "Pipeline de génération d'images et trois modes d'affichage."),
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown(
            '<div class="rp-prose">'
            "<h3>Génération par IA (Gemini Image)</h3>"
            "<p>Les 54 cartes du thème sombre ont été générées via l'API <strong>Gemini Image</strong>"
            " à l'aide d'un prompt structuré garantissant la cohérence stylistique entre familles."
            " Un pipeline <strong>Pillow</strong> post-traite chaque image : recadrage à 300×420 px,"
            " surimpression du rang, du symbole de famille et du numéro Bridge.</p>"
            "<h3>Trois thèmes disponibles</h3>"
            "<ul>"
            "<li><strong>Cyberpunk (sombre)</strong> — 54 PNG générés par Gemini Image</li>"
            "<li><strong>Classique (réaliste)</strong> — vraies cartes photographiées</li>"
            "<li><strong>Académique (SVG)</strong> — cartes minimalistes CSS, utilisées dans ce rapport</li>"
            "</ul>"
            "<p>Le module <code>visuals/card_loader.py</code> centralise le chargement"
            " et le cache des images selon le thème actif, avec un fallback SVG"
            " si l'image est absente.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        sample_cards = _cards_row([1, 14, 27, 40, 53, 54])
        st.markdown(
            _panel(
                f'<div class="rp-eyebrow" style="margin-bottom:10px;">'
                "Style académique (SVG)</div>"
                f'<div style="font-family:var(--rp-sans);font-size:12px;'
                f'color:var(--rp-mute);margin-bottom:12px;">'
                "Rendu CSS pur · As de chaque famille + jokers</div>"
                f"{sample_cards}",
                sunken=True,
            ),
            unsafe_allow_html=True,
        )

    # Screenshot de l'interface cartes classiques
    st.markdown('<div class="sp-24"></div>', unsafe_allow_html=True)
    _img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "app_deskcarteclassique.png"
    if _img.exists():
        st.image(str(_img), caption="Interface de chiffrement — paquet de 54 cartes en thème classique (réaliste).", use_container_width=True)

    # Carte générée à titre d'exemple
    _king = Path(__file__).parent.parent / "docs" / "rapport_assets" / "13_king.png"
    if _king.exists():
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.image(str(_king), caption="Roi de Trèfle — thème Cyberpunk généré par Gemini Image.", width=200)


def _render_s6() -> None:
    from pathlib import Path

    st.markdown(
        _section_head(6, "Intégration IA",
                      "Trois composantes : RAG, génération d'images et interprétation analytique."),
        unsafe_allow_html=True,
    )

    # 6a. RAG
    st.markdown(
        _panel(
            '<div class="rp-eyebrow" style="margin-bottom:8px;">Composante 1 — Assistant RAG</div>'
            '<div class="rp-prose">'
            "<h3>Architecture du RAG (ChromaDB + Gemini 2.5 Flash)</h3>"
            "<ol style='padding-left:20px;line-height:1.9;'>"
            "<li>Base de connaissances construite à partir de fichiers <code>.txt</code>"
            " dans <code>ai/knowledge/</code>, complétée par des <em>chunks</em> codés en dur.</li>"
            "<li>Au démarrage, tous les chunks sont encodés via <strong>gemini-embedding-001</strong>"
            " et stockés dans une collection <strong>ChromaDB</strong> en mémoire.</li>"
            "<li>Pour chaque question, les 5 passages les plus proches (similarité cosinus)"
            " sont injectés dans le prompt de <strong>Gemini 2.5 Flash</strong>.</li>"
            "</ol>"
            "<p>L'assistant s'appuie sur les sources primaires (Schneier 1999, Crowley 1999),"
            " plutôt que sur les connaissances générales du modèle.</p>"
            "</div>",
        ),
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        _rag_img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "app_rag.png"
        if _rag_img.exists():
            st.image(str(_rag_img),
                     caption="Assistant RAG : réponse sur l'espace de clés — valeurs issues des chunks ChromaDB indexés.",
                     use_container_width=True)
    with col2:
        st.code(
            "def retrieve(self, query: str,\n"
            "             n_results: int = 5\n"
            "             ) -> list[dict]:\n"
            "    emb = self._embed([query])[0]\n"
            "    return self._collection.query(\n"
            "        query_embeddings=[emb],\n"
            "        n_results=n_results,\n"
            "        include=[\n"
            "            'documents',\n"
            "            'metadatas',\n"
            "            'distances',\n"
            "        ],\n"
            "    )",
            language="python",
        )

    st.markdown('<div class="sp-32"></div>', unsafe_allow_html=True)

    # 6b. Generation d'images
    st.markdown(
        _panel(
            '<div class="rp-eyebrow" style="margin-bottom:8px;">Composante 2 — Génération d\'images par Gemini Image</div>'
            '<div class="rp-prose">'
            "<p>Les 54 cartes du thème Cyberpunk ont été produites via l'API <strong>Gemini Image</strong>"
            " avec un prompt structuré par famille garantissant la cohérence visuelle."
            " Un pipeline <code>Pillow</code> normalise les dimensions, surimprime le numéro Bridge,"
            " le rang et le symbole de famille, et exporte les PNG dans <code>visuals/real_deck/</code>."
            " Le module <code>visuals/card_loader.py</code> centralise le chargement et le cache.</p>"
            "</div>",
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sp-32"></div>', unsafe_allow_html=True)

    # 6c. Interpretation analytique
    st.markdown(
        _panel(
            '<div class="rp-eyebrow" style="margin-bottom:8px;">Composante 3 — Interprétation analytique (Gemini 2.5 Pro)</div>'
            '<div class="rp-prose">'
            "<p>L'onglet Analyse intègre un bouton <em>Interpréter ces résultats avec l'IA</em>."
            " Les métriques calculées (chi2, entropie de Shannon, IC, test des runs NIST)"
            " sont transmises à <strong>Gemini 2.5 Pro</strong> positionné comme cryptanalyste"
            " mathématicien. Il produit une synthèse académique en prose, sans emoji.</p>"
            "</div>",
        ),
        unsafe_allow_html=True,
    )

    _interp_img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "app_interpretationanalsye.png"
    if _interp_img.exists():
        st.image(str(_interp_img),
                 caption="Interprétation IA des résultats statistiques par Gemini 2.5 Pro : synthèse académique du chi2, de l'entropie et du test des runs.",
                 use_container_width=True)


def _render_s7() -> None:
    st.markdown(
        _section_head(7, "Sécurité et analyse statistique",
                      "Espace de clés, tests d'uniformité et vulnérabilités structurelles."),
        unsafe_allow_html=True,
    )
    st.latex(r"|\mathcal{K}| = 54! \approx 2{,}31 \times 10^{71} \approx 2^{237}")

    st.markdown(
        '<div class="rp-prose" style="font-size:15px;margin-bottom:24px;">'
        "L'onglet <strong>Analyse</strong> de cette application permet d'exécuter en temps réel "
        "des tests statistiques rigoureux sur le flux de clés généré par Solitaire. Les calculs "
        "incluent l'entropie de Shannon $H(X)$, l'indice de coïncidence, l'autocorrélation $C(\\tau)$, "
        "et le test des runs du NIST."
        "</div>",
        unsafe_allow_html=True,
    )

    # Capture de l'onglet Analyse
    from pathlib import Path
    _analyse_img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "app_analyse.png"
    if _analyse_img.exists():
        st.image(str(_analyse_img),
                 caption="Onglet Analyse : distribution empirique, autocorrelation C(tau), entropie de Shannon et indice de coincidence -- calculs en temps reel sur le flux Solitaire.",
                 use_container_width=True)
    st.markdown('<div class="sp-24"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("**Biais de Crowley (1999)**")
        st.markdown(
            '<div class="rp-prose" style="font-size:15px;">'
            "Contrairement à une distribution uniforme où $\\Pr[K_2 = K_1] = 1/26$, "
            "le biais inhérent aux coupes de Solitaire donne :"
            "</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"\Pr[K_2 = K_1] \approx \frac{1}{22{,}5}")
        st.markdown(
            '<div class="rp-prose" style="font-size:15px;">'
            "Cet écart significatif (>15%) devient mesurable via un test du $\\chi^2$ "
            "dès que l'échantillon dépasse quelques milliers de caractères."
            "</div>",
            unsafe_allow_html=True,
        )
        _chi2_img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "chi2_graph.png"
        if _chi2_img.exists():
            st.image(str(_chi2_img), caption="Distribution des valeurs du flux Solitaire (1 000 échantillons) — test d'uniformité χ².", use_container_width=True)
    with col2:
        st.markdown("**Réutilisation de clé**")
        st.markdown(
            '<div class="rp-prose" style="font-size:15px;">'
            "Le chiffrement par flot implique :"
            "</div>",
            unsafe_allow_html=True,
        )
        st.latex(
            r"C_1 - C_2 \equiv M_1 - M_2 \pmod{26}"
        )
        st.markdown(
            '<div class="rp-prose" style="font-size:15px;">'
            "L'adversaire obtient la différence mathématique des clairs sans "
            "connaître le flux $K$. Cela permet une attaque par texte clair connu "
            "ou deviné."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        _callout(
            "<strong>Crib-dragging :</strong> en supposant qu'un mot $w$ apparaît dans $M_1$, "
            "on glisse $w$ sur chaque position $j$ pour déduire un fragment de $M_2$ : "
            "<br/><center>$M_2[j:j+k] = w - (C_1 - C_2)[j:j+k] \\pmod{26}$</center><br/>"
            "Un score fondé sur les probabilités d'apparition des lettres valide l'hypothèse.",
            label="Attaque par texte supposé",
            variant="warn",
        ),
        unsafe_allow_html=True,
    )

    _avalanche_img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "avalanche_graph.png"
    if _avalanche_img.exists():
        st.markdown('<div class="sp-16"></div>', unsafe_allow_html=True)
        st.image(str(_avalanche_img), caption="Effet avalanche : % de valeurs du flux modifiées selon la distance de modification de la clé. Convergence vers ~50% dès la 2ᵉ modification.", use_container_width=True)


def _render_s8() -> None:
    st.markdown(
        _section_head(8, "Tests",
                      "Validation complète par les vecteurs de Schneier et les cas limites."),
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([2, 3], gap="large")
    with col1:
        st.markdown(
            '<div class="rp-stat" style="margin-bottom:24px;">'
            '<div class="v">115/115</div>'
            '<div class="s">tests passés, 0 échec</div>'
            '<div class="l">Suite pytest complète</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            _panel(
                "<ul style='font-family:var(--rp-sans);font-size:12.5px;"
                "line-height:1.85;margin:0;padding-left:16px;color:var(--rp-ink2);'>"
                "<li>test_deck.py — ~15 tests</li>"
                "<li>test_solitaire.py — ~20 tests</li>"
                "<li>test_encryption.py — ~15 tests</li>"
                "<li>test_schneier_vectors.py — 3 vecteurs</li>"
                "<li>test_vectors.py — ~10 vecteurs étendus</li>"
                "<li>test_edge_cases.py — ~15 cas limites</li>"
                "<li>test_integration.py — ~10 tests</li>"
                "<li>test_performance.py — ~7 tests O(n)</li>"
                "</ul>",
                sunken=True, title="8 fichiers de tests",
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("**Vecteurs officiels de Bruce Schneier**")
        st.markdown(
            "<table style='width:100%;border-collapse:collapse;"
            "font-family:var(--rp-sans);font-size:13px;'>"
            "<thead><tr>"
            "<th style='padding:9px 12px;border-bottom:2px solid var(--rp-ink,#1a1a1a);"
            "font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:var(--rp-mute);"
            "text-align:left;'>#</th>"
            "<th style='padding:9px 12px;border-bottom:2px solid var(--rp-ink,#1a1a1a);"
            "font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:var(--rp-mute);"
            "text-align:left;'>Clé</th>"
            "<th style='padding:9px 12px;border-bottom:2px solid var(--rp-ink,#1a1a1a);"
            "font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:var(--rp-mute);"
            "text-align:left;'>Clair</th>"
            "<th style='padding:9px 12px;border-bottom:2px solid var(--rp-ink,#1a1a1a);"
            "font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:var(--rp-mute);"
            "text-align:left;'>Chiffré</th>"
            "<th style='padding:9px 12px;border-bottom:2px solid var(--rp-ink,#1a1a1a);"
            "text-align:center;'>✓</th>"
            "</tr></thead><tbody>"
            "<tr><td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule,#d8d3c5);'>1</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);'><em>aucune</em></td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "font-family:var(--rp-mono);font-size:12px;letter-spacing:0.06em;'>AAAAAAAAAA</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "font-family:var(--rp-mono);font-size:12px;letter-spacing:0.06em;color:var(--rp-accent);'>EXKYIZSGEH</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "text-align:center;color:var(--rp-ok);font-weight:700;'>✓</td></tr>"
            "<tr><td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);'>2</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "font-family:var(--rp-mono);font-size:12px;'>FOO</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "font-family:var(--rp-mono);font-size:12px;letter-spacing:0.06em;'>AAAAAAAAAAAAAAA</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "font-family:var(--rp-mono);font-size:12px;letter-spacing:0.06em;color:var(--rp-accent);'>ITHZUJIWGRFARMW</td>"
            "<td style='padding:9px 12px;border-bottom:1px solid var(--rp-rule);"
            "text-align:center;color:var(--rp-ok);font-weight:700;'>✓</td></tr>"
            "<tr><td style='padding:9px 12px;'>3</td>"
            "<td style='padding:9px 12px;font-family:var(--rp-mono);font-size:12px;'>CRYPTONOMICON</td>"
            "<td style='padding:9px 12px;font-family:var(--rp-mono);font-size:12px;letter-spacing:0.06em;'>SOLITAIREX</td>"
            "<td style='padding:9px 12px;font-family:var(--rp-mono);font-size:12px;"
            "letter-spacing:0.06em;color:var(--rp-accent);'>KIRAKSFJAN</td>"
            "<td style='padding:9px 12px;text-align:center;color:var(--rp-ok);font-weight:700;'>✓</td></tr>"
            "</tbody></table>",
            unsafe_allow_html=True,
        )

    # Graphique de complexité O(n)
    from pathlib import Path
    _complexite_img = Path(__file__).parent.parent / "docs" / "rapport_assets" / "complexite_graph.png"
    if _complexite_img.exists():
        st.markdown('<div class="sp-24"></div>', unsafe_allow_html=True)
        st.markdown("**Complexité temporelle O(n) — mesures expérimentales**")
        st.image(str(_complexite_img),
                 caption="Temps d'exécution (échelle log-log) en fonction du nombre de caractères : linéarité confirmée de 1 à 10 000 caractères.",
                 use_container_width=True)


def _render_s9() -> None:
    st.markdown(
        _section_head(9, "Difficultés rencontrées",
                      "Cas limites, cohérence visuelle et intégration de l'assistant."),
        unsafe_allow_html=True,
    )
    difficulties = [
        ("Cas limites des jokers",
         "La gestion du retour circulaire des jokers A et B constitue la principale source "
         "d'erreurs d'implémentation. Lorsque le Joker A se trouve en dernière position, il doit "
         "passer en deuxième et non en première — un détail que la description originale de "
         "Schneier laisse ambigu. Plusieurs sessions de débogage ont été nécessaires, guidées par "
         "les vecteurs de test officiels, avant d'obtenir un comportement conforme."),
        ("Cohérence des visuels entre thèmes",
         "La génération de 54 images par l'API Gemini ne garantit pas la cohérence stylistique "
         "entre les familles. Un pipeline de post-traitement Pillow a été mis en place pour "
         "normaliser les dimensions, ajouter les indicateurs (valeur Bridge, symbole de famille) "
         "et harmoniser les teintes de fond. Le maintien de trois thèmes simultanés "
         "(moderne, classique, SVG) impose une abstraction rigoureuse dans le module "
         "<code>card_loader.py</code>."),
        ("Qualité des réponses du RAG",
         "L'assistant IA produit des réponses pertinentes lorsque la question correspond bien "
         "aux passages indexés. En revanche, pour des questions transversales (comparaison "
         "Solitaire/AES, par exemple), la similarité cosinus retourne parfois des passages "
         "peu pertinents. L'ajout de chunks codés en dur pour les thèmes récurrents a permis "
         "d'améliorer la couverture sans complexifier le pipeline d'ingestion."),
    ]
    for title, desc in difficulties:
        st.markdown(
            f'<div class="rp-panel" style="margin-bottom:16px;">'
            f'<div class="ph">{title}</div>'
            f'<div style="font-family:var(--rp-serif);font-size:15px;line-height:1.6;'
            f'color:var(--rp-ink2);">{desc}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_s10() -> None:
    st.markdown(
        _section_head(10, "Conclusion",
                      "Bilan, limites de l'algorithme et mise en perspective."),
        unsafe_allow_html=True,
    )

    st.markdown("**Bilan du projet**")
    st.markdown(
        '<div class="rp-twocol" style="margin-bottom:36px;">'
        "<p>L'implémentation couvre l'ensemble de l'algorithme Solitaire (version complète et"
        " version simplifiée), avec une validation rigoureuse contre les vecteurs officiels de"
        " Schneier. L'interface Streamlit rend l'algorithme accessible à un non-spécialiste"
        " grâce à la démonstration pas-à-pas et à l'assistant IA.</p>"
        "<p>Les éléments les plus instructifs du projet ont été : la gestion des cas limites des"
        " jokers, qui révèle à quel point un détail d'implémentation peut corrompre l'intégralité"
        " du flux ; la démonstration de la réutilisation de clé, qui illustre pourquoi les stream"
        " ciphers demandent une discipline d'usage plus stricte ; et l'intégration du RAG, qui"
        " montre comment combiner une base structurée et un LLM pour des réponses fiables et sourcées.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("**Limites de Solitaire**")
    limits = [
        ("01 — Biais statistique",
         "Le flux n'est pas indistinguable d'une source aléatoire uniforme (Crowley, 1999),"
         " contrairement à ce que requiert un stream cipher moderne."),
        ("02 — Vitesse",
         "≈ 4 opérations par lettre. En Python non optimisé, quelques ms par lettre —"
         " des millions de fois plus lent qu'AES-CTR."),
        ("03 — Dépendance au mot de passe",
         "L'espace effectif dépend de la qualité du mot de passe."
         " Schneier recommande 64–80 caractères — irréaliste en pratique."),
        ("04 — Pas d'authentification",
         "Aucune garantie d'intégrité. Un adversaire actif peut modifier le chiffré sans détection."),
    ]
    cols = st.columns(4, gap="small")
    for i, (label, desc) in enumerate(limits):
        with cols[i]:
            st.markdown(
                f'<div class="rp-panel" style="height:100%;">'
                f'<div class="rp-eyebrow" style="color:var(--rp-err,#8a1515);">{label}</div>'
                f'<div style="font-family:var(--rp-sans);font-size:13px;line-height:1.6;'
                f'color:var(--rp-ink2);margin-top:8px;">{desc}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="sp-32"></div>', unsafe_allow_html=True)
    st.markdown("**Comparaison avec les algorithmes modernes**")
    st.markdown(
        "<table style='width:100%;border-collapse:collapse;"
        "font-family:var(--rp-sans);font-size:13px;margin:16px 0 24px;'>"
        "<thead><tr>"
        + "".join(
            f'<th style="padding:9px 14px;border-bottom:2px solid var(--rp-ink,#1a1a1a);'
            f'font-size:11px;letter-spacing:0.1em;text-transform:uppercase;'
            f'color:var(--rp-mute);text-align:left;">{h}</th>'
            for h in ["Critère", "Solitaire", "AES-GCM", "ChaCha20-Poly1305"]
        )
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join(
                f'<td style="padding:9px 14px;border-bottom:1px solid var(--rp-rule,#d8d3c5);">{c}</td>'
                for c in row
            ) + "</tr>"
            for row in [
                ["Type", "Stream cipher", "Block cipher (CTR)", "Stream cipher"],
                ["Espace de clés", "~2²³⁷ (théorique)", "2¹²⁸ – 2²⁵⁶", "2²⁵⁶"],
                ["Biais statistique", "Oui (Crowley)", "Non", "Non"],
                ["Authentification", "Non", "Oui (GCM)", "Oui (Poly1305)"],
                ["Sans ordinateur", "Oui ✓", "Non", "Non"],
                ["Usage recommandé", "Pédagogique", "Chiffrement général", "Mobile, TLS 1.3"],
            ]
        )
        + "</tbody></table>",
        unsafe_allow_html=True,
    )

    st.markdown(
        _callout(
            "Solitaire reste avant tout un objet <strong>pédagogique</strong> :"
            " il démontre qu'un algorithme de chiffrement peut être décrit en quelques pages et"
            " exécuté sans support électronique, tout en produisant un flux résistant à une analyse"
            " naïve. Ses faiblesses illustrent en retour pourquoi la cryptographie contemporaine"
            " privilégie des constructions dont la sécurité est mathématiquement démontrable.",
            label="Synthèse",
            variant="info",
        ),
        unsafe_allow_html=True,
    )

    # ── Références ──
    st.markdown('<div class="sp-48"></div>', unsafe_allow_html=True)
    st.markdown(
        _section_head(11, "Références",
                      "Sources primaires consultées pour ce projet."),
        unsafe_allow_html=True,
    )
    refs = [
        ("[1] B. Schneier, « The Solitaire Encryption Algorithm », 1999. "
         "Disponible sur : <em>https://www.schneier.com/academic/solitaire/</em>"),
        ("[2] P. Crowley, « Problems with Bruce Schneier's Solitaire », 1999. "
         "Analyse statistique du biais de répétition du flux."),
        ("[3] N. Stephenson, <em>Cryptonomicon</em>, Avon Books, 1999. "
         "Roman à l'origine de la conception de l'algorithme."),
        ("[4] NIST, « A Statistical Test Suite for Random and Pseudorandom "
         "Number Generators for Cryptographic Applications », SP 800-22, 2010."),
        ("[5] Documentation Streamlit, <em>https://docs.streamlit.io</em>"),
        ("[6] Documentation ChromaDB, <em>https://docs.trychroma.com</em>"),
    ]
    st.markdown(
        '<div class="rp-prose" style="font-size:14.5px;line-height:1.8;">'
        + "".join(f"<p style='margin:6px 0;'>{r}</p>" for r in refs)
        + "</div>",
        unsafe_allow_html=True,
    )



# ── Point d'entrée ────────────────────────────────────────────────────────────

def render() -> None:
    """Affiche le rapport complet style éditorial académique."""
    st.markdown(_CSS, unsafe_allow_html=True)

    # Conteneur principal avec les variables CSS du design
    st.markdown('<div class="rp">', unsafe_allow_html=True)

    # ── Download bar ──
    raw = _load_raw()
    pdf_data = _load_pdf()
    col_md, col_pdf, _ = st.columns([1, 1, 4])
    with col_md:
        if raw:
            st.download_button(
                label=" Télécharger .md",
                data=raw.encode("utf-8"),
                file_name="rapport_solitaire.md",
                mime="text/markdown",
            )
        else:
            st.button(" .md indisponible", disabled=True)
    with col_pdf:
        if pdf_data is not None:
            st.download_button(
                label=" Télécharger .pdf",
                data=pdf_data,
                file_name="rapport_solitaire.pdf",
                mime="application/pdf",
            )
        else:
            st.button(
                " PDF indisponible",
                disabled=True,
                help="Ajoutez docs/rapport_final.pdf pour activer ce téléchargement.",
            )

    # ── Topbar ──
    _render_topbar()

    # ── Hero ──
    _render_hero()

    # ── Stats blocks ──
    _render_stats()

    # ── Sections ──
    _render_s1()
    st.divider()
    _render_s2()
    st.divider()
    _render_s3()
    st.divider()
    _render_s4()
    st.divider()
    _render_s5()
    st.divider()
    _render_s6()
    st.divider()
    _render_s7()
    st.divider()
    _render_s8()
    st.divider()
    _render_s9()
    st.divider()
    _render_s10()

    st.markdown("</div>", unsafe_allow_html=True)
