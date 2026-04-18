# Projet Solitaire Cipher

Implémentation de l'algorithme de chiffrement Solitaire de Bruce Schneier,
avec interface Streamlit, assistant IA, et analyse cryptographique.

## Structure du projet

```
core/           → Algorithme Solitaire (deck, chiffrement, keystream)
visuals/        → Génération et rendu des cartes (API Gemini + Pillow)
ai/             → Assistant RAG + cryptanalyse ML
network/        → Chat chiffré WebSocket + échange de clés DH
security/       → Démonstrations de sécurité (réutilisation clé, fréquences)
tests/          → Tests unitaires et vecteurs officiels Schneier
docs/           → Rapport et captures d'écran
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancer les tests

```bash
pytest
```

## Lancer l'application

```bash
streamlit run app.py
```
