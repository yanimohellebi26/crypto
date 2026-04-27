"""Sidebar et en-tête de l'application Streamlit."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from core.deck import shuffle_deck
from visuals.card_loader import classic_theme_available

_CARD_THEME_MAP: dict[str, str] = {
    "Moderne (sombre)": "modern",
    "Classique (réaliste)": "classic",
    "Minimaliste (SVG)": "academic",
}
_CARD_THEME_REVERSE: dict[str, str] = {v: k for k, v in _CARD_THEME_MAP.items()}
_CARD_THEME_LABELS = list(_CARD_THEME_MAP.keys())

_UI_THEME_MAP: dict[str, str] = {
    "Sombre": "dark",
    "Clair": "light",
}
_UI_THEME_REVERSE: dict[str, str] = {v: k for k, v in _UI_THEME_MAP.items()}
_UI_THEME_LABELS = list(_UI_THEME_MAP.keys())


@dataclass(frozen=True)
class AppConfig:
    """Paramètres de la sidebar."""
    algorithm: str
    passphrase: str | None
    card_theme: str
    ui_theme: str
    initial_deck: tuple[int, ...] | None = None


def render_sidebar() -> AppConfig:
    """Affiche la sidebar et renvoie la configuration courante."""
    # ── Valeurs appliquées (ce qui est réellement actif) ──
    if "applied_algorithm" not in st.session_state:
        st.session_state["applied_algorithm"] = "Solitaire complet"
    if "applied_passphrase" not in st.session_state:
        st.session_state["applied_passphrase"] = None
    if "applied_initial_deck" not in st.session_state:
        st.session_state["applied_initial_deck"] = None
    if "applied_card_theme" not in st.session_state:
        st.session_state["applied_card_theme"] = st.session_state.get("card_theme", "modern")
    if "applied_ui_theme" not in st.session_state:
        st.session_state["applied_ui_theme"] = st.session_state.get("ui_theme", "light")

    # ── Valeurs des widgets (ce que l'utilisateur a saisi) ──
    if "cfg_algorithm_input" not in st.session_state:
        st.session_state["cfg_algorithm_input"] = st.session_state["applied_algorithm"]
    if "cfg_key_mode_input" not in st.session_state:
        if st.session_state["applied_initial_deck"] is not None:
            st.session_state["cfg_key_mode_input"] = "Deck aléatoire"
        elif st.session_state["applied_passphrase"]:
            st.session_state["cfg_key_mode_input"] = "Phrase de passe"
        else:
            st.session_state["cfg_key_mode_input"] = "Aucune (deck standard)"
    if "cfg_passphrase_input" not in st.session_state:
        st.session_state["cfg_passphrase_input"] = st.session_state["applied_passphrase"] or ""
    if "cfg_card_theme_input" not in st.session_state:
        applied_ct = st.session_state["applied_card_theme"]
        st.session_state["cfg_card_theme_input"] = _CARD_THEME_REVERSE.get(applied_ct, "Moderne (sombre)")
    if "cfg_ui_theme_input" not in st.session_state:
        applied_ut = st.session_state["applied_ui_theme"]
        st.session_state["cfg_ui_theme_input"] = _UI_THEME_REVERSE.get(applied_ut, "Clair")

    with st.sidebar:
        st.markdown("## Configuration")

        # ── Algorithme ──
        algo = st.radio(
            "Algorithme",
            ["Solitaire complet", "Solitaire simplifié"],
            key="cfg_algorithm_input",
            help="Le Solitaire complet utilise les 5 opérations de Schneier.",
        )
        st.divider()

        # ── Clé de chiffrement ──
        key_mode = st.radio(
            "Clé de chiffrement",
            ["Aucune (deck standard)", "Phrase de passe", "Deck aléatoire"],
            key="cfg_key_mode_input",
            help="Un deck aléatoire offre l'entropie maximale (recommandation de Schneier).",
        )
        passphrase: str | None = None
        pending_initial_deck: tuple[int, ...] | None = None

        if key_mode == "Phrase de passe":
            raw = st.text_input(
                "Phrase de passe",
                type="password",
                key="cfg_passphrase_input",
                placeholder="Ex: CRYPTONOMICON",
                help="Sert à initialiser le paquet par permutation (méthode Schneier).",
            )
            passphrase = raw.strip() or None
            st.caption(
                "Une même phrase de passe produit le même deck initial, "
                "donc le même flux de clés pour le correspondant."
            )
        elif key_mode == "Deck aléatoire":
            if "cfg_random_deck" not in st.session_state:
                st.session_state["cfg_random_deck"] = shuffle_deck()
            pending_initial_deck = st.session_state["cfg_random_deck"]
            if st.button("Nouveau mélange", key="btn_reshuffle"):
                st.session_state["cfg_random_deck"] = shuffle_deck()
                pending_initial_deck = st.session_state["cfg_random_deck"]
            if st.button("Réinitialiser (deck standard)", key="btn_reset_to_standard"):
                st.session_state["applied_initial_deck"] = None
                st.session_state.pop("cfg_random_deck", None)
                st.session_state.pop("cfg_key_mode_input", None)
                st.rerun()
            deck_str = "-".join(str(c) for c in pending_initial_deck)
            st.text_area(
                "Ordre du deck (partagez avec votre correspondant)",
                value=deck_str,
                height=80,
                key="cfg_deck_display",
            )

        st.divider()

        # ── Thème de l'interface ──
        ui_theme_label = st.radio(
            "Thème de l'interface",
            _UI_THEME_LABELS,
            key="cfg_ui_theme_input",
            help="Sombre : interface monospace sur fond sombre. Clair : style académique.",
        )
        ui_theme = _UI_THEME_MAP[ui_theme_label]

        st.divider()

        # ── Style des cartes ──
        card_theme_label = st.radio(
            "Style des cartes",
            _CARD_THEME_LABELS,
            key="cfg_card_theme_input",
            help=(
                "Moderne : images au rendu sombre. "
                "Classique : cartes réalistes photographiées. "
                "Minimaliste : cartes SVG, toujours disponibles."
            ),
        )
        card_theme = _CARD_THEME_MAP[card_theme_label]

        # ── Détection des changements en attente ──
        has_pending_changes = (
            algo != st.session_state["applied_algorithm"]
            or passphrase != st.session_state["applied_passphrase"]
            or pending_initial_deck != st.session_state["applied_initial_deck"]
            or card_theme != st.session_state["applied_card_theme"]
            or ui_theme != st.session_state["applied_ui_theme"]
        )

        if has_pending_changes:
            st.info("Changements en attente — cliquez sur Appliquer.")

        if st.button("Appliquer la configuration", type="primary", use_container_width=True):
            st.session_state["applied_algorithm"] = algo
            st.session_state["applied_passphrase"] = passphrase
            st.session_state["applied_initial_deck"] = pending_initial_deck
            st.session_state["applied_card_theme"] = card_theme
            st.session_state["card_theme"] = card_theme
            st.session_state["applied_ui_theme"] = ui_theme
            st.session_state["ui_theme"] = ui_theme
            st.success("Configuration appliquée.")

        applied_theme = st.session_state["applied_card_theme"]
        st.session_state["card_theme"] = applied_theme

        if applied_theme == "classic" and not classic_theme_available():
            st.warning(
                "Le paquet classique est introuvable. "
                "Ajoutez les cartes dans visuals/real_deck/.",
            )

        st.divider()
        footer_color = "#3a4050" if st.session_state.get("ui_theme", "light") == "dark" else "#000000"
        st.markdown(
            f'<div style="font-size:10px;color:{footer_color};font-family:\'JetBrains Mono\',monospace;'
            f'letter-spacing:0.06em;padding-top:10px;">'
            "SOLITAIRE &bull; Bruce Schneier (1999)<br>"
            "Python &bull; Streamlit &bull; ChromaDB</div>",
            unsafe_allow_html=True,
        )

    return AppConfig(
        algorithm=st.session_state["applied_algorithm"],
        passphrase=st.session_state["applied_passphrase"],
        card_theme=st.session_state["applied_card_theme"],
        ui_theme=st.session_state["applied_ui_theme"],
        initial_deck=st.session_state["applied_initial_deck"],
    )


def render_header() -> None:
    """Affiche le titre de l'application (adapté au thème courant)."""
    ui_theme = st.session_state.get("ui_theme", "light")
    if ui_theme == "light":
        st.markdown(
            '<h1 class="term-title"><em>Pontifex</em> — Solitaire</h1>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<h1 class="term-title">SOLITAIRE</h1>',
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
