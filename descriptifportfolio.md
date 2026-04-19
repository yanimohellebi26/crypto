# Pontifex — Solitaire Cipher Suite

## Tagline
Full implementation of Bruce Schneier's Solitaire cipher with Streamlit UI, RAG assistant, and cryptanalysis tools.

## Description
A complete implementation of the Solitaire/Pontifex cipher (from Neal Stephenson's Cryptonomicon) — a stream cipher operable by hand with a deck of playing cards. Features a multi-tab Streamlit UI for encryption/decryption/demo, security vulnerability demonstrations (key reuse, frequency analysis), and a RAG-powered AI assistant using ChromaDB + Gemini for cryptography Q&A.

## Motivation
Cryptography course project combining classical cipher implementation with modern AI-assisted analysis — demonstrating both the elegance and vulnerabilities of hand-operable cryptographic systems.

## Tech Stack
- **Frontend**: Streamlit (multi-tab UI)
- **Backend**: Python
- **AI/ML**: Google Gemini API, ChromaDB, Sentence-Transformers
- **Analysis**: Plotly, NumPy, SciPy
- **Testing**: pytest
- **Visualization**: Pillow (card rendering)

## Key Features
- Complete Solitaire/Pontifex cipher (encrypt, decrypt, keystream) with all 5 deck operations
- Multi-tab Streamlit UI (encrypt, decrypt, demo, analysis, AI assistant)
- RAG assistant with ChromaDB vector store + Gemini LLM for crypto Q&A
- Security demonstrations: key reuse vulnerability and frequency analysis
- Card visualization via Gemini image generation + Pillow

## Skills Demonstrated
- Cryptographic algorithm implementation
- RAG pipeline design (ChromaDB + Gemini)
- Interactive data visualization (Plotly, Streamlit)
- Security analysis and vulnerability demonstration
- Scientific computing (NumPy, SciPy)

## Category
`Security` · `Cryptography` · `AI` · `Academic`

## Status
Complete

## Complexity
⭐⭐⭐⭐⭐ Advanced

## Links
- GitHub: https://github.com/yanimohellebi26/crypto
