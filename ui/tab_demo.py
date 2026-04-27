"""Onglet Démonstration pas-à-pas du chiffrement Solitaire."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from core.deck import shuffle_deck
from ui.components import AppConfig
from ui.demo_engine import EncryptionStep, precompute_encryption_steps
from ui.styles import DEMO_CSS
from visuals.card_loader import render_immersive_spotlight, render_poker_table

def render(config: AppConfig) -> None:
    """Point d'entrée du tab Démonstration."""
    st.markdown(DEMO_CSS, unsafe_allow_html=True)

    phase = st.session_state.demo_phase

    if phase == "input":
        _render_input_phase(config)
    elif phase in ("playing", "finished"):
        _render_playing_phase()



def _render_input_phase(config: AppConfig) -> None:
    """Formulaire de saisie du mot à chiffrer."""
    st.markdown(
        '<div style="text-align:center;margin:20px 0 10px;">'
        '<span style="font-family:\'JetBrains Mono\',monospace;font-size:1.1em;'
        'color:#e0a840;letter-spacing:0.08em;">DÉMONSTRATION PAS À PAS</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="demo-bubble">'
        '<div class="demo-bubble-title" style="color:#e0a840;">Principe de la démonstration</div>'
        '<div class="demo-bubble-text">'
        "Saisissez un mot, puis observez les cinq opérations de l'algorithme "
        "Solitaire (Schneier, 1999) appliquées à chaque lettre. "
        "Le paquet de 54 cartes est manipulé à chaque étape pour produire "
        "une valeur de flux qui chiffre la lettre courante.</div>"
        '<div class="demo-bubble-tip">'
        "L'intérêt de cette visualisation est de rendre concrètes les "
        "permutations qui restent abstraites dans la description théorique.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    demo_word = st.text_input(
        "Mot à chiffrer",
        placeholder="Ex: HELLO, CRYPTO, ALICE...",
        key="demo_word_input",
        max_chars=20,
    )

    # Deck status
    if config.initial_deck is not None:
        deck_label = "Paquet aléatoire (synchronisé avec l'onglet Chiffrement)"
        deck_color = "#e0a840"
    elif config.passphrase:
        deck_label = "Paquet initialisé par phrase de passe"
        deck_color = "#5a9a6a"
    else:
        deck_label = "Paquet standard Bridge (1 à 54)"
        deck_color = "#64748b"

    st.markdown(
        f'<span style="color:{deck_color};font-size:0.85em;">Paquet : {deck_label}</span>',
        unsafe_allow_html=True,
    )

    col_shuf, col_reset = st.columns(2)
    with col_shuf:
        if st.button("Mélanger le paquet", use_container_width=True, key="demo_shuffle"):
            new_deck = shuffle_deck()
            st.session_state["applied_initial_deck"] = new_deck
            st.session_state["cfg_random_deck"] = new_deck
            st.session_state.pop("cfg_key_mode_input", None)
            st.rerun()
    with col_reset:
        if config.initial_deck is not None or config.passphrase:
            if st.button("Réinitialiser (paquet standard)", use_container_width=True, key="demo_reset"):
                st.session_state["applied_initial_deck"] = None
                st.session_state["applied_passphrase"] = None
                st.session_state.pop("cfg_key_mode_input", None)
                st.session_state.pop("cfg_passphrase_input", None)
                st.rerun()

    if st.button(
        "Lancer la démonstration",
        type="primary",
        use_container_width=True,
        key="demo_launch",
    ):
        word = "".join(c for c in (demo_word or "").strip().upper() if c.isalpha())
        if not word:
            st.warning("Écrivez un mot à chiffrer (lettres uniquement).")
        else:
            steps = precompute_encryption_steps(word, None, config.initial_deck)
            st.session_state.demo_steps = steps
            st.session_state.demo_step_idx = 0
            st.session_state.demo_phase = "playing"
            st.session_state.demo_plain_text = word
            st.session_state.demo_cipher_text = ""
            st.session_state.demo_current_letter = 0
            st.rerun()



