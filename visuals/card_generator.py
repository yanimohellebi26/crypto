"""Générateur de cartes à jouer via l'API Gemini + post-traitement Pillow."""

import os
import sys
import time
import json
import base64
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERREUR: GEMINI_API_KEY manquant dans .env")
    sys.exit(1)

GEMINI_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

ASSETS_DIR = Path(__file__).parent / "assets"
SUIT_DIRS = {
    "clubs": ASSETS_DIR / "clubs",
    "diamonds": ASSETS_DIR / "diamonds",
    "hearts": ASSETS_DIR / "hearts",
    "spades": ASSETS_DIR / "spades",
    "jokers": ASSETS_DIR / "jokers",
}

for d in SUIT_DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

COLORS = {
    "clubs": "#10b981",      # Vert émeraude — CPU
    "diamonds": "#06b6d4",   # Cyan — DATA/IA
    "hearts": "#f43f5e",     # Rouge — Sécurité
    "spades": "#a855f7",     # Violet — Quantique
}

SUIT_NAMES_FR = {
    "clubs": "CPU",
    "diamonds": "DATA",
    "hearts": "SHIELD",
    "spades": "QUBIT",
}

RANK_NAMES = {
    1: "A", 2: "2", 3: "3", 4: "4", 5: "5",
    6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "V", 12: "D", 13: "R",
}



@dataclass(frozen=True)
class CardSpec:
    card_number: int       # 1-54 (valeur Solitaire)
    suit: str              # clubs, diamonds, hearts, spades, jokers
    rank: int              # 1-13 pour les cartes normales, 0 pour jokers
    name_fr: str           # Nom français
    concept: str           # Concept thématique
    prompt_detail: str     # Description visuelle pour le prompt


