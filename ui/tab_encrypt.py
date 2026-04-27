"""Onglet Chiffrement : saisie du texte et affichage du résultat."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from core.deck import create_deck, shuffle_deck
from core.encryption import normalize_text, numbers_to_text, text_to_numbers
from core.keystream import generate_keystream, key_deck
from ui.components import AppConfig
from visuals.card_loader import render_deck_grid


def _get_initial_deck(config: AppConfig) -> tuple[int, ...]:
    """Retourne le deck initial selon la configuration."""
    if config.initial_deck is not None:
        return config.initial_deck
    if config.passphrase:
        return key_deck(config.passphrase)
    return create_deck()


def _render_deck_section(config: AppConfig, key_suffix: str = "") -> None:
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
        if st.button("Mélanger", key=f"btn_shuffle{key_suffix}",
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
    """Point d'entrée du tab Chiffrement."""
    st.subheader("Chiffrement de message")
    _render_deck_section(config, key_suffix="_enc")
    st.divider()

    plain_text = st.text_area(
        "Message en clair",
        placeholder="Entrez votre texte ici…",
        height=120,
        key="enc_input",
    )
    do_encrypt = st.button("Chiffrer", type="primary", key="btn_enc")

    if do_encrypt and plain_text.strip():
        _process_encryption(plain_text, config)
    elif do_encrypt:
        st.warning("Entrez un message à chiffrer.")


def _process_encryption(plain_text: str, config: AppConfig) -> None:
    """Effectue le chiffrement et affiche les résultats."""
    normalized = normalize_text(plain_text)
    if not normalized:
        st.error("Le message ne contient aucune lettre.")
        return

    key_arg = config.passphrase
    initial_deck = _get_initial_deck(config)
    try:
        cipher_text, final_deck, ks, plain_nums, cipher_nums = _compute(
            plain_text, normalized, key_arg, config.algorithm, initial_deck,
        )
    except ValueError as e:
        st.error(str(e))
        return

    _display_results(normalized, ks, cipher_text, plain_nums, cipher_nums, final_deck, key_arg, config.algorithm)


def _compute(
    plain_text: str,
    normalized: str,
    key_arg: str | None,
    algorithm: str,
    initial_deck: tuple[int, ...] | None = None,
) -> tuple[str, tuple[int, ...], list[int], list[int], list[int]]:
    """Chiffre selon l'algorithme choisi et renvoie tous les détails."""
    base_deck = initial_deck if initial_deck is not None else (
        key_deck(key_arg) if key_arg else create_deck()
    )
    if algorithm == "Solitaire simplifié":
        from core.solitaire_simple import generate_simple_keystream
        final_deck, ks = generate_simple_keystream(base_deck, len(normalized))
        plain_nums = text_to_numbers(normalized)
        cipher_nums = [(p + k - 1) % 26 + 1 for p, k in zip(plain_nums, ks)]
        cipher_text = numbers_to_text(cipher_nums)
    else:
        plain_nums = text_to_numbers(normalized)
        final_deck, ks = generate_keystream(base_deck, len(plain_nums))
        cipher_nums = [(p + k - 1) % 26 + 1 for p, k in zip(plain_nums, ks)]
        cipher_text = numbers_to_text(cipher_nums)

    return cipher_text, final_deck, ks, plain_nums, cipher_nums


def _display_results(
    normalized: str,
    ks: list[int],
    cipher_text: str,
    plain_nums: list[int],
    cipher_nums: list[int],
    final_deck: tuple,
    key_arg: str | None,
    algorithm: str,
) -> None:
    """Affiche les résultats du chiffrement."""
    st.markdown("**Texte normalisé**")
    st.markdown(f'<div class="out-plain">{normalized}</div>', unsafe_allow_html=True)
    st.markdown("**Flux de clés**")
    ks_str = " ".join(f"{k:02d}" for k in ks)
    st.markdown(f'<div class="out-key">{ks_str}</div>', unsafe_allow_html=True)
    st.markdown("**Texte chiffré**")
    st.markdown(f'<div class="out-cipher">{cipher_text}</div>', unsafe_allow_html=True)

    st.divider()

    # Métriques
    letters_col, key_col, algo_col = st.columns(3)
    letters_col.metric("Lettres", len(normalized))
    key_col.metric("Clé", key_arg if key_arg else "Aucune")
    algo_col.metric(
        "Algorithme",
        "Complet" if algorithm == "Solitaire complet" else "Simplifié",
    )

    # Tableau lettre par lettre
    with st.expander("Détail lettre par lettre"):
        _render_letter_table(normalized, plain_nums, ks, cipher_nums, cipher_text)

    # Paquet final
    with st.expander("Paquet final (54 cartes)"):
        st.markdown(render_deck_grid(final_deck), unsafe_allow_html=True)


def _render_letter_table(
    normalized: str,
    plain_nums: list[int],
    ks: list[int],
    cipher_nums: list[int],
    cipher_text: str,
) -> None:
    """Génère et affiche le tableau HTML lettre par lettre."""
    rows = "".join(
        f"<tr>"
        f'<td style="color:#64748b">{i + 1}</td>'
        f'<td style="color:#5a9a6a;font-weight:bold">{normalized[i]}</td>'
        f'<td style="color:#94a3b8">{plain_nums[i]}</td>'
        f'<td style="color:#7a72a8">{ks[i]}</td>'
        f'<td style="color:#94a3b8">{cipher_nums[i]}</td>'
        f'<td style="color:#b85040;font-weight:bold">{cipher_text[i]}</td>'
        f"</tr>"
        for i in range(len(normalized))
    )
    table_html = (
        '<table class="letter-table">'
        "<thead><tr>"
        '<th style="color:#64748b">#</th>'
        '<th style="color:#5a9a6a">Clair</th>'
        '<th style="color:#94a3b8">Valeur</th>'
        '<th style="color:#7a72a8">Flux</th>'
        '<th style="color:#94a3b8">Somme</th>'
        '<th style="color:#b85040">Chiffré</th>'
        "</tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)
        
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
