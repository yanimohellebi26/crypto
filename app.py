"""Point d'entrée Streamlit de l'application Solitaire."""

from __future__ import annotations

import sys
from pathlib import Path

# Garantir que le dossier racine du projet est dans sys.path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from ui.components import render_header, render_sidebar
from ui.state import init_session_state
from ui.styles import MAIN_CSS
from ui import tab_analysis, tab_assistant, tab_decrypt, tab_demo, tab_encrypt

st.set_page_config(
    page_title="Pontifex — Solitaire Cipher",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injection du CSS et initialisation de l'état
st.markdown(f"<style>{MAIN_CSS}</style>", unsafe_allow_html=True)
init_session_state()

config = render_sidebar()
render_header()

# Onglets principaux
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Chiffrement",
    "Déchiffrement",
    "Démonstration",
    "Analyse",
    "Assistant IA",
])

with tab1:
    tab_encrypt.render(config)
with tab2:
    tab_decrypt.render(config)
with tab3:
    tab_demo.render()
with tab4:
    tab_analysis.render()
with tab5:
    tab_assistant.render()

