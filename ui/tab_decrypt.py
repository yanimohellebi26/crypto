"""Onglet Déchiffrement : saisie du chiffré et récupération du clair."""

from __future__ import annotations

import streamlit as st

from core.deck import create_deck, shuffle_deck
from core.encryption import decrypt, normalize_text, numbers_to_text, text_to_numbers
from core.keystream import generate_keystream, key_deck
from core.solitaire_simple import generate_simple_keystream
from ui.components import AppConfig
from visuals.card_loader import render_deck_grid


def _get_initial_deck(config: AppConfig) -> tuple[int, ...]:
    """Retourne le deck initial selon la configuration."""
    if config.initial_deck is not None:
        return config.initial_deck
    if config.passphrase:
        return key_deck(config.passphrase)
    return create_deck()


def _render_deck_section(config: AppConfig) -> None:
    """Bouton mélange + expander visuel du deck de départ."""
    deck = _get_initial_deck(config)

    if config.initial_deck is not None:
        mode_label = "Clé : paquet aléatoire"
        mode_color = "#e0a840"
    elif config.passphrase:
        mode_label = "Clé : phrase de passe"
        mode_color = "#5a9a6a"
    else:
        mode_label = "Clé : paquet standard (ordre Bridge, 1 à 54)"
        mode_color = "#64748b"

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            f'<span style="color:{mode_color};font-size:0.9em;">{mode_label}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Mélanger", key="btn_shuffle_dec",
                     help="Génère un nouveau paquet aléatoire comme clé"):
            new_deck = shuffle_deck()
            st.session_state["applied_initial_deck"] = new_deck
            st.session_state["cfg_random_deck"] = new_deck
            st.session_state.pop("cfg_key_mode_input", None)
            st.rerun()

    with st.expander("Afficher toutes les cartes (54)"):
        html = render_deck_grid(tuple(deck))
        st.markdown(html, unsafe_allow_html=True)


def render(config: AppConfig) -> None:
    """Point d'entrée du tab Déchiffrement."""
    st.subheader("Déchiffrement de message")
    _render_deck_section(config)
    st.divider()

    cipher_input = st.text_area(
        "Texte chiffré",
        placeholder="EXKYIZSGEH…",
        height=120,
        key="dec_input",
    )
    do_decrypt = st.button("Déchiffrer", type="primary", key="btn_dec")

    if do_decrypt and cipher_input.strip():
        _process_decryption(cipher_input, config)
    elif do_decrypt:
        st.warning("Entrez un texte chiffré.")


def _process_decryption(cipher_input: str, config: AppConfig) -> None:
    """Effectue le déchiffrement et affiche les résultats."""
    key_arg = config.passphrase
    initial_deck = _get_initial_deck(config)
    try:
        if config.algorithm == "Solitaire simplifié":
            normalized_c = normalize_text(cipher_input)
            _final_deck, ks = generate_simple_keystream(initial_deck, len(normalized_c))
            cipher_nums = text_to_numbers(normalized_c)
            plain_nums = [(c - k - 1) % 26 + 1 for c, k in zip(cipher_nums, ks)]
            plain_text_out = numbers_to_text(plain_nums)
        else:
            if config.initial_deck is not None:
                # Deck aléatoire : on chiffre en inverse directement
                from core.encryption import numbers_to_text
                normalized_c = normalize_text(cipher_input)
                _, ks = generate_keystream(initial_deck, len(normalized_c))
                cipher_nums = text_to_numbers(normalized_c)
                plain_nums = [(c - k - 1) % 26 + 1 for c, k in zip(cipher_nums, ks)]
                plain_text_out = numbers_to_text(plain_nums)
            else:
                plain_text_out, _final_deck = decrypt(cipher_input, key=key_arg)
                normalized_c = normalize_text(cipher_input)
                _, ks = generate_keystream(initial_deck, len(normalized_c))

        st.markdown("**Texte chiffré**")
        st.markdown(
            f'<div class="out-cipher">{normalize_text(cipher_input)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("**Flux de clés**")
        ks_str = " ".join(f"{k:02d}" for k in ks)
        st.markdown(f'<div class="out-key">{ks_str}</div>', unsafe_allow_html=True)
        st.markdown("**Texte en clair**")
        st.markdown(
            f'<div class="out-plain">{plain_text_out}</div>',
            unsafe_allow_html=True,
        )
    except ValueError as e:
        st.error(str(e))