def _build_card_specs() -> list[CardSpec]:
    specs: list[CardSpec] = []

    # ── CPU (Clubs) 1-13 ──
    clubs_cards = [
        (1, "As de CPU", "Le Transistor",
         "A single glowing green transistor symbol floating in dark space, with faint electric pulses emanating from it. Minimal, elegant, one CPU chip icon in center. Dark background with subtle circuit traces. Green (#10b981) neon glow."),
        (2, "2 de CPU", "Portes logiques",
         "Two interconnected logic gates (AND/OR) drawn with green neon lines on dark background. Small data streams flowing between them. Circuit board aesthetic. Green accent (#10b981)."),
        (3, "3 de CPU", "Le Registre",
         "Three glowing memory registers stacked vertically, displaying binary values (101, 110, 011). Green holographic display effect. Dark data center background."),
        (4, "4 de CPU", "Le Processeur",
         "A detailed CPU chip viewed from above, four cores visible with green glow patterns. Heat dissipation lines radiating outward. Dark PCB background with gold traces."),
        (5, "5 de CPU", "La Carte Mère",
         "Five major components connected on a motherboard: CPU, RAM, GPU, SSD, network chip. Green circuit paths linking them. Bird's-eye view on dark background."),
        (6, "6 de CPU", "Le Rack Serveur",
         "Six server units stacked in a rack, each with blinking green LED status lights. Dark server room ambiance, cool lighting. Cable management visible."),
        (7, "7 de CPU", "Le Cluster",
         "Seven interconnected server nodes forming a compute cluster. Green data flow lines between nodes. Network topology visible. Dark room with green ambient light. Isometric perspective."),
        (8, "8 de CPU", "Le Data Center",
         "A vast data center hall with eight rows of server racks, green LED lights reflecting on polished floor. Cool mist, industrial scale. Atmospheric perspective."),
        (9, "9 de CPU", "Le Réseau Global",
         "Nine glowing nodes on a world map connected by green fiber optic lines. Earth viewed from low orbit. Submarine cables visible. Dark space background. Futuristic cartography."),
        (10, "10 de CPU", "L'Hyperscaler",
         "A massive planetary-scale infrastructure: multiple data centers connected by a green mesh network around Earth. Satellites, undersea cables, edge nodes. Epic scale, dark space backdrop."),
        (11, "Valet de CPU", "SRE",
         "A focused Site Reliability Engineer in a dark hoodie, holographic terminal floating in front of them. Server metrics and uptime dashboards visible. Green neon accents. Double-headed portrait symmetrical top and bottom."),
        (12, "Dame de CPU", "Cloud Architect",
         "A confident cloud architect with holographic blueprints of cloud infrastructure (VPC, load balancers, auto-scaling groups). Green architectural diagrams floating around. Double-headed portrait symmetrical."),
        (13, "Roi de CPU", "CTO",
         "A powerful CTO on a throne of servers and circuit boards. Green holographic dashboards showing global infrastructure. Crown made of fiber optic cables. Double-headed portrait symmetrical."),
    ]
    for rank, name, concept, prompt in clubs_cards:
        specs.append(CardSpec(rank, "clubs", rank, name, concept, prompt))

    # ── DATA (Diamonds) 14-26 ──
    diamonds_cards = [
        (1, "As de DATA", "Le Bit",
         "A single luminous cyan bit (a glowing '1') floating in a void of data. Minimal, elegant. Particle effects around it. Cyan (#06b6d4) neon accent."),
        (2, "2 de DATA", "L'Embedding",
         "Two data points mapped as glowing dots in a 3D vector space with cyan coordinate axes. Dimensionality reduction visualization. Holographic feel."),
        (3, "3 de DATA", "Le Dataset",
         "Three streams of structured data (tables, JSON, images) flowing into a central repository. Cyan data pipeline aesthetic. Database icons."),
        (4, "4 de DATA", "Le Tensor",
         "A 3D tensor visualized as a glowing cyan cube made of numbers, rotating in space. Matrix mathematics visible in background. Neural network aesthetic."),
        (5, "5 de DATA", "Le Réseau de neurones",
         "Five layers of a neural network visualized with cyan nodes and connections. Forward pass highlighted with flowing light particles. Deep learning diagram aesthetic."),
        (6, "6 de DATA", "Le Transformer",
         "Six attention heads visualized as concentric cyan rings with crossing attention lines. Self-attention mechanism beautifully illustrated. Mathematical elegance."),
        (7, "7 de DATA", "Le Training Loop",
         "Seven epochs shown as a spiraling cyan helix of training progress. Loss curve decreasing. Gradient descent visualization. GPU cluster in background."),
        (8, "8 de DATA", "Le LLM",
         "A massive language model represented as a towering cyan holographic brain made of text tokens. Billions of parameters visualized as flowing data streams. Awe-inspiring scale."),
        (9, "9 de DATA", "L'Agent IA",
         "Nine tools floating around a central AI agent core: search, code, vision, speech, reasoning, memory, planning, execution, learning. Cyan aura. Autonomous AI aesthetic."),
        (10, "10 de DATA", "L'AGI",
         "An artificial general intelligence represented as a luminous cyan eye surrounded by all domains of knowledge: math, art, science, language, music. Transcendent, near-divine scale."),
        (11, "Valet de DATA", "ML Engineer",
         "A data scientist surrounded by floating datasets, Jupyter notebooks, and model metrics. Cyan holographic training curves. Double-headed portrait symmetrical top and bottom."),
        (12, "Dame de DATA", "Chief AI Officer",
         "A visionary AI leader surrounded by transformer diagrams, benchmark leaderboards in cyan holographics. Double-headed portrait symmetrical."),
        (13, "Roi de DATA", "AI Visionary",
         "A visionary figure with eyes reflecting neural network patterns. Cyan data streams flowing from their hands. AGI roadmap floating behind. Crown of data crystals. Double-headed."),
    ]
    for rank, name, concept, prompt in diamonds_cards:
        specs.append(CardSpec(rank + 13, "diamonds", rank, name, concept, prompt))

    # ── SHIELD (Hearts) 27-39 ──
    hearts_cards = [
        (1, "As de SHIELD", "La Clé",
         "A single ornate cryptographic key glowing red, floating in darkness. Digital lock mechanism visible. Minimal, powerful. Red (#f43f5e) neon accent."),
        (2, "2 de SHIELD", "Le Hash",
         "Two identical documents fed into a hash function, producing two unique red fingerprints. SHA-256 aesthetic. Collision resistance visualized."),
        (3, "3 de SHIELD", "Le Chiffrement",
         "Three stages of encryption: plaintext, cipher process with gears and math, ciphertext. Red data streams flowing through a padlock. Classic crypto visualization."),
        (4, "4 de SHIELD", "Le Pare-feu",
         "Four hexagonal shield layers deflecting incoming red threat arrows. Firewall rules visible as floating code. Network security aesthetic."),
        (5, "5 de SHIELD", "Le Certificat",
         "Five chain links forming a certificate chain of trust. Digital signatures, X.509 aesthetic. Root CA at top glowing red. TLS handshake visualization."),
        (6, "6 de SHIELD", "L'Authentification",
         "Six authentication factors in a circle: password, fingerprint, token, SMS, hardware key, behavioral. Red verification checkmarks."),
        (7, "7 de SHIELD", "Le SOC",
         "Seven monitoring screens in a Security Operations Center showing threat dashboards, alerts, network maps. Red alert indicators. Dark room, dramatic lighting."),
        (8, "8 de SHIELD", "Le Pentest",
         "Eight vulnerability points probed on a network diagram by red scanning beams. Ethical hacking tools visible. Matrix-style data overlay."),
        (9, "9 de SHIELD", "Zero Trust",
         "Nine access control checkpoints in a network, each with red verification gates. Never trust always verify architecture. Micro-segmentation visible."),
        (10, "10 de SHIELD", "La Forteresse",
         "A complete cybersecurity fortress: layered defenses (IDS, WAF, SIEM, EDR, SOC, encryption, MFA, backup, DLP) forming an impenetrable red-glowing citadel. Epic scale."),
        (11, "Valet de SHIELD", "Pentester",
         "A hooded ethical hacker with a red-glowing laptop, vulnerability scan results floating around. Lock-picking tools and exploit code visible. Double-headed portrait symmetrical."),
        (12, "Dame de SHIELD", "CISO",
         "A commanding CISO reviewing threat intelligence dashboards, zero-day alerts, and compliance frameworks in red holographics. Double-headed portrait symmetrical."),
        (13, "Roi de SHIELD", "Cryptographer-in-Chief",
         "A master cryptographer surrounded by mathematical proofs, cipher machines (Enigma homage), and encryption algorithms in red. Crown of keys. Double-headed."),
    ]
    for rank, name, concept, prompt in hearts_cards:
        specs.append(CardSpec(rank + 26, "hearts", rank, name, concept, prompt))

    # ── QUBIT (Spades) 40-52 ──
    spades_cards = [
        (1, "As de QUBIT", "Le Qubit",
         "A single qubit in superposition, visualized as a glowing violet Bloch sphere with state vector. Quantum uncertainty aesthetic. Minimal, elegant. Violet (#a855f7)."),
        (2, "2 de QUBIT", "L'Intrication",
         "Two entangled qubits connected by a violet quantum link across space. Bell state visualization. Spooky action at a distance. Particles mirroring each other."),
        (3, "3 de QUBIT", "La Porte quantique",
         "Three quantum gates (Hadamard, CNOT, Toffoli) as violet geometric portals on a quantum circuit diagram. Clean, mathematical beauty."),
        (4, "4 de QUBIT", "Le Circuit quantique",
         "Four qubit lines running through a sequence of violet quantum gates. Circuit diagram aesthetic with flowing probability amplitudes. Interference patterns."),
        (5, "5 de QUBIT", "La Correction d'erreurs",
         "Five redundant qubits protecting one logical qubit, forming a surface code pattern. Violet error syndrome detection. Topological code aesthetic."),
        (6, "6 de QUBIT", "Algorithme de Shor",
         "Six stages of Shor's algorithm: quantum Fourier transform, modular exponentiation, period finding. Violet computation waves. Number theory meets quantum."),
        (7, "7 de QUBIT", "Algorithme de Grover",
         "Seven iterations of Grover's search as a violet amplitude amplification spiral converging on the solution in an unsorted database."),
        (8, "8 de QUBIT", "Le Processeur quantique",
         "A detailed quantum processor chip with eight qubit clusters, dilution refrigerator cooling elements. Violet glow from superconducting circuits. Lab aesthetic."),
        (9, "9 de QUBIT", "Le Cloud quantique",
         "Nine quantum processors accessible via cloud, connected to classical computers. Hybrid classical-quantum architecture. Violet quantum channels through cloud infrastructure."),
        (10, "10 de QUBIT", "La Suprématie",
         "A quantum computer achieving supremacy: solving a massive equation that classical computers cannot crack. Violet energy explosion. Monumental scale."),
        (11, "Valet de QUBIT", "Quantum Developer",
         "A young researcher at a quantum computing terminal, Qiskit code on holographic screens. Violet Bloch spheres floating nearby. Double-headed portrait symmetrical."),
        (12, "Dame de QUBIT", "Quantum Physicist",
         "A scientist surrounded by quantum equations, Dirac notation, and probability distributions in violet holographics. Lab coat with quantum insignia. Double-headed portrait symmetrical."),
        (13, "Roi de QUBIT", "Director Quantum Research",
         "A commanding figure in front of a functioning quantum computer. Violet energy flowing through the dilution refrigerator behind. Crown of entangled particles. Double-headed."),
    ]
    for rank, name, concept, prompt in spades_cards:
        specs.append(CardSpec(rank + 39, "spades", rank, name, concept, prompt))

    # ── Jokers 53-54 ──
    specs.append(CardSpec(
        53, "jokers", 0,
        "Joker A (Noir)", "IA Générative — Chaos créatif",
        "A mysterious dark entity made of swirling generative art: half-formed images, text, music notes, code fragments. Glitch effects, multimodal creativity. Colors shifting between green, cyan, red, violet. Abstract face barely visible in the chaos. Dark background with explosion of creative particles.",
    ))
    specs.append(CardSpec(
        54, "jokers", 0,
        "Joker B (Rouge)", "IA de Gouvernance — Ordre & Éthique",
        "A serene, symmetrical AI figure made of balanced geometric shapes: scales of justice, alignment graphs, safety barriers, ethical frameworks. Calm white-gold glow contrasting with dark background. All four suit colors present but harmonized. A watchful eye at center representing oversight. Perfect order.",
    ))

    return specs


