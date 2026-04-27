# PLAN MAITRE - Projet Solitaire Cipher (Note Parfaite : 14/14)

## Barème

| Critère | Points | Poids |
|---------|--------|-------|
| **Convivialité** (manip, visuel, clarté) | 3 | 21% |
| **Fonctionnement** | 7 | 50% |
| **Originalité** | 1 | 7% |
| **Fiabilité, sécurité** | 2 | 14% |
| **Tests** | 1 | 7% |

## État d'avancement (MAJ : 18/04/2026)

- [x] Phase 1 terminée et validée
- [x] Vecteurs officiels de Schneier validés (3/3 ✅)
- [x] Tests automatisés en place (`115 passed`)
- [x] Phase 2 terminée (app.py Streamlit + 54 cartes cyberpunk + visualisation interactive)
- [x] Phase 3 démarrée : Assistant IA RAG (ChromaDB + gemini-embedding-001 + gemini-2.5-flash)
- [x] Phase 4 démarrée : Démonstration réutilisation de clé + métriques de sécurité
- [ ] Phase 5 finalisée (tests déjà à 115, à compléter)

---

## Choix technologique : Python + Streamlit

**Pourquoi Python :**
- Langage natif de l'IA (PyTorch, scikit-learn, ChromaDB, Ollama)
- Excellentes bibliothèques de visualisation (Pillow, matplotlib, plotly)
- Parfait pour la cryptographie (opérations modulaires, manipulation de listes)
- Frameworks GUI modernes (Streamlit, Gradio, Flet)
- Intégration facile des APIs LLM (Gemini, OpenAI, Ollama)
- Bibliothèques de test solides (pytest)

**Architecture du projet :**

```
projet-solitaire/
├── app.py                        # Interface Streamlit principale
├── core/
│   ├── deck.py                   # Représentation du paquet de 54 cartes
│   ├── solitaire.py              # Algorithme Solitaire complet (5 opérations)
│   ├── solitaire_simple.py       # Version simplifiée
│   ├── encryption.py             # Chiffrement/déchiffrement (mod 26)
│   └── keystream.py              # Génération du flux de clés
├── visuals/
│   ├── card_generator.py         # Génération des visuels via API Gemini
│   ├── card_renderer.py          # Post-traitement avec Pillow
│   └── assets/
│       ├── clubs/                # Trèfles (cartes 1-13)
│       ├── diamonds/             # Carreaux (cartes 14-26)
│       ├── hearts/               # Coeurs (cartes 27-39)
│       ├── spades/               # Piques (cartes 40-52)
│       └── jokers/               # Joker noir (53), Joker rouge (54)
├── ai/
│   ├── assistant.py              # Assistant LLM avec RAG (Gemini API)
│   ├── cryptanalysis.py          # Analyse IA du chiffrement (LSTM/CNN)
│   └── randomness_analyzer.py    # Tests NIST + comparaison statistique
├── network/
│   ├── chat_server.py            # Serveur de chat chiffré (WebSocket)
│   ├── chat_client.py            # Client de chat
│   └── key_exchange.py           # Échange de clés Diffie-Hellman
├── security/
│   ├── key_reuse_demo.py         # Démonstration réutilisation de clé
│   └── frequency_analysis.py     # Analyse fréquentielle comparative
├── tests/
│   ├── test_deck.py
│   ├── test_solitaire.py
│   ├── test_encryption.py
│   ├── test_vectors.py           # Vecteurs de test officiels Schneier
│   └── test_edge_cases.py
├── docs/
│   └── screenshots/
└── requirements.txt
```

---

## PHASE 0 : Préparation (Jour 1-2)

### 0.1 Comprendre l'algorithme à fond
- [ ] Lire l'article original de Bruce Schneier : https://www.schneier.com/academic/solitaire/
- [ ] Lire l'analyse de Paul Crowley (faiblesses connues) : http://www.ciphergoth.org/crypto/solitaire/
- [ ] Lire la page Wikipedia sur le Solitaire cipher
- [ ] Comprendre le contexte : le roman "Cryptonomicon" de Neal Stephenson
- [ ] **Faire l'algorithme à la main** avec un vrai jeu de 54 cartes pour intérioriser chaque étape