def _render_playing_phase() -> None:
    """Affiche l'étape courante et les contrôles de navigation."""
    steps = st.session_state.demo_steps
    idx = st.session_state.demo_step_idx
    plain = st.session_state.demo_plain_text
    phase = st.session_state.demo_phase
    total_steps = len(steps)

    if not steps:
        st.session_state.demo_phase = "input"
        st.rerun()

    current_step = steps[min(idx, total_steps - 1)]

    _render_cipher_tracker(plain, steps, idx, current_step)
    _render_progress_bar(idx, total_steps, current_step, plain)
    _render_step_bubble(current_step)
    _render_card_display(current_step)
    _render_deck_expander(current_step)
    _render_navigation(idx, total_steps, phase)
    if phase == "finished":
        _render_final_result(steps, plain)



def _render_cipher_tracker(
    plain: str,
    steps: list[EncryptionStep],
    idx: int,
    current_step: EncryptionStep,
) -> None:
    """Bandeau de suivi lettre par lettre."""
    cipher_up_to = ""
    for s in steps[:idx + 1]:
        if s.cipher_so_far:
            cipher_up_to = s.cipher_so_far

    chars_html: list[str] = []
    for i, ch in enumerate(plain):
        if i < len(cipher_up_to):
            chars_html.append(
                f'<div style="display:inline-block;text-align:center;margin:0 4px;">'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7em;color:#9098a8;">{ch}</div>'
                f'<div style="font-size:1.2em;color:#9098a8;">--</div>'
                f'<span class="demo-cipher-char demo-cipher-done">{cipher_up_to[i]}</span>'
                f'</div>'
            )
        elif i == len(cipher_up_to) and current_step.letter_idx == i:
            chars_html.append(
                f'<div style="display:inline-block;text-align:center;margin:0 4px;">'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7em;color:#5a9a6a;">{ch}</div>'
                f'<div style="font-size:1.2em;color:#5a9a6a;">--</div>'
                f'<span class="demo-cipher-char demo-cipher-current">?</span>'
                f'</div>'
            )
        else:
            chars_html.append(
                f'<div style="display:inline-block;text-align:center;margin:0 4px;">'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7em;color:#484f58;">{ch}</div>'
                f'<div style="font-size:1.2em;color:#484f58;">--</div>'
                f'<span class="demo-cipher-char demo-cipher-pending">.</span>'
                f'</div>'
            )

    st.markdown(
        f'<div style="text-align:center;padding:12px;background:rgba(0,0,0,0.2);'
        f'border-radius:12px;border:1px solid #3a4050;margin-bottom:12px;">'
        f'<div class="demo-progress-label">Chiffrement en cours</div>'
        f'<div style="display:flex;justify-content:center;align-items:flex-end;flex-wrap:wrap;">'
        f'{"".join(chars_html)}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_progress_bar(
    idx: int, total_steps: int, current_step: EncryptionStep, plain: str,
) -> None:
    progress = (idx + 1) / total_steps if total_steps > 0 else 0
    letter_num = current_step.letter_idx + 1
    st.progress(
        progress,
        text=f"Lettre {letter_num}/{len(plain)} — Étape {idx + 1}/{total_steps}",
    )


def _render_step_bubble(current_step: EncryptionStep) -> None:
    """Bulle d'info de l'opération courante."""
    c = current_step.op_color
    st.markdown(
        f'<div class="demo-bubble">'
        f'<div class="demo-bubble-title" style="color:{c};">{current_step.op_name}</div>'
        f'<div class="demo-bubble-text">{current_step.op_desc}</div>'
        f'<div class="demo-bubble-tip">{current_step.op_tip}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_card_display(current_step: EncryptionStep) -> None:
    """Cartes centrales sur la table de poker."""
    if current_step.center_cards:
        immersive_html = render_immersive_spotlight(
            center_cards=current_step.center_cards,
            highlights=current_step.highlights,
            op_name=current_step.op_name,
            op_color=current_step.op_color,
            op_num=current_step.op_num,
            card_width=180,
        )
        components.html(immersive_html, height=640, scrolling=False)
    elif current_step.op_num == "encrypt":
        _render_encrypt_equation(current_step)


def _render_encrypt_equation(step: EncryptionStep) -> None:
    """Affiche P + K = C sur un tapis de poker."""
    p_char = step.plain_char
    o_val = step.output_val if step.output_val is not None else "?"
    c_char = step.cipher_char or "?"
    components.html(f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;overflow:hidden;font-family:'JetBrains Mono',monospace;}}
