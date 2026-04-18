"""Onglet Déchiffrement : saisie du chiffré et récupération du clair."""

from __future__ import annotations

import streamlit as st

from core.deck import create_deck
from core.encryption import decrypt, normalize_text, numbers_to_text, text_to_numbers
from core.keystream import generate_keystream, key_deck
from core.solitaire_simple import generate_simple_keystream
from ui.components import AppConfig


def render(config: AppConfig) -> None:
    """Point d'entrée du tab Déchiffrement."""
    st.subheader("Déchiffrement de message")

    cipher_input = st.text_area(
        "Texte chiffré",
        placeholder="EXKYIZSGEH…",
        height=120,
        key="dec_input",
    )
    do_decrypt = st.button("Déchiffrer  →", type="primary", key="btn_dec")

    if do_decrypt and cipher_input.strip():
        _process_decryption(cipher_input, config)
    elif do_decrypt:
        st.warning("Entrez un texte chiffré.")


def _process_decryption(cipher_input: str, config: AppConfig) -> None:
    """Effectue le déchiffrement et affiche les résultats."""
    key_arg = config.passphrase
    try:
        if config.algorithm == "Solitaire simplifié":
            normalized_c = normalize_text(cipher_input)
            init_deck = key_deck(key_arg) if key_arg else create_deck()
            _final_deck, ks = generate_simple_keystream(init_deck, len(normalized_c))
            cipher_nums = text_to_numbers(normalized_c)
            plain_nums = [(c - k - 1) % 26 + 1 for c, k in zip(cipher_nums, ks)]
            plain_text_out = numbers_to_text(plain_nums)
        else:
            plain_text_out, _final_deck = decrypt(cipher_input, key=key_arg)
            normalized_c = normalize_text(cipher_input)
            init_deck = key_deck(key_arg) if key_arg else create_deck()
            _, ks = generate_keystream(init_deck, len(normalized_c))

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
