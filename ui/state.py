"""Initialisation de l'état de session Streamlit (valeurs par défaut)."""

from __future__ import annotations

import streamlit as st

from core.deck import create_deck


def init_session_state() -> None:
    """Définit les valeurs par défaut si elles n'existent pas encore."""
    defaults: dict = {
        # Demo playback state
        "demo_steps": [],
        "demo_step_idx": -1,
        "demo_phase": "input",
        "demo_plain_text": "",
        "demo_cipher_text": "",
        "demo_current_letter": 0,
        # Utilisés par l'assistant IA (ai/assistant.py → build_context_from_state)
        "demo_deck": create_deck(),
        "demo_highlights": {},
        "demo_spotlight": [],
        "demo_log": [],
        "demo_output_val": None,
        "demo_step_info": None,
        "demo_center_cards": [],
        "demo_message": "",
        "demo_step_count": 0,
        "demo_keystream_letters": [],
        "card_theme": "modern",
        "ui_theme": "light",
        "applied_ui_theme": "light",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
