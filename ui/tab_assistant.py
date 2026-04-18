"""Onglet Assistant IA : chat RAG (ChromaDB + Gemini) sur le Solitaire."""

from __future__ import annotations

import streamlit as st


def render() -> None:
    """Point d'entrée du tab Assistant IA."""
    st.subheader("Assistant IA Cryptographique")
    _render_intro()
    _init_assistant()

    if st.session_state.get("ai_error"):
        _render_error()
    else:
        _render_chat_interface()



def _render_intro() -> None:
    kb_info = ""
    if st.session_state.get("ai_assistant"):
        kc = st.session_state.ai_assistant.knowledge_count
        kb_info = (
            f' Base vectorielle : <b style="color:#22c55e">{kc} passages</b> '
            f"(article Schneier · analyse Crowley · prérequis M1 · fallback)."
        )
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.9em;">'
        "NEXUS est un assistant IA spécialisé en chiffrement Solitaire. "
        "Il utilise un RAG (ChromaDB + Gemini) alimenté par les sources primaires : "
        "l'article original de Schneier, l'analyse de Crowley (1999) et le document de prérequis M1."
        + kb_info
        + "</p>",
        unsafe_allow_html=True,
    )


def _init_assistant() -> None:
    """Initialise l'assistant IA dans le session state si nécessaire."""
    for key in ("ai_messages", "ai_assistant", "ai_error"):
        if key not in st.session_state:
            st.session_state[key] = [] if key == "ai_messages" else ("" if key == "ai_error" else None)

    if st.session_state.ai_assistant is not None or st.session_state.ai_error:
        return

    with st.spinner("Chargement de l'assistant IA..."):
        try:
            import importlib
            import sys
            for mod_name in list(sys.modules.keys()):
                if mod_name.startswith("ai.") or mod_name == "ai":
                    importlib.invalidate_caches()
                    del sys.modules[mod_name]
            from ai.assistant import SolitaireAssistant
            st.session_state.ai_assistant = SolitaireAssistant()
        except Exception as exc:
            st.session_state.ai_error = str(exc)


def _render_error() -> None:
    st.error(f"Erreur d'initialisation de l'assistant : {st.session_state.ai_error}")
    if st.button("↺ Réessayer", key="ai_retry"):
        st.session_state.ai_error = ""
        st.session_state.ai_assistant = None
        st.rerun()



def _render_chat_interface() -> None:
    # Bouton reset
    _, ai_col2 = st.columns([6, 1])
    with ai_col2:
        if st.button("Effacer", key="ai_clear"):
            st.session_state.ai_messages = []
            st.rerun()

    _render_message_history()
    _render_chat_form()
    _render_suggestions()


def _render_message_history() -> None:
    with st.container():
        if not st.session_state.ai_messages:
            st.markdown(
                '<div style="background:#161b22;border:1px solid #30363d;border-radius:2px;'
                'padding:20px;color:#30363d;text-align:center;font-family:\'JetBrains Mono\',monospace;'
                'font-size:0.82em;letter-spacing:0.06em;">'
                "Posez une question sur le chiffrement Solitaire.<br>"
                '<span style="color:#21262d;font-size:0.9em;">'
                "Ex : &laquo;&nbsp;Comment fonctionne la triple coupe&nbsp;?&nbsp;&raquo; &bull; "
                "&laquo;&nbsp;Quels sont les vecteurs de Schneier&nbsp;?&nbsp;&raquo;</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        for msg in st.session_state.ai_messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div style="background:#1a2030;border-left:3px solid #5f82a6;'
                    f'padding:10px 14px;border-radius:2px;margin:6px 0;color:#d8dbe2;'
                    f"font-family:'JetBrains Mono',monospace;\">"
                    f'<span style="color:#88a8c5;font-family:\'JetBrains Mono\',monospace;'
                    f'font-size:0.75em;letter-spacing:0.1em;text-transform:uppercase;">Vous</span>'
                    f'<br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#1a2518;border-left:3px solid #5a9a6a;'
                    f'padding:10px 14px;border-radius:2px;margin:6px 0;">'
                    f'<span style="color:#5a9a6a;font-family:\'JetBrains Mono\',monospace;'
                    f'font-size:0.75em;letter-spacing:0.1em;text-transform:uppercase;">Solitaire AI</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(msg["content"])


def _render_chat_form() -> None:
    assistant = st.session_state.ai_assistant
    with st.form("ai_chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Votre question",
            placeholder="Ex: Explique-moi l'opération 3 du chiffrement Solitaire...",
            height=80,
            label_visibility="collapsed",
        )
        send_col, ctx_col = st.columns([3, 2])
        with send_col:
            submitted = st.form_submit_button(
                "Envoyer  →",
                use_container_width=True,
                type="primary",
            )
        with ctx_col:
            include_context = st.form_submit_button(
                "Envoyer + contexte démo",
                use_container_width=True,
                help="Inclut l'état actuel du paquet dans la question",
            )

    if not (submitted or include_context) or not user_input.strip():
        return

    question = user_input.strip()

    app_context = None
    if include_context:
        from ai.assistant import build_context_from_state
        app_context = build_context_from_state(dict(st.session_state))

    st.session_state.ai_messages.append({"role": "user", "content": question})

    with st.spinner("NEXUS réfléchit..."):
        try:
            response_text = ""
            response_placeholder = st.empty()
            for chunk in assistant.stream_ask(
                question=question,
                conversation_history=st.session_state.ai_messages[:-1],
                context=app_context,
            ):
                response_text += chunk
                response_placeholder.markdown(response_text + "▌")
            response_placeholder.empty()
            st.session_state.ai_messages.append({
                "role": "assistant",
                "content": response_text,
            })
        except Exception as exc:
            st.error(f"Erreur lors de la génération : {exc}")

    st.rerun()


def _render_suggestions() -> None:
    st.markdown("---")
    st.markdown("**Questions fréquentes :**")
    suggestions = [
        ("♠  Les 5 opérations", "Explique-moi les 5 opérations du chiffrement Solitaire en détail"),
        ("♦  Espace de clés", "Quelle est la taille de l'espace de clés de Solitaire ? Est-il sûr ?"),
        ("△  Biais de Crowley", "Qu'est-ce que le biais statistique découvert par Paul Crowley ?"),
        ("♣  Réutilisation clé", "Pourquoi la réutilisation de clé est-elle dangereuse en Solitaire ?"),
        ("◆  Tests NIST", "Quels tests NIST s'appliquent au chiffrement Solitaire ?"),
        ("◈  Solitaire vs AES", "Compare le chiffrement Solitaire avec AES"),
    ]
    sugg_cols = st.columns(3)
    for i, (label, question) in enumerate(suggestions):
        col = sugg_cols[i % 3]
        with col:
            if st.button(label, key=f"sugg_{i}", use_container_width=True):
                _handle_suggestion(question)


def _handle_suggestion(question: str) -> None:
    assistant = st.session_state.ai_assistant
    st.session_state.ai_messages.append({"role": "user", "content": question})
    with st.spinner("NEXUS réfléchit..."):
        try:
            response_text = ""
            for chunk in assistant.stream_ask(
                question=question,
                conversation_history=st.session_state.ai_messages[:-1],
            ):
                response_text += chunk
            st.session_state.ai_messages.append({
                "role": "assistant",
                "content": response_text,
            })
        except Exception as exc:
            st.session_state.ai_messages.pop()
            st.error(f"Erreur : {exc}")
    st.rerun()
