"""Onglet Chiffrement : saisie du texte et affichage du résultat."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from core.deck import create_deck
from core.encryption import normalize_text, numbers_to_text, text_to_numbers
from core.keystream import generate_keystream, key_deck
from ui.components import AppConfig
from visuals.card_loader import render_deck_chips


def render(config: AppConfig) -> None:
    """Point d'entrée du tab Chiffrement."""
    st.subheader("Chiffrement de message")

    plain_text = st.text_area(
        "Message en clair",
        placeholder="Entrez votre texte ici…",
        height=120,
        key="enc_input",
    )
    do_encrypt = st.button("Chiffrer  →", type="primary", key="btn_enc")

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
    try:
        cipher_text, final_deck, ks, plain_nums, cipher_nums = _compute(
            plain_text, normalized, key_arg, config.algorithm,
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
) -> tuple[str, tuple[int, ...], list[int], list[int], list[int]]:
    """Chiffre selon l'algorithme choisi et renvoie tous les détails."""
    if algorithm == "Solitaire simplifié":
        from core.solitaire_simple import generate_simple_keystream
        init_deck = key_deck(key_arg) if key_arg else create_deck()
        final_deck, ks = generate_simple_keystream(init_deck, len(normalized))
        plain_nums = text_to_numbers(normalized)
        cipher_nums = [(p + k - 1) % 26 + 1 for p, k in zip(plain_nums, ks)]
        cipher_text = numbers_to_text(cipher_nums)
    else:
        # On calcule le keystream une seule fois et on dérive tout depuis celui-ci
        plain_nums = text_to_numbers(normalized)
        init_deck = key_deck(key_arg) if key_arg else create_deck()
        final_deck, ks = generate_keystream(init_deck, len(plain_nums))
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
    with st.expander("Paquet final"):
        deck_html = render_deck_chips(final_deck)
        components.html(deck_html, height=130)


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