CARD_SPECS = _build_card_specs()

STYLE_PREFIX = """You are generating a custom playing card for a deck themed "Nexus: Modern Computation" — a fusion of AI, cloud computing, quantum computing, and cybersecurity.

STYLE RULES (mandatory):
- Dark graphite background (#0a0e1a to #111827 gradient)
- Clean, professional digital illustration style, semi-realistic
- High contrast with neon accent lighting
- Playing card format, 3:4 aspect ratio
- Subtle circuit board trace patterns in the background
- Faint binary code watermark in the background
- Fine glowing border matching the suit accent color
- DO NOT include any text, numbers, or letters on the card — those will be added in post-processing
- Centered composition with the subject filling about 70% of the card height

Generate the following card:
"""

STYLE_SUFFIX = """

Style: clean digital illustration, semi-realistic, high detail, professional playing card design. Dark moody lighting with colored neon rim light. Centered composition. No watermarks. No extra text or numbers on the card."""


def build_prompt(spec: CardSpec) -> str:
    return f"{STYLE_PREFIX}\nCard: {spec.name_fr} — {spec.concept}\n\n{spec.prompt_detail}{STYLE_SUFFIX}"


MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds



def generate_card_image(spec: CardSpec, output_path: Path) -> bool:
    """Génère une image de carte via l'API Gemini et la sauvegarde."""
    if output_path.exists():
        print(f"  ⏭  {spec.name_fr} — existe déjà, skip")
        return True

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = build_prompt(spec)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(str(output_path))
                    print(f"  ✅ {spec.name_fr} → {output_path.name}")
                    return True

            print(f"  ⚠  {spec.name_fr} — pas d'image (tentative {attempt}/{MAX_RETRIES})")

        except Exception as e:
            print(f"  ⚠  {spec.name_fr} — erreur tentative {attempt}/{MAX_RETRIES}: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    print(f"  ❌ {spec.name_fr} — échec après {MAX_RETRIES} tentatives")
    return False


def get_output_path(spec: CardSpec) -> Path:
    """Détermine le chemin de sortie pour une carte."""
    if spec.suit == "jokers":
        name = f"{spec.card_number}_joker_{'a' if spec.card_number == 53 else 'b'}.png"
    else:
        rank_label = {1: "ace", 11: "jack", 12: "queen", 13: "king"}.get(spec.rank, str(spec.rank))
        name = f"{spec.card_number:02d}_{rank_label}.png"
    return SUIT_DIRS[spec.suit] / name



def generate_back() -> bool:
    """Génère le dos de carte."""
    output_path = ASSETS_DIR / "back.png"
    if output_path.exists():
        print("  ⏭  Dos de carte — existe déjà, skip")
        return True

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = """A dark, elegant playing card back design. Center: a glowing hexagonal shield icon containing the text "54!" in a monospace font. Surrounding the icon: concentric rings of faint binary code (0s and 1s) and circuit board trace patterns. Color scheme: dark graphite (#0a0e1a) background with subtle cyan (#06b6d4) and violet (#a855f7) glow effects. Four small icons in the corners: CPU chip (green), data crystal (cyan), shield (red), quantum atom (violet). Clean, symmetrical, professional design. No text other than "54!". Aspect ratio 3:4."""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(str(output_path))
                print(f"  ✅ Dos de carte → back.png")
                return True

        print("  ❌ Dos — aucune image dans la réponse")
        return False

    except Exception as e:
        print(f"  ❌ Dos — erreur: {e}")
        return False



def post_process_card(spec: CardSpec, image_path: Path) -> None:
    """Ajoute les indices (rang + symbole) et la bordure à une carte."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  ⚠  Pillow non installé, skip post-traitement")
        return

    if not image_path.exists():
        return

    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Couleur de la couleur
    suit_color = COLORS.get(spec.suit, "#ffffff")

    # Texte du rang
    if spec.suit == "jokers":
        rank_text = "★"
    else:
        rank_text = RANK_NAMES.get(spec.rank, "?")

    # Symbole de la couleur
    suit_symbols = {
        "clubs": "⬡",      # Hexagone pour CPU
        "diamonds": "◆",    # Diamant pour DATA
        "hearts": "⬢",      # Hexagone plein pour SHIELD
        "spades": "⚛",      # Atome pour QUBIT
        "jokers": "★",
    }
    suit_symbol = suit_symbols.get(spec.suit, "?")

    # Police (fallback système)
    font_size = max(28, w // 16)
    small_font_size = max(16, w // 28)
    try:
        font = ImageFont.truetype("consola.ttf", font_size)
        small_font = ImageFont.truetype("consola.ttf", small_font_size)
    except OSError:
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
            small_font = ImageFont.truetype("DejaVuSansMono.ttf", small_font_size)
        except OSError:
            font = ImageFont.load_default()
            small_font = font

    margin = max(12, w // 30)

    # Index haut-gauche
    draw.text((margin, margin), rank_text, fill=suit_color, font=font)
    draw.text((margin, margin + font_size + 2), suit_symbol, fill=suit_color, font=small_font)

    # Index bas-droite (inversé)
    temp_img = Image.new("RGBA", (font_size * 2, font_size * 2 + small_font_size), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((0, 0), rank_text, fill=suit_color, font=font)
    temp_draw.text((0, font_size + 2), suit_symbol, fill=suit_color, font=small_font)
    temp_img = temp_img.rotate(180, expand=False)
    img.paste(temp_img, (w - margin - font_size * 2, h - margin - font_size * 2 - small_font_size), temp_img)

    # Valeur Bridge (petit, en bas centre)
    bridge_text = str(spec.card_number)
    bbox = draw.textbbox((0, 0), bridge_text, font=small_font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, h - margin - small_font_size), bridge_text, fill="#64748b", font=small_font)

    # Bordure glow
    draw.rectangle([2, 2, w - 3, h - 3], outline=suit_color, width=2)

    img.save(str(image_path))



def main():
    import argparse

    parser = argparse.ArgumentParser(description="Générateur de cartes Nexus")
    parser.add_argument("--suit", choices=["clubs", "diamonds", "hearts", "spades", "jokers", "back", "all"],
                        default="all", help="Couleur à générer (défaut: all)")
    parser.add_argument("--card", type=int, help="Numéro de carte spécifique (1-54)")
    parser.add_argument("--no-post", action="store_true", help="Désactiver le post-traitement Pillow")
    parser.add_argument("--delay", type=float, default=2.0, help="Délai entre les requêtes API (secondes)")
    parser.add_argument("--dry-run", action="store_true", help="Afficher les prompts sans générer")
    args = parser.parse_args()

    print("=" * 60)
    print("🃏 Générateur de Cartes — Nexus: Modern Computation")
    print(f"   Modèle : {GEMINI_MODEL}")
    print(f"   Sortie : {ASSETS_DIR}")
    print("=" * 60)

    # Filtrer les cartes à générer
    if args.card:
        cards = [s for s in CARD_SPECS if s.card_number == args.card]
    elif args.suit == "all":
        cards = list(CARD_SPECS)
    elif args.suit == "back":
        cards = []
    else:
        cards = [s for s in CARD_SPECS if s.suit == args.suit]

    # Mode dry-run
    if args.dry_run:
        for spec in cards:
            print(f"\n{'─' * 40}")
            print(f"Carte #{spec.card_number}: {spec.name_fr}")
            print(f"Concept: {spec.concept}")
            print(f"Prompt:\n{build_prompt(spec)}")
        return

    # Génération
    success = 0
    total = len(cards) + (1 if args.suit in ("all", "back") else 0)

    for i, spec in enumerate(cards, 1):
        output = get_output_path(spec)
        print(f"\n[{i}/{total}] {spec.name_fr} ({spec.concept})")

        if generate_card_image(spec, output):
            if not args.no_post:
                post_process_card(spec, output)
            success += 1

        if i < len(cards):
            time.sleep(args.delay)

    # Génération du dos
    if args.suit in ("all", "back"):
        print(f"\n[{total}/{total}] Dos de carte")
        if generate_back():
            success += 1

    print(f"\n{'=' * 60}")
    print(f"✅ {success}/{total} cartes générées avec succès")
    print(f"📁 Fichiers dans : {ASSETS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
