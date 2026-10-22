"""
config.py — LE SOCLE DU KIT

À quoi sert ce fichier ?
    Il établit la connexion avec Groq, une seule fois, pour tous les autres
    scripts. Aucun script ne se connecte lui-même : ils commencent tous par
    « from config import client, MODEL ».

Ce qu'il produit, et que les autres fichiers importent :
    client   → la connexion configurée (elle sait où écrire et avec quelle clé)
    MODEL    → le nom du modèle à utiliser
    PROVIDER → le nom du fournisseur, pour l'affichage uniquement

À retenir :
    Groq n'est pas un modèle, c'est un hébergeur. Il fait tourner des modèles
    open-weight (GPT-OSS, Qwen…) sur ses serveurs, et nous y donne accès.
"""

# ─────────────────────────── 1. Les librairies ───────────────────────────

import os                            # pour lire les variables d'environnement
from dotenv import load_dotenv       # pour charger le fichier .env
from openai import OpenAI            # la librairie cliente — oui, même pour Groq


# ────────────────────── 2. Charger le fichier .env ───────────────────────

# Lit le fichier .env et place son contenu dans les variables d'environnement.
# C'est ce qui permet de garder la clé API hors du code, donc hors de GitHub.
load_dotenv()


# ──────────────────────── 3. Récupérer la clé ────────────────────────────

# Va chercher la clé dans le .env. Renvoie None si la ligne est absente.
api_key = os.getenv("GROQ_API_KEY")

# Garde-fou : clé absente, ou encore égale au texte d'exemple
# « colle_ta_cle_ici ». On arrête tout de suite avec une consigne précise,
# plutôt que de planter plus loin avec une erreur obscure.
if not api_key or api_key.startswith("colle_"):
    raise SystemExit(
        "❌ GROQ_API_KEY manquante.\n"
        "   1. Crée ta clé sur console.groq.com → API Keys → Create API Key\n"
        "   2. Copie .env.example en .env\n"
        "   3. Colle ta clé sur la ligne GROQ_API_KEY"
    )


# ───────────────── 4. Construire la connexion ────────────────────────────

# ★ LA LIGNE QUI CHANGE TOUT.
#   On utilise la librairie d'OpenAI, mais base_url l'envoie chez Groq.
#   C'est possible parce que Groq accepte le même format de requête : on dit
#   qu'il est « compatible OpenAI », devenu le standard du secteur.
#
#   Conséquence concrète : pour changer d'hébergeur, il suffit d'ajouter une
#   ligne BASE_URL=<autre adresse> dans le .env. Aucune autre ligne de code
#   ne bouge. C'est ce qui vous évite de dépendre d'une seule entreprise.
BASE_URL = os.getenv("BASE_URL", "https://api.groq.com/openai/v1")

client = OpenAI(api_key=api_key, base_url=BASE_URL)


# ──────────────────────── 5. Le modèle choisi ────────────────────────────

# Le nom du modèle. On peut le forcer en ajoutant MODEL=<nom> dans le .env.
# Lancez 02_lister_modeles.py pour voir les noms exacts disponibles.
MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")

# Sert uniquement à l'affichage, dans l'en-tête de l'application Streamlit.
PROVIDER = "Groq"