### 0.2 Étudier les implémentations existantes (référence uniquement)
- [ ] `keithfancher/Pontifex` (Python propre)
- [ ] `c-mart/solitaire-pontifex` (Python, mode verbose)
- [ ] dCode pour valider : https://www.dcode.fr/solitaire-cipher-schneier

### 0.3 Installer l'environnement
```
pip install streamlit pillow google-generativeai pytest plotly numpy
pip install chromadb sentence-transformers websockets scipy
```

### 0.4 Vecteurs de test officiels (Schneier) — CRITIQUES

| # | Clé | Clair | Chiffré attendu |
|---|-----|-------|-----------------|
| 1 | Deck standard (1-52, JokerA, JokerB) | `AAAAAAAAAA` | `EXKYIZSGEH` |
| 2 | `FOO` | `AAAAAAAAAAAAAAA` | `ITHZUJIWGRFARMW` |
| 3 | `CRYPTONOMICON` | `SOLITAIREX` | `KIRAKSFJAN` |

---

## PHASE 1 : Fonctionnement de l'algorithme — 7 POINTS (LE PLUS IMPORTANT)

### Suivi d'avancement Phase 1
- [x] 1.1 Représentation du paquet (`core/deck.py`)
- [x] 1.2 Conversion texte ↔ nombres (`core/encryption.py`)
- [x] 1.3 5 opérations de mélange (`core/solitaire.py`)
- [x] 1.4 Version simplifiée (`core/solitaire_simple.py`)
- [x] 1.5 Keying par mot de passe (`core/keystream.py`)
- [x] 1.6 Flux chiffrement/déchiffrement avec état de paquet
- [x] 1.7 Validation impérative (vecteurs Schneier + cas longs)

### Livrables implémentés
- `core/deck.py`
- `core/solitaire.py`
- `core/solitaire_simple.py`
- `core/keystream.py`
- `core/encryption.py`
- `tests/test_deck.py`
- `tests/test_solitaire.py`
- `tests/test_encryption.py`
- `tests/test_schneier_vectors.py`
- `tests/test_edge_cases.py`

### 1.1 Représentation du paquet (`deck.py`)

**Modélisation :**
- Chaque carte = un entier de 1 à 54
- 1-13 : Trèfles (As→Roi, ordre Bridge)
- 14-26 : Carreaux (As→Roi)
- 27-39 : Coeurs (As→Roi)
- 40-52 : Piques (As→Roi)
- 53 : Joker A (noir)
- 54 : Joker B (rouge)
- Le paquet = une liste ordonnée de 54 entiers

**Fonctions à implémenter :**
- `create_deck()` : paquet dans l'ordre standard
- `card_to_string(n)` : "As de Trèfle", "Roi de Pique", "Joker Rouge", etc.
- `card_value(n)` : valeur pour le chiffrement (1-52 pour cartes, 53 pour jokers)
- `card_bridge_value(n)` : valeur Bridge pour les coupes (1-53)
- `find_card(deck, card)` : trouver la position d'une carte
- `display_deck(deck)` : affichage formaté lisible

### 1.2 Conversion texte ↔ nombres (`encryption.py`)

**Prétraitement du message :**
- Supprimer tout ce qui n'est pas une lettre (espaces, ponctuation)
- Convertir en majuscules
- Remplacer les accents : é/è/ê→E, à→A, ù→U, ç→C, î/ï→I, etc.
- Chaque lettre → nombre : A=1, B=2, ..., Z=26

**Chiffrement :**
- `(valeur_clair + valeur_flux) mod 26`
- Si résultat = 0 → Z (26) ← **PIÈGE CLASSIQUE : 0 ≠ A**
- Convertir en lettre

**Déchiffrement :**
- `(valeur_chiffré - valeur_flux) mod 26`
- Si résultat ≤ 0 → ajouter 26
- Convertir en lettre

### 1.3 Les 5 opérations de mélange (`solitaire.py`)

