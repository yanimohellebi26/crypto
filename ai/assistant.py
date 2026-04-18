"""Assistant IA cryptographique — RAG (ChromaDB + Gemini).

Utilise une base de connaissances (fichiers txt dans ai/knowledge/) et des
chunks de secours codés en dur pour répondre aux questions sur Solitaire.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Iterator

# Supprimer l'avertissement de dépréciation (FutureWarning) du SDK legacy
warnings.filterwarnings("ignore", category=FutureWarning, module="google")

from dotenv import load_dotenv

load_dotenv()

# Chunks de secours (utilisés si les fichiers txt ne couvrent pas le sujet)
KNOWLEDGE_CHUNKS: list[dict[str, str]] = [
    {
        "id": "overview",
        "title": "Présentation du chiffrement Solitaire",
        "text": (
            "Le chiffrement Solitaire (aussi appelé Pontifex) a été conçu par Bruce Schneier "
            "et popularisé dans le roman 'Cryptonomicon' de Neal Stephenson (1999). "
            "C'est un algorithme de chiffrement symétrique par flux (stream cipher), "
            "qui utilise un jeu de 54 cartes (52 cartes classiques + 2 jokers) comme état interne. "
            "La clé secrète est l'ordre initial du paquet. "
            "Le principe fondamental : l'ordre du paquet évolue de façon pseudo-aléatoire "
            "pour générer un flux de clés (keystream), qui est utilisé pour chiffrer le message "
            "lettre par lettre en arithmétique modulo 26. "
            "Avantage unique : on peut effectuer le chiffrement avec un vrai jeu de cartes, "
            "sans ordinateur, ce qui en fait un outil théoriquement utilisable sur le terrain."
        ),
    },
    {
        "id": "operation1",
        "title": "Opération 1 : Recul du Joker Noir (A)",
        "text": (
            "Première opération du cycle Solitaire : déplacer le Joker A (Joker noir, valeur 53) "
            "d'une position vers le bas dans le paquet. "
            "Si le Joker A est en position i, il est échangé avec la carte en position i+1. "
            "Cas spécial critique : si le Joker A est en DERNIÈRE position, "
            "il est placé en DEUXIÈME position (pas en première). "
            "Cela signifie qu'il 'remonte' au début du paquet mais après la première carte. "
            "Cette règle de wrapping est une source fréquente d'erreur d'implémentation."
        ),
    },
    {
        "id": "operation2",
        "title": "Opération 2 : Recul du Joker Rouge (B)",
        "text": (
            "Deuxième opération : déplacer le Joker B (Joker rouge, valeur 54) "
            "de DEUX positions vers le bas. "
            "Cas spéciaux : si le Joker B est en dernière position, il passe en 3ème position. "
            "S'il est en avant-dernière position, il passe en 2ème position. "
            "Règle absolue : le Joker B ne peut JAMAIS se retrouver en 1ère position. "
            "Le déplacement de 2 positions utilise le même mécanisme de wrapping circulaire "
            "que pour le Joker A."
        ),
    },
    {
        "id": "operation3",
        "title": "Opération 3 : Triple coupe (triple cut)",
        "text": (
            "Troisième opération : réorganiser le paquet en trois segments par rapport aux jokers. "
            "Les deux jokers divisent le paquet en trois parties : "
            "segment supérieur (au-dessus du premier joker), "
            "segment central (entre les deux jokers, jokers inclus), "
            "segment inférieur (en dessous du second joker). "
            "L'opération échange le segment supérieur avec le segment inférieur. "
            "Le segment central (jokers + cartes entre eux) reste FIXE à sa position relative. "
            "Si un joker est en première ou dernière position, un des segments est vide, "
            "ce qui est un cas valide : l'opération porte alors sur les deux autres segments."
        ),
    },
    {
        "id": "operation4",
        "title": "Opération 4 : Coupe simple (count cut)",
        "text": (
            "Quatrième opération : effectuer une coupe déterminée par la valeur de la dernière carte. "
            "Regarder la DERNIÈRE carte du paquet et noter sa valeur Bridge (1 à 53 pour les jokers). "
            "Prendre les N premières cartes du dessus du paquet. "
            "Les insérer juste AU-DESSUS de la dernière carte (qui ne bouge JAMAIS). "
            "Règle critique : la dernière carte reste toujours en dernière position. "
            "Si la dernière carte est un joker (valeur Bridge = 53), "
            "on prend 53 cartes sur 54, donc le paquet ne change pratiquement pas. "
            "Cette opération assure que la valeur de la carte de fond influence le flux de clés."
        ),
    },
    {
        "id": "operation5",
        "title": "Opération 5 : Lecture de la valeur de sortie",
        "text": (
            "Cinquième opération (lecture) : extraire la valeur pseudo-aléatoire du cycle. "
            "Regarder la PREMIÈRE carte du paquet, noter sa valeur Bridge (N). "
            "Compter N cartes depuis le début du paquet. "
            "Regarder la carte en position N+1 (la suivante). "
            "Sa valeur est la sortie potentielle. "
            "Si cette carte est un JOKER : ignorer la valeur et recommencer le cycle entier (1-2-3-4-5). "
            "Si la valeur est supérieure à 26 : soustraire 26. "
            "Le résultat (1-26) est la prochaine valeur du flux de clés. "
            "IMPORTANT : cette opération NE MODIFIE PAS l'ordre du paquet. "
            "Le paquet est seulement LU, pas modifié."
        ),
    },
    {
        "id": "keying",
        "title": "Initialisation du paquet par mot de passe (keying)",
        "text": (
            "Pour initialiser le paquet avec un mot de passe secret (méthode de Schneier) : "
            "Partir du paquet dans l'ordre standard (1-52, Joker A, Joker B). "
            "Pour CHAQUE LETTRE du mot de passe, dans l'ordre : "
            "1) Effectuer les opérations 1, 2, 3, 4 (sans opération 5). "
            "2) Effectuer une coupe supplémentaire en utilisant la valeur numérique de cette lettre "
            "(A=1, B=2, ..., Z=26). "
            "Le résultat est un paquet dont l'ordre dépend entièrement du mot de passe. "
            "Schneier recommande un minimum de 64 à 80 caractères pour une sécurité maximale. "
            "Un mot de passe court produit un espace de clés plus petit et est vulnérable "
            "aux attaques par dictionnaire."
        ),
    },
    {
        "id": "encryption",
        "title": "Chiffrement et déchiffrement de messages",
        "text": (
            "Pré-traitement du message clair : supprimer tous les caractères non-alphabétiques, "
            "convertir en majuscules, remplacer les accents. "
            "Chiffrement lettre par lettre : "
            "(valeur_lettre_claire + valeur_keystream) modulo 26. "
            "Si le résultat est 0, la lettre chiffrée est Z (pas A). "
            "Déchiffrement : (valeur_lettre_chiffrée - valeur_keystream) modulo 26. "
            "Si le résultat est négatif ou nul, ajouter 26. "
            "Valeurs : A=1, B=2, ..., Z=26. "
            "L'état du paquet est conservé entre messages successifs : "
            "deux messages chiffrés avec la même clé partagent un flux continu."
        ),
    },
    {
        "id": "security_keyspace",
        "title": "Espace de clés et sécurité théorique",
        "text": (
            "L'espace de clés du chiffrement Solitaire est 54! (factorielle 54). "
            "54! ≈ 2.31 × 10^71, soit environ 2^237 ordres possibles. "
            "En comparaison : AES-128 a 2^128 clés, AES-256 a 2^256 clés. "
            "Solitaire offre donc théoriquement plus de clés que AES-128. "
            "Cependant, en pratique, le mot de passe utilisé pour initialiser le paquet "
            "est généralement beaucoup plus court, ce qui réduit drastiquement l'espace effectif. "
            "Une attaque par force brute exhaustive est impossible même avec des ordinateurs quantiques, "
            "mais une attaque par dictionnaire sur le mot de passe est réaliste. "
            "Durée estimée pour parcourir tout l'espace : des milliards d'années."
        ),
    },
    {
        "id": "crowley_bias",
        "title": "Biais statistique de Crowley (1999)",
        "text": (
            "Paul Crowley a publié en 1999 une analyse des faiblesses du chiffrement Solitaire. "
            "Il a découvert un biais statistique : la probabilité que la 2ème sortie du flux "
            "soit identique à la 1ère est de 1/22.5 au lieu de 1/26 attendu pour des données uniformes. "
            "Ce biais est dû à la structure déterministe des opérations sur les jokers. "
            "Bien que faible, ce biais est mesurable statistiquement et distingue Solitaire "
            "d'un générateur vraiment aléatoire. "
            "D'autres biais ont été trouvés dans la distribution des sorties consécutives. "
            "Ces faiblesses font de Solitaire un algorithme intéressant académiquement "
            "mais déconseillé pour des usages cryptographiques modernes sérieux."
        ),
    },
    {
        "id": "key_reuse",
        "title": "Danger de réutilisation de clé",
        "text": (
            "Comme tout chiffrement par flux, Solitaire est vulnérable à la réutilisation de clé. "
            "Si deux messages M1 et M2 sont chiffrés avec le MÊME flux de clés K : "
            "C1 = M1 + K (mod 26) et C2 = M2 + K (mod 26). "
            "Alors C1 - C2 = M1 - M2 (mod 26). "
            "Un attaquant qui observe C1 et C2 peut calculer leur différence, "
            "qui est exactement la différence des textes clairs. "
            "Technique d'attaque : 'crib dragging' — essayer des mots courants à chaque position "
            "pour déduire des fragments du clair. "
            "Règle absolue en cryptographie par flux : JAMAIS réutiliser une clé."
        ),
    },
    {
        "id": "nist_tests",
        "title": "Tests NIST de randomness",
        "text": (
            "Les tests NIST SP 800-22 sont une suite de tests statistiques pour évaluer "
            "la qualité pseudo-aléatoire d'un générateur. "
            "Tests principaux : test de fréquence (distribution des bits 0/1), "
            "test des runs (alternances 0-1), test du bloc de fréquence, "
            "test des runs de uns les plus longs, test du rang des matrices, "
            "test FFT (spectre de fréquence), test de sérialité, test d'entropie approximative. "
            "Pour Solitaire : les tests NIST révèlent le biais de Crowley dans certaines conditions. "
            "Un générateur cryptographiquement sûr (comme /dev/urandom) passe tous ces tests. "
            "Python random.random() passe aussi ces tests (Mersenne Twister). "
            "Solitaire présente des anomalies sur certains tests avec des clés courtes."
        ),
    },
    {
        "id": "comparison_aes",
        "title": "Comparaison Solitaire vs AES",
        "text": (
            "AES (Advanced Encryption Standard) est l'algorithme de chiffrement symétrique moderne. "
            "AES est un chiffrement par blocs (128 bits), Solitaire est un chiffrement par flux. "
            "AES-128 : 2^128 clés possibles (≈3.4×10^38), vitesse : milliards de blocs/seconde. "
            "AES-256 : 2^256 clés (résistant aux ordinateurs quantiques). "
            "Solitaire : ~2^237 ordres, mais biais statistique. "
            "Vitesse : Solitaire est extrêmement lent (quelques cartes/seconde manuellement, "
            "1000-10000 fois plus lent qu'AES en logiciel). "
            "Avantage de Solitaire : peut être effectué sans ordinateur avec un jeu de cartes. "
            "AES requiert du matériel ou un logiciel."
        ),
    },
    {
        "id": "comparison_rc4",
        "title": "Comparaison Solitaire vs RC4",
        "text": (
            "RC4 (Rivest Cipher 4) était le principal chiffrement par flux concurrent de Solitaire. "
            "RC4 est maintenant interdit dans TLS (RFC 7465, 2015) en raison de biais statistiques. "
            "Solitaire et RC4 sont tous deux des chiffrements par flux avec état interne évolutif. "
            "RC4 : état de 256 octets, beaucoup plus rapide que Solitaire. "
            "Les deux souffrent de biais statistiques : RC4 présente des biais dans les premiers octets. "
            "Solitaire présente le biais de Crowley sur les 2ème sorties. "
            "Ni RC4 ni Solitaire ne sont recommandés pour des applications sécurisées modernes. "
            "Les successeurs modernes des chiffrements par flux sont ChaCha20 et Salsa20."
        ),
    },
    {
        "id": "schneier_vectors",
        "title": "Vecteurs de test officiels de Schneier",
        "text": (
            "Bruce Schneier a publié trois vecteurs de test pour valider les implémentations : "
            "Vecteur 1 : Paquet standard (1 à 52, Joker A, Joker B), "
            "chiffrer 'AAAAAAAAAA' → résultat attendu 'EXKYIZSGEH'. "
            "Vecteur 2 : Clé 'FOO', chiffrer 'AAAAAAAAAAAAAAA' → résultat 'ITHZUJIWGRFARMW'. "
            "Vecteur 3 : Clé 'CRYPTONOMICON', chiffrer 'SOLITAIREX' → résultat 'KIRAKSFJAN'. "
            "Ces trois vecteurs doivent être reproduits exactement pour valider une implémentation. "
            "Une seule erreur dans les opérations provoque une propagation d'erreur complète."
        ),
    },
    {
        "id": "history",
        "title": "Contexte historique et le roman Cryptonomicon",
        "text": (
            "Solitaire a été créé par Bruce Schneier, cryptographe renommé auteur de 'Cryptographie Appliquée'. "
            "Il a été commissionné par Neal Stephenson pour son roman 'Cryptonomicon' (1999), "
            "un thriller technologique mettant en scène des cryptographes pendant la Seconde Guerre mondiale "
            "et dans les années 1990. "
            "Dans le roman, le chiffrement s'appelle 'Pontifex' pour le déguiser. "
            "L'idée était qu'agents secrets pourraient communiquer secrètement "
            "en utilisant un jeu de cartes ordinaire. "
            "Schneier reconnaît lui-même que Solitaire n'a pas été soumis à une cryptanalyse rigoureuse "
            "avant publication, et les biais découverts par Crowley confirment cette prudence."
        ),
    },
    {
        "id": "implementation_tips",
        "title": "Conseils d'implémentation et pièges courants",
        "text": (
            "Pièges courants lors de l'implémentation du chiffrement Solitaire : "
            "1) Joker A en dernière position : il passe en 2ème, pas en 1ère. "
            "2) Joker B en avant-dernière : passe en 2ème; en dernière : passe en 3ème. "
            "3) Modulo 26 = 0 : le résultat 0 représente Z (26), jamais A (1). "
            "4) Opération 4 : la dernière carte ne bouge JAMAIS. "
            "5) Opération 5 : le paquet N'EST PAS MODIFIÉ, seulement lu. "
            "6) Si la sortie est un joker, recommencer TOUT le cycle 1-2-3-4-5. "
            "7) Valeur Bridge (opération 4) : jokers valent 53 (pas 54). "
            "8) Valeur de chiffrement (opération 5) : jokers sont ignorés. "
            "Conseil : valider les vecteurs officiels de Schneier dès le début du développement."
        ),
    },
]

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def _load_knowledge_files() -> list[dict[str, str]]:
    """Charge les chunks depuis les fichiers .txt dans ai/knowledge/.

    Format attendu :
        === (séparateur de chunks)
        CHUNK: identifiant_unique
        TITLE: Titre du chunk

        Contenu textuel...

    Renvoie une liste de dicts {id, title, text}, vide si aucun fichier trouvé.
    """
    if not _KNOWLEDGE_DIR.exists():
        return []

    chunks: list[dict[str, str]] = []
    for txt_file in sorted(_KNOWLEDGE_DIR.glob("*.txt")):
        try:
            content = txt_file.read_text(encoding="utf-8")
            source_prefix = txt_file.stem  # ex : "phase0_prerequis"

            # Diviser par les séparateurs ===
            raw_blocks = content.split("\n===\n")
            for raw in raw_blocks:
                raw = raw.strip()
                # Sauter les blocs d'en-tête SOURCE: ou vides
                if not raw or raw.startswith("SOURCE:"):
                    continue

                lines = raw.split("\n")
                chunk_id: str | None = None
                title: str | None = None
                text_lines: list[str] = []
                in_text = False

                for line in lines:
                    if line.startswith("CHUNK:"):
                        chunk_id = line[6:].strip()
                    elif line.startswith("TITLE:"):
                        title = line[6:].strip()
                        in_text = True  # le texte commence après TITLE:
                    elif in_text:
                        text_lines.append(line)

                if chunk_id and title:
                    text = "\n".join(text_lines).strip()
                    if text:
                        chunks.append({
                            "id": f"{source_prefix}__{chunk_id}",
                            "title": title,
                            "text": text,
                        })
        except Exception:
            pass  # Fichier illisible → ignorer silencieusement

    return chunks


def _build_all_chunks() -> list[dict[str, str]]:
    """Fusionne les chunks de fichiers et les chunks de secours."""
    file_chunks = _load_knowledge_files()
    file_ids = {c["id"] for c in file_chunks}

    # Ajouter les chunks hardcodés qui ne sont pas déjà couverts
    fallback = [c for c in KNOWLEDGE_CHUNKS if c["id"] not in file_ids]
    return file_chunks + fallback


# Base de connaissances finale
ALL_KNOWLEDGE_CHUNKS: list[dict[str, str]] = _build_all_chunks()

# Prompt système
SYSTEM_PROMPT = """Tu es un assistant IA intégré à l'application Solitaire Cipher.
Tu es un expert en cryptographie, spécialisé dans le chiffrement Solitaire de Bruce Schneier.

