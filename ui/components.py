"""Sidebar et en-tête de l'application Streamlit."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class AppConfig:
    """Paramètres de la sidebar."""
    algorithm: str
    passphrase: str | None


def render_sidebar() -> AppConfig:
    """Affiche la sidebar et renvoie la configuration courante."""
    with st.sidebar:
        st.markdown("## Configuration")
        algo = st.radio(
            "Algorithme",
            ["Solitaire complet", "Solitaire simplifié"],
            help="Le Solitaire complet utilise les 5 opérations de Schneier.",
        )
        st.divider()
        key_mode = st.radio(
            "Clé de chiffrement",
            ["Aucune (deck standard)", "Phrase de passe"],
        )
        passphrase: str | None = None
        if key_mode == "Phrase de passe":
            raw = st.text_input(
                "Phrase de passe",
                type="password",
                placeholder="Ex: CRYPTONOMICON",
                help="Lettres uniquement. Majuscules automatiques.",
            )
            passphrase = raw.strip() or None
        st.divider()
        st.markdown(
            '<div style="font-size:10px;color:#30363d;font-family:\'JetBrains Mono\',monospace;'
            'letter-spacing:0.06em;border-top:1px solid #21262d;padding-top:10px;margin-top:4px;">'
            "SOLITAIRE &bull; Bruce Schneier (1999)<br>"
            "Python &bull; Streamlit &bull; ChromaDB</div>",
            unsafe_allow_html=True,
        )
    return AppConfig(algorithm=algo, passphrase=passphrase)


def render_header() -> None:
    """Affiche le titre et le sous-titre de l'application."""
    st.markdown(
        '<h1 class="term-title">&gt; SOLITAIRE</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="term-byline">'
        "Algorithme de chiffrement par flux &mdash; Bruce Schneier, 1999</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="term-divider">&#9830; &nbsp; &#9824; &nbsp; &#9829; &nbsp; &#9827;</p>',
        unsafe_allow_html=True,
    )