#### Opération 1 : Recul du Joker Noir (A) d'une position
- Trouver la position du Joker A (valeur 53)
- Permuter avec la carte juste après
- **CAS SPÉCIAL** : Si Joker A est en **dernière position** → il passe en **2ème position**
- ⚠️ Piège #1 — tester ce cas en priorité

#### Opération 2 : Recul du Joker Rouge (B) de deux positions
- Trouver la position du Joker B (valeur 54)
- Déplacer de 2 positions vers le bas
- **CAS SPÉCIAUX** :
  - Si en **dernière position** → passe en **3ème position**
  - Si en **avant-dernière position** → passe en **2ème position**
- ⚠️ Le Joker B ne peut JAMAIS se retrouver en 1ère position

#### Opération 3 : Double coupe par rapport aux jokers
- Repérer les positions des deux jokers (peu importe A ou B, prendre l'ordre de position)
- 3 segments : [au-dessus du 1er joker] | [1er joker...2nd joker] | [sous le 2nd joker]
- Intervertir segment du dessus avec segment du dessous
- Les jokers et les cartes entre eux restent en place
- Si un joker est en 1ère ou dernière position → un segment est vide (cas valide)

#### Opération 4 : Coupe simple déterminée par la dernière carte
- Regarder la **dernière carte** du paquet → sa valeur Bridge (1-53)
- Prendre les n premières cartes du dessus
- Les placer juste **au-dessus de la dernière carte**
- ⚠️ **La dernière carte ne bouge JAMAIS**
- ⚠️ Si la dernière carte est un joker (valeur 53) → on prend 53 cartes sur 54 → en pratique le paquet ne change pas

#### Opération 5 : Lecture d'une lettre pseudo-aléatoire
- Regarder la 1ère carte du paquet → soit n sa valeur (1-53)
- Compter n cartes depuis le début → regarder la carte en position **n+1**
- Soit m sa valeur
- **Si c'est un joker** → recommencer TOUT le cycle (1-2-3-4-5) sans compter cette itération
- Si m > 26 → soustraire 26
- Le résultat (1-26) est la lettre suivante du flux de clés
- ⚠️ **Cette opération ne modifie PAS l'ordre du paquet**

### 1.4 Version simplifiée (`solitaire_simple.py`)
- Après lecture de la carte du dessus :
  - Tour impair → placer la carte en **dernière** position
  - Tour pair → placer la carte en **avant-dernière** position
- Alterner ces deux opérations (plus simple, moins sûr)

### 1.5 Clé initiale — Keying du paquet

**Méthode 1 — Ordre fixe :** paquet dans un ordre convenu à l'avance

**Méthode 2 — Keying par mot de passe (Schneier) :**
- Pour chaque lettre du mot de passe :
  1. Effectuer les opérations 1, 2, 3, 4 (pas de lecture)
  2. Faire une coupe supplémentaire en utilisant la valeur de la lettre (A=1, B=2...)
- Schneier recommande au minimum 64-80 caractères

### 1.6 Flux complet chiffrement/déchiffrement
- L'état du paquet **est conservé entre les messages** successifs
- Chaque nouveau message reprend là où le précédent s'est arrêté

### 1.7 Validation impérative
- Tester les 3 vecteurs officiels de Schneier → tout doit correspondre exactement
- Tester chiffrement puis déchiffrement → retrouver le message original
- Tester avec des messages longs (100+ caractères)

---

## PHASE 2 : Convivialité & Visuels — 3 POINTS

### 2.1 Génération des 54 visuels de cartes uniques

**Thème recommandé : Cyberpunk Cryptographie**
- Fond sombre (noir/bleu nuit)
- Accents néon (cyan, magenta, vert)
- Motifs de circuits imprimés dans les bordures
- Texte chiffré en filigrane dans le fond
- Figures (V, D, R) comme personnages cyberpunk/hackers
- Jokers comme entités IA mystérieuses
- Symboles redesignés : Trèfle=Chip, Carreau=Cristal, Coeur=Bouclier, Pique=Clé

**Pipeline de génération :**
1. Script Python → API Gemini (`gemini-3.1-flash-image-preview`) ← **gratuit ou ~$3.62 pour 54 cartes**
2. Prompt structuré pour chaque carte (style cohérent avec seed fixe)
3. Post-traitement Pillow : ajouter numéro, couleur, valeur Bridge visible
4. Exporter en PNG → dossier `assets/`

**Alternatives :**
- ComfyUI / AUTOMATIC1111 (Stable Diffusion local, gratuit)
- FLUX Schnell via Replicate (~$0.16 pour 54 cartes)
- Canva (design manuel, export PNG)

### 2.2 Interface Streamlit

**Page principale :**
- Titre + logo du projet
- Sélection du mode : Chiffrement / Déchiffrement / Démo step-by-step / Chat chiffré / Analyse IA
- Zone de saisie du message + zone de saisie/génération de la clé
- Bouton Chiffrer / Déchiffrer
- Résultat affiché avec code couleur : vert = clair, rouge = chiffré, bleu = flux de clé

**Visualisation du paquet :**
- Afficher les 54 cartes avec leurs images dans l'ordre actuel
- Mode step-by-step : à chaque opération, les cartes concernées sont surlignées
  - Joker A se déplace → animation/highlight rouge
  - Joker B se déplace → animation/highlight bleu
  - Triple coupe → 3 segments colorés qui s'intervertissent
  - Coupe simple → la carte du bas s'illumine, les n premières cartes glissent
  - Lecture → la carte output s'agrandit et affiche la lettre générée

**Sidebar :**
- Choix de la clé (manuelle / mot de passe / aléatoire)
- Choix algorithme (complet vs simplifié)
- Mode verbose (afficher chaque étape intermédiaire)
- Thème visuel (possibilité de régénérer les cartes avec un nouveau prompt IA)
- Historique des messages chiffrés de la session

### 2.3 Commodité des manipulations
- Bouton "Copier le résultat" en un clic
- Import/export de l'état du paquet (fichier JSON)
- Sauvegarde/chargement de sessions
- Messages d'erreur clairs en français
- Tooltips explicatifs sur chaque bouton/étape
- Mode "Tutoriel" guidé pour les débutants

### 2.4 Clarté
- Chaque étape de l'algorithme expliquée en temps réel dans un panneau dédié
- Code couleur cohérent et documenté
- Indicateur de progression pour les longs messages
- Glossaire intégré (flux de clé, joker, coupe simple, triple coupe, etc.)

---

## PHASE 3 : Originalité & Intégration IA — 1 POINT (+ fort différenciateur)

### 3.1 Assistant IA Cryptographique avec RAG

**Un chatbot Gemini intégré qui :**
- Explique chaque étape de l'algorithme quand l'utilisateur demande
- Répond aux questions sur la cryptographie (stream ciphers, one-time pad, etc.)
- Compare Solitaire à AES, RSA, RC4
- Explique la sécurité : 54! ≈ 2.3 × 10^71 ordres possibles

**RAG (Retrieval-Augmented Generation) :**
- Base vectorielle ChromaDB avec les documents clés :
  - Article original de Schneier
  - Analyse de Paul Crowley (biais connus)
  - Articles du cours de cryptographie
- Embeddings avec `text-embedding-004` (Google, gratuit)
- Sur chaque question : top-5 passages pertinents → injectés dans le prompt Gemini
- Plus impressionnant qu'un chatbot basique, montre la maîtrise du RAG

### 3.2 Cryptanalyse assistée par ML

**a) Détection du biais statistique (Crowley 1999) :**
- Générer 2 datasets : sorties Solitaire vs données vraiment aléatoires
- Entraîner un classifieur binaire (LSTM 1D ou CNN 1D) pour les distinguer
- Si précision > 50% significativement → on démontre la faiblesse réelle du cipher
- Paul Crowley a prouvé un biais : 2ème lettre a 1/22.5 chance d'être identique à la 1ère (vs 1/26 attendu)