Tes sources de connaissances :
- L'article original de Schneier (schneier.com/academic/solitaire/)
- L'analyse de Paul Crowley sur les faiblesses statistiques (1999)
- Les vecteurs de test officiels de Schneier
- Le document de prérequis académiques complet (PHASE_0_PREREQUIS.md)

Tes capacités :
- Expliquer en détail chaque étape de l'algorithme Solitaire (5 opérations)
- Décrire le keying, les vecteurs de test, les deux systèmes de valeurs (Bridge vs chiffrement)
- Analyser les biais de Crowley (1/22.5 vs 1/26, 159 sigma, non-réversibilité)
- Expliquer les attaques (réutilisation de clé, crib-dragging)
- Comparer Solitaire à AES, RC4, ChaCha20, OTP
- Répondre aux questions sur la cryptographie générale

Style de réponse :
- Réponds en français, de manière claire et pédagogique
- Utilise des exemples concrets et des formules quand c'est utile
- Structure tes réponses avec des points ou des étapes numérotées
- Sois précis sur les détails techniques (valeurs, formules, cas limites)
- N'invente pas d'informations : base-toi sur le contexte RAG fourni

IMPORTANT : Les passages de la base de connaissances fournis dans le contexte sont issus
des sources primaires (Schneier, Crowley, prérequis académiques). Utilise-les prioritairement.
"""


class SolitaireAssistant:
    """Assistant RAG : ChromaDB pour les embeddings, Gemini pour la génération."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY manquant. Définissez-le dans .env")

        # Import et configuration du SDK (ici, pas au niveau module pour éviter les conflits)
        import google.generativeai as genai
        genai.configure(api_key=self._api_key)
        self._genai = genai

        self._collection = self._init_collection()
        self.knowledge_count = self._collection.count()

    # -- Initialisation ChromaDB --

    def _init_collection(self):
        """Crée ou charge la collection ChromaDB avec embeddings Gemini."""
        import chromadb

        chroma = chromadb.Client()  # in-memory (pas de persistance nécessaire)
        collection = chroma.get_or_create_collection(
            name="solitaire_knowledge",
            metadata={"hnsw:space": "cosine"},
        )

        # Remplir seulement si vide
        if collection.count() == 0:
            self._populate_collection(collection)

        return collection

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Génère les embeddings via gemini-embedding-001."""
        result = self._genai.embed_content(
            model="models/gemini-embedding-001",
            content=texts,
        )
        # Quand content est une liste, embedding est une liste de vecteurs
        emb = result["embedding"]
        if isinstance(emb[0], (int, float)):
            # Cas d'un seul texte → envelopper
            return [emb]
        return emb

    def _populate_collection(self, collection) -> None:
        """Embeds tous les chunks et les ajoute à ChromaDB."""
        texts = [c["text"] for c in ALL_KNOWLEDGE_CHUNKS]
        ids = [c["id"] for c in ALL_KNOWLEDGE_CHUNKS]
        metadatas = [{"title": c["title"]} for c in ALL_KNOWLEDGE_CHUNKS]

        embeddings = self._embed(texts)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

    # -- Retrieval --

    def retrieve(self, query: str, n_results: int = 5) -> list[dict]:
        """Récupère les N passages les plus pertinents pour la requête."""
        query_embedding = self._embed([query])[0]
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        passages = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            passages.append({
                "title": meta["title"],
                "text": doc,
                "score": 1 - dist,  # cosine similarity
            })
        return passages

    # -- Génération --

    def _build_prompt(
        self,
        question: str,
        passages: list[dict],
        context: str | None = None,
    ) -> str:
        """Construit le prompt avec les passages RAG et le contexte applicatif."""
        parts = []

        if context:
            parts.append(f"CONTEXTE APPLICATIF ACTUEL:\n{context}\n")

        if passages:
            parts.append("PASSAGES PERTINENTS DE LA BASE DE CONNAISSANCES:")
            for i, p in enumerate(passages, 1):
                parts.append(f"\n[{i}] {p['title']} (pertinence: {p['score']:.2f})\n{p['text']}")
            parts.append("")

        parts.append(f"QUESTION: {question}")
        return "\n".join(parts)

    def _get_model(self):
        """Retourne le modèle Gemini configuré avec le prompt système."""
        return self._genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
        )

    def _history_to_parts(
        self, history: list[dict] | None
    ) -> list[dict]:
        """Convertit l'historique en format Contents pour le SDK."""
        if not history:
            return []
        contents = []
        for msg in history[-6:]:  # 3 derniers échanges
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})
        return contents

    def ask(
        self,
        question: str,
        conversation_history: list[dict] | None = None,
        context: str | None = None,
        n_passages: int = 5,
    ) -> str:
        """Répond à une question via RAG + Gemini. Retourne la réponse complète."""
        passages = self.retrieve(question, n_results=n_passages)
        prompt = self._build_prompt(question, passages, context)

        model = self._get_model()
        history_parts = self._history_to_parts(conversation_history)

        chat = model.start_chat(history=history_parts)
        response = chat.send_message(prompt)
        return response.text or ""

    def stream_ask(
        self,
        question: str,
        conversation_history: list[dict] | None = None,
        context: str | None = None,
        n_passages: int = 5,
    ) -> Iterator[str]:
        """Répond en streaming. Retourne un itérateur de chunks de texte."""
        passages = self.retrieve(question, n_results=n_passages)
        prompt = self._build_prompt(question, passages, context)

        model = self._get_model()
        history_parts = self._history_to_parts(conversation_history)

        chat = model.start_chat(history=history_parts)
        for chunk in chat.send_message(prompt, stream=True):
            if chunk.text:
                yield chunk.text



def build_context_from_state(state: dict) -> str:
    """Génère un contexte textuel depuis l'état de la session Streamlit."""
    lines = []
    if state.get("demo_deck"):
        deck = state["demo_deck"]
        from visuals.card_loader import card_short_name
        deck_str = " ".join(card_short_name(c) for c in deck[:10]) + "..."
        lines.append(f"Paquet actuel (10 premières cartes) : {deck_str}")
    if state.get("demo_log"):
        last_log = state["demo_log"][-1] if state["demo_log"] else ""
        lines.append(f"Dernière opération effectuée : {last_log}")
    if state.get("demo_output_val"):
        lines.append(f"Dernière valeur de sortie : {state['demo_output_val']}")
    return "\n".join(lines) if lines else ""
