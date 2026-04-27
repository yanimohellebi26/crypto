# PHASE 0 — Tout comprendre avant de coder

> **Objectif :** Maîtriser parfaitement l'algorithme Solitaire, ses fondements cryptographiques, ses pièges, et ses faiblesses **avant d'écrire la moindre ligne de code**.

---

## Table des matières

1. [Contexte historique](#1-contexte-historique)
2. [Prérequis mathématiques](#2-prérequis-mathématiques)
3. [Prérequis cryptographiques](#3-prérequis-cryptographiques)
4. [Le jeu de 54 cartes — modélisation](#4-le-jeu-de-54-cartes--modélisation)
5. [Le codage/décodage par addition modulaire](#5-le-codagedecodage-par-addition-modulaire)
6. [Les 5 opérations de mélange — description formelle](#6-les-5-opérations-de-mélange--description-formelle)
7. [Le keying du paquet (initialisation par mot de passe)](#7-le-keying-du-paquet-initialisation-par-mot-de-passe)
8. [La version simplifiée](#8-la-version-simplifiée)
9. [Vecteurs de test officiels de Schneier](#9-vecteurs-de-test-officiels-de-schneier)
10. [Pourquoi ne jamais réutiliser la clé](#10-pourquoi-ne-jamais-réutiliser-la-clé)
11. [Faiblesses connues (Crowley 1999)](#11-faiblesses-connues-crowley-1999)
12. [Pièges d'implémentation critiques](#12-pièges-dimplémentation-critiques)
13. [Exercice à la main](#13-exercice-à-la-main--faire-lalgorithme-sur-papier)
14. [Ressources de référence](#14-ressources-de-référence)
15. [Glossaire](#15-glossaire)

---

## 1. Contexte historique

### L'origine : *Cryptonomicon* de Neal Stephenson (1999)

Le roman *Cryptonomicon* de Neal Stephenson met en scène des personnages qui utilisent un système cryptographique nommé **« Pontifex »** pour communiquer secrètement. L'un d'eux, Enoch Root, explique le fonctionnement du système à Randy Waterhouse — et révèle ensuite que les étapes correspondent à des manipulations d'un **jeu de cartes ordinaire**. Le nom de code « Pontifex » servait à masquer l'utilisation de cartes à jouer.

### Le concepteur : Bruce Schneier

**Bruce Schneier** est un cryptographe de renommée mondiale, auteur du livre de référence *Applied Cryptography* (1996). C'est Neal Stephenson qui lui a demandé de concevoir un algorithme réaliste pour le roman. Schneier a relevé le défi en créant **Solitaire** — un chiffrement qui :

- Peut être exécuté **entièrement à la main** avec un jeu de 54 cartes
- Offre une sécurité comparable aux algorithmes informatiques
- Ne nécessite **aucun matériel électronique** ni outil suspect
- Est conçu pour résister même aux attaquants les plus puissants (NSA, etc.)

### Pourquoi un chiffrement manuel ?

Dans un contexte d'espionnage ou de régime totalitaire :
- Un **ordinateur avec des outils crypto** = preuve incriminante
- Un **jeu de cartes** = objet anodin, inoffensif
- Un agent de terrain peut chiffrer/déchiffrer sans aucune technologie
- Même condamné à ne plus toucher un ordinateur (cas de Kevin Mitnick), on peut encore utiliser des cartes

### Temps nécessaire

Schneier prévient : Solitaire n'est pas rapide. Il faut **une soirée entière** pour chiffrer ou déchiffrer un message raisonnablement long (quelques milliers de caractères max). C'est comparable aux vrais chiffrements manuels utilisés par les espions soviétiques (décrit dans *Kahn on Codes* de David Kahn).

---

## 2. Prérequis mathématiques

### 2.1 Arithmétique modulaire (mod 26)

L'arithmétique modulaire est le cœur du chiffrement. Le **modulo** donne le reste d'une division entière.

**Définition :**
```
a mod n = reste de la division de a par n
```

**Exemples avec mod 26 :**
```
 5 mod 26 = 5       (5 < 26, donc reste = 5)
27 mod 26 = 1       (27 = 1×26 + 1)
52 mod 26 = 0       (52 = 2×26 + 0)
26 mod 26 = 0       (26 = 1×26 + 0)
```

**Analogie de l'horloge :** Imaginons un cadran de 26 positions (A à Z). Quand on dépasse Z, on revient à A. C'est exactement comme une horloge de 12 heures : 11h + 3h = 2h (14 mod 12 = 2).

### ⚠️ PIÈGE CRITIQUE : le cas mod 26 = 0

En cryptographie, les lettres sont numérotées **A=1, B=2, ..., Z=26** (et non de 0 à 25).

Quand le résultat du modulo vaut **0**, ce n'est **pas A (1)** mais **Z (26)** !

```
Chiffrement : (valeur_clair + valeur_flux) mod 26
  → Si résultat = 0, alors la lettre est Z (26), PAS A

Déchiffrement : (valeur_chiffré - valeur_flux)
  → Si résultat ≤ 0, ajouter 26
```

**Exemple :**
```
Chiffrement de Z (26) avec flux M (13) :
  26 + 13 = 39
  39 mod 26 = 13 → M

Chiffrement de M (13) avec flux N (14) :
  13 + 14 = 27
  27 mod 26 = 1 → A

Chiffrement de N (14) avec flux L (12) :
  14 + 12 = 26
  26 mod 26 = 0 → Z (PAS A !)
```

### 2.2 Permutations

Une permutation est un **réarrangement** d'un ensemble d'éléments. Un paquet de 54 cartes dans un ordre donné est une permutation de {1, 2, 3, ..., 54}.

**Le nombre total de permutations de 54 cartes :**
$$54! = 54 \times 53 \times 52 \times \ldots \times 2 \times 1 \approx 2.31 \times 10^{71}$$

En bits d'entropie :
$$\log_2(54!) \approx 226 \text{ bits}$$

Pour comparaison :
| Algorithme | Taille de clé |
|-----------|---------------|
| AES-128 | 128 bits |
| AES-256 | 256 bits |
| Solitaire | **~226 bits** |
| RSA-2048 | ~112 bits (sécurité effective) |

→ L'espace de clés de Solitaire est **immense**. Le brute force est impossible.

### 2.3 Indexation et position dans une liste

Le paquet de cartes est une **liste ordonnée** de 54 éléments. L'indexation commence à **0** en Python, mais l'algorithme original raisonne en positions **1 à 54**.

**Attention :** les opérations de coupe, de déplacement et de lecture utilisent des indices. Une erreur d'indice de ±1 (erreur « off-by-one ») corrompt **tout** le flux de clés qui suit.

---

## 3. Prérequis cryptographiques

### 3.1 Chiffrement par flux (Stream Cipher)

Solitaire est un **chiffrement par flux en mode output-feedback (OFB)**. Cela signifie :

1. Un **générateur pseudo-aléatoire** (CPRNG) produit une séquence de nombres (**flux de clés** / keystream)
2. Chaque nombre du flux est combiné avec un caractère du message clair
3. La combinaison se fait par **addition modulo 26** (chiffrement) ou **soustraction modulo 26** (déchiffrement)

```
Chiffrement : Ci = (Pi + Ki) mod 26     (0 → 26)
Déchiffrement : Pi = (Ci - Ki) mod 26   (≤0 → +26)

où Pi = lettre claire, Ki = lettre du flux, Ci = lettre chiffrée
```

**Le flux de clés est déterministe** : à partir du même état initial du paquet, on génère toujours la même séquence. C'est pourquoi l'émetteur et le récepteur doivent partager le même ordre initial.

### 3.2 Masque jetable (One-Time Pad)

Le **masque jetable** est la seule méthode de chiffrement **mathématiquement prouvée inviolable** (Shannon, 1949). Ses conditions :
- La clé est **aussi longue** que le message
- La clé est **parfaitement aléatoire**
- La clé n'est **jamais réutilisée**

Solitaire s'en inspire : il produit un flux pseudo-aléatoire qui simule un masque jetable. La différence : le flux n'est pas réellement aléatoire, il est **déterministe** (déterminé par l'état du paquet). C'est pourquoi Solitaire est un **stream cipher** et non un vrai masque jetable.

### 3.3 CPRNG — Générateur pseudo-aléatoire

Le cœur de Solitaire est un **CPRNG** (Cryptographically secure Pseudo-Random Number Generator). À chaque itération de l'algorithme :
- Les 5 opérations de mélange transforment l'état du paquet
- L'opération 5 lit une valeur de sortie (1-26) sans modifier le paquet
- Si la sortie est un joker, on recommence sans compter cette itération

**Propriétés recherchées :**
- **Période longue** : la séquence ne se répète pas avant très longtemps
- **Uniformité** : chaque valeur (1 à 26) a une probabilité ≈ 1/26
- **Imprévisibilité** : connaître les N premières sorties ne permet pas de deviner la N+1ème

### 3.4 Comparaison avec d'autres algorithmes

| Propriété | Solitaire | RC4 | AES-CTR | OTP |
|-----------|-----------|-----|---------|-----|
| Type | Stream cipher | Stream cipher | Block cipher (mode flux) | Masque jetable |
| Implémentation | Manuelle (cartes) | Logicielle | Logicielle/Matérielle | Manuelle possible |
| Sécurité prouvée | Non | Non | Non (mais confiance élevée) | **Oui** |
| Taille de clé | ~226 bits | 40-2048 bits | 128/256 bits | = longueur message |
| Biais connu | Oui (Crowley) | Oui (pire) | Non connu | Aucun |

---

## 4. Le jeu de 54 cartes — modélisation

### 4.1 Les 54 cartes

Un jeu standard de 52 cartes + 2 jokers. Chaque carte reçoit un **numéro unique de 1 à 54**.

**Ordre Bridge (standard international) :**

| Couleur | Symbole | Cartes | Numéros |
|---------|---------|--------|---------|
| **Trèfle** (Clubs) | ♣ | As → Roi | 1 → 13 |
| **Carreau** (Diamonds) | ♦ | As → Roi | 14 → 26 |
| **Cœur** (Hearts) | ♥ | As → Roi | 27 → 39 |
| **Pique** (Spades) | ♠ | As → Roi | 40 → 52 |
| **Joker A** (noir/petit) | 🃏 | — | **53** |
| **Joker B** (rouge/grand) | 🃏 | — | **54** |

**Remarque :** les jokers doivent être distinguables. Schneier conseille de prendre le « plus grand » comme B.

### 4.2 Deux systèmes de valeurs — NE PAS CONFONDRE

C'est un piège majeur. Il existe **deux** façons d'évaluer une carte :

#### Valeur Bridge (pour les opérations de coupe — opérations 4 et 5)
```
Trèfle  : As=1,  2=2,  ..., Roi=13
Carreau : As=14, 2=15, ..., Roi=26
Cœur    : As=27, 2=28, ..., Roi=39
Pique   : As=40, 2=41, ..., Roi=52
Joker A : 53
Joker B : 53  (les deux jokers valent 53 en Bridge)
```
Utilisée dans : opération 4 (coupe simple) et opération 5 (lecture de la position de sortie).

#### Valeur de chiffrement (pour la sortie finale — opération 5 uniquement)
```
Trèfle  : As=1,  2=2,  ..., Roi=13    (identique)
Carreau : As=14, 2=15, ..., Roi=26     (identique)
Cœur    : As=1,  2=2,  ..., Roi=13     (SOUSTRAIRE 26 !)
Pique   : As=14, 2=15, ..., Roi=26     (SOUSTRAIRE 26 !)
Joker   : INVALIDE → recommencer le cycle
```
Autrement dit : si la valeur Bridge > 26, on soustrait 26 pour obtenir un nombre entre 1 et 26.

### 4.3 Le paquet = une liste ordonnée

Le paquet est modélisé comme une **liste ordonnée de 54 entiers**.

```
Paquet initial standard (non clé) :
[1, 2, 3, 4, 5, ..., 52, 53, 54]

Signification :
   Position 0 (dessus) → carte 1 = As de Trèfle
   Position 1           → carte 2 = 2 de Trèfle
   ...
   Position 51          → carte 52 = Roi de Pique
   Position 52          → carte 53 = Joker A (noir)
   Position 53 (dessous)→ carte 54 = Joker B (rouge)
```

**Le dessus** (top) = index 0 = première carte de la liste
**Le dessous** (bottom) = index 53 = dernière carte de la liste

### 4.4 Le paquet est circulaire (conceptuellement)

Pour les opérations 1 et 2 (déplacement des jokers), le paquet est traité comme un **anneau** : la carte après la dernière est la première (mais avec des règles spécifiques — voir section 6).

---

## 5. Le codage/décodage par addition modulaire

### 5.1 Prétraitement du message

Avant de chiffrer, le message est nettoyé :

1. **Supprimer** tout ce qui n'est pas une lettre : espaces, ponctuation, chiffres
2. **Convertir** en majuscules
3. **Remplacer** les caractères accentués : é/è/ê → E, à → A, ù → U, ç → C, î/ï → I, ô → O, etc.
4. **Convertir** chaque lettre en nombre : A=1, B=2, ..., Z=26

**Exemple :**
```
Message : "L'attaque est pour demain !"
Nettoyé : "LATTAQUEESTPOURDEMAIN"
Nombres : [12, 1, 20, 20, 1, 17, 21, 5, 5, 19, 20, 16, 15, 21, 18, 4, 5, 13, 1, 9, 14]
```

### 5.2 Regroupement en blocs de 5 (convention)

Par convention (tradition cryptographique), le texte chiffré est présenté en **groupes de 5 lettres**. Si le dernier groupe est incomplet, on le complète avec des **X**.

```
Message clair : DONOT USEPC X    (padded with X)
Chiffré      : OSKJJ JGTMW
```

Cela masque la structure du message (longueur des mots, etc.).

### 5.3 Chiffrement

Pour chaque lettre du message :
```
chiffré = (clair + flux) mod 26
Si chiffré = 0 → chiffré = 26 (= Z)
```

**Exemple détaillé (extrait de Schneier) :**
```
Message clair : D  O  N  O  T    U  S  E  P  C
Nombres       : 4  15 14 15 20   21 19 5  16 3
Flux de clés  : 11 4  23 21 16   15 14 15 23 20
               + ─────────────────────────────────
Addition      : 15 19 37 36 36   36 33 20 39 23
mod 26        : 15 19 11 10 10   10 7  20 13 23
Lettres       : O  S  K  J  J    J  G  T  M  W
```

### 5.4 Déchiffrement

Pour chaque lettre du message chiffré :
```
clair = (chiffré - flux)
Si clair ≤ 0 → clair += 26
```

**Exemple :**
```
Message chiffré : O  S  K  J  J    J  G  T  M  W
Nombres         : 15 19 11 10 10   10 7  20 13 23
Flux de clés    : 11 4  23 21 16   15 14 15 23 20
                 - ─────────────────────────────────
Soustraction    : 4  15 -12 -11 -6  -5 -7 5  -10 3
ajuster (≤0→+26): 4  15 14  15  20   21 19 5  16  3
Lettres         : D  O  N   O   T    U  S  E  P   C
```

---

## 6. Les 5 opérations de mélange — description formelle

### Vue d'ensemble

À chaque caractère à chiffrer :
1. Déplacer le Joker A d'une position vers le bas
2. Déplacer le Joker B de deux positions vers le bas
3. Triple coupe autour des jokers
4. Coupe simple selon la dernière carte
5. Lire la valeur de sortie (sans modifier le paquet)

Si l'étape 5 donne un joker → **recommencer de l'étape 1** (ce tour ne compte pas).

Les étapes **1 à 4 modifient le paquet**. L'étape **5 ne modifie PAS** le paquet.

---

### Opération 1 : Recul du Joker A (noir, valeur 53) d'une position

**Règle :** Trouver le Joker A, le permuter avec la carte **juste après** lui dans le paquet.

**Cas normal :**
```
Avant : ... X [A] Y Z ...
Après : ... X Y [A] Z ...
```

**⚠️ CAS SPÉCIAL — Joker A en dernière position :**
Le Joker A ne revient **pas** en première position. Il passe en **deuxième position** (juste après la première carte du dessus).

```
Avant : 7 3 5 9 2 [A]
Après : 7 [A] 3 5 9 2
```

**Explication conceptuelle :** Le paquet est vu comme un cycle. Quand le Joker A est en bas, « une position après le bas » serait le dessus — mais en réalité on le place **juste après le dessus**, c'est-à-dire en 2ème position. Le Joker A ne peut **jamais** se retrouver en 1ère position par cette opération.

---

### Opération 2 : Recul du Joker B (rouge, valeur 54) de deux positions

**Règle :** Trouver le Joker B, le déplacer de **deux positions** vers le bas.

**Cas normal :**
```
Avant : ... X [B] Y Z W ...
Après : ... X Y Z [B] W ...
```

**⚠️ CAS SPÉCIAL #1 — Joker B en dernière position :**
Il passe en **3ème position** (après les 2 premières cartes).
```
Avant : 7 3 5 9 [B]
Après : 7 3 [B] 5 9
```

**⚠️ CAS SPÉCIAL #2 — Joker B en avant-dernière position :**
Il passe en **2ème position** (après la première carte).
```
Avant : 7 3 5 [B] 9
Après : 7 [B] 3 5 9
```

**Règle absolue :** Le Joker B ne peut **JAMAIS** se retrouver en 1ère position par cette opération.

**⚠️ ORDRE CRITIQUE :** Il faut **toujours** faire l'opération 1 (Joker A) **avant** l'opération 2 (Joker B). Si les deux jokers sont proches, l'ordre compte !

**Exemple de Schneier :**
```
Avant étape 1 : A 7 2 B 9 4 1
Après étape 1 : 7 A 2 B 9 4 1     (A descend de 1)
Après étape 2 : 7 A 2 9 4 B 1     (B descend de 2)
```

```
Avant étape 1 : 3 A B 8 9 6
Après étape 1 : 3 B A 8 9 6     (A descend de 1 — passe après B)
Après étape 2 : 3 A 8 B 9 6     (B descend de 2)
```

---

### Opération 3 : Triple coupe (double coupe par rapport aux jokers)

**Règle :** Le paquet est divisé en **3 segments** par les deux jokers :

```
[Segment HAUT] [Joker_premier ... Joker_second] [Segment BAS]
```

On **intervertit** le segment HAUT avec le segment BAS. Les jokers (et tout ce qui est entre eux) restent en place.

```
Avant : 2 4 6 | B 5 8 7 1 A | 3 9
Après : 3 9   | B 5 8 7 1 A | 2 4 6
```

**Important :**
- « Premier joker » = celui qui est le **plus près du dessus** (peu importe A ou B)
- « Second joker » = celui qui est le **plus près du dessous**
- On ignore la désignation A/B pour cette étape, on regarde seulement les **positions**

**Cas limites (segments vides) :**

Si un joker est en première position → le segment HAUT est vide :
```
Avant : B 5 8 7 1 A | 3 9
Après : 3 9 | B 5 8 7 1 A
```

Si un joker est en dernière position → le segment BAS est vide :
```
Avant : 3 9 | B 5 8 7 1 A
Après : B 5 8 7 1 A | 3 9
```

Si les deux jokers sont aux extrémités → les deux segments sont vides → **pas de changement** :
```
Avant : B 5 8 7 1 A
Après : B 5 8 7 1 A    (identique)
```

Si les jokers sont adjacents → le segment du milieu ne contient que les deux jokers :
```
Avant : 3 9 2 | A B | 7 4
Après : 7 4   | A B | 3 9 2
```

---

### Opération 4 : Coupe simple déterminée par la dernière carte

**Règle :**
1. Regarder la **dernière carte** du paquet → soit `n` sa valeur Bridge (1-53)
2. Prendre les `n` premières cartes du dessus
3. Les placer juste **au-dessus de la dernière carte** (= en avant-dernière position)
4. **La dernière carte ne bouge JAMAIS** (c'est crucial pour la réversibilité mathématique)

```
Dernière carte = 9
Avant : | 7 ... cartes ... 4 | 5 ... cartes ... 8 | 9 |
         ← n=9 premières →      reste
Après : | 5 ... cartes ... 8 | 7 ... cartes ... 4 | 9 |
```

**⚠️ CAS SPÉCIAL — Dernière carte = Joker (valeur 53) :**
On devrait prendre 53 cartes sur 54 → il resterait 1 carte + le joker en bas → en pratique **le paquet ne change pas**. (Déplacer 53 cartes au-dessus de la 54ème = pas de changement.)

---

### Opération 5 : Lecture de la valeur de sortie

**Règle :**
1. Regarder la **1ère carte** (dessus du paquet) → soit `n` sa valeur Bridge (1-53)
2. Compter `n` cartes depuis le dessus → la carte en position **n+1** (la carte juste après les `n` premières) est la carte de sortie
3. Lire sa **valeur de chiffrement** (= valeur Bridge, mais si > 26, soustraire 26)
4. **Si c'est un joker → ignorer ce tour, recommencer toutes les opérations 1-2-3-4-5**
5. **Cette opération ne modifie PAS le paquet**

**Exemple (Schneier, paquet initial non clé) :**
```
Paquet après op. 1-4 : 2 3 4 ... 52 A B 1
Première carte = 2 → compter 2 positions → position 3 = carte 4
Valeur Bridge de 4 = 4 → la sortie est 4 (= lettre D)
```

---

## 7. Le keying du paquet (initialisation par mot de passe)

### Méthode 1 : Ordre fixe

L'émetteur et le récepteur se mettent d'accord sur un **ordre précis** des 54 cartes. C'est l'équivalent d'une clé secrète. Cet ordre peut être :
- Un mélange aléatoire d'un paquet physique (au moins 6 brassages)
- Un ordre tiré d'une colonne de bridge dans un journal
- N'importe quelle convention partagée

### Méthode 2 : Keying par passphrase (recommandé par Schneier)

On part du **paquet dans l'ordre standard** (1 à 52, Joker A, Joker B), puis on applique la passphrase :

**Pour chaque lettre de la passphrase :**
1. Exécuter les opérations 1, 2, 3, 4 (seulement — PAS l'opération 5)
2. Faire une **coupe supplémentaire** en utilisant la valeur numérique de la lettre :
   - A=1, B=2, ..., Z=26
   - Couper `n` cartes du dessus et les placer au-dessus de la dernière carte (même principe que l'opération 4, mais avec la valeur de la lettre au lieu de la dernière carte)

**Longueur minimale de la passphrase :**
- Schneier recommande **au minimum 64 caractères**, idéalement **80+**
- L'anglais contient environ **1.4 bits d'entropie par caractère**
- 80 caractères × 1.4 bits ≈ 112 bits de sécurité effective

### La persistance d'état : CRITIQUE

> **L'état du paquet est conservé entre les messages successifs.**

Quand on chiffre un 1er message de 10 lettres, le paquet subit 10 cycles d'opérations 1-2-3-4-5. Pour le 2ème message, on reprend le paquet **dans l'état où il se trouve** après le 1er message. Le récepteur fait exactement pareil de son côté.

---

## 8. La version simplifiée

Le sujet propose une version simplifiée pour un premier prototype :

**Après la lecture de la carte du dessus :**
- **Tour impair** : placer cette carte en **dernière** position
- **Tour pair** : placer cette carte en **avant-dernière** position
- Alterner ces deux opérations

C'est beaucoup plus simple à implémenter mais **beaucoup moins sûr** (les cartes ne sont pas suffisamment mélangées). Cette version est utile pour :
- Valider rapidement la logique de chiffrement/déchiffrement
- Tester l'interface
- Comparer ensuite avec l'algorithme complet

---

## 9. Vecteurs de test officiels de Schneier

Ces vecteurs sont **non négociables**. Si votre implémentation ne les reproduit pas exactement, il y a un bug.

### Vecteur 1 : Paquet non clé (standard)

```
Clé       : aucune (paquet dans l'ordre 1..52, A, B)
Clair     : AAAAAAAAAAAAAAA
Keystream : 4 49 10 (53) 24 8 51 44 6 4 33 20 39 19 34 42
                        ↑ sauté (joker)
Chiffré   : EXKYIZSGEH UNTIQ
```

**Les 10 premières sorties du keystream (paquet initial non clé) :**
```
4, 49, 10, (53=skip), 24, 8, 51, 44, 6, 4, 33
```

### Vecteur 2 : Clé "FOO"

```
Clé       : FOO
Clair     : AAAAAAAAAAAAAAA
Keystream : 8 19 7 25 20 (53) 9 8 22 32 43 5 26 17 (53) 38 48
Chiffré   : ITHZUJIWGRFARMW
```

### Vecteur 3 : Clé "CRYPTONOMICON"

```
Clé       : CRYPTONOMICON
Clair     : SOLITAIREX    (SOLITAIRE + X de padding)
Chiffré   : KIRAKSFJAN
```

### Vecteurs supplémentaires (pour validation exhaustive)

| Clé | Clair (15×A) | Chiffré |
|-----|--------------|---------|
| `f` | AAAAAAAAAAAAAAA | XYIUQBMHKKJBEGY |
| `fo` | AAAAAAAAAAAAAAA | TUJYMBERLGXNDIW |
| `foo` | AAAAAAAAAAAAAAA | ITHZUJIWGRFARMW |
| `a` | AAAAAAAAAAAAAAA | XODALGSCULIQNSC |
| `aa` | AAAAAAAAAAAAAAA | OHGWMXXCAIMCIQP |
| `aaa` | AAAAAAAAAAAAAAA | DCSQYHBQZNGDRUT |
| `b` | AAAAAAAAAAAAAAA | XQEEMOITLZVDSQS |
| `bc` | AAAAAAAAAAAAAAA | QNGRKQIHCLGWSCE |
| `bcd` | AAAAAAAAAAAAAAA | FMUBYBMAXHNQXCJ |
| `cryptonomicon` | AAAAAAAAAAAAAAAAAAAAAAAAA | SUGSRSXSWQRMXOHIPBFPXARYQ |

---

## 10. Pourquoi ne jamais réutiliser la clé

> **Règle n°1 de Schneier : « NEVER USE THE SAME KEY TO ENCRYPT TWO DIFFERENT MESSAGES. »**

### L'attaque mathématique

Si deux messages A et B sont chiffrés avec la **même** clé K :

$$C_A = A + K \pmod{26}$$
$$C_B = B + K \pmod{26}$$

En soustrayant :

$$C_A - C_B = (A + K) - (B + K) = A - B$$

**La clé K disparaît !** On obtient directement la différence des deux textes clairs. Or :
- Les langues naturelles ont des fréquences de lettres prévisibles
- La redondance linguistique (en français : « q est presque toujours suivi de u », fréquence du E ≈ 17%, etc.) permet aux cryptanalystes de reconstruire A et B à partir de A−B

### L'attaque par crib-dragging

1. L'attaquant suppose un mot probable dans l'un des messages (ex : « BONJOUR », « URGENT »)
2. Il soustrait ce « crib » (texte supposé) de A−B à chaque position
3. Si le résultat ressemble à du français → le crib est correct à cette position
4. En itérant, on reconstitue progressivement les deux messages

### Conséquence pour Solitaire

- Chaque message doit utiliser un **état du paquet différent**
- Soit on utilise la fonctionnalité de **persistance d'état** (le paquet évolue entre les messages)
- Soit on utilise un **nouveau mot de passe** pour chaque message
- En aucun cas on ne revient à l'état initial entre deux messages

---

## 11. Faiblesses connues (Crowley 1999)

### Le biais de répétition

Paul Crowley a découvert en 1999 que le CPRNG de Solitaire présente un **biais statistique** :

> La probabilité que deux lettres consécutives du keystream soient identiques est d'environ **1/22.5** au lieu du **1/26** attendu pour un générateur parfaitement aléatoire.

Ce biais est **statistiquement significatif** : sur 26 000 001 échantillons, Crowley mesure **159 écarts-types** au-dessus de la moyenne — une déviation astronomique.

### Cause principale

Quand la valeur de la carte du dessus est **identique** sur deux tours consécutifs (probabilité ≈ 2%), la probabilité que la sortie soit aussi identique monte à **~34%** (au lieu de ~3.85%). Cela arrive parce que si la carte du dessus est la même, il est probable que beaucoup d'autres cartes soient aussi aux mêmes positions.

### Non-réversibilité

Crowley a aussi montré que le CPRNG n'est **pas toujours réversible**, contrairement à ce que Schneier pensait. Quand le Joker A est en dernière position ou en première position, il se retrouve dans les deux cas en deuxième position après l'opération 1 → **deux états initiaux différents mènent au même état suivant**.

### Impact pratique

- **Pour des messages courts** (quelques centaines de caractères) : la sécurité reste acceptable
- **Pour des messages longs** : Solitaire fuit de l'information au rythme de **~0.0005 bits par caractère**
- Un adversaire avec suffisamment de texte chiffré peut exploiter ce biais
- Schneier recommande de toute façon de garder les messages **courts** (quelques milliers de caractères max)

---

## 12. Pièges d'implémentation critiques

### Résumé des pièges

| # | Piège | Erreur classique | Solution |
|---|-------|------------------|----------|
| 1 | **Wrapping Joker A** | Le mettre en 1ère position quand il est en dernière | → Le mettre en **2ème** position |
| 2 | **Wrapping Joker B (dernier)** | Le mettre en 2ème position | → Le mettre en **3ème** position |
| 3 | **Wrapping Joker B (avant-dernier)** | Le mettre en 1ère position | → Le mettre en **2ème** position |
| 4 | **Modulo 26 = 0** | Interpréter 0 comme A (1) | → 0 signifie **Z (26)** |
| 5 | **Dernière carte immobile (op. 4)** | Déplacer la dernière carte | → Elle ne bouge **JAMAIS** |
| 6 | **Skip joker en sortie** | Prendre la valeur du joker comme sortie | → **Recommencer** tout le cycle 1-5 |
| 7 | **Op. 5 modifie le paquet** | Retirer des cartes pendant la lecture | → Lecture **seule**, aucune modification |
| 8 | **Deux systèmes de valeurs** | Utiliser la valeur Bridge (1-52) pour la sortie finale | → Sortie = 1-26 (soustraire 26 si > 26) |
| 9 | **Ordre op. 1 et 2** | Déplacer A et B dans n'importe quel ordre | → **Toujours** A d'abord, B ensuite |
| 10 | **Erreur off-by-one** | Compter à partir de 0 au lieu de 1, ou inversement | → Tester avec les vecteurs officiels dès que possible |
| 11 | **Mutation du paquet** | Modifier le paquet original au lieu d'une copie | → Travailler sur des **copies** (immutabilité) |
| 12 | **Propagation d'erreur** | « Je corrigerai plus tard » | → **1 erreur = tout le reste est faux**. Valider les vecteurs immédiatement |

### La règle d'or

> **Chaque étape doit être exacte. Une seule erreur dans une seule opération corrompt l'intégralité du flux de clés.**

C'est pourquoi les vecteurs de test de Schneier doivent être validés **en priorité absolue**, avant toute autre fonctionnalité.

---

## 13. Exercice à la main — Faire l'algorithme sur papier

### Pourquoi c'est indispensable

Schneier lui-même recommande de faire l'algorithme à la main avec un vrai jeu de cartes pour **intérioriser chaque étape**. Cela permet de :
- Comprendre le rôle de chaque opération
- Détecter les cas limites naturellement
- Développer une intuition sur le fonctionnement du mélange

### Exercice guidé : Premier caractère du keystream avec le paquet non clé

**État initial :**
```
Pos:  0  1  2  3  ...  51 52 53
Carte: 1  2  3  4  ...  52  A  B
```

**Opération 1 — Déplacer Joker A (53) d'une position :**
```
A est en position 52. La carte en 53 est B.
On permute A et B.
Résultat : 1 2 3 4 ... 52 B A
```

**Opération 2 — Déplacer Joker B (54) de deux positions :**
```
B est en position 52 (après op.1). Il est en avant-dernière position.
CAS SPÉCIAL : avant-dernière → passe en 2ème position.
Résultat : 1 B 2 3 4 ... 52 A
```

**Opération 3 — Triple coupe :**
```
Premier joker (le plus haut) : B en position 1
Second joker (le plus bas)   : A en position 53
Segment HAUT : [1] (position 0)
Segment MILIEU : [B 2 3 ... 52 A] (positions 1 à 53)
Segment BAS : [] (vide — A est le dernier)
On intervertit HAUT et BAS : [vide] + [B 2 3 ... 52 A] + [1]
Résultat : B 2 3 4 ... 52 A 1
```

**Opération 4 — Coupe simple :**
```
Dernière carte = 1 → valeur Bridge = 1
Prendre 1 carte du dessus (le B) et la placer juste au-dessus de la dernière (le 1).
Résultat : 2 3 4 ... 52 A B 1
```

**Opération 5 — Lecture :**
```
Première carte = 2 → valeur Bridge = 2
Compter 2 cartes : position 1 (carte 3), position 2 (carte 4)
La carte en position 2 est le 4 → valeur Bridge = 4
4 ≤ 26 → valeur de chiffrement = 4

SORTIE = 4  ✓ (correspond au vecteur de test Schneier)
```

### À vous !

Prenez un jeu de 54 cartes physique et faites les étapes suivantes :
1. Rangez le paquet dans l'ordre standard (As Trèfle → Roi Pique → Joker A → Joker B)
2. Générez les 5 premiers caractères du keystream à la main
3. Vérifiez que vous obtenez : **4, 49, 10, (53=skip), 24, 8**
4. Si oui, vous avez compris l'algorithme

---

## 14. Ressources de référence

### Sources primaires (OBLIGATOIRES)

| Ressource | URL | Priorité |
|-----------|-----|----------|
| Article original de Schneier | https://www.schneier.com/academic/solitaire/ | ⭐⭐⭐ |
| Analyse de Paul Crowley | http://www.ciphergoth.org/crypto/solitaire/ | ⭐⭐⭐ |
| Vecteurs de test officiels | https://www.schneier.com/wp-content/uploads/2015/12/sol-test.txt | ⭐⭐⭐ |
| Wikipedia — Solitaire cipher | https://en.wikipedia.org/wiki/Solitaire_(cipher) | ⭐⭐ |

### Outils de validation

| Outil | URL | Utilité |
|-------|-----|---------|
| dCode Solitaire | https://www.dcode.fr/solitaire-cipher-schneier | Valider le chiffrement/déchiffrement en ligne |

### Implémentations de référence (LIRE, ne pas copier)

| Projet | Langage | Notes |
|--------|---------|-------|
| `keithfancher/Pontifex` | Python | Propre, bonne référence |
| `c-mart/solitaire-pontifex` | Python | Mode verbose utile pour déboguer |
| Script Perl officiel de Schneier | Perl | Seule implémentation testée par Schneier |

### Articles académiques (pour l'analyse de sécurité)

| Article | Auteur | Année |
|---------|--------|-------|
| *Problems with Bruce Schneier's "Solitaire"* | Paul Crowley | 1999 |
| *Properties of the Transformation Semigroup...* | Pogorelov & Pudovkina | 2003 |
| *Probabilistic Cycle Detection for Schneier's Solitaire...* | Tounsi et al. | 2014 |
| *Analysis of Solitaire* | Daniel Shiu | 2019 |

### Livres de référence (contexte)

- **Applied Cryptography** — Bruce Schneier (1996) — Bible de la cryptographie appliquée
- **The Codebreakers** — David Kahn (1996) — Histoire de la cryptographie
- **Cryptonomicon** — Neal Stephenson (1999) — Le roman qui a motivé la création de Solitaire

---

## 15. Glossaire

| Terme | Définition |
|-------|------------|
| **Bridge (ordre)** | Convention internationale de classement des couleurs : Trèfle < Carreau < Cœur < Pique |
| **Chiffrement par flux** (Stream cipher) | Algorithme qui chiffre caractère par caractère en combinant le message avec un flux pseudo-aléatoire |
| **Coupe simple** (Count cut) | L'opération 4 : prendre N cartes du dessus et les placer au-dessus de la dernière carte |
| **CPRNG** | Cryptographically secure Pseudo-Random Number Generator |
| **Crib-dragging** | Technique d'attaque utilisant des mots supposés pour déchiffrer quand la clé est réutilisée |
| **Flux de clés** (Keystream) | Séquence de nombres pseudo-aléatoires combinée avec le message |
| **Joker A** | Joker noir/petit, valeur 53, opération 1 le déplace d'une position |
| **Joker B** | Joker rouge/grand, valeur 54, opération 2 le déplace de deux positions |
| **Keying** | Processus d'initialisation du paquet à partir d'un mot de passe |
| **Masque jetable** (One-Time Pad) | Chiffrement parfait : clé aléatoire, aussi longue que le message, jamais réutilisée |
| **Modulo 26** | Reste de la division par 26 ; si résultat = 0, on prend 26 (pas 0) en cryptographie |
| **OFB** (Output Feedback) | Mode de chiffrement par flux où la sortie du générateur est réinjectée |
| **Persistance d'état** | Le paquet conserve son état entre les messages successifs |
| **Pontifex** | Nom de code original dans *Cryptonomicon* pour masquer l'utilisation de cartes |
| **Triple coupe** (Triple cut) | L'opération 3 : intervertir les segments au-dessus et au-dessous des jokers |
| **Valeur Bridge** | Numérotation de 1 à 53 (jokers = 53) utilisée pour les coupes |
| **Valeur de chiffrement** | Numérotation de 1 à 26 (Bridge mod 26, si > 26 soustraire 26) pour la sortie |
| **Wrapping** | Le fait qu'une carte en bout de paquet « revienne » au début (comportement circulaire) |

---

## Checklist Phase 0 — Êtes-vous prêt à coder ?

- [ ] J'ai lu l'article original de Schneier et compris chaque étape
- [ ] J'ai lu l'analyse de Crowley et compris le biais
- [ ] J'ai lu le sujet du projet (M1_projet_25_26.md) en entier
- [ ] Je sais expliquer les 5 opérations sans regarder mes notes
- [ ] J'ai fait l'algorithme à la main et obtenu la sortie 4 pour le premier caractère
- [ ] Je comprends la différence entre valeur Bridge et valeur de chiffrement
- [ ] Je sais pourquoi 0 mod 26 = Z (26) et pas A (1)
- [ ] Je sais pourquoi le Joker A va en 2ème position quand il est en dernière
- [ ] Je sais pourquoi il ne faut JAMAIS réutiliser la clé
- [ ] Je connais les 3 vecteurs de test principaux par cœur
- [ ] Je sais ce qu'est un stream cipher et pourquoi Solitaire en est un
- [ ] J'ai installé mon environnement Python (streamlit, pytest, pillow, etc.)