**b) Démonstration du danger de réutilisation de clé :**
- Chiffrer 2 messages différents avec la même clé
- Montrer visuellement que : chiffré1 - chiffré2 = clair1 - clair2
- Appliquer une attaque par crib-dragging automatisée
- Scorer les candidats avec un modèle de langue (le français valide le bon déchiffrement)
- Graphique des probabilités

**c) Tests NIST de randomness :**
- Implémenter les tests NIST SP 800-22 (fréquence, runs, chi-carré, autocorrélation)
- Comparer Solitaire vs `random.random()` Python vs `/dev/urandom`
- Graphiques comparatifs plotly
- L'assistant IA interprète les résultats

**d) Réseau récurrent prédicteur :**
- Entraîner un LSTM/GRU sur des séquences de flux de clés
- Mesurer si le modèle prédit mieux que 1/26 (= 3.85%)
- Courbe d'apprentissage visualisée
- Même un échec est intéressant : "le réseau n'arrive pas à prédire → le flux résiste à l'analyse ML"

### 3.3 Génération dynamique de thèmes de cartes
- L'utilisateur tape un thème libre ("médiéval", "spatial", "steampunk", "Art Nouveau")
- Gemini génère 54 nouvelles cartes avec ce thème
- Rend l'application infiniment personnalisable