.scene{{perspective:1000px;display:flex;justify-content:center;padding:20px;}}
.board{{
  width:90%;max-width:600px;
  background:radial-gradient(ellipse at 50% 40%,#1a6832,#0e4820);
  border-radius:50%/30%;padding:40px 30px;text-align:center;
  transform:rotateX(3deg);position:relative;
  box-shadow:0 20px 60px rgba(0,0,0,0.7),inset 0 0 80px rgba(0,0,0,0.3);
}}
.board::before{{
  content:'';position:absolute;top:-10px;left:-10px;right:-10px;bottom:-10px;
  background:linear-gradient(145deg,#5a3a1a,#2a1a08);
  border-radius:50%/30%;z-index:-1;
  box-shadow:0 25px 80px rgba(0,0,0,0.8);
}}
.equation{{
  font-size:3em;font-weight:800;color:#e0a840;
  animation:revealEq 0.6s cubic-bezier(0.34,1.56,0.64,1);
  letter-spacing:0.05em;
}}
.sub{{font-size:0.35em;color:#9098a8;letter-spacing:0.12em;text-transform:uppercase;margin-top:8px;}}
@keyframes revealEq{{
  0%{{transform:scale(0.5) translateY(20px);opacity:0;filter:blur(4px);}}
  100%{{transform:scale(1) translateY(0);opacity:1;filter:blur(0);}}
}}
</style></head><body>
<div class="scene"><div class="board">
  <div class="equation">{p_char} + {o_val} = {c_char}</div>
  <div class="sub">Clair + Flux de clé = Lettre chiffrée</div>
</div></div>
</body></html>''', height=260, scrolling=False)


def _render_deck_expander(current_step: EncryptionStep) -> None:
    """Expandeur pour voir le paquet complet."""
    deck_to_show = current_step.deck_after
    if not deck_to_show:
        return
    deck_hl = {
        c: current_step.highlights[c]
        for c in current_step.center_cards
        if c in current_step.highlights
    }
    with st.expander("Voir le paquet complet (54 cartes)", expanded=False):
        table_html = render_poker_table(
            deck_to_show,
            highlights=deck_hl,
            center_cards=[],
            card_width=52,
        )
        st.markdown(table_html, unsafe_allow_html=True)


def _render_navigation(idx: int, total_steps: int, phase: str) -> None:
    """Boutons précédent / suivant / tout voir."""
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    with nav_left:
        if idx > 0:
            if st.button("Précédent", use_container_width=True, key="demo_prev"):
                st.session_state.demo_step_idx = idx - 1
                st.rerun()
    with nav_mid:
        if phase == "finished":
            if st.button("Recommencer", type="primary", use_container_width=True, key="demo_new"):
                st.session_state.demo_phase = "input"
                st.session_state.demo_steps = []
                st.session_state.demo_step_idx = -1
                st.rerun()
        else:
            if st.button("Suivant", type="primary", use_container_width=True, key="demo_next"):
                if idx < total_steps - 1:
                    st.session_state.demo_step_idx = idx + 1
                    st.rerun()
                else:
                    st.session_state.demo_phase = "finished"
                    st.rerun()
    with nav_right:
        if phase != "finished" and idx < total_steps - 1:
            if st.button("Tout voir", use_container_width=True, key="demo_skip"):
                st.session_state.demo_step_idx = total_steps - 1
                st.session_state.demo_phase = "finished"
                st.rerun()


def _render_final_result(steps: list[EncryptionStep], plain: str) -> None:
    """Résultat final de la démonstration."""
    final_cipher = ""
    for s in steps:
        if s.cipher_so_far:
            final_cipher = s.cipher_so_far
    st.markdown(
        f'<div class="demo-scoreboard" style="margin-top:16px;">'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7em;'
        f'color:#8b949e;letter-spacing:0.12em;text-transform:uppercase;">Résultat final</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:2.4em;'
        f'font-weight:700;color:#e0a840;'
        f'margin:8px 0;">{plain} → {final_cipher}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7em;'
        f'color:#9098a8;">Chiffré par l\'algorithme Solitaire (Schneier, 1999)</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
