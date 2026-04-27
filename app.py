"""Point d'entrée Streamlit de l'application Solitaire."""

from __future__ import annotations

import sys
from pathlib import Path

# Garantir que le dossier racine du projet est dans sys.path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from ui.components import render_header, render_sidebar
from ui.state import init_session_state
from ui.styles import get_main_css
from ui import tab_analysis, tab_assistant, tab_decrypt, tab_demo, tab_encrypt, tab_rapport
from visuals.card_loader import set_card_theme

st.set_page_config(
    page_title="Pontifex — Solitaire Cipher",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialiser l'état avant l'injection CSS (ui_theme doit être présent)
init_session_state()

# Injection du CSS selon le thème actif
ui_theme = st.session_state.get("ui_theme", "light")
st.markdown(get_main_css(ui_theme), unsafe_allow_html=True)

config = render_sidebar()

# Synchroniser le thème UI pour le prochain rendu
st.session_state["ui_theme"] = config.ui_theme

set_card_theme(config.card_theme)
render_header()

# ── Onglets principaux ──
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Chiffrement",
    "Déchiffrement",
    "Démonstration",
    "Analyse",
    "Assistant IA",
    "Rapport",
])

with tab1:
    tab_encrypt.render(config)
with tab2:
    tab_decrypt.render(config)
with tab3:
    tab_demo.render(config)
with tab4:
    tab_analysis.render()
with tab5:
    tab_assistant.render()
with tab6:
    tab_rapport.render()