### 3.4 IA pour suggérer des clés fortes
- Algorithme génétique qui optimise les ordres de paquet
- Fonction fitness = score aux tests NIST sur les N premières sorties
- Visualiser l'évolution de la fitness sur les générations

---

## PHASE 4 : Fiabilité & Sécurité — 2 POINTS

### 4.1 Robustesse du code

**Validation de toutes les entrées :**
- Message : gérer les caractères spéciaux, accents, ponctuation, chiffres
- Clé manuelle : vérifier 54 cartes, pas de doublons, valeurs 1-54
- Mot de passe : avertir si < 64 caractères (recommandation Schneier)
- Message vide : message d'erreur clair

**Gestion des cas limites :**
- Message uniquement composé de caractères non-alphabétiques
- Jokers adjacents dans le paquet initial
- Joker en première ou dernière position au départ
- Message très long (1000+ caractères)
- Toutes les lettres identiques (ex : "AAAA...") pour tester le biais

**Pas de crash :**
- Chaque erreur est catchée avec try/except
- Message d'erreur lisible en français affiché dans l'UI
- Logs en mode debug pour faciliter le débogage

### 4.2 Sécurité cryptographique

**Démonstration réutilisation de clé (Section 2 du sujet) :**
- Implémentation complète de l'attaque
- Visualisation graphique du mécanisme
- L'assistant IA explique pourquoi c'est catastrophique

**Analyse de la force de la clé :**
- Calculer l'entropie : log2(54!) ≈ **226 bits**
- Comparaison : AES-128 (128 bits), AES-256 (256 bits)
- 54! ≈ 2.3 × 10^71 → brute force impossible
- Durée estimée d'une attaque brute force (affiché dans l'UI)

**Mesures implémentées :**
- Avertissement si l'utilisateur réutilise un paquet déjà utilisé
- Compteur du nombre de messages chiffrés avec la même clé
- Ne jamais stocker les clés en plaintext dans des logs
- Avertissement si mot de passe trop court

### 4.3 Fiabilité
- Résultats reproductibles : même entrée → même sortie toujours
- Utiliser des copies du paquet (pas de mutation en place) ← **votre règle de coding style**
- Journalisation des opérations pour audit (optionnel)

---

## PHASE 5 : Tests — 1 POINT

### 5.1 Tests unitaires (pytest)

**Tests du paquet (`test_deck.py`) :**
- `test_create_deck` : 54 cartes, toutes différentes, valeurs 1-54
- `test_card_to_string` : conversion correcte pour chaque carte
- `test_card_bridge_value` : jokers = 53, vérification toutes couleurs
- `test_find_card` : trouver jokers, as, rois

**Tests des 5 opérations (`test_solitaire.py`) :**
- `test_move_joker_a_normal` : cas standard
- `test_move_joker_a_last_position` : ⚠️ cas critique → passe en 2ème
- `test_move_joker_b_normal` : cas standard
- `test_move_joker_b_last_position` : ⚠️ cas critique → passe en 3ème
- `test_move_joker_b_second_to_last` : ⚠️ cas critique → passe en 2ème
- `test_triple_cut_normal` : cas standard
- `test_triple_cut_joker_at_top` : segment vide en haut
- `test_triple_cut_joker_at_bottom` : segment vide en bas
- `test_triple_cut_jokers_adjacent` : les jokers sont côte à côte
- `test_count_cut_normal` : cas standard
- `test_count_cut_joker_last` : paquet ne change pas
- `test_read_output_normal` : lecture standard → valeur entre 1 et 26
- `test_read_output_skip_joker` : si sortie = joker, refaire le cycle
- `test_read_output_does_not_modify_deck` : le paquet reste identique

**Tests chiffrement (`test_encryption.py`) :**
- `test_text_preprocessing` : accents, espaces, ponctuation correctement traités
- `test_encrypt_single_letter`
- `test_decrypt_single_letter`
- `test_encrypt_decrypt_roundtrip_short` : message court
- `test_encrypt_decrypt_roundtrip_long` : message de 200 caractères

**Vecteurs officiels (`test_vectors.py`) :**
- `test_vector_1_unkeyed_deck` : "AAAAAAAAAA" → "EXKYIZSGEH"
- `test_vector_2_key_foo` : clé "FOO", "AAAAAAAAAAAAAAA" → "ITHZUJIWGRFARMW"
- `test_vector_3_key_cryptonomicon` : clé "CRYPTONOMICON", "SOLITAIREX" → "KIRAKSFJAN"

**Cas limites (`test_edge_cases.py`) :**
- `test_empty_message` : message vide → erreur claire
- `test_all_spaces` : message avec seulement des espaces
- `test_all_same_letters` : "AAAA..." de 100 caractères
- `test_message_state_persists` : chiffrer msg1 puis msg2, vérifier que le paquet a évolué
- `test_deck_always_54_cards` : après chaque opération, 54 cartes exactement
- `test_no_duplicate_cards` : après chaque opération, aucun doublon

### 5.2 Tests d'intégration
- Chiffrement multi-messages successifs avec persistance d'état
- Keying par mot de passe + chiffrement + déchiffrement complet
- Version simplifiée : chiffrement + déchiffrement

### 5.3 Tests de performance
- Mesurer le temps pour 1, 10, 100, 1000, 10000 caractères
- Graphique temps vs longueur (pour montrer la scalabilité linéaire)

---

## PHASE 6 : Réseau & Communication chiffrée (BONUS)

### 6.1 Chat chiffré en temps réel
- Serveur WebSocket Python (`websockets`)
- 2 clients qui se connectent et échangent des messages
- Chaque message est chiffré avec Solitaire avant envoi
- Le serveur est un relais aveugle (ne voit que le texte chiffré)
- Interface dans Streamlit ou terminal

### 6.2 Échange de clés Diffie-Hellman
- Les deux parties effectuent un DH classique → secret partagé S
- S sert de seed à un PRNG cryptographiquement sûr (HMAC-DRBG)
- Le PRNG effectue un Fisher-Yates shuffle → même ordre du paquet pour les deux
- Aucun ordre de paquet transmis sur le réseau
- Parallèle TLS 1.3 expliqué par l'assistant IA

### 6.3 Démonstration Man-in-the-Middle
- Mode "attaquant" qui intercepte le DH sans authentification
- Montrer comment l'attaque fonctionne
- Montrer la solution : signatures numériques (station-to-station protocol)

---

## PHASE 7 : Rapport

### Structure du rapport
1. Introduction : contexte, Schneier, Cryptonomicon
2. L'algorithme Solitaire : description formelle, les 5 opérations, justification mathématique
3. Choix techniques : pourquoi Python, architecture, bibliothèques
4. Implémentation : détails de chaque module
5. Visuels : processus de génération des cartes par IA, choix du thème
6. Intégration IA : assistant RAG, cryptanalyse ML, génération de visuels
7. Sécurité : analyse de robustesse, danger de réutilisation, tests NIST
8. Tests : méthodologie, couverture, résultats des vecteurs officiels
9. Réseau (si implémenté) : architecture, DH, chat chiffré
10. Conclusion : limites de Solitaire, comparaison avec algorithmes modernes

---

## CALENDRIER DE TRAVAIL

| Jour | Phase | Tâches | Points visés |
|------|-------|--------|--------------|
| 1-2 | Phase 0 | Comprendre algo, setup env, vecteurs de test | — |
| 3-5 | Phase 1.1-1.3 | Deck + 5 opérations + version simplifiée | ✅ 4/7 |
| 6-7 | Phase 1.4-1.7 | Chiffrement/déchiffrement + keying + validation | ✅ **7/7** |
| 8-9 | Phase 2.1 | 54 visuels de cartes (API Gemini) | 1/3 |
| 10-11 | Phase 2.2-2.4 | Interface Streamlit complète + animations | **3/3** |
| 12-13 | Phase 3.1 | Assistant IA + RAG (ChromaDB + Gemini) | 0.5/1 |
| 14 | Phase 3.2-3.4 | Cryptanalyse ML + génération thèmes | **1/1** |
| 15-16 | Phase 4 | Sécurité, robustesse, gestion erreurs | **2/2** |
| 17 | Phase 5 | Tests complets avec pytest | **1/1** |
| 18-19 | Phase 6 | Chat chiffré + Diffie-Hellman (bonus) | bonus |
| 20 | Phase 7 | Rapport + screenshots + polish final | — |

---

## PIÈGES CRITIQUES À ÉVITER

| # | Piège | Description | Solution |
|---|-------|-------------|----------|
| 1 | **Wrapping Joker A** | En dernière position → 2ème (pas 1ère) | Tester ce cas en premier |
| 2 | **Wrapping Joker B** | Dernière → 3ème, avant-dernière → 2ème | Deux cas spéciaux distincts |
| 3 | **Modulo 26 = 0** | 0 doit être Z (26), pas A (1) | Vérifier avec vecteur #1 |
| 4 | **Dernière carte immobile** | Dans l'opération 4, la dernière carte ne bouge jamais | Ne jamais la déplacer |
| 5 | **Skip des jokers en sortie** | Si sortie = joker, refaire TOUT le cycle 1-2-3-4-5 | Boucle while jusqu'à sortie valide |
| 6 | **Opération 5 = lecture seule** | N'MODIFIE PAS le paquet | Travailler sur une copie |
| 7 | **Propagation d'erreur** | 1 erreur corrompt TOUT le reste du flux | Valider les vecteurs tôt |
| 8 | **Valeur Bridge vs valeur de chiffrement** | Coupes : 1-53 / Sortie finale : 1-26 | Deux fonctions séparées |

---


| Aspect | La plupart des étudiants | Vous |
|--------|--------------------------|------|
| Interface | Terminal / `print()` | Streamlit avec 54 cartes animées |
| Visuels | Aucun | 54 cartes uniques générées par IA, thème cyberpunk |
| IA | Rien | Assistant RAG + cryptanalyse LSTM + génération visuelle |
| Sécurité | Mention basique | Démo réutilisation clé + tests NIST + attaque crib-dragging |
| Tests | Quelques `print()` | pytest complet + 3 vecteurs officiels Schneier |
| Réseau | Rien | Chat chiffré + échange de clés DH |
| Personnalisation | Aucune | Thèmes régénérés dynamiquement par prompt utilisateur |

---

## RESSOURCES CLÉS

- **Algorithme original** : https://www.schneier.com/academic/solitaire/
- **Analyse des faiblesses** : http://www.ciphergoth.org/crypto/solitaire/
- **Valider vos résultats** : https://www.dcode.fr/solitaire-cipher-schneier
- **Référence Python propre** : https://github.com/keithfancher/Pontifex
- **Cartes SVG libres** : https://github.com/htdebeer/SVG-cards
- **API Gemini** : https://ai.google.dev/gemini-api/docs
- **Streamlit** : https://docs.streamlit.io
- **ChromaDB (RAG)** : https://docs.trychroma.com
- **Tests NIST** : https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final
